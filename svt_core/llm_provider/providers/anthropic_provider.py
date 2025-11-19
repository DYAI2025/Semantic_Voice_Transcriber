from __future__ import annotations

import os
from typing import Any, Dict

import anthropic

from svt_core.llm_provider.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        super().__init__(name="anthropic")
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = anthropic.Anthropic(api_key=key)
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        res = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.5),
            messages=[{"role": "user", "content": prompt}],
        )
        text = res.content[0].text
        usage = getattr(res, "usage", {})
        metadata = {"model": self.model}
        return LLMResponse(text=text, usage=usage, metadata=metadata)

    def health_check(self) -> Dict[str, Any]:
        try:
            self.client.messages.count_tokens(model=self.model, messages=[])
            return {"status": "ok", "details": "Anthropic reachable"}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "details": str(exc)}

    def describe(self) -> Dict[str, Any]:
        return {"name": self.name, "model": self.model}
