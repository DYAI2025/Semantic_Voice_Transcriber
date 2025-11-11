#!/usr/bin/env python3
"""
Speaker Diarization Module for Semantic Voice Transcriber
Uses pyannote.audio for automatic speaker segmentation
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import torch

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    logging.warning("pyannote.audio not available. Speaker diarization disabled.")

logger = logging.getLogger(__name__)


class SpeakerDiarizer:
    """
    Automatic speaker diarization using pyannote.audio

    Features:
    - Automatic speaker segmentation (Speaker A, B, C, ...)
    - Hugging Face model integration
    - GPU acceleration support
    - Configurable number of speakers
    """

    def __init__(
        self,
        use_auth_token: Optional[str] = None,
        device: Optional[str] = None,
        min_speakers: int = 1,
        max_speakers: int = 10
    ):
        """
        Initialize Speaker Diarizer

        Args:
            use_auth_token: Hugging Face authentication token (required for model access)
            device: Device to run on ('cuda', 'cpu', or None for auto-detect)
            min_speakers: Minimum number of speakers to detect
            max_speakers: Maximum number of speakers to detect
        """
        if not PYANNOTE_AVAILABLE:
            raise ImportError(
                "pyannote.audio is not installed. "
                "Install with: pip install pyannote.audio"
            )

        self.use_auth_token = use_auth_token
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers

        # Auto-detect device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        logger.info(f"Speaker Diarizer initialized on {self.device}")

        # Pipeline will be loaded on first use
        self.pipeline = None
        self.osd_pipeline = None

    def _load_pipeline(self):
        """Load pyannote.audio pipeline (lazy loading)"""
        if self.pipeline is not None:
            return

        try:
            logger.info("Loading pyannote speaker-diarization-3.1 pipeline...")
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.use_auth_token
            )
            self.pipeline.to(self.device)
            logger.info("Pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load pipeline: {e}")
            logger.error(
                "You may need to:\n"
                "1. Accept pyannote/segmentation-3.0 user agreement at: "
                "https://huggingface.co/pyannote/segmentation-3.0\n"
                "2. Accept pyannote/speaker-diarization-3.1 user agreement at: "
                "https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                "3. Create a token at: https://huggingface.co/settings/tokens\n"
                "4. Pass token via use_auth_token parameter"
            )
            raise

    def _load_osd_pipeline(self):
        """Load pyannote.audio Overlapped Speech Detection pipeline (lazy loading)"""
        if self.osd_pipeline is not None:
            return

        try:
            from pyannote.audio.pipelines import MultiLabelSegmentation

            logger.info("Loading pyannote Overlapped Speech Detection pipeline...")

            # Load segmentation model for overlap detection
            # Using pyannote/segmentation-3.0 which can detect overlapped speech
            self.osd_pipeline = MultiLabelSegmentation(
                segmentation="pyannote/segmentation-3.0",
                token=self.use_auth_token
            )

            logger.info("OSD pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load OSD pipeline: {e}")
            raise

    def detect_overlapped_speech(
        self,
        audio_path: Path,
        min_duration_on: float = 0.0,
        min_duration_off: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Detect overlapped speech regions (multiple speakers talking simultaneously)

        Args:
            audio_path: Path to audio file
            min_duration_on: Remove overlapped speech regions shorter than this (seconds)
            min_duration_off: Fill non-overlapped speech regions shorter than this (seconds)

        Returns:
            List of overlap segments with format:
            [
                {
                    'start': 12.5,
                    'end': 14.2,
                    'duration': 1.7,
                    'overlap_type': 'simultaneous_speech'
                },
                ...
            ]
        """
        self._load_osd_pipeline()

        logger.info(f"Running overlapped speech detection on {audio_path.name}...")

        # Configure hyperparameters for overlap detection
        # pyannote/segmentation-3.0 has labels including 'OVERLAP'
        HYPER_PARAMETERS = {
            "onset": 0.5,
            "offset": 0.5,
            "min_duration_on": min_duration_on,
            "min_duration_off": min_duration_off
        }
        self.osd_pipeline.instantiate(HYPER_PARAMETERS)

        # Run OSD
        try:
            osd_annotation = self.osd_pipeline(str(audio_path))
        except Exception as e:
            logger.error(f"OSD failed: {e}")
            raise

        # Convert pyannote format to our format
        # Extract only the OVERLAP label regions
        overlaps = []
        for segment, _, label in osd_annotation.itertracks(yield_label=True):
            # Filter for overlap-related labels (e.g., 'OVERLAP')
            if 'OVERLAP' in str(label).upper() or label == 'overlap':
                overlaps.append({
                    'start': segment.start,
                    'end': segment.end,
                    'duration': segment.end - segment.start,
                    'overlap_type': 'simultaneous_speech'
                })

        logger.info(
            f"OSD complete: Found {len(overlaps)} overlapped speech regions"
        )

        return overlaps

    def diarize(
        self,
        audio_path: Path,
        num_speakers: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform speaker diarization on audio file

        Args:
            audio_path: Path to audio file
            num_speakers: Fixed number of speakers (None for auto-detect)

        Returns:
            List of speaker segments with format:
            [
                {
                    'start': 5.2,
                    'end': 7.8,
                    'speaker': 'Speaker A',
                    'speaker_id': 'SPEAKER_00'
                },
                ...
            ]
        """
        self._load_pipeline()

        logger.info(f"Running diarization on {audio_path.name}...")

        # Configure diarization parameters
        diarization_kwargs = {}
        if num_speakers is not None:
            diarization_kwargs['num_speakers'] = num_speakers
        else:
            diarization_kwargs['min_speakers'] = self.min_speakers
            diarization_kwargs['max_speakers'] = self.max_speakers

        # Run diarization
        try:
            diarization = self.pipeline(str(audio_path), **diarization_kwargs)
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            raise

        # Convert pyannote format to our format
        segments = []
        speaker_mapping = {}  # Map SPEAKER_00 -> Speaker A
        next_speaker_index = 0

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # Create human-readable speaker labels
            if speaker not in speaker_mapping:
                speaker_label = chr(ord('A') + next_speaker_index)  # A, B, C, ...
                speaker_mapping[speaker] = f"Speaker {speaker_label}"
                next_speaker_index += 1

            segments.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker_mapping[speaker],
                'speaker_id': speaker
            })

        logger.info(
            f"Diarization complete: Found {len(speaker_mapping)} speakers, "
            f"{len(segments)} segments"
        )

        return segments

    def align_with_transcription(
        self,
        diarization_segments: List[Dict[str, Any]],
        transcription_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Align speaker diarization with Whisper transcription segments

        Args:
            diarization_segments: Output from diarize()
            transcription_segments: Whisper segments with 'start', 'end', 'text'

        Returns:
            Transcription segments with added 'speaker' field
        """
        aligned = []

        for trans_seg in transcription_segments:
            trans_start = trans_seg['start']
            trans_end = trans_seg['end']
            trans_mid = (trans_start + trans_end) / 2

            # Find overlapping speaker segment
            # Strategy: Use speaker at midpoint of transcription segment
            best_speaker = "Speaker A"  # Default fallback
            max_overlap = 0

            for dia_seg in diarization_segments:
                dia_start = dia_seg['start']
                dia_end = dia_seg['end']

                # Calculate overlap
                overlap_start = max(trans_start, dia_start)
                overlap_end = min(trans_end, dia_end)
                overlap = max(0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = dia_seg['speaker']

                # Alternative: Check if midpoint is within diarization segment
                if dia_start <= trans_mid <= dia_end:
                    best_speaker = dia_seg['speaker']
                    break

            # Add speaker to transcription segment
            aligned_seg = trans_seg.copy()
            aligned_seg['speaker'] = best_speaker
            aligned.append(aligned_seg)

        return aligned

    @staticmethod
    def get_speaker_statistics(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate speaker statistics

        Args:
            segments: Diarization or aligned segments

        Returns:
            Dictionary with speaker statistics
        """
        stats = {}
        total_duration = 0

        for seg in segments:
            speaker = seg.get('speaker', 'Unknown')
            duration = seg['end'] - seg['start']

            if speaker not in stats:
                stats[speaker] = {
                    'total_duration': 0,
                    'num_segments': 0,
                    'percentage': 0
                }

            stats[speaker]['total_duration'] += duration
            stats[speaker]['num_segments'] += 1
            total_duration += duration

        # Calculate percentages
        for speaker in stats:
            if total_duration > 0:
                stats[speaker]['percentage'] = (
                    stats[speaker]['total_duration'] / total_duration * 100
                )

        return stats


def test_diarization():
    """Test speaker diarization with sample audio"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python speaker_diarizer.py <audio_file> [hf_token]")
        print("\nYou need a Hugging Face token to use this model.")
        print("Get one at: https://huggingface.co/settings/tokens")
        return

    audio_path = Path(sys.argv[1])
    hf_token = sys.argv[2] if len(sys.argv) > 2 else None

    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        return

    # Initialize diarizer
    diarizer = SpeakerDiarizer(use_auth_token=hf_token)

    # Run diarization
    segments = diarizer.diarize(audio_path)

    # Print results
    print(f"\n{'='*80}")
    print(f"SPEAKER DIARIZATION RESULTS: {audio_path.name}")
    print(f"{'='*80}\n")

    for seg in segments:
        print(
            f"[{seg['start']:6.2f}s - {seg['end']:6.2f}s] "
            f"{seg['speaker']:12s} (ID: {seg['speaker_id']})"
        )

    # Statistics
    stats = SpeakerDiarizer.get_speaker_statistics(segments)
    print(f"\n{'='*80}")
    print("SPEAKER STATISTICS")
    print(f"{'='*80}\n")

    for speaker, data in sorted(stats.items()):
        print(
            f"{speaker:12s}: {data['total_duration']:6.2f}s "
            f"({data['percentage']:5.1f}%) - {data['num_segments']} segments"
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    test_diarization()
