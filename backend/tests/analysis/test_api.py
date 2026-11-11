from tests.analysis.conftest import full_llm
from tests.helpers import auth, drain
from tests.postings.fixtures import POSTING_TEXT
from tests.resumes.factories import make_image_only_pdf, make_pdf


async def _start(client, vid, pid, email="a@example.com", force=False):
    return await client.post(
        "/api/analyses",
        headers=auth(email),
        json={"resume_version_id": vid, "posting_id": pid, "force": force},
    )


async def _result(client, task_id, email="a@example.com") -> dict:
    return (await client.get(f"/api/tasks/{task_id}", headers=auth(email))).json()


async def test_full_analysis_flow_and_cache(client, services, ready_resume, ready_posting):
    services.llm = full_llm()
    vid, pid = await ready_resume(), await ready_posting()

    r = await _start(client, vid, pid)
    assert r.status_code == 202
    await drain(services)
    aid = (await _result(client, r.json()["task_id"]))["result_ref"]["analysis_id"]

    a = (await client.get(f"/api/analyses/{aid}", headers=auth())).json()
    # coverage = (3*1 + 0 + 3*0.5 + 0) / 10 = 0.45 ; years 8.7 -> senior fit 100 ; 38.25 + 15
    assert a["score"] == 53
    assert a["score_breakdown"]["must_missing_count"] == 1
    assert a["score_breakdown"]["years_experience"] == 8.7
    assert [e["status"] for e in a["evidence"]] == ["met", "missing", "partial", "missing"]
    assert [g["requirement_id"] for g in a["gaps"]] == ["r2", "r3"]
    assert a["posting"]["title"] == "Senior Backend Engineer"
    assert a["resume_version"]["resume_title"] == "Backend"
    assert len(a["requirements"]) == 4

    cached = await _start(client, vid, pid)
    assert cached.status_code == 200 and cached.json() == {"analysis_id": aid, "task_id": None}
    usage = (await client.get("/api/me/usage", headers=auth())).json()
    assert usage["items"]["analysis"]["used"] == 1

    forced = await _start(client, vid, pid, force=True)
    assert forced.status_code == 202

    listing = (await client.get("/api/analyses", headers=auth())).json()
    assert listing[0]["id"] == aid and listing[0]["score"] == 53


async def test_image_only_resume_is_not_analyzable(client, services, ready_resume, ready_posting):
    services.llm = full_llm()
    vid = await ready_resume(data=make_image_only_pdf())
    pid = await ready_posting()
    r = await _start(client, vid, pid)
    assert r.status_code == 422 and r.json()["code"] == "NOT_ANALYZABLE"


async def test_posting_without_requirements_is_refused(client, services, ready_resume):
    services.llm = full_llm()
    vid = await ready_resume()
    services.llm.responders["LLMPosting"] = {"title": "Vague job", "requirements": []}
    r = await client.post("/api/postings", headers=auth(), json={"text": POSTING_TEXT})
    await drain(services)
    pid = (await _result(client, r.json()["task_id"]))["result_ref"]["posting_id"]
    r = await _start(client, vid, pid)
    assert r.status_code == 422 and r.json()["code"] == "NO_REQUIREMENTS"


async def test_pending_resume_is_not_analyzable(client, services, ready_posting):
    services.llm = full_llm()
    pid = await ready_posting()
    r = await client.post(
        "/api/resumes",
        headers=auth(),
        files={"file": ("cv.pdf", make_pdf(), "application/pdf")},
        data={"title": "Not parsed yet"},
    )
    r = await _start(client, r.json()["resume_version_id"], pid)
    assert r.status_code == 422 and "still being processed" in r.json()["message"]


async def test_cross_user_ids_are_404(client, services, ready_resume, ready_posting):
    services.llm = full_llm()
    owner, intruder = "owner@example.com", "intruder@example.com"
    vid = await ready_resume(owner)
    pid = await ready_posting(owner)
    other_pid = await ready_posting(intruder)
    assert (await _start(client, vid, other_pid, intruder)).status_code == 404
    r = await _start(client, vid, pid, owner)
    await drain(services)
    aid = (await _result(client, r.json()["task_id"], owner))["result_ref"]["analysis_id"]
    assert (await client.get(f"/api/analyses/{aid}", headers=auth(intruder))).status_code == 404
    assert (await client.get("/api/analyses", headers=auth(intruder))).json() == []


async def test_llm_failure_fails_task_without_consuming_quota(
    client, services, ready_resume, ready_posting
):
    services.llm = full_llm()
    vid, pid = await ready_resume(), await ready_posting()
    services.llm.responders["LLMEvidence"] = RuntimeError("model down")
    r = await _start(client, vid, pid)
    await drain(services)
    assert (await _result(client, r.json()["task_id"]))["status"] == "failed"
    usage = (await client.get("/api/me/usage", headers=auth())).json()
    assert usage["items"]["analysis"]["used"] == 0
