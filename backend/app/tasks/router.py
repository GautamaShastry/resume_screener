import asyncio
import time
import uuid

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.auth.models import User
from app.core.deps import get_services, get_session
from app.core.services import Services
from app.tasks.models import Task
from app.tasks.schemas import TaskOut
from app.tasks.service import get_task_for_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
STREAM_LIMIT_S = 600


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    active: bool = Query(False),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc()).limit(50)
    if active:
        stmt = stmt.where(Task.status.in_(["queued", "running"]))
    return list((await session.execute(stmt)).scalars())


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    return await get_task_for_user(session, task_id, user.id)


@router.get("/{task_id}/events")
async def task_events(
    task_id: uuid.UUID,
    request: Request,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> StreamingResponse:
    await get_task_for_user(session, task_id, user.id)  # 404 before streaming
    user_id = user.id
    poll = services.settings.sse_poll_s

    async def stream():
        last = None
        deadline = time.monotonic() + STREAM_LIMIT_S
        while time.monotonic() < deadline:
            async with services.sessionmaker() as s:
                task = await get_task_for_user(s, task_id, user_id)
                payload = TaskOut.model_validate(task).model_dump_json()
                status = task.status
            if payload != last:
                yield f"event: progress\ndata: {payload}\n\n"
                last = payload
            if status in ("succeeded", "failed"):
                event = "done" if status == "succeeded" else "failed"
                yield f"event: {event}\ndata: {payload}\n\n"
                return
            if await request.is_disconnected():
                return
            await asyncio.sleep(poll)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
