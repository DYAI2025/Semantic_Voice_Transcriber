#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prosody Extractor - Extracts prosodic features from audio segments
Implements Phase 1: Big 4 Features (Tempo, Pitch, Energy, Pauses)
"""

import librosa
import parselmouth
from parselmouth.praat import call
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProsodyFeatures:
    """Container for prosody features of a single segment"""
    # Temporal information
    start_time: float
    end_time: float
    duration: float

    # Tempo features
    tempo_wpm: Optional[float] = None  # Words per minute
    word_count: int = 0

    # Pitch features (F0)
    pitch_mean_hz: Optional[float] = None
    pitch_std_hz: Optional[float] = None
    pitch_min_hz: Optional[float] = None
    pitch_max_hz: Optional[float] = None

    # Energy features
    energy_rms: Optional[float] = None
    energy_db: Optional[float] = None

    # Pause detection
    pause_before_ms: float = 0.0
    pause_after_ms: float = 0.0

    # Advanced parselmouth features (jitter/shimmer for voice quality)
    jitter_local: Optional[float] = None
    shimmer_local: Optional[float] = None

    # Deviation from baseline (will be calculated later)
    tempo_deviation_pct: Optional[float] = None
    pitch_deviation_pct: Optional[float] = None
    energy_deviation_pct: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ProsodyBaseline:
    """Baseline prosody features for comparison"""
    tempo_wpm_mean: float = 0.0
    tempo_wpm_std: float = 0.0

    pitch_mean_hz: float = 0.0
    pitch_std_hz: float = 0.0

    energy_rms_mean: float = 0.0
    energy_rms_std: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ProsodyExtractor:
    """
    Extracts prosodic features from audio segments

    Phase 1 Implementation:
    - Extract Big 4: Tempo, Pitch, Energy, Pauses
    - Per Whisper segment (3-10s chunks)
    - Calculate global baseline for deviation detection
    - Prepare for ATO marker triggering
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        pitch_floor: float = 75.0,  # Hz, typical for male voice
        pitch_ceiling: float = 500.0,  # Hz, typical for female voice
    ):
        """
        Initialize prosody extractor

        Args:
            sample_rate: Audio sample rate (Whisper uses 16kHz)
            pitch_floor: Minimum pitch to detect (Hz)
            pitch_ceiling: Maximum pitch to detect (Hz)
        """
        self.sample_rate = sample_rate
        self.pitch_floor = pitch_floor
        self.pitch_ceiling = pitch_ceiling
        self.baseline: Optional[ProsodyBaseline] = None

    def extract_segment_features(
        self,
        audio_segment: np.ndarray,
        start_time: float,
        end_time: float,
        text: str = "",
        previous_segment_end: Optional[float] = None,
        next_segment_start: Optional[float] = None
    ) -> ProsodyFeatures:
        """
        Extract prosody features from a single audio segment

        Args:
            audio_segment: Audio data (numpy array)
            start_time: Segment start time in seconds
            end_time: Segment end time in seconds
            text: Transcribed text for word counting
            previous_segment_end: End time of previous segment (for pause detection)
            next_segment_start: Start time of next segment (for pause detection)

        Returns:
            ProsodyFeatures object with extracted features
        """
        duration = end_time - start_time

        # Initialize features
        features = ProsodyFeatures(
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )

        # 1. TEMPO: Calculate WPM
        if text:
            word_count = len(text.split())
            features.word_count = word_count
            if duration > 0:
                features.tempo_wpm = (word_count / duration) * 60.0

        # 2. PITCH: Extract F0 using Parselmouth (Praat)
        try:
            # Create Parselmouth Sound object
            snd = parselmouth.Sound(
                audio_segment,
                sampling_frequency=self.sample_rate
            )

            # Extract pitch
            pitch = snd.to_pitch(
                time_step=0.01,  # 10ms steps
                pitch_floor=self.pitch_floor,
                pitch_ceiling=self.pitch_ceiling
            )

            # Get pitch values (excluding unvoiced frames)
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]  # Filter out unvoiced

            if len(pitch_values) > 0:
                features.pitch_mean_hz = float(np.mean(pitch_values))
                features.pitch_std_hz = float(np.std(pitch_values))
                features.pitch_min_hz = float(np.min(pitch_values))
                features.pitch_max_hz = float(np.max(pitch_values))

            # Extract jitter and shimmer (voice quality measures)
            try:
                point_process = call(snd, "To PointProcess (periodic, cc)",
                                    self.pitch_floor, self.pitch_ceiling)
                features.jitter_local = call(point_process, "Get jitter (local)",
                                           0, 0, 0.0001, 0.02, 1.3)
                features.shimmer_local = call([snd, point_process], "Get shimmer (local)",
                                             0, 0, 0.0001, 0.02, 1.3, 1.6)
            except Exception as e:
                logger.debug(f"Could not extract jitter/shimmer: {e}")

        except Exception as e:
            logger.warning(f"Pitch extraction failed: {e}")

        # 3. ENERGY: Calculate RMS energy
        try:
            rms = librosa.feature.rms(y=audio_segment)[0]
            features.energy_rms = float(np.mean(rms))

            # Convert to dB
            if features.energy_rms > 0:
                features.energy_db = float(20 * np.log10(features.energy_rms))
        except Exception as e:
            logger.warning(f"Energy extraction failed: {e}")

        # 4. PAUSES: Detect pauses before and after segment
        if previous_segment_end is not None:
            pause_before = start_time - previous_segment_end
            features.pause_before_ms = max(0.0, pause_before * 1000.0)

        if next_segment_start is not None:
            pause_after = next_segment_start - end_time
            features.pause_after_ms = max(0.0, pause_after * 1000.0)

        return features

    def extract_from_segments(
        self,
        audio_path: str,
        segments: List[Dict[str, Any]],
        calculate_baseline: bool = True
    ) -> Tuple[List[ProsodyFeatures], Optional[ProsodyBaseline]]:
        """
        Extract prosody features from all segments

        Args:
            audio_path: Path to audio file
            segments: List of Whisper segments with 'start', 'end', 'text'
            calculate_baseline: Whether to calculate baseline from this audio

        Returns:
            Tuple of (list of features, baseline)
        """
        logger.info(f"Extracting prosody from {len(segments)} segments...")

        # Load full audio file
        try:
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            return [], None

        all_features = []

        # Process each segment
        for i, segment in enumerate(segments):
            start_time = segment.get('start', 0.0)
            end_time = segment.get('end', 0.0)
            text = segment.get('text', '')

            # Extract audio segment
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            audio_segment = audio[start_sample:end_sample]

            # Determine previous and next segment times for pause detection
            prev_end = segments[i-1]['end'] if i > 0 else None
            next_start = segments[i+1]['start'] if i < len(segments)-1 else None

            # Extract features
            features = self.extract_segment_features(
                audio_segment,
                start_time,
                end_time,
                text,
                prev_end,
                next_start
            )

            all_features.append(features)

        # Calculate baseline if requested
        baseline = None
        if calculate_baseline and all_features:
            baseline = self._calculate_baseline(all_features)
            self.baseline = baseline

            # Calculate deviations from baseline
            self._add_baseline_deviations(all_features, baseline)

        logger.info(f"✅ Extracted prosody for {len(all_features)} segments")

        return all_features, baseline

    def _calculate_baseline(self, features_list: List[ProsodyFeatures]) -> ProsodyBaseline:
        """
        Calculate global baseline from all features

        Args:
            features_list: List of ProsodyFeatures

        Returns:
            ProsodyBaseline with mean and std values
        """
        # Collect valid values
        tempos = [f.tempo_wpm for f in features_list if f.tempo_wpm is not None]
        pitches = [f.pitch_mean_hz for f in features_list if f.pitch_mean_hz is not None]
        energies = [f.energy_rms for f in features_list if f.energy_rms is not None]

        baseline = ProsodyBaseline()

        if tempos:
            baseline.tempo_wpm_mean = float(np.mean(tempos))
            baseline.tempo_wpm_std = float(np.std(tempos))

        if pitches:
            baseline.pitch_mean_hz = float(np.mean(pitches))
            baseline.pitch_std_hz = float(np.std(pitches))

        if energies:
            baseline.energy_rms_mean = float(np.mean(energies))
            baseline.energy_rms_std = float(np.std(energies))

        logger.info(f"Baseline: Tempo={baseline.tempo_wpm_mean:.1f} WPM, "
                   f"Pitch={baseline.pitch_mean_hz:.1f} Hz, "
                   f"Energy={baseline.energy_rms_mean:.4f}")

        return baseline

    def _add_baseline_deviations(
        self,
        features_list: List[ProsodyFeatures],
        baseline: ProsodyBaseline
    ):
        """
        Calculate and add deviation percentages to features

        Args:
            features_list: List of ProsodyFeatures to update
            baseline: Baseline to compare against
        """
        for features in features_list:
            # Tempo deviation
            if features.tempo_wpm is not None and baseline.tempo_wpm_mean > 0:
                deviation = features.tempo_wpm - baseline.tempo_wpm_mean
                features.tempo_deviation_pct = (deviation / baseline.tempo_wpm_mean) * 100.0

            # Pitch deviation
            if features.pitch_mean_hz is not None and baseline.pitch_mean_hz > 0:
                deviation = features.pitch_mean_hz - baseline.pitch_mean_hz
                features.pitch_deviation_pct = (deviation / baseline.pitch_mean_hz) * 100.0

            # Energy deviation
            if features.energy_rms is not None and baseline.energy_rms_mean > 0:
                deviation = features.energy_rms - baseline.energy_rms_mean
                features.energy_deviation_pct = (deviation / baseline.energy_rms_mean) * 100.0


# Standalone test
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python prosody_extractor.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]

    # Create dummy segments for testing
    test_segments = [
        {'start': 0.0, 'end': 3.5, 'text': 'Dies ist ein Test der Prosodieextraktion'},
        {'start': 3.5, 'end': 7.2, 'text': 'Wir messen Tempo Tonhöhe und Energie'},
        {'start': 8.0, 'end': 11.5, 'text': 'Auch Pausen werden erkannt'},
    ]

    extractor = ProsodyExtractor()
    features, baseline = extractor.extract_from_segments(audio_file, test_segments)

    print("\n=== Prosody Analysis ===")
    print(f"\nBaseline: {baseline}")
    print(f"\nSegment Features:")
    for i, f in enumerate(features):
        print(f"\nSegment {i+1} ({f.start_time:.1f}s - {f.end_time:.1f}s):")
        print(f"  Tempo: {f.tempo_wpm:.1f} WPM ({f.tempo_deviation_pct:+.1f}%)")
        print(f"  Pitch: {f.pitch_mean_hz:.1f} Hz ({f.pitch_deviation_pct:+.1f}%)")
        print(f"  Energy: {f.energy_rms:.4f} ({f.energy_deviation_pct:+.1f}%)")
        print(f"  Pause before: {f.pause_before_ms:.0f}ms")
