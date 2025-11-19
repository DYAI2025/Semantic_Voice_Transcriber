"""Bridge module exposing TurningPointPipeline for tests and lightweight imports."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ._turning_points_loader import load_module

_IMPL = load_module("turning_point_pipeline")

if _IMPL and hasattr(_IMPL, "TurningPointPipeline"):
    TurningPointPipeline = _IMPL.TurningPointPipeline  # type: ignore[attr-defined]
else:
    class TurningPointPipeline:  # pragma: no cover - simple fallback
        """Minimal stub used when the full turning-point stack is unavailable."""

        def __init__(self, config_path: Optional[Path] = None, config: Optional[Dict[str, Any]] = None):
            self.config_path = config_path
            self.config = config or {}

        def process(self, transcript_path: Path, audio_path: Optional[Path] = None) -> Dict[str, Any]:
            return {
                "metadata": {
                    "transcript_file": str(transcript_path),
                    "audio_file": str(audio_path) if audio_path else None
                },
                "turning_points": [],
                "cosd_timeline": [],
                "markers": []
            }
