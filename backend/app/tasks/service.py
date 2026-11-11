import logging
import uuid

from opentelemetry import propagate
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.tasks.models import Task
from app.tasks.queue import TaskQueue

log = logging.getLogger("app.tasks")


async def create_task(
    session: AsyncSession, queue: TaskQueue, *, user_id: uuid.UUID, type: str, input: dict
) -> Task:
    task = Task(user_id=user_id, type=type, status="queued", input=input, progress={})
    session.add(task)
    await session.commit()
    message: dict = {"task_id": str(task.id)}
    propagate.inject(message)
    try:
        await queue.send(message)
    except Exception:
        task.status = "failed"
        task.error_code = "ENQUEUE_FAILED"
        task.error_message = "Could not start the task. Try again."
        await session.commit()
        log.exception("task_enqueue_failed", extra={"task_id": str(task.id), "type": type})
        raise
    log.info("task_created", extra={"task_id": str(task.id), "type": type})
    return task


async def get_task_for_user(session: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
    task = await session.get(Task, task_id)
    if task is None or task.user_id != user_id:
        raise NotFound("Task not found")
    return task
