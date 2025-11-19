from unittest.mock import MagicMock, patch

import importlib.util
import pytest

from svt_core.llm_provider.base import LLMResponse


@patch("svt_core.llm_provider.providers.openai_provider.OpenAI")
def test_openai_provider_generate(mock_client):
    from svt_core.llm_provider.providers.openai_provider import OpenAIProvider

    instance = MagicMock()
    instance.responses.create.return_value = MagicMock(
        output=[MagicMock(content=[MagicMock(text="hi")])], usage={"tokens": 1}
    )
    mock_client.return_value = instance

    provider = OpenAIProvider(api_key="test", model="gpt")
    resp = provider.generate("hello")
    assert isinstance(resp, LLMResponse)
    assert resp.text == "hi"


def test_anthropic_provider_generate():  # pragma: no cover
    if importlib.util.find_spec("anthropic") is None:
        pytest.skip("anthropic SDK not installed")
    from svt_core.llm_provider.providers.anthropic_provider import AnthropicProvider

    with patch("svt_core.llm_provider.providers.anthropic_provider.anthropic.Anthropic") as mock_client:
        instance = MagicMock()
        instance.messages.create.return_value = MagicMock(content=[MagicMock(text="ok")], usage={})
        mock_client.return_value = instance

        provider = AnthropicProvider(api_key="test", model="claude")
        resp = provider.generate("hello")
        assert resp.text == "ok"


def test_google_provider_generate():  # pragma: no cover
    if importlib.util.find_spec("vertexai") is None:
        pytest.skip("vertexai SDK not installed")
    from svt_core.llm_provider.providers.google_provider import GoogleProvider

    with patch("svt_core.llm_provider.providers.google_provider.vertex_init") as mock_init, \
            patch("svt_core.llm_provider.providers.google_provider.GenerativeModel") as mock_model:
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = MagicMock(text="gemini", usage={})
        mock_instance.count_tokens.return_value = {}
        mock_model.return_value = mock_instance

        provider = GoogleProvider(project="p", location="loc", model="gemini")
        resp = provider.generate("hello")
        assert resp.text == "gemini"


@patch("svt_core.llm_provider.providers.grok_provider.requests.post")
def test_grok_provider_generate(mock_post):
    from svt_core.llm_provider.providers.grok_provider import GrokProvider

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "grok"}}],
        "usage": {},
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    provider = GrokProvider(api_key="key", model="grok")
    resp = provider.generate("hello")
    assert resp.text == "grok"
