#!/usr/bin/env python3
"""Simple test runner for prosody_analyzer tests"""

import sys
import numpy as np
from prosody_analyzer import ProsodyAnalyzer

def test_prosody_analyzer_initialization():
    """Test that ProsodyAnalyzer initializes correctly"""
    analyzer = ProsodyAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'extract_prosody')
    print("✓ test_prosody_analyzer_initialization passed")

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
    print("✓ test_extract_prosody_returns_dict passed")

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
    print("✓ test_pitch_extraction passed")

def test_tempo_extraction():
    """Test tempo/rhythm extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    tempo_data = result['tempo']
    assert 'bpm' in tempo_data
    assert 'speech_rate' in tempo_data
    print("✓ test_tempo_extraction passed")

def test_energy_extraction():
    """Test energy/loudness extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    energy_data = result['energy']
    assert 'mean' in energy_data
    assert 'std' in energy_data
    assert 'dynamic_range' in energy_data
    print("✓ test_energy_extraction passed")

if __name__ == '__main__':
    tests = [
        test_prosody_analyzer_initialization,
        test_extract_prosody_returns_dict,
        test_pitch_extraction,
        test_tempo_extraction,
        test_energy_extraction
    ]

    passed = 0
    failed = 0

    print("\nRunning prosody_analyzer tests...\n")

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print(f"{'='*50}\n")

    sys.exit(0 if failed == 0 else 1)
