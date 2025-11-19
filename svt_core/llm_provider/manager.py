"""Provider manager that handles configuration and fallback."""
from __future__ import annotations

import logging
from typing import Dict, Optional

from .base import LLMProvider, LLMResponse
from .local_ollama import LocalOllamaProvider

logger = logging.getLogger(__name__)


class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {
            "local": LocalOllamaProvider(),
        }
        self.active_key = "local"

    def register(self, key: str, provider: LLMProvider) -> None:
        self.providers[key] = provider

    def set_active(self, key: str) -> None:
        if key not in self.providers:
            raise KeyError(f"unknown provider {key}")
        self.active_key = key

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        provider = self.providers.get(self.active_key)
        if not provider:
            provider = self.providers["local"]
            self.active_key = "local"

        try:
            return provider.generate(prompt, **kwargs)
        except Exception as exc:
            logger.error("Provider %s failed: %s", provider.name, exc)
            if provider.name != "local":
                self.active_key = "local"
                logger.warning("Falling back to local provider")
                return self.providers["local"].generate(prompt, **kwargs)
            raise

    def describe_active(self) -> Dict[str, Optional[str]]:
        provider = self.providers.get(self.active_key)
        return provider.describe() if provider else {"name": "unknown"}
