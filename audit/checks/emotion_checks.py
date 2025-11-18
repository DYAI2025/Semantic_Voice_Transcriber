"""Checks for the emotional analysis pipeline."""
from __future__ import annotations

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from audit.feature_registry import FeatureMetadata


def emotion_availability(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from auto_transcriber_v4_emotion import EmotionalAnalyzer  # noqa
        analyzer = EmotionalAnalyzer()
        markers = analyzer._load_emotional_markers()  # type: ignore[attr-defined]
        details = "Markers loaded" if markers else "Default markers"
        return {"status": "ok", "details": details}
    except Exception as exc:  # pragma: no cover - dependency errors
        return {"status": "error", "details": str(exc)}


def emotion_smoke(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from auto_transcriber_v4_emotion import EmotionalAnalyzer  # noqa

        analyzer = EmotionalAnalyzer()
        analyzer._load_emotional_markers()  # type: ignore[attr-defined]
        return {"status": "pass", "details": "Analyzer initialized"}
    except Exception as exc:
        return {"status": "fail", "details": str(exc)}
