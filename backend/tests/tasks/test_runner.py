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


async def _force_running(services, task_id, lease_delta: timedelta) -> None:
    async with services.sessionmaker() as s:
        await s.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(
                status="running",
                attempts=1,
                started_at=datetime.now(UTC),
                lease_expires_at=datetime.now(UTC) + lease_delta,
            )
        )
        await s.commit()


async def test_task_of_crashed_worker_is_reclaimed_after_lease_expiry(services, make_user, reg):
    """A worker killed mid-task leaves status=running; the redelivered message must re-run it."""
    user = await make_user()
    calls: list[int] = []

    @reg.register("test.crash", steps=["Run"])
    async def crash(ctx):
        calls.append(1)
        return TaskResult({"ok": True})

    task = await _task(services, user, "test.crash")
    await _force_running(services, task.id, timedelta(seconds=-1))  # lease expired
    await drain(services, reg)
    t = await _get(services, task.id)
    assert calls == [1]
    assert (t.status, t.attempts) == ("succeeded", 2)


async def test_live_lease_keeps_message_for_later(services, make_user, reg):
    user = await make_user()
    calls: list[int] = []

    @reg.register("test.live", steps=["Run"])
    async def live(ctx):
        calls.append(1)
        return TaskResult({})

    task = await _task(services, user, "test.live")
    await _force_running(services, task.id, timedelta(minutes=5))  # another worker holds it
    [msg] = await services.queue.receive(1, 0)
    from app.tasks.runner import Lease, process_message

    await process_message(services, reg, Lease(msg))
    assert calls == []
    assert len(services.queue) == 1  # message not deleted


async def test_commit_failure_is_a_task_failure_not_a_stuck_task(services, make_user, reg):
    import uuid as _uuid

    user = await make_user()

    @reg.register("test.badcommit", steps=["Run"])
    async def bad(ctx):
        ctx.session.add(Resume(user_id=_uuid.uuid4(), title="orphan"))  # FK violation at commit
        return TaskResult({})

    task = await _task(services, user, "test.badcommit")
    await drain(services, reg)
    t = await _get(services, task.id)
    assert t.status == "failed" and t.attempts == 3


async def test_unknown_task_type_fails_instead_of_sticking(services, make_user, reg):
    user = await make_user()
    task = await _task(services, user, "test.unregistered")
    await drain(services, reg)
    assert (await _get(services, task.id)).status == "failed"


async def test_failed_attempt_retries_after_short_backoff_not_full_lease(services, make_user, reg):
    from app.tasks.runner import Lease, process_message
    from tests.tasks.test_queue import Clock

    user = await make_user()
    services.settings.task_retry_backoff_s = 10
    clock = Clock()
    services.queue = InMemoryQueue(clock=clock)

    @reg.register("test.flaky", steps=["Run"])
    async def flaky(ctx):
        raise RuntimeError("transient")

    task = await _task(services, user, "test.flaky")
    [msg] = await services.queue.receive(1, 300)
    await process_message(services, reg, Lease(msg))
    assert (await _get(services, task.id)).status == "queued"
    clock.t = 9
    assert await services.queue.receive(1, 300) == []
    clock.t = 11
    assert len(await services.queue.receive(1, 300)) == 1
