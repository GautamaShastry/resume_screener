from collections.abc import Callable
from typing import Any

from app.llm.client import LLMBadOutput, LLMUsage, T

Responder = dict | list | Callable[[str, str], dict] | Exception


class FakeLLM:
    def __init__(self, responders: dict[str, Responder] | None = None):
        self.responders: dict[str, Any] = dict(responders or {})
        self.calls: list[tuple[str, str, str]] = []

    async def structured(
        self,
        *,
        system: str,
        user: str,
        schema: type[T],
        usage: LLMUsage | None = None,
        temperature: float | None = None,
    ) -> T:
        name = schema.__name__
        self.calls.append((name, system, user))
        responder = self.responders.get(name)
        if responder is None:
            raise LLMBadOutput(f"FakeLLM has no response for {name}")
        if isinstance(responder, Exception):
            raise responder
        if isinstance(responder, list):
            data = responder.pop(0)
        elif callable(responder):
            data = responder(system, user)
        else:
            data = responder
        if usage is not None:
            usage.tokens_in += 10
            usage.tokens_out += 5
        return schema.model_validate(data)
