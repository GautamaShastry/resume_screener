import uuid

from app.analysis.service import run_analysis
from app.core.errors import NotFound
from app.postings.models import Posting
from app.resumes.models import ResumeVersion
from app.tasks.registry import TaskContext, TaskResult, registry

STEPS = ["Matching requirements", "Checking seniority", "Scoring", "Finding gaps"]


@registry.register("analysis.run", steps=STEPS)
async def analyze(ctx: TaskContext) -> TaskResult:
    data = ctx.task.input
    version = await ctx.session.get(ResumeVersion, uuid.UUID(data["resume_version_id"]))
    posting = await ctx.session.get(Posting, uuid.UUID(data["posting_id"]))
    owner = ctx.task.user_id
    if version is None or posting is None or version.user_id != owner or posting.user_id != owner:
        raise NotFound("Résumé or job not found")
    batch = uuid.UUID(data["batch_id"]) if data.get("batch_id") else None
    analysis = await run_analysis(ctx.services, version, posting, ctx.usage, ctx.progress, batch)
    ctx.session.add(analysis)
    await ctx.session.flush()
    return TaskResult({"analysis_id": str(analysis.id)}, quota_kind="analysis")
