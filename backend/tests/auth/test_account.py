import uuid

import pytest
from sqlalchemy import select

from app.auth.models import User
from app.core.errors import NotFound
from app.llm.fake import FakeLLM
from app.resumes.models import ResumeVersion
from tests.helpers import auth, drain
from tests.resumes.factories import make_pdf, resume_llm_response


def _file():
    return {"file": ("cv.pdf", make_pdf(), "application/pdf")}


async def test_delete_account_removes_rows_and_files(client, services, db_session):
    services.llm = FakeLLM({"LLMResume": resume_llm_response()})
    bye, stay = auth("bye@example.com"), auth("stay@example.com")
    r = await client.post("/api/resumes", headers=bye, files=_file(), data={"title": "x"})
    await drain(services)
    keep = await client.post("/api/resumes", headers=stay, files=_file(), data={"title": "y"})
    version = await db_session.get(ResumeVersion, uuid.UUID(r.json()["resume_version_id"]))
    path = version.blob_path

    assert (await client.delete("/api/me", headers=bye)).status_code == 204

    db_session.expire_all()
    emails = (await db_session.execute(select(User.email))).scalars().all()
    assert emails == ["stay@example.com"]
    with pytest.raises(NotFound):
        await services.blob.get(path)
    kept_vid = keep.json()["resume_version_id"]
    other = await client.get(f"/api/resume-versions/{kept_vid}/download", headers=stay)
    assert other.status_code == 200
