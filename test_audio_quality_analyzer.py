#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for AudioQualityAnalyzer
"""
import pytest
import numpy as np
from pathlib import Path
from audio_quality_analyzer import AudioQualityAnalyzer


def test_calculate_snr_clean_audio():
    """Test SNR calculation with clean synthetic audio"""
    # Create clean sine wave (high SNR)
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    clean_signal = np.sin(2 * np.pi * 440 * t)  # 440 Hz tone

    analyzer = AudioQualityAnalyzer()
    snr = analyzer._calculate_snr(clean_signal, sample_rate)

    # Clean sine wave should have very high SNR (>40 dB)
    assert snr > 40.0, f"Expected SNR > 40 dB for clean signal, got {snr:.2f}"


def test_calculate_snr_noisy_audio():
    """Test SNR calculation with noisy synthetic audio"""
    # Create noisy signal (low SNR)
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    signal = np.sin(2 * np.pi * 440 * t)
    noise = np.random.normal(0, 0.5, signal.shape)  # Heavy noise
    noisy_signal = signal + noise

    analyzer = AudioQualityAnalyzer()
    snr = analyzer._calculate_snr(noisy_signal, sample_rate)

    # Noisy signal should have low SNR (<20 dB)
    assert snr < 20.0, f"Expected SNR < 20 dB for noisy signal, got {snr:.2f}"


def test_detect_clipping_clean_audio():
    """Test clipping detection with audio in normal range"""
    # Audio in range [-0.8, 0.8] - no clipping
    audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000)) * 0.8

    analyzer = AudioQualityAnalyzer()
    clipping_ratio = analyzer._detect_clipping(audio)

    # Should detect no clipping (< 0.01)
    assert clipping_ratio < 0.01, f"Expected clipping ratio < 0.01, got {clipping_ratio:.4f}"


def test_detect_clipping_clipped_audio():
    """Test clipping detection with clipped audio"""
    # Create clipped audio (values at ±1.0)
    audio = np.clip(np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000)) * 1.5, -1.0, 1.0)

    analyzer = AudioQualityAnalyzer()
    clipping_ratio = analyzer._detect_clipping(audio)

    # Should detect significant clipping (> 0.05)
    assert clipping_ratio > 0.05, f"Expected clipping ratio > 0.05, got {clipping_ratio:.4f}"


def test_detect_silence_mostly_silent():
    """Test silence detection with mostly silent audio"""
    # Create audio that's 80% silence (amplitude < 0.01)
    audio = np.random.normal(0, 0.005, 16000)  # Very quiet noise

    analyzer = AudioQualityAnalyzer()
    silence_ratio = analyzer._detect_silence(audio)

    # Should detect high silence ratio (> 0.7)
    assert silence_ratio > 0.7, f"Expected silence ratio > 0.7, got {silence_ratio:.4f}"


def test_detect_silence_active_speech():
    """Test silence detection with active speech-like audio"""
    # Simulate speech with varying amplitude
    t = np.linspace(0, 1, 16000)
    audio = np.sin(2 * np.pi * 200 * t) * (0.3 + 0.3 * np.sin(2 * np.pi * 5 * t))

    analyzer = AudioQualityAnalyzer()
    silence_ratio = analyzer._detect_silence(audio)

    # Should detect low silence ratio (< 0.3)
    assert silence_ratio < 0.3, f"Expected silence ratio < 0.3, got {silence_ratio:.4f}"


def test_calculate_quality_score_high_quality():
    """Test quality score calculation for high-quality audio"""
    # High SNR, no clipping, minimal silence
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    audio = np.sin(2 * np.pi * 440 * t) * 0.7  # Clean tone at good level

    analyzer = AudioQualityAnalyzer()
    score = analyzer.calculate_quality_score(audio, sample_rate)

    # High quality should score > 0.7
    assert score > 0.7, f"Expected quality score > 0.7, got {score:.4f}"
    assert 0.0 <= score <= 1.0, f"Quality score must be in [0, 1], got {score:.4f}"


def test_calculate_quality_score_low_quality():
    """Test quality score calculation for low-quality audio"""
    # Low SNR, some clipping, lots of silence
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Noisy, clipped, with silent sections
    signal = np.sin(2 * np.pi * 440 * t)
    noise = np.random.normal(0, 0.4, signal.shape)
    audio = np.clip(signal + noise, -1.0, 1.0)
    audio[:3200] = 0.0  # 20% silence at start

    analyzer = AudioQualityAnalyzer()
    score = analyzer.calculate_quality_score(audio, sample_rate)

    # Low quality should score < 0.5
    assert score < 0.5, f"Expected quality score < 0.5, got {score:.4f}"
    assert 0.0 <= score <= 1.0, f"Quality score must be in [0, 1], got {score:.4f}"


def test_analyze_audio_file(tmp_path):
    """Test full audio file analysis"""
    import soundfile as sf

    # Create temporary audio file
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t) * 0.6

    audio_file = tmp_path / "test_audio.wav"
    sf.write(audio_file, audio, sample_rate)

    analyzer = AudioQualityAnalyzer()
    result = analyzer.analyze_audio_file(str(audio_file))

    # Check result structure
    assert isinstance(result, dict)
    assert "quality_score" in result
    assert "snr_db" in result
    assert "clipping_ratio" in result
    assert "silence_ratio" in result
    assert "sample_rate" in result
    assert "duration" in result

    # Check value ranges
    assert 0.0 <= result["quality_score"] <= 1.0
    assert result["snr_db"] > 0
    assert result["sample_rate"] == sample_rate
    assert abs(result["duration"] - duration) < 0.1  # Allow small tolerance
