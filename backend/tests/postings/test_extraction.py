from app.llm.client import LLMUsage
from app.llm.fake import FakeLLM
from app.postings.extraction import extract_posting
from app.postings.sources import FetchedPosting
from tests.postings.fixtures import POSTING_TEXT, posting_llm_response


async def test_ids_assigned_and_ungrounded_requirements_dropped():
    invented = {
        "text": "PhD required",
        "kind": "must",
        "category": "education",
        "source_phrase": "PhD in physics required",
    }
    llm = FakeLLM({"LLMPosting": posting_llm_response(invented)})
    out = await extract_posting(llm, POSTING_TEXT, None, LLMUsage())
    assert [r["id"] for r in out["requirements"]] == ["r1", "r2", "r3", "r4"]
    assert not any("PhD" in r["text"] for r in out["requirements"])
    assert out["seniority"] == "senior"
    _, system, user = llm.calls[0]
    assert "untrusted" in system.lower() and "<job_description>" in user


async def test_hints_override_llm_metadata():
    llm = FakeLLM({"LLMPosting": posting_llm_response()})
    hints = FetchedPosting(
        "greenhouse", "https://x", "Backend Engineer II", "Acme Inc", "NYC", POSTING_TEXT
    )
    out = await extract_posting(llm, POSTING_TEXT, hints, LLMUsage())
    assert (out["title"], out["company"], out["location"]) == (
        "Backend Engineer II",
        "Acme Inc",
        "NYC",
    )
