import pytest
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ato_correlation_engine import CorrelationEngine
from ato_correlation_types import ProsodyFeatureVector, MarkerCorrelation

def test_engine_initialization():
    """Test correlation engine initialization."""
    engine = CorrelationEngine(speaker_id="test_speaker")
    assert engine.speaker_id == "test_speaker"
    assert engine.model is not None

def test_calculate_correlation():
    """Test calculating correlation between features and marker."""
    engine = CorrelationEngine(speaker_id="test")

    features = [
        ProsodyFeatureVector(0.2, -0.1, 0.15, 2.0, 0.35),
        ProsodyFeatureVector(0.25, -0.15, 0.1, 2.5, 0.4),
        ProsodyFeatureVector(0.15, -0.05, 0.2, 1.5, 0.3)
    ]

    marker_presence = [True, True, False]

    correlation = engine.calculate_correlation(
        "ATO_ANXIETY_HESITATION",
        features,
        marker_presence
    )

    assert correlation.marker_name == "ATO_ANXIETY_HESITATION"
    assert 0 <= correlation.confidence <= 1
    assert correlation.sample_count == 3

def test_predict_markers():
    """Test predicting markers from prosody features."""
    engine = CorrelationEngine(speaker_id="test")

    # Add some training data
    engine.model.correlations["ATO_ANXIETY_HESITATION"] = [
        MarkerCorrelation(
            marker_name="ATO_ANXIETY_HESITATION",
            confidence=0.85,
            sample_count=20,
            contributing_features={"pitch_variability": 0.7}
        )
    ]

    features = ProsodyFeatureVector(0.2, -0.12, 0.18, 2.3, 0.38)
    predictions = engine.predict_markers(features, threshold=0.5)

    assert isinstance(predictions, list)
    assert all(p.marker_name for p in predictions)