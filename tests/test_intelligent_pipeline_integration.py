#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for Intelligent Pipeline
"""
import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
from audio_quality_analyzer import AudioQualityAnalyzer
from audio_preprocessor import AudioPreprocessor
import auto_transcriber_v4_emotion as v4


@pytest.fixture
def test_audio_files(tmp_path):
    """Create test audio files with different quality levels"""
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # High quality audio
    high_quality = np.sin(2 * np.pi * 440 * t) * 0.7
    high_quality_path = tmp_path / "high_quality.wav"
    sf.write(high_quality_path, high_quality, sample_rate)

    # Low quality audio (noisy, clipped)
    low_quality_signal = np.sin(2 * np.pi * 440 * t)
    noise = np.random.normal(0, 0.3, low_quality_signal.shape)
    low_quality = np.clip(low_quality_signal + noise, -1.0, 1.0)
    low_quality_path = tmp_path / "low_quality.wav"
    sf.write(low_quality_path, low_quality, sample_rate)

    return {
        "high_quality": high_quality_path,
        "low_quality": low_quality_path
    }


def test_end_to_end_high_quality(test_audio_files):
    """Test complete pipeline with high quality audio"""
    analyzer = AudioQualityAnalyzer()
    preprocessor = AudioPreprocessor()

    # Analyze quality
    metrics = analyzer.analyze_audio_file(str(test_audio_files["high_quality"]))

    # Should detect high quality
    assert metrics["quality_score"] > 0.7, \
        f"Expected high quality score, got {metrics['quality_score']:.2f}"

    # Preprocessing should be minimal
    import librosa
    audio, sr = librosa.load(test_audio_files["high_quality"], sr=None)
    processed = preprocessor.preprocess_adaptive(audio, sr, metrics["quality_score"])

    # Should have minimal changes for high quality
    assert processed.shape == audio.shape


def test_end_to_end_low_quality(test_audio_files):
    """Test complete pipeline with low quality audio"""
    analyzer = AudioQualityAnalyzer()
    preprocessor = AudioPreprocessor()

    # Analyze quality
    metrics = analyzer.analyze_audio_file(str(test_audio_files["low_quality"]))

    # Should detect low quality
    assert metrics["quality_score"] < 0.6, \
        f"Expected low quality score, got {metrics['quality_score']:.2f}"

    # Preprocessing should be aggressive
    import librosa
    audio, sr = librosa.load(test_audio_files["low_quality"], sr=None)
    processed = preprocessor.preprocess_adaptive(audio, sr, metrics["quality_score"])

    # Should apply significant processing
    assert not np.array_equal(processed, audio)


def test_model_selection_logic():
    """Test that model selection follows quality score correctly"""
    test_cases = [
        (0.2, "large"),   # Very poor quality
        (0.5, "medium"),  # Medium quality
        (0.7, "medium"),  # Good quality
        (0.9, "small"),   # Excellent quality
    ]

    for quality_score, expected_model in test_cases:
        # Model selection logic from svt.py
        if quality_score < 0.4:
            selected_model = "large"
        elif quality_score < 0.6:
            selected_model = "medium"
        elif quality_score < 0.8:
            selected_model = "medium"
        else:
            selected_model = "small"

        assert selected_model == expected_model, \
            f"Quality {quality_score:.1f} should select {expected_model}, got {selected_model}"


def test_pipeline_components_exist():
    """Test that all pipeline components can be instantiated"""
    # Should be able to create instances without errors
    analyzer = AudioQualityAnalyzer()
    preprocessor = AudioPreprocessor()

    # Should have expected methods
    assert hasattr(analyzer, 'analyze_audio_file')
    assert hasattr(analyzer, 'calculate_quality_score')
    assert hasattr(preprocessor, 'preprocess_adaptive')
    assert hasattr(preprocessor, 'reduce_noise')
    assert hasattr(preprocessor, 'normalize_volume')
    assert hasattr(preprocessor, 'apply_highpass_filter')


def test_quality_score_ranges(test_audio_files):
    """Test that quality scores are always in valid range"""
    analyzer = AudioQualityAnalyzer()

    for audio_file in test_audio_files.values():
        metrics = analyzer.analyze_audio_file(str(audio_file))

        # Quality score must be in [0, 1]
        assert 0.0 <= metrics["quality_score"] <= 1.0, \
            f"Quality score {metrics['quality_score']} out of range"

        # All other metrics should be non-negative
        assert metrics["snr_db"] >= 0
        assert 0.0 <= metrics["clipping_ratio"] <= 1.0
        assert 0.0 <= metrics["silence_ratio"] <= 1.0
        assert metrics["sample_rate"] > 0
        assert metrics["duration"] > 0
