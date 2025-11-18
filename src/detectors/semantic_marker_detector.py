"""Bridge/placeholder for SemanticMarkerDetector used in tests."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._turning_points_loader import load_module

_IMPL = load_module("detectors.semantic_marker_detector")

if _IMPL and hasattr(_IMPL, "SemanticMarkerDetector"):
    SemanticMarkerDetector = _IMPL.SemanticMarkerDetector  # type: ignore[attr-defined]
else:
    class SemanticMarkerDetector:  # pragma: no cover - fallback
        """Simple detector stub returning no markers."""

        def __init__(self, *_, **__):
            pass

        def detect_markers(
            self,
            transcript: Optional[List[Dict[str, Any]]],
            prosody_features: Optional[List[Dict[str, Any]]] = None
        ) -> List[Dict[str, Any]]:
            return []
