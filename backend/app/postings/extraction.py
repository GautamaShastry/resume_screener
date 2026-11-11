from typing import Literal

from pydantic import BaseModel, Field

from app.llm.client import UNTRUSTED_NOTE, LLMClient, LLMUsage, data_block
from app.postings.sources import FetchedPosting
from app.resumes.structuring import is_grounded, normalize

PROMPT_VERSION = "posting-v1"


class LLMRequirement(BaseModel):
    text: str
    kind: Literal["must", "nice"]
    category: Literal["skill", "experience", "education", "other"]
    source_phrase: str


class LLMPosting(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    seniority: Literal["intern", "junior", "mid", "senior", "staff+", "unknown"] = "unknown"
    requirements: list[LLMRequirement] = Field(default_factory=list)


SYSTEM = f"""You extract the requirements of a job posting.
Rules:
- Each requirement is ONE atomic, checkable qualification (a skill, an amount of experience, a degree, a certification).
- kind "must" when phrased as required / must / minimum, or when not qualified; "nice" for preferred / bonus / plus / nice to have.
- source_phrase is copied VERBATIM from the description and is the phrase the requirement came from.
- Ignore benefits, company descriptions, salary, and equal-opportunity statements.
- seniority: intern, junior, mid, senior, staff+ (staff/principal/lead), or unknown.
{UNTRUSTED_NOTE}"""  # noqa: E501


async def extract_posting(
    llm: LLMClient, description: str, hints: FetchedPosting | None, usage: LLMUsage
) -> dict:
    out = await llm.structured(
        system=SYSTEM,
        user=data_block("job_description", description),
        schema=LLMPosting,
        usage=usage,
    )
    source = normalize(description)
    requirements = []
    for req in out.requirements:
        if not is_grounded(req.source_phrase, source):
            continue
        requirements.append(
            {
                "id": f"r{len(requirements) + 1}",
                "text": req.text.strip(),
                "kind": req.kind,
                "category": req.category,
                "source_phrase": req.source_phrase.strip(),
            }
        )
    return {
        "title": (hints.title if hints and hints.title else out.title)[:300],
        "company": (hints.company if hints and hints.company else out.company)[:200],
        "location": (hints.location if hints and hints.location else out.location)[:200],
        "seniority": out.seniority,
        "requirements": requirements,
    }
