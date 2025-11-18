"""Checks for speaker visualization."""
from __future__ import annotations

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from audit.feature_registry import FeatureMetadata


def speaker_view_availability(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        import speaker_visualizer_v2  # noqa
        return {"status": "ok", "details": "Visualizer module available"}
    except Exception as exc:
        return {"status": "warn", "details": str(exc)}


def speaker_view_smoke(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        import speaker_visualizer_v2 as viz  # noqa

        dummy_segments = [
            {"start": 0.0, "end": 0.5, "speaker": "Speaker A"},
            {"start": 0.5, "end": 1.0, "speaker": "Speaker B"},
        ]
        _ = viz.build_speaker_timeline(dummy_segments)
        return {"status": "pass", "details": "Timeline built"}
    except Exception as exc:
        return {"status": "fail", "details": str(exc)}
