# LLM Provider Interface

## Concepts
- ``LLMProvider`` is an abstract base class with three required methods:
  - ``generate(prompt: str, **kwargs) -> LLMResponse``: unified completion call.
  - ``health_check() -> dict``: returns ``{"status": "ok|warn|error", "details": str}``.
  - ``describe() -> dict``: static metadata (model name, endpoint, etc.).
- ``LLMResponse`` is a dataclass with ``text`` plus optional ``usage`` and ``metadata`` dicts.

## Dummy Provider
- ``DummyProvider`` is a no-op implementation used in smoke tests, ensuring the interface works without hitting any external API.

## Usage Pattern
```python
from svt_core.llm_provider.base import LLMProvider

provider: LLMProvider = LocalOllamaProvider(config)
resp = provider.generate(prompt="Analyze this transcript")
print(resp.text)
```

## Next Steps
- Real providers (LocalOllama, OpenAI, Anthropic, Google, Grok) will subclass ``LLMProvider`` and map their native SDK responses into ``LLMResponse``.
