import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.auth.models import User
from app.core.deps import get_services, get_session
from app.core.ownership import get_owned
from app.core.services import Services
from app.postings.models import Posting
from app.postings.schemas import PostingCreate, PostingOut, PostingSummary
from app.postings.sources import detect_source
from app.quotas.service import check_quota
from app.tasks.schemas import TaskStarted
from app.tasks.service import create_task

router = APIRouter(prefix="/api/postings", tags=["postings"])


@router.get("", response_model=list[PostingSummary])
async def list_postings(
    user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> list[PostingSummary]:
    rows = (
        await session.execute(
            select(Posting).where(Posting.user_id == user.id).order_by(Posting.created_at.desc())
        )
    ).scalars()
    return [
        PostingSummary(
            id=p.id,
            title=p.title,
            company=p.company,
            location=p.location,
            source=p.source,
            source_url=p.source_url,
            requirements_count=len(p.requirements or []),
            created_at=p.created_at,
        )
        for p in rows
    ]


@router.post("", response_model=TaskStarted, status_code=status.HTTP_202_ACCEPTED)
async def create_posting(
    body: PostingCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> TaskStarted:
    if body.url:
        detect_source(body.url)  # raises UnsupportedSource immediately
    await check_quota(session, services.settings, user.id, "posting_import")
    task = await create_task(
        session,
        services.queue,
        user_id=user.id,
        type="postings.import",
        input=body.model_dump(exclude_none=True),
    )
    return TaskStarted(task_id=task.id)


@router.get("/{posting_id}", response_model=PostingOut)
async def get_posting(
    posting_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> Posting:
    return await get_owned(session, Posting, posting_id, user.id)


@router.delete("/{posting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_posting(
    posting_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    posting = await get_owned(session, Posting, posting_id, user.id)
    await session.delete(posting)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
