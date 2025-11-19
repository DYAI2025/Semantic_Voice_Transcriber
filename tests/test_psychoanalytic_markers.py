# tests/test_psychoanalytic_markers.py
import pytest
from pathlib import Path
import yaml

MARKER_DIR = Path(__file__).parent.parent / "VP_ATO" / "psychoanalytic"

EXPECTED_MARKERS = [
    "ATO_DEFENSE_DENIAL",
    "ATO_DEFENSE_PROJECTION",
    "ATO_DEFENSE_RATIONALIZATION",
    "ATO_DEFENSE_DISPLACEMENT",
    "ATO_DEFENSE_REGRESSION",
    "ATO_RESISTANCE_SILENCE",
    "ATO_RESISTANCE_TOPIC_CHANGE",
    "ATO_RESISTANCE_HUMOR",
    "ATO_RESISTANCE_LATE_CANCEL",
    "ATO_TRANSFERENCE_POSITIVE",
    "ATO_TRANSFERENCE_NEGATIVE",
    "ATO_TRANSFERENCE_EROTIC",
    "ATO_THEME_SEPARATION_ANXIETY",
    "ATO_THEME_CONTROL",
    "ATO_THEME_ABANDONMENT",
    "ATO_THEME_SHAME_GUILT",
]

def test_all_16_markers_exist():
    """All 16 psychoanalytic markers should exist as YAML files"""
    for marker in EXPECTED_MARKERS:
        marker_path = MARKER_DIR / f"{marker}.yaml"
        assert marker_path.exists(), f"Marker {marker}.yaml not found"

def test_marker_structure_valid():
    """Each marker must have id, frame, examples, category fields"""
    for marker in EXPECTED_MARKERS:
        marker_path = MARKER_DIR / f"{marker}.yaml"
        with open(marker_path) as f:
            data = yaml.safe_load(f)

        assert data["id"] == marker
        assert "frame" in data
        assert "signal" in data["frame"]
        assert "concept" in data["frame"]
        assert "pragmatics" in data["frame"]
        assert "examples" in data
        assert len(data["examples"]) >= 5, f"{marker} needs at least 5 examples"
        assert "category" in data
        assert data["category"] in ["defense", "resistance", "transference", "theme"]

def test_regex_patterns_valid():
    """Signal patterns should be valid regex"""
    import re
    for marker in EXPECTED_MARKERS:
        marker_path = MARKER_DIR / f"{marker}.yaml"
        with open(marker_path) as f:
            data = yaml.safe_load(f)

        signals = data["frame"]["signal"]
        for signal in signals:
            if isinstance(signal, dict) and "pattern" in signal:
                pattern = signal["pattern"]
                try:
                    re.compile(pattern)
                except re.error as e:
                    pytest.fail(f"{marker} has invalid regex '{pattern}': {e}")
