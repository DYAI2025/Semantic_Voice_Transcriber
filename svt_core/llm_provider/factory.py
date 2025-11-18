"""Factory helpers for provider manager setup."""
from __future__ import annotations

import os

from .manager import ProviderManager
from svt_core.config.settings import ProviderProfile

try:
    from .providers import OpenAIProvider  # type: ignore
except ImportError:  # pragma: no cover
    OpenAIProvider = None
try:
    from .providers import AnthropicProvider  # type: ignore
except ImportError:  # pragma: no cover
    AnthropicProvider = None
try:
    from .providers import GoogleProvider  # type: ignore
except ImportError:  # pragma: no cover
    GoogleProvider = None
try:
    from .providers import GrokProvider  # type: ignore
except ImportError:  # pragma: no cover
    GrokProvider = None


def build_default_manager() -> ProviderManager:
    mgr = ProviderManager()

    if OpenAIProvider and os.environ.get("OPENAI_API_KEY"):
        try:
            mgr.register("openai", OpenAIProvider())
        except Exception:  # pragma: no cover
            pass
    if AnthropicProvider and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            mgr.register("anthropic", AnthropicProvider())
        except Exception:  # pragma: no cover
            pass
    if GoogleProvider and os.environ.get("GOOGLE_PROJECT_ID"):
        try:
            mgr.register("google", GoogleProvider())
        except Exception:  # pragma: no cover
            pass
    if GrokProvider and os.environ.get("GROK_API_KEY"):
        try:
            mgr.register("grok", GrokProvider())
        except Exception:  # pragma: no cover
            pass

    return mgr


def build_provider_from_profile(profile: ProviderProfile):
    builders = {}
    if OpenAIProvider:
        builders["openai"] = lambda: OpenAIProvider(api_key=profile.extra.get("key"), model=profile.model or None)
    if AnthropicProvider:
        builders["anthropic"] = lambda: AnthropicProvider(api_key=profile.extra.get("key"), model=profile.model or None)
    if GoogleProvider:
        builders["google"] = lambda: GoogleProvider(project=profile.extra.get("project"), location=profile.extra.get("location"), model=profile.model or None)
    if GrokProvider:
        builders["grok"] = lambda: GrokProvider(api_key=profile.extra.get("key"), model=profile.model or None)
    builder = builders.get(profile.key)
    if not builder:
        raise ValueError(f"Unsupported provider {profile.key}")
    return builder()
