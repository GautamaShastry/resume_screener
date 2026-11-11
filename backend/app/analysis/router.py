import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.models import Analysis
from app.analysis.schemas import (
    AnalysisCreate,
    AnalysisOut,
    AnalysisStartOut,
    AnalysisSummary,
)
from app.analysis.service import (
    analysis_out,
    analysis_summary,
    ensure_analyzable,
    latest_analysis,
)
from app.auth.deps import current_user
from app.auth.models import User
from app.core.deps import get_services, get_session
from app.core.ownership import get_owned
from app.core.services import Services
from app.postings.models import Posting
from app.quotas.service import check_quota
from app.resumes.models import ResumeVersion
from app.tasks.service import create_task

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


@router.post(
    "",
    response_model=AnalysisStartOut,
    responses={status.HTTP_202_ACCEPTED: {"model": AnalysisStartOut}},
)
async def start_analysis(
    body: AnalysisCreate,
    response: Response,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> AnalysisStartOut:
    version = await get_owned(session, ResumeVersion, body.resume_version_id, user.id)
    posting = await get_owned(session, Posting, body.posting_id, user.id)
    ensure_analyzable(version, posting)
    if not body.force:
        existing = await latest_analysis(session, version.id, posting.id)
        if existing is not None:
            return AnalysisStartOut(analysis_id=existing.id)
    await check_quota(session, services.settings, user.id, "analysis")
    task = await create_task(
        session,
        services.queue,
        user_id=user.id,
        type="analysis.run",
        input={"resume_version_id": str(version.id), "posting_id": str(posting.id)},
    )
    response.status_code = status.HTTP_202_ACCEPTED
    return AnalysisStartOut(task_id=task.id)


@router.get("", response_model=list[AnalysisSummary])
async def list_analyses(
    resume_version_id: uuid.UUID | None = Query(None),
    posting_id: uuid.UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> list[AnalysisSummary]:
    stmt = select(Analysis).where(Analysis.user_id == user.id)
    if resume_version_id:
        stmt = stmt.where(Analysis.resume_version_id == resume_version_id)
    if posting_id:
        stmt = stmt.where(Analysis.posting_id == posting_id)
    rows = (await session.execute(stmt.order_by(Analysis.created_at.desc()).limit(limit))).scalars()
    return [await analysis_summary(session, a) for a in rows]


@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> AnalysisOut:
    analysis = await get_owned(session, Analysis, analysis_id, user.id)
    return await analysis_out(session, analysis)
