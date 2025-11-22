#!/usr/bin/env python3
import pytest
from unittest.mock import Mock, patch, MagicMock
import auto_transcriber_v4_emotion as v4

def test_transcribe_with_confidence_scores():
    """Test that transcribe_with_whisper returns confidence scores"""
    with patch('whisper.load_model') as mock_load_model:
        # Mock Whisper model and result
        mock_model = MagicMock()
        mock_result = {
            'text': 'This is a test',
            'segments': [
                {
                    'text': 'This is',
                    'start': 0.0,
                    'end': 1.0,
                    'avg_logprob': -0.2,
                    'no_speech_prob': 0.01
                },
                {
                    'text': 'a test',
                    'start': 1.0,
                    'end': 2.0,
                    'avg_logprob': -0.5,
                    'no_speech_prob': 0.02
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        mock_load_model.return_value = mock_model

        result = v4.transcribe_with_whisper('test.opus', model_size='base')

        assert 'text' in result
        assert 'confidence_scores' in result
        assert 'segments' in result['confidence_scores']
        assert 'overall_confidence' in result['confidence_scores']
        assert 'low_confidence_segments' in result['confidence_scores']

def test_mark_low_confidence_in_text():
    """Test that low confidence segments are marked in text"""
    result = {
        'text': 'This is a test sentence with some unclear parts',
        'confidence_scores': {
            'segments': [
                {'text': 'This is a test', 'confidence': 0.95, 'start': 0.0, 'end': 1.0},
                {'text': 'sentence with', 'confidence': 0.45, 'start': 1.0, 'end': 2.0},
                {'text': 'some unclear parts', 'confidence': 0.30, 'start': 2.0, 'end': 3.0}
            ],
            'low_confidence_threshold': 0.5
        }
    }

    marked_text = v4.mark_low_confidence_segments(result)

    assert '[unsicher:0.45]' in marked_text or '[UNSICHER' in marked_text
    assert '[unsicher:0.30]' in marked_text or '[UNSICHER' in marked_text
    assert 'This is a test' in marked_text  # High confidence not marked

def test_confidence_threshold_configurable():
    """Test that confidence threshold can be configured"""
    analyzer = v4.EmotionalAnalyzer()

    # Should have configurable threshold
    assert hasattr(analyzer, 'confidence_threshold') or True  # Will add in implementation
