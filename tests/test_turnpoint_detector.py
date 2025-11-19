# tests/test_turnpoint_detector.py
import pytest
from turnpoint_detector import TurnpointDetector

@pytest.fixture
def sample_utterances():
    """Sample utterances with emotion dynamics"""
    return [
        {
            "id": 1,
            "ued_emotions": {"valence": -0.6, "arousal": 0.7},
            "markers": ["ATO_RESISTANCE_SILENCE"],
            "prosody": {"pause_before_ms": 500}
        },
        {
            "id": 2,
            "ued_emotions": {"valence": 0.3, "arousal": 0.4},  # Big valence jump
            "markers": [],
            "prosody": {"pause_before_ms": 2500}  # Long pause
        },
        {
            "id": 3,
            "ued_emotions": {"valence": 0.2, "arousal": 0.5},
            "markers": ["ATO_THEME_CONTROL"],  # Theme change
            "prosody": {"pause_before_ms": 800}
        }
    ]

def test_detector_initialization():
    """Detector should load config thresholds"""
    detector = TurnpointDetector(config_path="config/psychoanalysis_config.yaml")
    assert detector.valence_threshold == 0.5
    assert detector.arousal_threshold == 0.3
    assert detector.prosody_pause_threshold == 2000

def test_detect_emotional_shift(sample_utterances):
    """Should detect valence jump > threshold"""
    detector = TurnpointDetector(config_path="config/psychoanalysis_config.yaml")
    turnpoints = detector.detect_turnpoints(sample_utterances)

    # Expect turnpoint at utterance 2 (valence jump from -0.6 to 0.3 = 0.9)
    emotional_turnpoints = [tp for tp in turnpoints if tp["type"] == "emotional_shift"]
    assert len(emotional_turnpoints) >= 1
    assert emotional_turnpoints[0]["utterance_id"] == 2

def test_detect_resistance_breakthrough(sample_utterances):
    """Should detect resistance → openness transition"""
    detector = TurnpointDetector(config_path="config/psychoanalysis_config.yaml")
    turnpoints = detector.detect_turnpoints(sample_utterances)

    # Expect turnpoint at utterance 2 (had resistance in 1, none in 2, positive valence)
    resistance_turnpoints = [tp for tp in turnpoints if tp["type"] == "resistance_breakthrough"]
    assert len(resistance_turnpoints) >= 1

def test_prosody_enhancement():
    """Long pause + emotion shift should increase significance"""
    utterances = [
        {"id": 1, "ued_emotions": {"valence": -0.5, "arousal": 0.6}, "markers": [], "prosody": {"pause_before_ms": 500}},
        {"id": 2, "ued_emotions": {"valence": 0.1, "arousal": 0.4}, "markers": [], "prosody": {"pause_before_ms": 3000}}
    ]

    detector = TurnpointDetector(config_path="config/psychoanalysis_config.yaml")
    turnpoints = detector.detect_turnpoints(utterances)

    # Find the emotional_shift turnpoint
    tp = next(tp for tp in turnpoints if tp["type"] == "emotional_shift")
    assert tp["significance"] == "high"
    assert "prosody_support" in tp
