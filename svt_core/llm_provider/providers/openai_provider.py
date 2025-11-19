"""OpenAI-based provider."""
from __future__ import annotations

import os
from typing import Any, Dict

from openai import OpenAI

from svt_core.llm_provider.base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        super().__init__(name="openai")
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=key)
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        res = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=kwargs.get("temperature", 0.5),
            max_output_tokens=kwargs.get("max_tokens", 1024),
        )
        text = res.output[0].content[0].text
        usage = getattr(res, "usage", {})
        metadata = {"model": self.model}
        return LLMResponse(text=text, usage=usage, metadata=metadata)

    def health_check(self) -> Dict[str, Any]:
        try:
            _ = self.client.models.list()
            return {"status": "ok", "details": "OpenAI reachable"}
        except Exception as exc:  # pragma: no cover - network error
            return {"status": "error", "details": str(exc)}

    def describe(self) -> Dict[str, Any]:
        return {"name": self.name, "model": self.model}
