import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import psychoanalysis_api
from psychoanalysis_api import PsychoanalysisAPI


class DummyRateLimitError(Exception):
    pass


@pytest.fixture(autouse=True)
def patch_rate_limit(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("DASHBOARD_MAX_RETRIES", "4")
    monkeypatch.setenv("DASHBOARD_RETRY_BASE_DELAY", "0.1")
    monkeypatch.setenv("DASHBOARD_RETRY_MAX_DELAY", "0.2")
    monkeypatch.setenv("DASHBOARD_RETRY_JITTER", "0.0")
    monkeypatch.setattr(psychoanalysis_api, "RateLimitError", DummyRateLimitError)
    monkeypatch.setattr(psychoanalysis_api, "OpenAIError", Exception)
    monkeypatch.setattr(psychoanalysis_api.time, "sleep", lambda *_: None)
    yield


def _make_api(tmp_path):
    client = MagicMock()
    return PsychoanalysisAPI(client=client, config_path="config/psychoanalysis_config.yaml")


def test_retry_succeeds_after_backoff(tmp_path, monkeypatch):
    api = _make_api(tmp_path)

    attempts = {"count": 0}

    def flaky_call():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise DummyRateLimitError("429")
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(function_call=SimpleNamespace(arguments=json.dumps({"utterance_states": [], "ued_metrics": {}, "marker_summary": {}}))))])
        return response

    result = api._call_with_retry(flaky_call)
    assert result.choices
    assert api.last_retry_count == 2


def test_retry_raises_after_max_attempts(tmp_path):
    api = _make_api(tmp_path)

    def always_fail():
        raise DummyRateLimitError("429")

    with pytest.raises(DummyRateLimitError):
        api._call_with_retry(always_fail)
    assert api.last_retry_count == api.retry_max_attempts


def test_non_rate_limit_errors_not_retried(tmp_path):
    api = _make_api(tmp_path)

    class OtherError(Exception):
        pass

    def bad_call():
        raise OtherError("boom")

    with pytest.raises(OtherError):
        api._call_with_retry(bad_call)
    assert api.last_retry_count == 0
