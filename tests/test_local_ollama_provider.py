from unittest.mock import MagicMock, patch

import pytest
from requests import RequestException

from svt_core.llm_provider.local_ollama import LocalOllamaProvider, OllamaSettings


@patch("svt_core.llm_provider.local_ollama.requests.post")
def test_generate_success(mock_post):
    provider = LocalOllamaProvider(OllamaSettings(base_url="http://test", model="mini"))
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "response": "ok",
        "eval_count": 10,
        "prompt_eval_count": 5,
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    result = provider.generate("hello")
    assert result.text == "ok"
    assert result.metadata["model"] == "mini"
    mock_post.assert_called_once()


@patch("svt_core.llm_provider.local_ollama.requests.get")
def test_health_check_ok(mock_get):
    provider = LocalOllamaProvider(OllamaSettings(base_url="http://test", model="mini"))
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"models": [{"name": "mini"}]}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    status = provider.health_check()
    assert status["status"] == "ok"


@patch("svt_core.llm_provider.local_ollama.requests.get")
def test_health_check_error(mock_get):
    provider = LocalOllamaProvider()
    mock_get.side_effect = RequestException("no service")

    status = provider.health_check()
    assert status["status"] == "error"


@patch("svt_core.llm_provider.local_ollama.requests.post")
def test_generate_error_propagates(mock_post):
    provider = LocalOllamaProvider()
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("boom")
    mock_post.return_value = mock_resp

    with pytest.raises(Exception):
        provider.generate("bad")
