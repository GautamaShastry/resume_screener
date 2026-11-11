from app.postings.extraction import extract_posting
from app.postings.models import Posting
from app.postings.sources import fetch_posting
from app.tasks.registry import TaskContext, TaskResult, registry

STEPS = ["Fetching job posting", "Extracting requirements"]
MAX_DESCRIPTION = 50_000


@registry.register("postings.import", steps=STEPS)
async def import_posting(ctx: TaskContext) -> TaskResult:
    data = ctx.task.input
    await ctx.progress("Fetching job posting")
    hints = None
    if data.get("url"):
        hints = await fetch_posting(ctx.services.http, data["url"])
        description = hints.description_text
    else:
        description = data["text"]
    description = description[:MAX_DESCRIPTION]

    await ctx.progress("Extracting requirements")
    extracted = await extract_posting(ctx.services.llm, description, hints, ctx.usage)
    posting = Posting(
        user_id=ctx.task.user_id,
        source=hints.source if hints else "paste",
        source_url=data.get("url"),
        title=data.get("title") or extracted["title"],
        company=data.get("company") or extracted["company"],
        location=extracted["location"],
        description_text=description,
        requirements=extracted["requirements"],
        seniority=extracted["seniority"],
    )
    ctx.session.add(posting)
    await ctx.session.flush()
    return TaskResult({"posting_id": str(posting.id)}, quota_kind="posting_import")
