import re

from app.analysis.evidence import collect_evidence, render_requirements, render_resume
from app.analysis.gaps import analyze_gaps
from app.llm.client import LLMUsage
from app.llm.fake import FakeLLM
from app.resumes.structuring import structure_resume
from tests.analysis.conftest import evidence_responder, gaps_responder
from tests.postings.fixtures import posting_llm_response
from tests.resumes.factories import BULLETS, STANDARD_RESUME, resume_llm_response


async def _structured():
    llm = FakeLLM({"LLMResume": resume_llm_response()})
    s, _ = await structure_resume(llm, STANDARD_RESUME, LLMUsage())
    return s


def _reqs():
    return [{**r, "id": f"r{i}"} for i, r in enumerate(posting_llm_response()["requirements"], 1)]


async def test_render_formats():
    s = await _structured()
    assert f"[b7] {BULLETS[0]}" in render_resume(s)
    assert "[r4] (nice) Kubernetes experience" in render_requirements(_reqs())


async def test_evidence_resolves_quotes_and_downgrades_unsupported():
    s = await _structured()
    llm = FakeLLM({"LLMEvidence": evidence_responder})
    ev = await collect_evidence(llm, s, _reqs(), LLMUsage())
    by_id = {e["requirement_id"]: e for e in ev}
    assert by_id["r1"]["status"] == "met"
    assert by_id["r1"]["quotes"] == [{"bullet_id": "b7", "text": BULLETS[0]}]
    assert by_id["r2"]["status"] == "missing" and by_id["r2"]["quotes"] == []
    assert by_id["r3"]["status"] == "partial"
    assert [e["requirement_id"] for e in ev] == ["r1", "r2", "r3", "r4"]


async def test_evidence_chunks_requirements_and_fills_missing_items():
    s = await _structured()
    reqs = [
        {
            "id": f"r{i}",
            "text": f"Skill {i}",
            "kind": "must",
            "category": "skill",
            "source_phrase": "",
        }
        for i in range(1, 21)
    ]

    def only_first_five(system, user):
        ids = re.findall(r"^\[(r\d+)\]", user, re.M)
        return {
            "items": [
                {"requirement_id": rid, "status": "partial", "bullet_ids": ["b7"]}
                for rid in ids[:5]
            ]
        }

    llm = FakeLLM({"LLMEvidence": only_first_five})
    ev = await collect_evidence(llm, s, reqs, LLMUsage())
    assert len(llm.calls) == 2
    assert len(ev) == 20
    assert sum(1 for e in ev if e["status"] == "missing") == 10


async def test_gaps_validate_targets_and_ids():
    s = await _structured()
    reqs = _reqs()
    ev = await collect_evidence(FakeLLM({"LLMEvidence": evidence_responder}), s, reqs, LLMUsage())
    llm = FakeLLM({"LLMGaps": gaps_responder})
    gaps = await analyze_gaps(llm, s, reqs, ev, LLMUsage())
    by_id = {g["requirement_id"]: g for g in gaps}
    assert set(by_id) == {"r2", "r3"}  # r4 has only invalid related ids; r1 is met
    assert by_id["r2"]["type"] == "not_stated"
    assert by_id["r2"]["related_quotes"] == [{"bullet_id": "b7", "text": BULLETS[0]}]
    assert by_id["r2"]["project"] is None
    assert by_id["r3"]["type"] == "real_gap" and by_id["r3"]["suggested_bullet"] is None
    _, _, user = llm.calls[0]
    assert "[r1]" not in user  # only missing/partial requirements are sent


async def test_gaps_skip_llm_when_everything_met():
    s = await _structured()
    reqs = _reqs()[:1]
    ev = [{"requirement_id": "r1", "status": "met", "quotes": [], "note": ""}]
    llm = FakeLLM({})
    assert await analyze_gaps(llm, s, reqs, ev, LLMUsage()) == []
    assert llm.calls == []
