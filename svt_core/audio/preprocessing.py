#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Preprocessor - Applies adaptive preprocessing to improve transcription quality
"""
import numpy as np
import noisereduce as nr
from scipy import signal
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AudioPreprocessor:
    """Applies preprocessing techniques to enhance audio quality"""

    def __init__(self):
        """Initialize the preprocessor"""
        pass

    def reduce_noise(self, audio: np.ndarray, sample_rate: int,
                     stationary: bool = True) -> np.ndarray:
        """
        Reduce background noise using spectral gating

        Args:
            audio: Audio signal as numpy array
            sample_rate: Sample rate in Hz
            stationary: Whether to assume stationary noise (default: True)

        Returns:
            Denoised audio signal
        """
        # Use noisereduce library for spectral noise reduction
        denoised = nr.reduce_noise(
            y=audio,
            sr=sample_rate,
            stationary=stationary,
            prop_decrease=1.0  # Full noise reduction
        )

        logger.info("Applied noise reduction")

        return denoised

    def normalize_volume(self, audio: np.ndarray, target_level: float = -20) -> np.ndarray:
        """
        Normalize audio volume to target level in dBFS

        Args:
            audio: Audio signal as numpy array
            target_level: Target RMS level in dBFS (default: -20)

        Returns:
            Normalized audio signal
        """
        # Calculate current RMS level
        rms = np.sqrt(np.mean(audio ** 2))

        if rms == 0:
            logger.warning("Audio RMS is zero, skipping normalization")
            return audio

        # Convert to dB
        current_db = 20 * np.log10(rms)

        # Calculate required gain
        gain_db = target_level - current_db
        gain_linear = 10 ** (gain_db / 20)

        # Apply gain
        normalized = audio * gain_linear

        # Prevent clipping
        max_val = np.max(np.abs(normalized))
        if max_val > 0.95:
            normalized = normalized * (0.95 / max_val)

        logger.info(f"Normalized audio: {current_db:.1f} dB -> {target_level:.1f} dB")

        return normalized

    def apply_highpass_filter(self, audio: np.ndarray, sample_rate: int,
                              cutoff: float = 80) -> np.ndarray:
        """
        Apply high-pass filter to remove low-frequency noise (rumble, hum)

        Args:
            audio: Audio signal as numpy array
            sample_rate: Sample rate in Hz
            cutoff: Cutoff frequency in Hz (default: 80 Hz)

        Returns:
            Filtered audio signal
        """
        # Design Butterworth high-pass filter
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff / nyquist

        # 4th order filter for good rolloff
        b, a = signal.butter(4, normalized_cutoff, btype='high')

        # Apply filter
        filtered = signal.filtfilt(b, a, audio)

        logger.info(f"Applied high-pass filter at {cutoff} Hz")

        return filtered

    def preprocess_adaptive(self, audio: np.ndarray, sample_rate: int,
                           quality_score: float) -> np.ndarray:
        """
        Apply adaptive preprocessing based on quality score

        Quality ranges:
        - 0.0-0.4: Aggressive (denoise + normalize + filter)
        - 0.4-0.6: Moderate (denoise + normalize)
        - 0.6-0.8: Light (normalize only)
        - 0.8-1.0: Minimal (no processing)

        Args:
            audio: Audio signal as numpy array
            sample_rate: Sample rate in Hz
            quality_score: Quality score from 0.0 to 1.0

        Returns:
            Preprocessed audio signal
        """
        processed = audio.copy()

        if quality_score >= 0.8:
            # High quality - no preprocessing needed
            logger.info(f"Quality {quality_score:.2f}: No preprocessing")
            return processed

        if quality_score >= 0.6:
            # Good quality - light normalization only
            logger.info(f"Quality {quality_score:.2f}: Light preprocessing (normalize)")
            processed = self.normalize_volume(processed)
            return processed

        if quality_score >= 0.4:
            # Medium quality - denoise + normalize
            logger.info(f"Quality {quality_score:.2f}: Moderate preprocessing (denoise + normalize)")
            processed = self.reduce_noise(processed, sample_rate)
            processed = self.normalize_volume(processed)
            return processed

        # Low quality - full pipeline
        logger.info(f"Quality {quality_score:.2f}: Aggressive preprocessing (all techniques)")
        processed = self.apply_highpass_filter(processed, sample_rate)
        processed = self.reduce_noise(processed, sample_rate)
        processed = self.normalize_volume(processed)

        return processed
