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
