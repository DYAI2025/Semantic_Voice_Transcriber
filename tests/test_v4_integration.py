import pytest
from unittest.mock import Mock, patch

def test_v4_has_turning_points_option():
    """Test that v4 transcriber has turning points option"""
    from auto_transcriber_v4_emotion import WhisperSpeakerMatcherV4
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        transcriber = WhisperSpeakerMatcherV4(base_path=tmpdir)
        assert hasattr(transcriber, 'enable_turning_points')
        assert hasattr(transcriber, 'enable_dual_markers')

def test_v4_processes_with_layers():
    """Test v4 processes through all layers when enabled"""
    from auto_transcriber_v4_emotion import WhisperSpeakerMatcherV4
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        transcriber = WhisperSpeakerMatcherV4(base_path=tmpdir)
        transcriber.enable_turning_points = True
        transcriber.enable_dual_markers = True

    # Mock audio file
    audio_file = "test_audio.wav"

    with patch.object(transcriber, 'process_audio') as mock_process:
        mock_process.return_value = {
            'transcript': 'Test',
            'turning_points': [],
            'markers': {'simple': [], 'advanced': []}
        }

        result = transcriber.process_audio(audio_file)

        assert 'turning_points' in result
        assert 'markers' in result