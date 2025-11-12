import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ato_correlation_engine import CorrelationEngine
from ato_correlation_types import ProsodyFeatureVector

def test_apply_correlations_to_segment():
    """Test applying correlations during transcription."""
    from auto_transcriber_v4_emotion import apply_ato_correlations

    engine = CorrelationEngine(speaker_id="test")

    segment = {
        "text": "I'm not really sure about this",
        "prosody_features": {
            "pitch_deviation": 0.25,
            "tempo_deviation": -0.15,
            "energy_deviation": -0.10,
            "pause_frequency": 3.0,
            "pitch_variability": 0.40
        }
    }

    enhanced_segment = apply_ato_correlations(segment, engine)

    assert "ato_markers" in enhanced_segment
    assert "correlation_confidence" in enhanced_segment

def test_correlation_explanation_generation():
    """Test generating human-readable explanations."""
    from auto_transcriber_v4_emotion import generate_correlation_explanation

    prediction = Mock(
        marker_name="ATO_ANXIETY_HESITATION",
        confidence=0.85,
        contributing_features={
            "pitch_variability": 0.70,
            "pause_frequency": 0.65
        }
    )

    explanation = generate_correlation_explanation(prediction)

    assert "ATO_ANXIETY_HESITATION" in explanation
    assert "85%" in explanation or "0.85" in explanation
    assert "pitch_variability" in explanation