import re
from typing import Literal

from pydantic import BaseModel, Field
from rapidfuzz import fuzz

from app.llm.client import UNTRUSTED_NOTE, LLMClient, LLMUsage, data_block

PROMPT_VERSION = "structure-v1"
GROUNDING_MIN = 90


class LLMContact(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[str] = Field(default_factory=list)


class LLMEntry(BaseModel):
    org: str = ""
    role: str = ""
    start: str = ""
    end: str = ""
    location: str = ""
    bullets: list[str] = Field(default_factory=list)


class LLMSection(BaseModel):
    kind: Literal["experience", "education", "projects", "other"]
    title: str
    entries: list[LLMEntry] = Field(default_factory=list)


class LLMResume(BaseModel):
    contact: LLMContact = Field(default_factory=LLMContact)
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    sections: list[LLMSection] = Field(default_factory=list)


SYSTEM = f"""You convert résumé text into structured JSON.
Rules:
- Copy every bullet, the summary, and each skill VERBATIM from the résumé. Do not rephrase, merge, split, or add content.
- A bullet is one accomplishment or responsibility line under a job, project, or education entry.
- Use kind "experience" for jobs, "education" for schooling, "projects" for projects, "other" for anything else.
- Leave a field empty if the résumé does not state it.
{UNTRUSTED_NOTE}"""  # noqa: E501


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def is_grounded(snippet: str, normalized_source: str) -> bool:
    s = normalize(snippet)
    return bool(s) and fuzz.partial_ratio(s, normalized_source) >= GROUNDING_MIN


async def structure_resume(llm: LLMClient, text: str, usage: LLMUsage) -> tuple[dict, int]:
    out = await llm.structured(
        system=SYSTEM, user=data_block("resume", text), schema=LLMResume, usage=usage
    )
    source = normalize(text)
    counter = 0
    dropped = 0

    def next_id() -> str:
        nonlocal counter
        counter += 1
        return f"b{counter}"

    summary = (
        {"id": next_id(), "text": out.summary.strip()} if is_grounded(out.summary, source) else None
    )
    skills = [{"id": next_id(), "text": s.strip()} for s in out.skills if is_grounded(s, source)]
    sections = []
    for si, section in enumerate(out.sections, 1):
        entries = []
        for ei, entry in enumerate(section.entries, 1):
            bullets = []
            for bullet in entry.bullets:
                if is_grounded(bullet, source):
                    bullets.append({"id": next_id(), "text": bullet.strip()})
                else:
                    dropped += 1
            entries.append(
                {
                    "id": f"s{si}e{ei}",
                    "org": entry.org,
                    "role": entry.role,
                    "start": entry.start,
                    "end": entry.end,
                    "location": entry.location,
                    "bullets": bullets,
                }
            )
        sections.append(
            {"id": f"s{si}", "kind": section.kind, "title": section.title, "entries": entries}
        )
    structured = {
        "contact": out.contact.model_dump(),
        "summary": summary,
        "skills": skills,
        "sections": sections,
    }
    return structured, dropped


def all_bullets(structured: dict) -> dict[str, str]:
    items: dict[str, str] = {}
    if structured.get("summary"):
        items[structured["summary"]["id"]] = structured["summary"]["text"]
    for skill in structured.get("skills", []):
        items[skill["id"]] = skill["text"]
    for section in structured.get("sections", []):
        for entry in section["entries"]:
            for bullet in entry["bullets"]:
                items[bullet["id"]] = bullet["text"]
    return items
