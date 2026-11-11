from typing import Literal

from pydantic import BaseModel, Field

from app.analysis.evidence import render_requirements, render_resume
from app.llm.client import UNTRUSTED_NOTE, LLMClient, LLMUsage, data_block
from app.resumes.structuring import all_bullets


class LLMProject(BaseModel):
    title: str
    scope: str
    deliverables: list[str] = Field(default_factory=list)
    resume_bullet: str


class LLMGapItem(BaseModel):
    requirement_id: str
    type: Literal["not_stated", "real_gap"]
    related_bullet_ids: list[str] = Field(default_factory=list)
    suggested_bullet: str | None = None
    project: LLMProject | None = None


class LLMGaps(BaseModel):
    items: list[LLMGapItem] = Field(default_factory=list)


SYSTEM = f"""You help a job seeker understand gaps between their résumé and a job.
For each listed requirement decide:
- "not_stated": the résumé shows related experience that suggests they likely have it but did not say so. Cite related_bullet_ids from the résumé and write suggested_bullet: one résumé bullet that states it using only facts from those bullets.
- "real_gap": the résumé shows no related experience. Propose a project of about two weeks that would demonstrate the skill: title, scope, deliverables, and the résumé bullet they could add once it is done.
{UNTRUSTED_NOTE}"""  # noqa: E501


async def analyze_gaps(
    llm: LLMClient,
    structured: dict,
    requirements: list[dict],
    evidence: list[dict],
    usage: LLMUsage,
) -> list[dict]:
    status = {e["requirement_id"]: e["status"] for e in evidence}
    targets = [r for r in requirements if status.get(r["id"]) in ("missing", "partial")]
    if not targets:
        return []
    user = (
        f"{data_block('resume', render_resume(structured))}\n\n"
        f"Requirements to analyze:\n{data_block('requirements', render_requirements(targets))}"
    )
    out = await llm.structured(system=SYSTEM, user=user, schema=LLMGaps, usage=usage)
    bullets = all_bullets(structured)
    target_ids = {r["id"] for r in targets}
    gaps: dict[str, dict] = {}
    for item in out.items:
        if item.requirement_id not in target_ids or item.requirement_id in gaps:
            continue
        related = [b for b in dict.fromkeys(item.related_bullet_ids) if b in bullets]
        if item.type == "not_stated" and related and item.suggested_bullet:
            gaps[item.requirement_id] = {
                "requirement_id": item.requirement_id,
                "type": "not_stated",
                "related_bullet_ids": related,
                "related_quotes": [{"bullet_id": b, "text": bullets[b]} for b in related],
                "suggested_bullet": item.suggested_bullet.strip(),
                "project": None,
            }
        elif item.type == "real_gap" and item.project:
            gaps[item.requirement_id] = {
                "requirement_id": item.requirement_id,
                "type": "real_gap",
                "related_bullet_ids": [],
                "related_quotes": [],
                "suggested_bullet": None,
                "project": item.project.model_dump(),
            }
    return [gaps[r["id"]] for r in targets if r["id"] in gaps]
