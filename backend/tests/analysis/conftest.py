import re
from datetime import date

import pytest

from app.analysis import service as analysis_service
from app.llm.fake import FakeLLM
from tests.helpers import auth, drain
from tests.postings.fixtures import POSTING_TEXT, posting_llm_response
from tests.resumes.factories import make_pdf, resume_llm_response

# IDs produced by resume_llm_response(): summary b1, skills b2-b6, Acme b7-b8, Beta b9


def evidence_responder(system: str, user: str) -> dict:
    statuses = {
        "r1": ("met", ["b7", "b999"]),  # b999 does not exist -> dropped
        "r2": ("met", []),  # met without quotes -> downgraded to missing
        "r3": ("partial", ["b8"]),
        "r4": ("missing", []),
    }
    ids = re.findall(r"^\[(r\d+)\]", user, re.M)
    return {
        "items": [
            {
                "requirement_id": rid,
                "status": statuses.get(rid, ("missing", []))[0],
                "bullet_ids": statuses.get(rid, ("missing", []))[1],
                "note": f"note {rid}",
            }
            for rid in ids
        ]
    }


def gaps_responder(system: str, user: str) -> dict:
    return {
        "items": [
            {
                "requirement_id": "r2",
                "type": "not_stated",
                "related_bullet_ids": ["b7"],
                "suggested_bullet": "Built REST APIs with FastAPI.",
            },
            {
                "requirement_id": "r3",
                "type": "real_gap",
                "related_bullet_ids": [],
                "project": {
                    "title": "Tune a Postgres workload",
                    "scope": "Two weeks",
                    "deliverables": ["Benchmark report"],
                    "resume_bullet": "Cut query latency 40%.",
                },
            },
            {"requirement_id": "r4", "type": "not_stated", "related_bullet_ids": ["b999"]},
            {"requirement_id": "r1", "type": "real_gap", "related_bullet_ids": []},
        ]
    }


def full_llm() -> FakeLLM:
    return FakeLLM(
        {
            "LLMResume": resume_llm_response(),
            "LLMPosting": posting_llm_response(),
            "LLMEvidence": evidence_responder,
            "LLMGaps": gaps_responder,
        }
    )


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    monkeypatch.setattr(analysis_service, "today", lambda: date(2025, 1, 1))


@pytest.fixture
def ready_resume(client, services):
    async def _make(email: str = "a@example.com", data: bytes | None = None) -> str:
        r = await client.post(
            "/api/resumes",
            headers=auth(email),
            files={"file": ("cv.pdf", data or make_pdf(), "application/pdf")},
            data={"title": "Backend"},
        )
        await drain(services)
        return r.json()["resume_version_id"]

    return _make


@pytest.fixture
def ready_posting(client, services):
    async def _make(email: str = "a@example.com") -> str:
        r = await client.post("/api/postings", headers=auth(email), json={"text": POSTING_TEXT})
        await drain(services)
        task = (await client.get(f"/api/tasks/{r.json()['task_id']}", headers=auth(email))).json()
        return task["result_ref"]["posting_id"]

    return _make
