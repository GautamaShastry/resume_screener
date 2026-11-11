import uuid

import pytest
from sqlalchemy import select

from app.core.errors import NotFound
from app.llm.fake import FakeLLM
from app.resumes.models import ResumeVersion
from app.tasks.models import Task
from tests.helpers import auth, drain
from tests.resumes.factories import make_image_only_pdf, make_pdf, resume_llm_response


def _pdf_upload(data: bytes | None = None, name: str = "cv.pdf"):
    return {"file": (name, data or make_pdf(), "application/pdf")}


async def _upload(client, email="a@example.com", data=None):
    r = await client.post(
        "/api/resumes", headers=auth(email), files=_pdf_upload(data), data={"title": "Backend"}
    )
    assert r.status_code == 202, r.text
    return r.json()


async def test_upload_parse_and_read(client, services):
    services.llm = FakeLLM({"LLMResume": resume_llm_response()})
    started = await _upload(client)
    await drain(services)

    task = (await client.get(f"/api/tasks/{started['task_id']}", headers=auth())).json()
    assert task["status"] == "succeeded"
    assert task["result_ref"]["resume_version_id"] == started["resume_version_id"]

    v = (
        await client.get(f"/api/resume-versions/{started['resume_version_id']}", headers=auth())
    ).json()
    assert v["parse_status"] == "ready"
    assert v["structured"]["skills"][0]["text"] == "Python"
    assert v["ats_report"]["parsed_view"]["fields"]["email"] == "jane@example.com"

    resumes = (await client.get("/api/resumes", headers=auth())).json()
    assert resumes[0]["title"] == "Backend"
    assert resumes[0]["versions"][0]["version_no"] == 1

    usage = (await client.get("/api/me/usage", headers=auth())).json()
    assert usage["items"]["resume_upload"]["used"] == 1


async def test_download_returns_original_bytes(client, services):
    services.llm = FakeLLM({"LLMResume": resume_llm_response()})
    data = make_pdf()
    started = await _upload(client, data=data)
    r = await client.get(
        f"/api/resume-versions/{started['resume_version_id']}/download", headers=auth()
    )
    assert r.status_code == 200
    assert r.content == data
    assert "attachment" in r.headers["content-disposition"]


async def test_new_version_increments(client, services):
    services.llm = FakeLLM({"LLMResume": resume_llm_response()})
    started = await _upload(client)
    r = await client.post(
        f"/api/resumes/{started['resume_id']}/versions", headers=auth(), files=_pdf_upload()
    )
    assert r.status_code == 202
    resume = (await client.get(f"/api/resumes/{started['resume_id']}", headers=auth())).json()
    assert [v["version_no"] for v in resume["versions"]] == [1, 2]


async def test_image_only_pdf_parses_with_no_structure(client, services):
    services.llm = FakeLLM({})  # must not be called
    started = await _upload(client, data=make_image_only_pdf())
    await drain(services)
    v = (
        await client.get(f"/api/resume-versions/{started['resume_version_id']}", headers=auth())
    ).json()
    assert v["parse_status"] == "ready"
    assert v["structured"] is None
    assert any(c["check"] == "no_text" for c in v["ats_report"]["checks"])
    assert services.llm.calls == []


async def test_parse_failure_marks_version_failed(client, services, db_session):
    services.llm = FakeLLM({"LLMResume": RuntimeError("model down")})
    started = await _upload(client)
    await drain(services)
    version = await db_session.get(ResumeVersion, uuid.UUID(started["resume_version_id"]))
    assert version.parse_status == "failed"
    task = await db_session.get(Task, uuid.UUID(started["task_id"]))
    assert (task.status, task.attempts) == ("failed", 3)
    usage = (await client.get("/api/me/usage", headers=auth())).json()
    assert usage["items"]["resume_upload"]["used"] == 0


async def test_rejects_non_pdf_docx_and_large_files(client):
    r = await client.post(
        "/api/resumes",
        headers=auth(),
        files={"file": ("cv.pdf", b"hello", "application/pdf")},
        data={"title": "x"},
    )
    assert r.status_code == 422 and r.json()["code"] == "VALIDATION"
    big = b"%PDF-" + b"0" * (5 * 1024 * 1024)
    r = await client.post(
        "/api/resumes", headers=auth(), files=_pdf_upload(big), data={"title": "x"}
    )
    assert r.status_code == 422


async def test_quota_blocks_upload(client, services, settings):
    settings.quota_limits["resume_upload"] = 1
    services.llm = FakeLLM({"LLMResume": resume_llm_response()})
    await _upload(client)
    await drain(services)
    r = await client.post("/api/resumes", headers=auth(), files=_pdf_upload(), data={"title": "x"})
    assert r.status_code == 429
    assert r.json()["code"] == "QUOTA_EXCEEDED"


async def test_cross_user_access_is_404(client, services):
    started = await _upload(client, email="owner@example.com")
    other = auth("intruder@example.com")
    rid, vid = started["resume_id"], started["resume_version_id"]
    assert (await client.get(f"/api/resumes/{rid}", headers=other)).status_code == 404
    assert (await client.get(f"/api/resume-versions/{vid}", headers=other)).status_code == 404
    assert (
        await client.get(f"/api/resume-versions/{vid}/download", headers=other)
    ).status_code == 404
    assert (
        await client.patch(f"/api/resumes/{rid}", headers=other, json={"title": "x"})
    ).status_code == 404
    assert (await client.delete(f"/api/resumes/{rid}", headers=other)).status_code == 404
    assert (await client.get("/api/resumes", headers=other)).json() == []


async def test_patch_and_delete_removes_blobs(client, services, db_session):
    services.llm = FakeLLM({"LLMResume": resume_llm_response()})
    started = await _upload(client)
    r = await client.patch(
        f"/api/resumes/{started['resume_id']}",
        headers=auth(),
        json={"title": "New", "archived": True},
    )
    assert r.json()["title"] == "New" and r.json()["archived"] is True
    version = await db_session.get(ResumeVersion, uuid.UUID(started["resume_version_id"]))
    path = version.blob_path
    r = await client.delete(f"/api/resumes/{started['resume_id']}", headers=auth())
    assert r.status_code == 204
    db_session.expire_all()
    assert (await db_session.execute(select(ResumeVersion))).first() is None
    with pytest.raises(NotFound):
        await services.blob.get(path)
