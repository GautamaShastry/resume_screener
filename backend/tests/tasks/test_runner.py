import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select, update

from app.core.errors import UnsupportedSource
from app.quotas.service import usage_today
from app.resumes.models import Resume
from app.tasks.models import Task
from app.tasks.queue import InMemoryQueue
from app.tasks.registry import TaskRegistry, TaskResult
from app.tasks.runner import recover_stuck
from app.tasks.service import create_task
from app.worker import run_worker
from tests.helpers import drain


@pytest.fixture
def reg():
    return TaskRegistry()


async def _task(services, user, type_: str) -> Task:
    async with services.sessionmaker() as s:
        return await create_task(s, services.queue, user_id=user.id, type=type_, input={"a": 1})


async def _get(services, task_id) -> Task:
    async with services.sessionmaker() as s:
        return await s.get(Task, task_id)


async def test_success_commits_result_progress_and_quota(services, make_user, reg):
    user = await make_user()

    @reg.register("test.ok", steps=["One", "Two"])
    async def ok(ctx):
        await ctx.progress("One")
        assert (await _get(services, ctx.task.id)).progress["percent"] == 0
        await ctx.progress("Two")
        ctx.session.add(Resume(user_id=ctx.task.user_id, title="made"))
        return TaskResult({"x": 1}, quota_kind="analysis")

    task = await _task(services, user, "test.ok")
    await drain(services, reg)

    t = await _get(services, task.id)
    assert t.status == "succeeded"
    assert t.result_ref == {"x": 1}
    assert t.progress["percent"] == 100
    assert t.attempts == 1
    assert t.finished_at is not None
    async with services.sessionmaker() as s:
        assert (await usage_today(s, services.settings, user.id))["analysis"]["used"] == 1
        assert (await s.execute(select(Resume.title))).scalar_one() == "made"
    assert len(services.queue) == 0


async def test_duplicate_delivery_runs_handler_once(services, make_user, reg):
    user = await make_user()
    calls: list[int] = []

    @reg.register("test.count", steps=["Run"])
    async def count(ctx):
        calls.append(1)
        return TaskResult({}, quota_kind="analysis")

    task = await _task(services, user, "test.count")
    await services.queue.send({"task_id": str(task.id)})
    await drain(services, reg)
    assert calls == [1]
    assert len(services.queue) == 0
    async with services.sessionmaker() as s:
        assert (await usage_today(s, services.settings, user.id))["analysis"]["used"] == 1


async def test_failure_retries_rolls_back_and_poisons(services, make_user, reg):
    user = await make_user()
    hooked: list = []

    async def on_failed(session, task):
        hooked.append(task.id)

    @reg.register("test.fail", steps=["Run"], on_failed=on_failed)
    async def fail(ctx):
        ctx.session.add(Resume(user_id=ctx.task.user_id, title="partial"))
        await ctx.session.flush()
        raise RuntimeError("secret detail")

    task = await _task(services, user, "test.fail")
    await drain(services, reg)

    t = await _get(services, task.id)
    assert t.status == "failed"
    assert t.attempts == 3
    assert t.error_code == "INTERNAL"
    assert t.error_message == "Something went wrong"
    assert hooked == [task.id]
    assert [m["task_id"] for m in services.queue.poison] == [str(task.id)]
    async with services.sessionmaker() as s:
        assert (await s.execute(select(Resume))).first() is None


async def test_non_retryable_app_error_fails_immediately(services, make_user, reg):
    user = await make_user()

    @reg.register("test.permanent", steps=["Run"])
    async def permanent(ctx):
        raise UnsupportedSource("Paste the description instead.")

    task = await _task(services, user, "test.permanent")
    await drain(services, reg)
    t = await _get(services, task.id)
    assert (t.status, t.attempts, t.error_code) == ("failed", 1, "UNSUPPORTED_SOURCE")
    assert t.error_message == "Paste the description instead."


async def test_recover_stuck_requeues(services, make_user, reg):
    user = await make_user()
    task = await _task(services, user, "test.any")
    services.queue = InMemoryQueue()
    async with services.sessionmaker() as s:
        await s.execute(
            update(Task)
            .where(Task.id == task.id)
            .values(status="running", started_at=datetime.now(UTC) - timedelta(minutes=20))
        )
        await s.commit()
    assert await recover_stuck(services) == 1
    assert (await _get(services, task.id)).status == "queued"
    assert len(services.queue) == 1


async def test_run_worker_processes_then_stops(services, make_user, reg):
    user = await make_user()

    @reg.register("test.loop", steps=["Run"])
    async def loop_handler(ctx):
        return TaskResult({"done": True})

    task = await _task(services, user, "test.loop")
    stop = asyncio.Event()
    worker = asyncio.create_task(run_worker(services, reg, stop=stop, poll_interval=0.01))
    for _ in range(300):
        if (await _get(services, task.id)).status == "succeeded":
            break
        await asyncio.sleep(0.01)
    stop.set()
    await asyncio.wait_for(worker, 5)
    assert (await _get(services, task.id)).status == "succeeded"
