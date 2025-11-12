import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataclasses import asdict
from ato_correlation_types import (
    ProsodyFeatureVector,
    MarkerCorrelation,
    CorrelationModel
)

def test_prosody_feature_vector_creation():
    """Test creating prosody feature vector from raw features."""
    vector = ProsodyFeatureVector(
        pitch_deviation=0.15,
        tempo_deviation=-0.10,
        energy_deviation=0.25,
        pause_frequency=2.5,
        pitch_variability=0.30
    )
    assert vector.pitch_deviation == 0.15
    assert vector.to_array().shape == (5,)

def test_marker_correlation_confidence():
    """Test marker correlation with confidence scoring."""
    correlation = MarkerCorrelation(
        marker_name="ATO_ANXIETY_HESITATION",
        confidence=0.82,
        sample_count=47,
        contributing_features={"pitch_jitter": 0.65}
    )
    assert correlation.is_confident(threshold=0.8) == True
    assert correlation.is_confident(threshold=0.9) == False

def test_correlation_model_initialization():
    """Test correlation model with empty state."""
    model = CorrelationModel(speaker_id="test_speaker")
    assert model.speaker_id == "test_speaker"
    assert len(model.correlations) == 0
    assert model.total_samples == 0