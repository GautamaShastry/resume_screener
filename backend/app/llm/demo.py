"""Deterministic stand-in for the LLM: lets the full app run locally and in e2e tests."""

import re

from app.llm.fake import FakeLLM

WORD = re.compile(r"[A-Za-z][A-Za-z+#.]{3,}")
STOP = {"with", "experience", "years", "strong", "skills", "building", "professional", "using"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
REQ_LINE = re.compile(r"^\[(r\d+)\] \((?:must|nice)\) (.+)$", re.M)


def _between(text: str, tag: str) -> str:
    m = re.search(rf"<{tag}>\n(.*)\n</{tag}>", text, re.S)
    return m.group(1) if m else text


def _words(text: str) -> set[str]:
    return {w.lower() for w in WORD.findall(text)} - STOP


def _resume(system: str, user: str) -> dict:
    text = _between(user, "resume")
    lines = [ln.strip(" •-\t") for ln in text.splitlines() if ln.strip()]
    email = EMAIL.search(text)
    skills_idx = next((i for i, ln in enumerate(lines) if ln.lower().startswith("skills")), None)
    skills: list[str] = []
    if skills_idx is not None and skills_idx + 1 < len(lines):
        skills = [s.strip() for s in lines[skills_idx + 1].split(",") if s.strip()]
    bullets = [ln for ln in lines if len(ln) >= 40][:40]
    return {
        "contact": {"name": lines[0] if lines else "", "email": email.group(0) if email else ""},
        "summary": "",
        "skills": skills,
        "sections": [
            {
                "kind": "experience",
                "title": "Experience",
                "entries": [{"org": "", "role": "", "start": "", "end": "", "bullets": bullets}],
            }
        ],
    }


def _posting(system: str, user: str) -> dict:
    text = _between(user, "job_description")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    reqs = []
    for ln in lines:
        if ln[:1] in "-•*" and len(ln) > 3:
            phrase = ln.lstrip("-•* ").strip()
            nice = re.search(r"\b(preferred|bonus|plus|nice)\b", phrase, re.I)
            reqs.append(
                {
                    "text": phrase,
                    "kind": "nice" if nice else "must",
                    "category": "skill",
                    "source_phrase": phrase,
                }
            )
    return {
        "title": lines[0][:120] if lines else "",
        "company": "",
        "location": "",
        "seniority": "unknown",
        "requirements": reqs[:30],
    }


def _evidence(system: str, user: str) -> dict:
    bullets = dict(re.findall(r"^\[(b\d+)\] (.+)$", user, re.M))
    items = []
    for rid, rtext in REQ_LINE.findall(user):
        want = _words(rtext)
        hits = [bid for bid, btext in bullets.items() if want & _words(btext)][:2]
        status = "met" if len(hits) >= 2 else "partial" if hits else "missing"
        items.append(
            {
                "requirement_id": rid,
                "status": status,
                "bullet_ids": hits,
                "note": "Demo mode: matched on shared keywords.",
            }
        )
    return {"items": items}


def _gaps(system: str, user: str) -> dict:
    return {
        "items": [
            {
                "requirement_id": rid,
                "type": "real_gap",
                "related_bullet_ids": [],
                "project": {
                    "title": f"Small project: {text[:50]}",
                    "scope": "About two weeks of evenings.",
                    "deliverables": ["Public repository", "Short write-up"],
                    "resume_bullet": f"Built a project demonstrating {text[:60]}.",
                },
            }
            for rid, text in REQ_LINE.findall(user)
        ]
    }


def demo_llm() -> FakeLLM:
    return FakeLLM(
        {"LLMResume": _resume, "LLMPosting": _posting, "LLMEvidence": _evidence, "LLMGaps": _gaps}
    )
