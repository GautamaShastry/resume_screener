import asyncio
from typing import Literal

from pydantic import BaseModel, Field

from app.llm.client import UNTRUSTED_NOTE, LLMClient, LLMUsage, data_block
from app.resumes.structuring import all_bullets

CHUNK_SIZE = 15


class LLMEvidenceItem(BaseModel):
    requirement_id: str
    status: Literal["met", "partial", "missing"]
    bullet_ids: list[str] = Field(default_factory=list)
    note: str = ""


class LLMEvidence(BaseModel):
    items: list[LLMEvidenceItem] = Field(default_factory=list)


SYSTEM = f"""You check whether a résumé demonstrates each job requirement.
For every requirement listed, return one item:
- status "met" when the résumé clearly demonstrates it, "partial" when there is related but weaker evidence, "missing" when there is none.
- bullet_ids: IDs (like b7) of résumé lines that directly support it. Only use IDs that appear in the résumé. Use [] for missing.
- note: one short sentence explaining the judgement.
{UNTRUSTED_NOTE}"""  # noqa: E501


def render_resume(structured: dict) -> str:
    lines: list[str] = []
    if structured.get("summary"):
        lines += ["## Summary", f"[{structured['summary']['id']}] {structured['summary']['text']}"]
    if structured.get("skills"):
        lines.append("## Skills")
        lines += [f"[{s['id']}] {s['text']}" for s in structured["skills"]]
    for section in structured.get("sections", []):
        lines.append(f"## {section['title']}")
        for entry in section["entries"]:
            dates = " – ".join(d for d in (entry.get("start"), entry.get("end")) if d)
            header = ", ".join(x for x in (entry.get("role"), entry.get("org")) if x)
            lines.append(f"# {header}" + (f" ({dates})" if dates else ""))
            lines += [f"[{b['id']}] {b['text']}" for b in entry["bullets"]]
    return "\n".join(lines)


def render_requirements(requirements: list[dict]) -> str:
    return "\n".join(f"[{r['id']}] ({r['kind']}) {r['text']}" for r in requirements)


async def collect_evidence(
    llm: LLMClient,
    structured: dict,
    requirements: list[dict],
    usage: LLMUsage,
    chunk_size: int = CHUNK_SIZE,
) -> list[dict]:
    bullets = all_bullets(structured)
    resume_block = data_block("resume", render_resume(structured))
    chunks = [requirements[i : i + chunk_size] for i in range(0, len(requirements), chunk_size)]

    async def run(chunk: list[dict]) -> LLMEvidence:
        reqs_block = data_block("requirements", render_requirements(chunk))
        user = f"{resume_block}\n\nRequirements:\n{reqs_block}"
        return await llm.structured(system=SYSTEM, user=user, schema=LLMEvidence, usage=usage)

    results = await asyncio.gather(*(run(c) for c in chunks))
    found: dict[str, LLMEvidenceItem] = {}
    for chunk, result in zip(chunks, results, strict=True):
        allowed = {r["id"] for r in chunk}
        for item in result.items:
            if item.requirement_id in allowed:
                found[item.requirement_id] = item

    evidence = []
    for req in requirements:
        item = found.get(req["id"])
        if item is None:
            evidence.append(
                {"requirement_id": req["id"], "status": "missing", "quotes": [], "note": ""}
            )
            continue
        quotes = [
            {"bullet_id": b, "text": bullets[b]}
            for b in dict.fromkeys(item.bullet_ids)
            if b in bullets
        ]
        status = item.status if (quotes or item.status == "missing") else "missing"
        evidence.append(
            {
                "requirement_id": req["id"],
                "status": status,
                "quotes": quotes,
                "note": item.note[:300],
            }
        )
    return evidence
