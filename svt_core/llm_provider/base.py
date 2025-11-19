"""Base abstractions for Semantic Voice Transcriber's LLM providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class LLMResponse:
    """Normalized response returned by every provider."""

    text: str
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Interface for every LLM backend (local or cloud)."""

    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate a completion for ``prompt``.

        Implementations may accept provider-specific kwargs; they should be
        documented and ignored when unsupported.
        """

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return provider health information.

        Expected keys:
            - ``status``: "ok", "warn", or "error"
            - ``details``: human-friendly description
        """

    @abstractmethod
    def describe(self) -> Dict[str, Any]:
        """Return static info (model name, endpoint, etc.)."""


class DummyProvider(LLMProvider):
    """Simple provider used for smoke tests."""

    def __init__(self):
        super().__init__("dummy")

    def generate(self, prompt: str, **_: Any) -> LLMResponse:
        return LLMResponse(text=f"dummy-response:{prompt[:32]}")

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "details": "dummy provider always ready"}

    def describe(self) -> Dict[str, Any]:
        return {"name": self.name}
