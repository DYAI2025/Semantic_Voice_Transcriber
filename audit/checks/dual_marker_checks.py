"""Checks for dual marker system."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from audit.feature_registry import FeatureMetadata

MARKER_DIR = Path("VP_ATO")


def dual_marker_availability(meta: "FeatureMetadata") -> Dict[str, str]:
    if not MARKER_DIR.exists():
        return {"status": "warn", "details": "Marker directory missing"}
    return {"status": "ok", "details": "Markers available"}


def dual_marker_smoke(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from Turning_Points_in_Transcription.integration.dual_marker_system import DualMarkerSystem  # noqa

        system = DualMarkerSystem(config=None)
        sample_transcript = {"segments": [{"text": "Test"}]}
        _ = system.apply_markers(sample_transcript)
        return {"status": "pass", "details": "Markers applied"}
    except Exception as exc:
        return {"status": "fail", "details": str(exc)}
