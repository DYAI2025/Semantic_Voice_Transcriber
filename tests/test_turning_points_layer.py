import pytest
from Turning_Points_in_Transcription.integration.turning_points_layer import TurningPointsLayer

def test_layer_initialization():
    """Test turning points layer can be initialized"""
    layer = TurningPointsLayer()
    assert layer is not None
    assert hasattr(layer, 'process_transcript')

def test_process_transcript_with_prosody():
    """Test processing transcript with prosody features"""
    layer = TurningPointsLayer()

    transcript = {
        'segments': [
            {
                'id': 0,
                'start': 0.0,
                'end': 5.0,
                'text': 'Test segment',
                'speaker': 'A'
            }
        ]
    }

    prosody_features = {
        0: {
            'tempo_wpm': 120,
            'pitch_mean_hz': 200,
            'energy_rms': 0.05,
            'hnr_mean': 15.0
        }
    }

    result = layer.process_transcript(transcript, prosody_features)
    assert 'turning_points' in result
    assert 'cosd_timeline' in result
    assert 'markers' in result