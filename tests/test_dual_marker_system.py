import pytest
from Turning_Points_in_Transcription.integration.dual_marker_system import DualMarkerSystem

def test_dual_marker_initialization():
    """Test dual marker system initialization"""
    marker_system = DualMarkerSystem()
    assert marker_system is not None
    assert hasattr(marker_system, 'apply_markers')

def test_apply_simple_markers():
    """Test applying simple prosody markers"""
    marker_system = DualMarkerSystem(mode='simple')

    text = "This is a test segment"
    prosody = {
        'tempo_deviation_pct': 25,
        'pitch_deviation_pct': -20,
        'pause_before_ms': 1500
    }

    result = marker_system.apply_markers(text, prosody=prosody)
    assert '[TEMPO↑]' in result
    assert '[PITCH↓]' in result
    assert '[PAUSE]' in result

def test_apply_dual_markers():
    """Test applying both simple and advanced markers"""
    marker_system = DualMarkerSystem(mode='dual')

    text = "This is a breakthrough moment"
    prosody = {
        'tempo_deviation_pct': 30,
        'hnr_mean': 18.5
    }
    turning_points = [{
        'type': 'INNER_CHANGE_POINT',
        'confidence': 0.85
    }]

    result = marker_system.apply_markers(text, prosody=prosody, turning_points=turning_points)
    assert '[TEMPO↑]' in result
    assert '[TURNING_POINT:' in result