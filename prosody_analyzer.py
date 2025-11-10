#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prosody Analyzer - Extracts prosodic features for Voice-Marker 2.0
Features: Pitch (F0), Tempo/Rhythm, Energy/Loudness
"""

import numpy as np
import librosa
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ProsodyAnalyzer:
    """Extracts prosodic features from audio for therapeutic analysis"""

    def __init__(self,
                 hop_length: int = 512,
                 frame_length: int = 2048,
                 fmin: float = 75.0,  # Minimum pitch (Hz) for human speech
                 fmax: float = 500.0):  # Maximum pitch (Hz) for human speech
        """
        Initialize prosody analyzer

        Args:
            hop_length: Number of samples between successive frames
            frame_length: Frame length for analysis
            fmin: Minimum frequency for pitch detection (Hz)
            fmax: Maximum frequency for pitch detection (Hz)
        """
        self.hop_length = hop_length
        self.frame_length = frame_length
        self.fmin = fmin
        self.fmax = fmax

    def extract_prosody(self,
                       audio_data: np.ndarray,
                       sr: int = 22050) -> Dict[str, Any]:
        """
        Extract all prosodic features from audio

        Args:
            audio_data: Audio time series as numpy array
            sr: Sample rate

        Returns:
            Dictionary with pitch, tempo, and energy features
        """
        try:
            pitch_features = self._extract_pitch(audio_data, sr)
            tempo_features = self._extract_tempo(audio_data, sr)
            energy_features = self._extract_energy(audio_data, sr)

            return {
                'pitch': pitch_features,
                'tempo': tempo_features,
                'energy': energy_features
            }
        except Exception as e:
            logger.error(f"Error extracting prosody: {e}")
            return {
                'pitch': {'mean': 0, 'std': 0, 'contour': []},
                'tempo': {'bpm': 0, 'speech_rate': 0},
                'energy': {'mean': 0, 'std': 0, 'dynamic_range': 0}
            }

    def _extract_pitch(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Extract pitch (F0) features

        Returns:
            Dict with mean, std, and contour of pitch
        """
        # Extract pitch using librosa's piptrack
        pitches, magnitudes = librosa.piptrack(
            y=audio_data,
            sr=sr,
            hop_length=self.hop_length,
            fmin=self.fmin,
            fmax=self.fmax
        )

        # Get pitch contour (select pitch with highest magnitude at each frame)
        pitch_contour = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:  # Only include voiced frames
                pitch_contour.append(float(pitch))

        if len(pitch_contour) > 0:
            mean_pitch = np.mean(pitch_contour)
            std_pitch = np.std(pitch_contour)
        else:
            mean_pitch = 0
            std_pitch = 0

        return {
            'mean': float(mean_pitch),
            'std': float(std_pitch),
            'contour': pitch_contour
        }

    def _extract_tempo(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Extract tempo and rhythm features

        Returns:
            Dict with bpm and speech_rate
        """
        # Extract tempo
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0]

        # Estimate speech rate (syllables per second)
        # Using onset detection as proxy for syllables
        onsets = librosa.onset.onset_detect(y=audio_data, sr=sr, units='time')
        duration = len(audio_data) / sr
        speech_rate = len(onsets) / duration if duration > 0 else 0

        return {
            'bpm': float(tempo),
            'speech_rate': float(speech_rate)
        }

    def _extract_energy(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Extract energy (loudness) features

        Returns:
            Dict with mean, std, and dynamic_range
        """
        # Calculate RMS energy
        rms = librosa.feature.rms(
            y=audio_data,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )[0]

        mean_energy = np.mean(rms)
        std_energy = np.std(rms)
        dynamic_range = np.max(rms) - np.min(rms) if len(rms) > 0 else 0

        return {
            'mean': float(mean_energy),
            'std': float(std_energy),
            'dynamic_range': float(dynamic_range)
        }

    def extract_from_file(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract prosody from audio file

        Args:
            audio_path: Path to audio file

        Returns:
            Prosody features dict or None on error
        """
        try:
            audio_data, sr = librosa.load(audio_path, sr=None)
            return self.extract_prosody(audio_data, sr)
        except Exception as e:
            logger.error(f"Error loading audio file {audio_path}: {e}")
            return None
