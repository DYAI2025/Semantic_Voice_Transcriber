"""Factory helpers for provider manager setup."""
from __future__ import annotations

import os

from .manager import ProviderManager
from .providers import (
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    GrokProvider,
)


def build_default_manager() -> ProviderManager:
    mgr = ProviderManager()

    if os.environ.get("OPENAI_API_KEY"):
        try:
            mgr.register("openai", OpenAIProvider())
        except Exception:  # pragma: no cover
            pass
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            mgr.register("anthropic", AnthropicProvider())
        except Exception:  # pragma: no cover
            pass
    if os.environ.get("GOOGLE_PROJECT_ID"):
        try:
            mgr.register("google", GoogleProvider())
        except Exception:  # pragma: no cover
            pass
    if os.environ.get("GROK_API_KEY"):
        try:
            mgr.register("grok", GrokProvider())
        except Exception:  # pragma: no cover
            pass

    return mgr
