import pytest
from enhanced_components.speaker_visualizer import SpeakerVisualizer

def test_visualizer_initialization():
    """Test speaker visualizer initialization"""
    visualizer = SpeakerVisualizer()
    assert visualizer is not None
    assert hasattr(visualizer, 'format_segment')

def test_format_segment_with_colors():
    """Test formatting segment with speaker colors"""
    visualizer = SpeakerVisualizer()

    segment = {
        'speaker': 'Therapeut',
        'text': 'Test text',
        'timestamp': '14:23:15',
        'confidence': 0.92
    }

    result = visualizer.format_segment(segment)
    assert 'Therapeut' in result
    assert 'Test text' in result
    assert '14:23:15' in result
    assert '0.92' in str(result) or 'confident' in result

def test_speaker_color_assignment():
    """Test automatic color assignment to speakers"""
    visualizer = SpeakerVisualizer()

    color1 = visualizer.get_speaker_color('Speaker A')
    color2 = visualizer.get_speaker_color('Speaker B')
    color3 = visualizer.get_speaker_color('Speaker A')  # Should get same color

    assert color1 != color2
    assert color1 == color3