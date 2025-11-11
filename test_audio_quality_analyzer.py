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
