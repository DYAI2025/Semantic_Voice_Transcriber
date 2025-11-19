from pathlib import Path
from unittest.mock import MagicMock, patch

from svt_core import health_check


def test_check_directories(tmp_path):
    paths = health_check.DefaultPaths(
        input_dir=tmp_path / "in",
        output_dir=tmp_path / "out",
        memory_dir=tmp_path / "mem",
    )
    result = health_check.check_directories(paths)
    assert result.status == "ok"


def test_check_disk_space(tmp_path):
    result = health_check.check_disk_space(tmp_path, min_gb=0.0)
    assert result.status == "ok"


def test_check_ollama_error(monkeypatch):
    fake_provider = MagicMock()
    fake_provider.health_check.return_value = {"status": "error", "details": "offline"}
    monkeypatch.setattr(health_check, "LocalOllamaProvider", lambda: fake_provider)
    result = health_check.check_ollama()
    assert result.status == "error"


def test_summarize(monkeypatch):
    results = [
        health_check.CheckResult("a", "ok", ""),
        health_check.CheckResult("b", "warn", "low space"),
    ]
    status, summary = health_check.summarize(results)
    assert status == "warn"
    assert "low space" in summary
