import asyncio
import uuid

from sqlalchemy import update

from app.tasks.models import Task
from app.tasks.service import create_task
from tests.helpers import auth


async def _user_id(client, email="a@example.com") -> uuid.UUID:
    return uuid.UUID((await client.get("/api/me", headers=auth(email))).json()["id"])


async def _task(services, user_id) -> Task:
    async with services.sessionmaker() as s:
        return await create_task(s, services.queue, user_id=user_id, type="t", input={})


async def test_get_and_list_active(client, services):
    uid = await _user_id(client)
    task = await _task(services, uid)
    r = await client.get(f"/api/tasks/{task.id}", headers=auth())
    assert r.status_code == 200
    assert r.json()["status"] == "queued"
    r = await client.get("/api/tasks?active=true", headers=auth())
    assert [t["id"] for t in r.json()] == [str(task.id)]


async def test_other_users_task_is_404(client, services):
    uid = await _user_id(client, "owner@example.com")
    task = await _task(services, uid)
    await _user_id(client, "intruder@example.com")
    r = await client.get(f"/api/tasks/{task.id}", headers=auth("intruder@example.com"))
    assert r.status_code == 404
    r = await client.get(f"/api/tasks/{task.id}/events", headers=auth("intruder@example.com"))
    assert r.status_code == 404


async def test_events_stream_progress_then_done(client, services):
    uid = await _user_id(client)
    task = await _task(services, uid)

    async def finish():
        await asyncio.sleep(0.05)
        async with services.sessionmaker() as s:
            await s.execute(
                update(Task)
                .where(Task.id == task.id)
                .values(status="succeeded", result_ref={"ok": True})
            )
            await s.commit()

    background = asyncio.create_task(finish())
    events: list[str] = []
    async with client.stream("GET", f"/api/tasks/{task.id}/events", headers=auth()) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        async for line in r.aiter_lines():
            if line.startswith("event: "):
                events.append(line[len("event: ") :])
                if events[-1] in ("done", "failed"):
                    break
    await background
    assert events[0] == "progress"
    assert events[-1] == "done"


async def test_events_stream_does_not_hold_a_db_connection(client, services):
    uid = await _user_id(client)
    task = await _task(services, uid)
    services.settings.sse_poll_s = 0.2
    checked_out: list[int] = []

    async def finish():
        # Sample across several poll cycles; between polls the stream must hold nothing.
        for _ in range(40):
            await asyncio.sleep(0.02)
            checked_out.append(services.engine.pool.checkedout())
        async with services.sessionmaker() as s:
            await s.execute(update(Task).where(Task.id == task.id).values(status="succeeded"))
            await s.commit()

    background = asyncio.create_task(finish())
    async with client.stream("GET", f"/api/tasks/{task.id}/events", headers=auth()) as r:
        async for _ in r.aiter_lines():
            pass
    await background
    assert min(checked_out) == 0
