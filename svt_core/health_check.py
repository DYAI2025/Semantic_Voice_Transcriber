"""Health-check utilities for SVT startup and CLI."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List

from svt_core.llm_provider.local_ollama import LocalOllamaProvider
from svt_core.config.defaults import DefaultPaths


@dataclass
class CheckResult:
    id: str
    status: str  # ok, warn, error
    details: str


STATUS_ORDER = {"ok": 0, "warn": 1, "error": 2}


def check_ollama() -> CheckResult:
    provider = LocalOllamaProvider()
    status = provider.health_check()
    return CheckResult("ollama", status.get("status", "error"), status.get("details", ""))


def check_directories(paths: DefaultPaths = DefaultPaths()) -> CheckResult:
    problems = []
    for path in (paths.input_dir, paths.output_dir, paths.memory_dir):
        try:
            path.mkdir(parents=True, exist_ok=True)
            test_file = path / ".svt_perm"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
        except Exception as exc:  # pragma: no cover - filesystem-specific
            problems.append(f"{path}: {exc}")
    if problems:
        return CheckResult("directories", "error", "; ".join(problems))
    return CheckResult("directories", "ok", "Directories writable")


def check_disk_space(path: Path = DefaultPaths().output_dir, min_gb: float = 1.0) -> CheckResult:
    usage = shutil.disk_usage(path)
    free_gb = usage.free / (1024 ** 3)
    if free_gb < min_gb:
        return CheckResult("disk", "warn", f"Nur {free_gb:.1f} GB frei in {path}")
    return CheckResult("disk", "ok", f"{free_gb:.1f} GB frei")


def check_pyannote_models() -> CheckResult:
    """
    Check if pyannote.audio models are cached locally

    Returns:
        CheckResult with status:
        - ok: All 3 models cached
        - warn: Some models missing (diarization will work but download on first use)
        - error: Should not happen (always returns ok or warn)
    """
    try:
        from svt_core.audio.download_models import check_models_cached

        status_dict = check_models_cached()
        cached_count = sum(1 for cached in status_dict.values() if cached)
        total_count = len(status_dict)

        if cached_count == total_count:
            return CheckResult(
                "pyannote_models",
                "ok",
                f"All {total_count} models cached"
            )
        elif cached_count > 0:
            return CheckResult(
                "pyannote_models",
                "warn",
                f"{cached_count}/{total_count} models cached. Run: python3 -m svt_core.audio.download_models"
            )
        else:
            return CheckResult(
                "pyannote_models",
                "warn",
                "No models cached. Run: python3 -m svt_core.audio.download_models"
            )
    except Exception as e:
        # Don't fail health check if model checking fails
        return CheckResult(
            "pyannote_models",
            "warn",
            f"Could not check model cache: {e}"
        )


def run_all() -> List[CheckResult]:
    results = [
        check_ollama(),
        check_directories(),
        check_disk_space(),
        check_pyannote_models()
    ]
    return results


def summarize(results: List[CheckResult]) -> tuple[str, str]:
    worst = max(results, key=lambda r: STATUS_ORDER.get(r.status, 2))
    lines = [f"{res.id}: {res.status.upper()} – {res.details}" for res in results]
    summary = "\n".join(lines)
    return worst.status, summary


def cli_main() -> None:
    results = run_all()
    status, summary = summarize(results)
    print(summary)
    if status == "error":
        raise SystemExit(1)


if __name__ == "__main__":
    cli_main()
