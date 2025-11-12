import pytest
import numpy as np
from prosody_extractor import ProsodyExtractor

def test_extract_hnr():
    """Test Harmonics-to-Noise Ratio extraction"""
    extractor = ProsodyExtractor()
    # Create test audio (1 second sine wave at 440Hz)
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    audio = np.sin(2 * np.pi * 440 * t)

    result = extractor.extract_hnr(audio, sample_rate)
    assert 'hnr_mean' in result
    assert 'hnr_std' in result
    assert result['hnr_mean'] > 0

def test_extract_jitter_shimmer():
    """Test jitter and shimmer extraction"""
    extractor = ProsodyExtractor()
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    audio = np.sin(2 * np.pi * 440 * t)

    result = extractor.extract_voice_quality(audio, sample_rate)
    assert 'jitter_local' in result
    assert 'shimmer_local' in result
    assert 0 <= result['jitter_local'] <= 1
    assert 0 <= result['shimmer_local'] <= 1