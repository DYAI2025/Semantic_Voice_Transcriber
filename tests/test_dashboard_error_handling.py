import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import logging
import pytest

import svt


class _DummyVar:
    def __init__(self, value: str):
        self._value = value

    def get(self) -> str:
        return self._value


def _make_gui(tmp_path: Path):
    gui = svt.SemanticVoiceTranscriberGUI.__new__(svt.SemanticVoiceTranscriberGUI)
    gui.output_dir_var = _DummyVar(str(tmp_path))
    gui._dashboard_retry_count = 0
    gui._log_messages = []

    def _fake_log(msg: str) -> None:
        gui._log_messages.append(msg)

    gui._log = _fake_log
    return gui


class DummyRateLimitError(Exception):
    """Simple stand-in for RateLimitError when OpenAI SDK is unavailable."""


def test_dashboard_pipeline_handles_rate_limit(tmp_path, monkeypatch, caplog):
    """Ensure RateLimit errors are surfaced without crashing the GUI workflow."""
    gui = _make_gui(tmp_path)
    latest_json = tmp_path / "session_transkript.prosody.json"
    latest_json.write_text(json.dumps({"segments": [], "duration_seconds": 0}), encoding="utf-8")

    monkeypatch.setenv("OPENAI_API_KEY_ALIAS", "primary")
    monkeypatch.setattr(svt, "RateLimitError", DummyRateLimitError)

    pipeline_mock = MagicMock()
    pipeline_mock.provider_name = "OpenAI"
    pipeline_mock.api = SimpleNamespace(model="gpt-4-test", api_key_alias="primary", last_retry_count=2)
    pipeline_mock.config = {"openai": {"model": "gpt-4-test"}}
    pipeline_mock.analyze_transcript.side_effect = DummyRateLimitError("429")

    with patch("psychoanalysis_pipeline.PsychoanalysisPipeline", return_value=pipeline_mock), \
        patch("dashboard_generator.DashboardGenerator"), \
        patch.object(svt.messagebox, "showerror") as mock_showerror:
        caplog.set_level(logging.ERROR)
        gui._run_dashboard_pipeline(latest_json)

    # GUI log contains the failure context without exposing secrets
    assert any("Dashboard-Fehler" in msg for msg in gui._log_messages)
    assert any("key_alias=primary" in msg for msg in gui._log_messages)

    # A visible dialog is triggered for the operator
    mock_showerror.assert_called_once()
    dialog_message = mock_showerror.call_args[0][1]
    assert "key_alias=primary" in dialog_message
    assert "model=gpt-4-test" in dialog_message

    # Python logging captures structured context for telemetry
    assert "key_alias=primary" in caplog.text
    assert "model=gpt-4-test" in caplog.text
