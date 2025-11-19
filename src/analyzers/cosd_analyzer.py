"""Bridge/placeholder for the CoSDAnalyzer class used in tests."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .._turning_points_loader import load_module

_IMPL = load_module("analyzers.cosd_analyzer")

if _IMPL and hasattr(_IMPL, "CoSDAnalyzer"):
    CoSDAnalyzer = _IMPL.CoSDAnalyzer  # type: ignore[attr-defined]
else:
    class CoSDAnalyzer:  # pragma: no cover - fallback behavior
        """Lightweight CoSD analyzer stub used when the full stack is absent."""

        def __init__(self, *_, **__):
            pass

        def analyze(
            self,
            transcript: Optional[List[Dict[str, Any]]],
            prosody_features: Optional[List[Dict[str, Any]]] = None,
            markers: Optional[List[Dict[str, Any]]] = None
        ) -> Tuple[List[Any], List[Any]]:
            return [], []
