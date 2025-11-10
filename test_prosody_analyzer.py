#!/usr/bin/env python3
import pytest
import numpy as np
from pathlib import Path
from prosody_analyzer import ProsodyAnalyzer

def test_prosody_analyzer_initialization():
    """Test that ProsodyAnalyzer initializes correctly"""
    analyzer = ProsodyAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'extract_prosody')

def test_extract_prosody_returns_dict():
    """Test that extract_prosody returns expected data structure"""
    analyzer = ProsodyAnalyzer()
    # Create dummy audio data (1 second at 22050 Hz)
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    assert isinstance(result, dict)
    assert 'pitch' in result
    assert 'tempo' in result
    assert 'energy' in result

def test_pitch_extraction():
    """Test pitch/F0 extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    pitch_data = result['pitch']
    assert 'mean' in pitch_data
    assert 'std' in pitch_data
    assert 'contour' in pitch_data
    assert isinstance(pitch_data['contour'], list)

def test_tempo_extraction():
    """Test tempo/rhythm extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    tempo_data = result['tempo']
    assert 'bpm' in tempo_data
    assert 'speech_rate' in tempo_data

def test_energy_extraction():
    """Test energy/loudness extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    energy_data = result['energy']
    assert 'mean' in energy_data
    assert 'std' in energy_data
    assert 'dynamic_range' in energy_data
