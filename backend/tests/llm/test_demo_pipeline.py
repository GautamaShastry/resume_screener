from app.llm.demo import demo_llm
from tests.helpers import auth, drain
from tests.postings.fixtures import POSTING_TEXT
from tests.resumes.factories import make_pdf


async def test_demo_llm_runs_the_whole_pipeline(client, services):
    services.llm = demo_llm()
    up = await client.post(
        "/api/resumes",
        headers=auth(),
        files={"file": ("cv.pdf", make_pdf(), "application/pdf")},
        data={"title": "Demo"},
    )
    job = await client.post("/api/postings", headers=auth(), json={"text": POSTING_TEXT})
    await drain(services)
    job_task = (await client.get(f"/api/tasks/{job.json()['task_id']}", headers=auth())).json()
    pid = job_task["result_ref"]["posting_id"]
    posting = (await client.get(f"/api/postings/{pid}", headers=auth())).json()
    assert len(posting["requirements"]) == 4

    r = await client.post(
        "/api/analyses",
        headers=auth(),
        json={"resume_version_id": up.json()["resume_version_id"], "posting_id": pid},
    )
    await drain(services)
    task = (await client.get(f"/api/tasks/{r.json()['task_id']}", headers=auth())).json()
    assert task["status"] == "succeeded", task
    aid = task["result_ref"]["analysis_id"]
    a = (await client.get(f"/api/analyses/{aid}", headers=auth())).json()
    assert 0 <= a["score"] <= 100
    assert any(e["status"] != "missing" for e in a["evidence"])
