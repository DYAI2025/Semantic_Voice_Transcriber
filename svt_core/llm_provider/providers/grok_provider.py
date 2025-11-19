from __future__ import annotations

import os
from typing import Any, Dict

import requests

from svt_core.llm_provider.base import LLMProvider, LLMResponse


class GrokProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        super().__init__(name="grok")
        self.api_key = api_key or os.environ.get("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("GROK_API_KEY not set")
        self.model = model or os.environ.get("GROK_MODEL", "grok-beta")
        self.base_url = os.environ.get("GROK_BASE_URL", "https://api.x.ai/v1")

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.5),
                "max_tokens": kwargs.get("max_tokens", 1024),
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        metadata = {"model": self.model}
        return LLMResponse(text=text, usage=usage, metadata=metadata)

    def health_check(self) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            resp.raise_for_status()
            return {"status": "ok", "details": "Grok reachable"}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "details": str(exc)}

    def describe(self) -> Dict[str, Any]:
        return {"name": self.name, "model": self.model}
