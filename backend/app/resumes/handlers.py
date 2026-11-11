import asyncio
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.resumes.ats import build_ats_report
from app.resumes.extract import extract
from app.resumes.models import ResumeVersion
from app.resumes.structuring import structure_resume
from app.tasks.models import Task
from app.tasks.registry import TaskContext, TaskResult, registry

log = logging.getLogger("app.resumes")
STEPS = ["Extracting text", "Checking ATS compatibility", "Structuring résumé"]


async def _mark_failed(session: AsyncSession, task: Task) -> None:
    version = await session.get(ResumeVersion, uuid.UUID(task.input["resume_version_id"]))
    if version is not None:
        version.parse_status = "failed"


@registry.register("resume.parse", steps=STEPS, on_failed=_mark_failed)
async def parse_resume(ctx: TaskContext) -> TaskResult:
    version = await ctx.session.get(ResumeVersion, uuid.UUID(ctx.task.input["resume_version_id"]))
    if version is None or version.user_id != ctx.task.user_id:
        raise NotFound("Résumé version not found")
    data = await ctx.services.blob.get(version.blob_path)

    await ctx.progress("Extracting text")
    doc = await asyncio.to_thread(extract, data, version.file_type)

    await ctx.progress("Checking ATS compatibility")
    report = build_ats_report(doc)
    version.text = doc.full_text
    version.ats_report = report

    await ctx.progress("Structuring résumé")
    if any(c["check"] == "no_text" for c in report["checks"]):
        version.structured = None
    else:
        structured, dropped = await structure_resume(ctx.services.llm, doc.full_text, ctx.usage)
        version.structured = structured
        log.info(
            "resume_structured",
            extra={"resume_version_id": str(version.id), "dropped_bullets": dropped},
        )
    version.parse_status = "ready"
    return TaskResult(
        {"resume_id": str(version.resume_id), "resume_version_id": str(version.id)},
        quota_kind="resume_upload",
    )
