from types import SimpleNamespace

import httpx
import openai
import pytest
from pydantic import BaseModel

from app.llm.azure_openai import AzureOpenAILLM
from app.llm.client import LLMBadOutput, LLMUnavailable, LLMUsage


class Out(BaseModel):
    answer: int


def _resp(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(prompt_tokens=7, completion_tokens=3),
    )


def _rate_limit():
    req = httpx.Request("POST", "https://x")
    return openai.RateLimitError("slow down", response=httpx.Response(429, request=req), body=None)


class FakeCompletions:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return _resp(item)


def _llm(script):
    completions = FakeCompletions(script)
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    sleeps: list[float] = []

    async def sleep(s):
        sleeps.append(s)

    return AzureOpenAILLM(client, "chat", max_retries=3, sleep=sleep), completions, sleeps


async def test_parses_valid_json_and_counts_tokens():
    llm, completions, _ = _llm(['{"answer": 42}'])
    usage = LLMUsage()
    out = await llm.structured(system="s", user="u", schema=Out, usage=usage)
    assert out.answer == 42
    assert (usage.tokens_in, usage.tokens_out) == (7, 3)
    call = completions.calls[0]
    assert call["response_format"] == {"type": "json_object"}
    assert call["model"] == "chat"
    assert "temperature" not in call
    assert '"answer"' in call["messages"][0]["content"]  # schema included in system prompt


async def test_repairs_once_then_succeeds():
    llm, completions, _ = _llm(['{"answer": "x"}', '{"answer": 1}'])
    out = await llm.structured(system="s", user="u", schema=Out)
    assert out.answer == 1
    assert len(completions.calls) == 2
    assert completions.calls[1]["messages"][-1]["role"] == "user"


async def test_raises_bad_output_after_failed_repair():
    llm, _, _ = _llm(["not json", '{"nope": 1}'])
    with pytest.raises(LLMBadOutput):
        await llm.structured(system="s", user="u", schema=Out)


async def test_retries_rate_limit_with_backoff():
    llm, completions, sleeps = _llm([_rate_limit(), _rate_limit(), '{"answer": 5}'])
    out = await llm.structured(system="s", user="u", schema=Out)
    assert out.answer == 5
    assert sleeps == [1, 2]


async def test_gives_up_after_max_retries():
    llm, _, sleeps = _llm([_rate_limit()] * 4)
    with pytest.raises(LLMUnavailable):
        await llm.structured(system="s", user="u", schema=Out)
    assert sleeps == [1, 2, 4]
