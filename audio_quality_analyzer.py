#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Quality Analyzer - Analyzes audio characteristics for intelligent preprocessing
"""
import numpy as np
import librosa
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AudioQualityAnalyzer:
    """Analyzes audio quality metrics to determine optimal transcription settings"""

    def __init__(self):
        """Initialize the analyzer"""
        pass

    def _calculate_snr(self, audio: np.ndarray, sample_rate: int) -> float:
        """
        Calculate Signal-to-Noise Ratio (SNR) in dB

        Uses spectral analysis to separate signal from noise components

        Args:
            audio: Audio signal as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            SNR in decibels (dB)
        """
        # Use spectral analysis to estimate signal and noise
        # Apply short-time Fourier transform
        stft = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)

        # Signal: top 75th percentile of magnitudes (strong components)
        # Noise: bottom 25th percentile (weak components)
        signal_threshold = np.percentile(magnitude, 75)
        noise_threshold = np.percentile(magnitude, 25)

        signal_power = np.mean(magnitude[magnitude > signal_threshold] ** 2)
        noise_power = np.mean(magnitude[magnitude < noise_threshold] ** 2)

        # Avoid division by zero
        if noise_power == 0:
            return 60.0  # Perfect signal

        # SNR in dB: 10 * log10(signal_power / noise_power)
        snr_db = 10 * np.log10(signal_power / noise_power)

        return float(snr_db)

    def _detect_clipping(self, audio: np.ndarray, threshold: float = 0.99) -> float:
        """
        Detect audio clipping (samples at maximum amplitude)

        Args:
            audio: Audio signal as numpy array
            threshold: Amplitude threshold for clipping detection (default: 0.99)

        Returns:
            Ratio of clipped samples (0.0 to 1.0)
        """
        # Count samples near maximum amplitude
        clipped_samples = np.sum(np.abs(audio) >= threshold)
        total_samples = len(audio)

        clipping_ratio = clipped_samples / total_samples if total_samples > 0 else 0.0

        return float(clipping_ratio)

    def _detect_silence(self, audio: np.ndarray, threshold_db: float = -40) -> float:
        """
        Detect silence ratio in audio

        Args:
            audio: Audio signal as numpy array
            threshold_db: Silence threshold in dB (default: -40 dB)

        Returns:
            Ratio of silent samples (0.0 to 1.0)
        """
        # Convert to dB scale
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        audio_db = 20 * np.log10(np.abs(audio) + epsilon)

        # Count samples below silence threshold
        silent_samples = np.sum(audio_db < threshold_db)
        total_samples = len(audio)

        silence_ratio = silent_samples / total_samples if total_samples > 0 else 0.0

        return float(silence_ratio)
