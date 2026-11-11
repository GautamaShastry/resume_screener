from app.llm.client import LLMUsage
from app.llm.fake import FakeLLM
from app.resumes.structuring import all_bullets, structure_resume
from tests.resumes.factories import BULLETS, STANDARD_RESUME, resume_llm_response


async def test_structure_assigns_ids_and_drops_invented_bullets():
    llm = FakeLLM(
        {"LLMResume": resume_llm_response("Won the Turing Award for distributed systems.")}
    )
    structured, dropped = await structure_resume(llm, STANDARD_RESUME, LLMUsage())
    assert dropped == 1
    bullets = all_bullets(structured)
    assert BULLETS[0] in bullets.values()
    assert not any("Turing" in t for t in bullets.values())
    assert structured["summary"]["id"] == "b1"
    assert [s["id"] for s in structured["skills"]] == ["b2", "b3", "b4", "b5", "b6"]
    exp = structured["sections"][0]
    assert exp["id"] == "s1" and exp["kind"] == "experience"
    assert exp["entries"][0]["bullets"][0] == {"id": "b7", "text": BULLETS[0]}
    assert structured["contact"]["email"] == "jane@example.com"


async def test_prompt_wraps_resume_as_untrusted_data():
    llm = FakeLLM({"LLMResume": resume_llm_response()})
    await structure_resume(llm, STANDARD_RESUME, LLMUsage())
    _, system, user = llm.calls[0]
    assert "untrusted" in system.lower()
    assert user.startswith("<resume>") and user.rstrip().endswith("</resume>")
