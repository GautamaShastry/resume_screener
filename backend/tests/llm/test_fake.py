import pytest
from pydantic import BaseModel

from app.llm.client import LLMBadOutput, LLMUsage
from app.llm.fake import FakeLLM


class Out(BaseModel):
    n: int


async def test_dict_list_callable_and_exception_responders():
    fake = FakeLLM({"Out": [{"n": 1}, {"n": 2}]})
    assert (await fake.structured(system="s", user="u", schema=Out)).n == 1
    assert (await fake.structured(system="s", user="u", schema=Out)).n == 2

    fake = FakeLLM({"Out": lambda system, user: {"n": len(user)}})
    usage = LLMUsage()
    assert (await fake.structured(system="s", user="abc", schema=Out, usage=usage)).n == 3
    assert usage.tokens_in > 0
    assert fake.calls == [("Out", "s", "abc")]

    fake = FakeLLM({"Out": RuntimeError("boom")})
    with pytest.raises(RuntimeError):
        await fake.structured(system="s", user="u", schema=Out)


async def test_missing_responder_is_bad_output():
    with pytest.raises(LLMBadOutput):
        await FakeLLM({}).structured(system="s", user="u", schema=Out)
