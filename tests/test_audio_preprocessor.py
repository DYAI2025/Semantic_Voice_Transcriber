#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for AudioPreprocessor
"""
import pytest
import numpy as np
from pathlib import Path
from audio_preprocessor import AudioPreprocessor


def test_reduce_noise():
    """Test noise reduction processes audio correctly"""
    # Create noisy audio
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    clean_signal = np.sin(2 * np.pi * 440 * t)
    noise = np.random.normal(0, 0.1, clean_signal.shape)
    noisy_audio = clean_signal + noise

    preprocessor = AudioPreprocessor()
    denoised_audio = preprocessor.reduce_noise(noisy_audio, sample_rate)

    # Output should have same shape
    assert denoised_audio.shape == noisy_audio.shape

    # Denoised audio should not be identical to input (something was done)
    # But also should not be all zeros or NaN
    assert not np.array_equal(denoised_audio, noisy_audio)
    assert not np.any(np.isnan(denoised_audio))
    assert np.abs(denoised_audio).max() > 0  # Not all zeros


def test_normalize_volume():
    """Test volume normalization"""
    # Create very quiet audio (max amplitude 0.05)
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    quiet_audio = np.sin(2 * np.pi * 440 * t) * 0.05

    preprocessor = AudioPreprocessor()
    normalized_audio = preprocessor.normalize_volume(quiet_audio, target_level=-20)

    # Normalized audio should have higher amplitude
    assert np.max(np.abs(normalized_audio)) > np.max(np.abs(quiet_audio))

    # But should not exceed reasonable bounds (< 1.0)
    assert np.max(np.abs(normalized_audio)) < 1.0


def test_normalize_volume_already_loud():
    """Test normalization doesn't over-amplify loud audio"""
    # Create already-loud audio
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    loud_audio = np.sin(2 * np.pi * 440 * t) * 0.9

    preprocessor = AudioPreprocessor()
    normalized_audio = preprocessor.normalize_volume(loud_audio, target_level=-20)

    # Should not clip
    assert np.max(np.abs(normalized_audio)) <= 1.0


def test_apply_highpass_filter():
    """Test high-pass filter removes low frequencies"""
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create signal with low frequency (50 Hz) and speech frequency (200 Hz)
    low_freq = np.sin(2 * np.pi * 50 * t) * 0.5
    speech_freq = np.sin(2 * np.pi * 200 * t) * 0.5
    audio = low_freq + speech_freq

    preprocessor = AudioPreprocessor()
    filtered = preprocessor.apply_highpass_filter(audio, sample_rate, cutoff=80)

    # Filtered audio should have reduced low-frequency component
    # Use FFT to check frequency content
    fft_original = np.fft.rfft(audio)
    fft_filtered = np.fft.rfft(filtered)
    freqs = np.fft.rfftfreq(len(audio), 1/sample_rate)

    # Energy at 50 Hz should be significantly reduced
    idx_50hz = np.argmin(np.abs(freqs - 50))
    assert np.abs(fft_filtered[idx_50hz]) < 0.5 * np.abs(fft_original[idx_50hz]), \
        "High-pass filter did not reduce low frequencies"


def test_preprocess_adaptive_high_quality():
    """Test adaptive preprocessing with high-quality audio (minimal processing)"""
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    audio = np.sin(2 * np.pi * 440 * t) * 0.7  # Clean audio

    preprocessor = AudioPreprocessor()
    processed = preprocessor.preprocess_adaptive(audio, sample_rate, quality_score=0.85)

    # High quality audio should have minimal changes
    # Should only normalize, no heavy processing
    assert processed.shape == audio.shape


def test_preprocess_adaptive_low_quality():
    """Test adaptive preprocessing with low-quality audio (full processing)"""
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create poor quality audio
    signal_audio = np.sin(2 * np.pi * 440 * t) * 0.3
    noise = np.random.normal(0, 0.15, signal_audio.shape)
    audio = signal_audio + noise

    preprocessor = AudioPreprocessor()
    processed = preprocessor.preprocess_adaptive(audio, sample_rate, quality_score=0.3)

    # Low quality should trigger full processing pipeline
    assert processed.shape == audio.shape
    # Processed audio should have changes (not identical)
    assert not np.allclose(processed, audio, rtol=0.1)
