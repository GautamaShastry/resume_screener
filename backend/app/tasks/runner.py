import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Literal

from sqlalchemy import and_, func, or_, update

from app.core.errors import AppError
from app.llm.client import LLMUsage
from app.quotas.service import consume
from app.tasks.models import Task
from app.tasks.queue import QueueMessage
from app.tasks.registry import Registration, TaskContext, TaskRegistry

if TYPE_CHECKING:
    from app.core.services import Services

MAX_ATTEMPTS = 3
LEASE_S = 300
LEGACY_STUCK_AFTER = timedelta(minutes=15)
log = logging.getLogger("app.tasks")


@dataclass
class Lease:
    msg: QueueMessage


def _lease_deadline():
    return func.now() + timedelta(seconds=LEASE_S)


async def _claim(services: "Services", task_id: uuid.UUID) -> Literal["claimed", "busy", "done"]:
    """Claim a queued task, or a running task whose worker's lease has expired (crashed worker).

    Returns "busy" when another worker holds a live lease (the message must be kept so it can be
    redelivered if that worker dies) and "done" when the task is finished or gone.
    """
    async with services.sessionmaker() as s:
        res = await s.execute(
            update(Task)
            .where(
                Task.id == task_id,
                or_(
                    Task.status == "queued",
                    and_(Task.status == "running", Task.lease_expires_at < func.now()),
                ),
            )
            .values(
                status="running",
                started_at=func.now(),
                attempts=Task.attempts + 1,
                lease_expires_at=_lease_deadline(),
            )
            .returning(Task.id)
        )
        claimed = res.scalar_one_or_none() is not None
        await s.commit()
        if claimed:
            return "claimed"
        task = await s.get(Task, task_id)
        return "busy" if task is not None and task.status == "running" else "done"


async def renew_lease(services: "Services", task_id: uuid.UUID) -> None:
    async with services.sessionmaker() as s:
        await s.execute(
            update(Task)
            .where(Task.id == task_id, Task.status == "running")
            .values(lease_expires_at=_lease_deadline())
        )
        await s.commit()


def _progress_writer(services: "Services", task_id: uuid.UUID, reg: Registration):
    async def progress(step: str) -> None:
        idx = reg.steps.index(step) if step in reg.steps else 0
        payload = {
            "step": step,
            "steps": reg.steps,
            "percent": int(100 * idx / max(len(reg.steps), 1)),
        }
        async with services.sessionmaker() as s:
            await s.execute(update(Task).where(Task.id == task_id).values(progress=payload))
            await s.commit()

    return progress


async def process_message(services: "Services", registry: TaskRegistry, lease: Lease) -> None:
    task_id = uuid.UUID(lease.msg.body["task_id"])
    outcome = await _claim(services, task_id)
    if outcome == "done":
        await services.queue.delete(lease.msg)
        return
    if outcome == "busy":
        return  # leave the message; it reappears if the lease holder dies

    usage = LLMUsage()
    reg: Registration | None = None
    async with services.sessionmaker() as s:
        task = await s.get(Task, task_id)
        assert task is not None
        task_type = task.type
        try:
            reg = registry.get(task.type)
            ctx = TaskContext(task, s, services, usage, _progress_writer(services, task_id, reg))
            result = await reg.handler(ctx)
            task.status = "succeeded"
            task.result_ref = result.result_ref
            task.progress = {
                "step": reg.steps[-1] if reg.steps else "",
                "steps": reg.steps,
                "percent": 100,
            }
            task.finished_at = datetime.now(UTC)
            task.lease_expires_at = None
            task.tokens_in += usage.tokens_in
            task.tokens_out += usage.tokens_out
            if result.quota_kind:
                await consume(s, task.user_id, result.quota_kind, result.quota_count)
            await s.commit()
        except Exception as exc:  # noqa: BLE001
            await s.rollback()
            await _handle_failure(services, reg, task_id, lease, exc, usage)
            return
    log.info(
        "task_finished",
        extra={
            "task_id": str(task_id),
            "type": task_type,
            "status": "succeeded",
            "tokens_in": usage.tokens_in,
            "tokens_out": usage.tokens_out,
        },
    )
    await services.queue.delete(lease.msg)


async def _handle_failure(
    services: "Services",
    reg: Registration | None,
    task_id: uuid.UUID,
    lease: Lease,
    exc: Exception,
    usage: LLMUsage,
) -> None:
    retryable = exc.retryable if isinstance(exc, AppError) else True
    final = (not retryable) or lease.msg.dequeue_count >= MAX_ATTEMPTS
    async with services.sessionmaker() as s:
        task = await s.get(Task, task_id)
        assert task is not None
        task.tokens_in += usage.tokens_in
        task.tokens_out += usage.tokens_out
        task.lease_expires_at = None
        if final:
            task.status = "failed"
            task.error_code = exc.code if isinstance(exc, AppError) else "INTERNAL"
            task.error_message = (
                exc.message if isinstance(exc, AppError) else "Something went wrong"
            )
            task.finished_at = datetime.now(UTC)
            if reg is not None and reg.on_failed:
                await reg.on_failed(s, task)
        else:
            task.status = "queued"
        await s.commit()
        task_type = task.type
    log.warning(
        "task_attempt_failed",
        extra={
            "task_id": str(task_id),
            "type": task_type,
            "attempt": lease.msg.dequeue_count,
            "final": final,
            "error_type": type(exc).__name__,
        },
        exc_info=not isinstance(exc, AppError),
    )
    if final:
        await services.queue.send_poison(lease.msg.body)
        await services.queue.delete(lease.msg)
        log.error("task_poisoned", extra={"task_id": str(task_id), "type": task_type})
        log.info(
            "task_finished",
            extra={"task_id": str(task_id), "type": task_type, "status": "failed"},
        )
    else:
        # Retry soon instead of waiting out the rest of the visibility timeout.
        backoff = int(services.settings.task_retry_backoff_s * lease.msg.dequeue_count)
        lease.msg = await services.queue.extend(lease.msg, backoff)


async def recover_stuck(services: "Services") -> int:
    """Requeue running tasks whose worker lease expired (crashed worker, lost message)."""
    now = datetime.now(UTC)
    async with services.sessionmaker() as s:
        res = await s.execute(
            update(Task)
            .where(
                Task.status == "running",
                or_(
                    Task.lease_expires_at < now,
                    and_(
                        Task.lease_expires_at.is_(None),
                        Task.started_at < now - LEGACY_STUCK_AFTER,
                    ),
                ),
            )
            .values(status="queued", lease_expires_at=None)
            .returning(Task.id)
        )
        ids = [row[0] for row in res.all()]
        await s.commit()
    for task_id in ids:
        await services.queue.send({"task_id": str(task_id)})
    if ids:
        log.warning("tasks_recovered", extra={"count": len(ids)})
    return len(ids)
