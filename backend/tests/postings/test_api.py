import httpx

from app.llm.fake import FakeLLM
from app.postings import fetch
from tests.helpers import auth, drain
from tests.postings.fixtures import (
    GREENHOUSE_JOB,
    POSTING_TEXT,
    mock_client,
    posting_llm_response,
    public_resolver,
)


async def _import_text(client, services, email="a@example.com") -> str:
    services.llm = FakeLLM({"LLMPosting": posting_llm_response()})
    r = await client.post("/api/postings", headers=auth(email), json={"text": POSTING_TEXT})
    assert r.status_code == 202, r.text
    await drain(services)
    task = (await client.get(f"/api/tasks/{r.json()['task_id']}", headers=auth(email))).json()
    assert task["status"] == "succeeded", task
    return task["result_ref"]["posting_id"]


async def test_paste_import_and_read(client, services):
    pid = await _import_text(client, services)
    p = (await client.get(f"/api/postings/{pid}", headers=auth())).json()
    assert p["source"] == "paste"
    assert p["title"] == "Senior Backend Engineer"
    assert p["requirements"][0] == {
        "id": "r1",
        "text": "5+ years of professional Python experience",
        "kind": "must",
        "category": "experience",
        "source_phrase": "5+ years of professional Python experience",
    }
    listing = (await client.get("/api/postings", headers=auth())).json()
    assert listing[0]["requirements_count"] == 4


async def test_linkedin_url_rejected_without_task(client):
    r = await client.post(
        "/api/postings", headers=auth(), json={"url": "https://www.linkedin.com/jobs/view/1"}
    )
    assert r.status_code == 422
    assert r.json()["code"] == "UNSUPPORTED_SOURCE"
    assert (await client.get("/api/tasks", headers=auth())).json() == []


async def test_greenhouse_url_import(client, services, monkeypatch):
    monkeypatch.setattr(fetch, "_resolve", public_resolver)
    services.http = mock_client(
        {
            "https://boards-api.greenhouse.io/v1/boards/acme/jobs/123": httpx.Response(
                200, json=GREENHOUSE_JOB
            )
        }
    )
    services.llm = FakeLLM(
        {
            "LLMPosting": lambda s, u: {
                "title": "",
                "company": "",
                "location": "",
                "seniority": "mid",
                "requirements": [
                    {
                        "text": "Python",
                        "kind": "must",
                        "category": "skill",
                        "source_phrase": "5+ years of professional Python experience",
                    }
                ],
            }
        }
    )
    r = await client.post(
        "/api/postings",
        headers=auth(),
        json={"url": "https://boards.greenhouse.io/acme/jobs/123"},
    )
    await drain(services)
    task = (await client.get(f"/api/tasks/{r.json()['task_id']}", headers=auth())).json()
    p = (
        await client.get(f"/api/postings/{task['result_ref']['posting_id']}", headers=auth())
    ).json()
    assert (p["source"], p["title"], p["company"]) == ("greenhouse", "Backend Engineer", "Acme")
    assert p["source_url"] == "https://boards.greenhouse.io/acme/jobs/123"


async def test_fetch_failure_fails_once_without_retry(client, services, monkeypatch):
    monkeypatch.setattr(fetch, "_resolve", public_resolver)
    services.http = mock_client({})  # everything 404s
    r = await client.post(
        "/api/postings", headers=auth(), json={"url": "https://careers.example.com/job/1"}
    )
    await drain(services)
    task = (await client.get(f"/api/tasks/{r.json()['task_id']}", headers=auth())).json()
    assert task["status"] == "failed" and task["error_code"] == "FETCH_FAILED"
    usage = (await client.get("/api/me/usage", headers=auth())).json()
    assert usage["items"]["posting_import"]["used"] == 0


async def test_validation(client):
    r = await client.post("/api/postings", headers=auth(), json={"text": "too short"})
    assert r.status_code == 422
    assert (await client.post("/api/postings", headers=auth(), json={})).status_code == 422
    both = {"text": POSTING_TEXT, "url": "https://jobs.lever.co/a/b"}
    assert (await client.post("/api/postings", headers=auth(), json=both)).status_code == 422


async def test_cross_user_and_delete(client, services):
    pid = await _import_text(client, services, "owner@example.com")
    other = auth("intruder@example.com")
    owner = auth("owner@example.com")
    assert (await client.get(f"/api/postings/{pid}", headers=other)).status_code == 404
    assert (await client.delete(f"/api/postings/{pid}", headers=other)).status_code == 404
    assert (await client.delete(f"/api/postings/{pid}", headers=owner)).status_code == 204
    assert (await client.get(f"/api/postings/{pid}", headers=owner)).status_code == 404
