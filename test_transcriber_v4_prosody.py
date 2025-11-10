#!/usr/bin/env python3
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np

# Import after we modify the file
import auto_transcriber_v4_emotion as v4

def test_emotional_analyzer_has_prosody_analyzer():
    """Test that EmotionalAnalyzer includes prosody analyzer"""
    analyzer = v4.EmotionalAnalyzer()
    assert hasattr(analyzer, 'prosody_analyzer')
    assert analyzer.prosody_analyzer is not None

def test_analyze_emotion_includes_prosody():
    """Test that analyze_emotion returns prosody data"""
    analyzer = v4.EmotionalAnalyzer()

    # Mock audio data
    audio_data = np.random.randn(22050).astype(np.float32)
    text = "This is a test sentence."

    result = analyzer.analyze_emotion(text, audio_data=audio_data, sr=22050)

    assert 'prosody' in result
    assert 'pitch' in result['prosody']
    assert 'tempo' in result['prosody']
    assert 'energy' in result['prosody']

def test_analyze_emotion_without_audio_data():
    """Test that analyze_emotion works without audio (text-only)"""
    analyzer = v4.EmotionalAnalyzer()
    text = "This is a test sentence."

    result = analyzer.analyze_emotion(text, audio_data=None)

    # Should still work but prosody may be empty/default
    assert 'prosody' in result
