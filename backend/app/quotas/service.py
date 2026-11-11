import uuid
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import QuotaExceeded
from app.core.settings import Settings
from app.quotas.models import Usage
from app.tasks.models import Task

# Tasks still queued/running count against the quota so bursts can't overspend.
TASK_TYPE_FOR_KIND = {
    "resume_upload": "resume.parse",
    "posting_import": "postings.import",
    "analysis": "analysis.run",
}


def utc_today() -> date:
    return datetime.now(UTC).date()


def next_reset() -> datetime:
    return datetime.combine(utc_today() + timedelta(days=1), time(0, 0), tzinfo=UTC)


async def _used(session: AsyncSession, user_id: uuid.UUID, kind: str) -> int:
    stmt = select(Usage.count).where(
        Usage.user_id == user_id, Usage.day == utc_today(), Usage.kind == kind
    )
    return (await session.execute(stmt)).scalar_one_or_none() or 0


async def _inflight(session: AsyncSession, user_id: uuid.UUID, kind: str) -> int:
    task_type = TASK_TYPE_FOR_KIND.get(kind)
    if task_type is None:
        return 0
    stmt = select(func.count()).where(
        Task.user_id == user_id, Task.type == task_type, Task.status.in_(["queued", "running"])
    )
    return (await session.execute(stmt)).scalar_one()


async def check_quota(
    session: AsyncSession, settings: Settings, user_id: uuid.UUID, kind: str, n: int = 1
) -> None:
    limit = settings.quota_limits[kind]
    used = await _used(session, user_id, kind) + await _inflight(session, user_id, kind)
    if used + n > limit:
        raise QuotaExceeded(
            "You've reached today's limit for this action.",
            {"kind": kind, "limit": limit, "used": used, "resets_at": next_reset().isoformat()},
        )


async def consume(session: AsyncSession, user_id: uuid.UUID, kind: str, n: int = 1) -> None:
    stmt = (
        insert(Usage)
        .values(user_id=user_id, day=utc_today(), kind=kind, count=n)
        .on_conflict_do_update(
            index_elements=[Usage.user_id, Usage.day, Usage.kind],
            set_={"count": Usage.count + n},
        )
    )
    await session.execute(stmt)


async def usage_today(
    session: AsyncSession, settings: Settings, user_id: uuid.UUID
) -> dict[str, dict]:
    rows = (
        await session.execute(
            select(Usage.kind, Usage.count).where(
                Usage.user_id == user_id, Usage.day == utc_today()
            )
        )
    ).all()
    used = {kind: count for kind, count in rows}
    return {
        kind: {"used": used.get(kind, 0), "limit": limit}
        for kind, limit in settings.quota_limits.items()
    }
