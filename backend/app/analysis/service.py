import uuid
from collections.abc import Awaitable, Callable
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.dates import years_of_experience
from app.analysis.evidence import collect_evidence
from app.analysis.gaps import analyze_gaps
from app.analysis.models import Analysis
from app.analysis.schemas import AnalysisOut, AnalysisSummary, PostingRef, VersionRef
from app.analysis.scoring import NoRequirements, compute_score, seniority_fit
from app.core.errors import AppError
from app.core.services import Services
from app.llm.client import LLMUsage
from app.postings.models import Posting
from app.resumes.models import Resume, ResumeVersion

PROMPT_VERSION = "analysis-v1"


class NotAnalyzable(AppError):
    status_code = 422
    code = "NOT_ANALYZABLE"


def today() -> date:
    return date.today()


def ensure_analyzable(version: ResumeVersion, posting: Posting) -> None:
    if version.parse_status == "pending":
        raise NotAnalyzable("This résumé is still being processed. Try again in a moment.")
    if version.parse_status == "failed":
        raise NotAnalyzable("We couldn't process this résumé. Upload it again.")
    if not version.structured:
        raise NotAnalyzable(
            "We couldn't read text from this résumé. Upload a text-based PDF or DOCX."
        )
    if not posting.requirements:
        raise NoRequirements("We couldn't find any requirements in this job description.")


async def run_analysis(
    services: Services,
    version: ResumeVersion,
    posting: Posting,
    usage: LLMUsage,
    progress: Callable[[str], Awaitable[None]],
    batch_id: uuid.UUID | None = None,
) -> Analysis:
    ensure_analyzable(version, posting)
    structured = version.structured or {}
    await progress("Matching requirements")
    evidence = await collect_evidence(services.llm, structured, posting.requirements, usage)
    await progress("Checking seniority")
    years = years_of_experience(structured, today())
    fit = seniority_fit(years, posting.seniority)
    await progress("Scoring")
    score, breakdown = compute_score(posting.requirements, evidence, fit)
    breakdown["years_experience"] = years
    await progress("Finding gaps")
    gaps = await analyze_gaps(services.llm, structured, posting.requirements, evidence, usage)
    settings = services.settings
    model = (
        settings.azure_openai_chat_deployment if settings.llm_provider == "azure_openai" else "fake"
    )
    return Analysis(
        user_id=version.user_id,
        resume_version_id=version.id,
        posting_id=posting.id,
        score=score,
        score_breakdown=breakdown,
        evidence=evidence,
        gaps=gaps,
        batch_id=batch_id,
        model=model,
        prompt_version=PROMPT_VERSION,
    )


async def latest_analysis(
    session: AsyncSession, version_id: uuid.UUID, posting_id: uuid.UUID
) -> Analysis | None:
    stmt = (
        select(Analysis)
        .where(Analysis.resume_version_id == version_id, Analysis.posting_id == posting_id)
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def _refs(session: AsyncSession, a: Analysis) -> tuple[Posting, PostingRef, VersionRef]:
    posting = await session.get(Posting, a.posting_id)
    version = await session.get(ResumeVersion, a.resume_version_id)
    assert posting is not None and version is not None
    resume = await session.get(Resume, version.resume_id)
    assert resume is not None
    return (
        posting,
        PostingRef(
            id=posting.id,
            title=posting.title,
            company=posting.company,
            location=posting.location,
            source_url=posting.source_url,
        ),
        VersionRef(
            id=version.id,
            resume_id=resume.id,
            version_no=version.version_no,
            resume_title=resume.title,
        ),
    )


async def analysis_summary(session: AsyncSession, a: Analysis) -> AnalysisSummary:
    _, posting_ref, version_ref = await _refs(session, a)
    return AnalysisSummary(
        id=a.id,
        score=a.score,
        created_at=a.created_at,
        posting=posting_ref,
        resume_version=version_ref,
    )


async def analysis_out(session: AsyncSession, a: Analysis) -> AnalysisOut:
    posting, posting_ref, version_ref = await _refs(session, a)
    return AnalysisOut.model_validate(
        {
            "id": a.id,
            "score": a.score,
            "created_at": a.created_at,
            "posting": posting_ref,
            "resume_version": version_ref,
            "score_breakdown": a.score_breakdown,
            "requirements": posting.requirements,
            "evidence": a.evidence,
            "gaps": a.gaps,
        }
    )
