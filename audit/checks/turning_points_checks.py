"""Checks for turning points detection."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from audit.feature_registry import FeatureMetadata

DETECTOR_DIR = Path("Turning_Points_in_Transcription")


def turning_points_availability(meta: "FeatureMetadata") -> Dict[str, str]:
    if not DETECTOR_DIR.exists():
        return {"status": "warn", "details": "Detector directory missing"}
    return {"status": "ok", "details": "Detector assets present"}


def turning_points_smoke(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from Turning_Points_in_Transcription.integration.turning_points_layer import TurningPointsLayer  # noqa

        layer = TurningPointsLayer()
        result = layer.process_transcript({"segments": []})
        if result is None:
            return {"status": "warn", "details": "No result returned"}
        return {"status": "pass", "details": "Layer processed empty transcript"}
    except Exception as exc:
        return {"status": "fail", "details": str(exc)}
