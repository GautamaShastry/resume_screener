import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

import openai
from pydantic import ValidationError

from app.core.settings import Settings
from app.llm.client import LLMBadOutput, LLMClient, LLMUnavailable, LLMUsage, T

RETRYABLE = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.InternalServerError,
)


class AzureOpenAILLM:
    def __init__(
        self,
        client: Any,
        deployment: str,
        max_retries: int = 3,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        self._client = client
        self._deployment = deployment
        self._max_retries = max_retries
        self._sleep = sleep

    async def _complete(self, messages: list[dict], temperature: float | None, usage) -> str:
        kwargs: dict[str, Any] = {
            "model": self._deployment,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        for attempt in range(self._max_retries + 1):
            try:
                resp = await self._client.chat.completions.create(**kwargs)
            except RETRYABLE as exc:
                if attempt == self._max_retries:
                    raise LLMUnavailable(
                        "The AI service is unavailable. Try again shortly."
                    ) from exc
                await self._sleep(2**attempt)
                continue
            if usage is not None and getattr(resp, "usage", None):
                usage.tokens_in += resp.usage.prompt_tokens
                usage.tokens_out += resp.usage.completion_tokens
            return resp.choices[0].message.content or ""
        raise LLMUnavailable("The AI service is unavailable. Try again shortly.")

    async def structured(
        self,
        *,
        system: str,
        user: str,
        schema: type[T],
        usage: LLMUsage | None = None,
        temperature: float | None = None,
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema())
        messages = [
            {
                "role": "system",
                "content": f"{system}\n\nRespond with one JSON object that conforms to this "
                f"JSON Schema:\n{schema_json}",
            },
            {"role": "user", "content": user},
        ]
        content = await self._complete(messages, temperature, usage)
        try:
            return schema.model_validate_json(content)
        except ValidationError as first:
            errors = json.dumps(first.errors(include_url=False), default=str)[:2000]
            messages += [
                {"role": "assistant", "content": content},
                {
                    "role": "user",
                    "content": f"That JSON did not match the schema. Errors: {errors}. "
                    "Return only the corrected JSON object.",
                },
            ]
            content = await self._complete(messages, temperature, usage)
            try:
                return schema.model_validate_json(content)
            except ValidationError as second:
                raise LLMBadOutput("The AI returned an unexpected format.") from second


def build_llm(settings: Settings) -> LLMClient:
    if settings.llm_provider == "fake":
        from app.llm.demo import demo_llm

        return demo_llm()
    from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
    from openai import AsyncAzureOpenAI

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        azure_ad_token_provider=token_provider,
        timeout=settings.llm_timeout_s,
        max_retries=0,
    )
    return AzureOpenAILLM(client, settings.azure_openai_chat_deployment)
