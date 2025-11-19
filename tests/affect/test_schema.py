import pytest
from src.affect.schema import validate_vad_output

def test_valid_vad_output():
    """Valid VAD output should pass validation."""
    valid_data = {
        "version": "1.0",
        "session_id": "test-123",
        "samples": [
            {
                "timestamp": 0.0,
                "speaker_id": "A",
                "valence": 0.5,
                "arousal": 0.3,
                "dominance": 0.2,
                "confidence": 0.85
            }
        ],
        "events": [],
        "provenance": {
            "model": "rule-based-v1",
            "config_hash": "abc123"
        }
    }
    assert validate_vad_output(valid_data) is True

def test_invalid_vad_output_missing_field():
    """Missing required field should fail validation."""
    invalid_data = {
        "version": "1.0",
        "samples": []
        # Missing session_id, events, provenance
    }
    with pytest.raises(ValueError, match="session_id"):
        validate_vad_output(invalid_data)

def test_vad_sample_out_of_range():
    """VAD values outside [-1, +1] should fail."""
    invalid_data = {
        "version": "1.0",
        "session_id": "test-123",
        "samples": [
            {
                "timestamp": 0.0,
                "speaker_id": "A",
                "valence": 1.5,  # Out of range!
                "arousal": 0.0,
                "dominance": 0.0,
                "confidence": 0.8
            }
        ],
        "events": [],
        "provenance": {"model": "test", "config_hash": "abc123"}
    }
    with pytest.raises(ValueError, match="1.5"):
        validate_vad_output(invalid_data)
