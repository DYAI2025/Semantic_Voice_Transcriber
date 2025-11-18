"""Local Ollama-backed provider (default offline LLM)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .base import LLMProvider, LLMResponse


@dataclass
class OllamaSettings:
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:7b"
    temperature: float = 0.7
    max_tokens: int = 1024


class LocalOllamaProvider(LLMProvider):
    """Provider that talks to a local Ollama daemon."""

    def __init__(self, settings: Optional[OllamaSettings] = None):
        super().__init__(name="local-ollama")
        self.settings = settings or OllamaSettings()

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        payload = {
            "model": self.settings.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.settings.temperature),
                "num_predict": kwargs.get("max_tokens", self.settings.max_tokens),
            },
        }
        resp = requests.post(
            f"{self.settings.base_url}/api/generate",
            json=payload,
            timeout=kwargs.get("timeout", 60),
        )
        resp.raise_for_status()
        body = resp.json()
        text = body.get("response", "")
        usage = {
            "num_predict": body.get("eval_count"),
            "prompt_eval_count": body.get("prompt_eval_count"),
        }
        metadata = {
            "model": self.settings.model,
            "base_url": self.settings.base_url,
        }
        return LLMResponse(text=text, usage=usage, metadata=metadata)

    def health_check(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.settings.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m.get("name") for m in resp.json().get("models", [])]
            if self.settings.model in models:
                return {"status": "ok", "details": f"model {self.settings.model} ready"}
            if models:
                return {"status": "warn", "details": "model missing; available: " + ", ".join(models)}
            return {"status": "warn", "details": "no models installed"}
        except requests.RequestException as exc:
            return {"status": "error", "details": str(exc)}

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "base_url": self.settings.base_url,
            "model": self.settings.model,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }
