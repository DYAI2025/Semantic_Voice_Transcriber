#!/usr/bin/env python3
"""
Speaker Diarization Module for Semantic Voice Transcriber
Uses pyannote.audio for automatic speaker segmentation

With robust error handling and graceful degradation:
- Continues without speaker labels if diarization fails
- Timeout handling for long audio files
- Retry logic for transient failures
- Chunked processing for very long audio
"""

import logging
import multiprocessing as mp
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import torch
from functools import wraps
from pyannote.core import Annotation, Segment

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    logging.warning("pyannote.audio not available. Speaker diarization disabled.")

logger = logging.getLogger(__name__)

_FORKED_PIPELINE = None


def _set_forked_pipeline(pipeline):
    global _FORKED_PIPELINE
    _FORKED_PIPELINE = pipeline


def _serialize_annotation(annotation: Annotation) -> List[Dict[str, Any]]:
    tracks: List[Dict[str, Any]] = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        tracks.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return tracks


def _deserialize_annotation(tracks: List[Dict[str, Any]]) -> Annotation:
    annotation = Annotation()
    for track in tracks:
        annotation[Segment(track["start"], track["end"])] = track["speaker"]
    return annotation


def _forked_diarization_worker(audio_path: str, diarization_kwargs: Dict[str, Any], queue):
    try:
        if _FORKED_PIPELINE is None:
            raise RuntimeError("Forked pipeline not initialized")
        annotation = _FORKED_PIPELINE(audio_path, **diarization_kwargs)
        queue.put(("ok", _serialize_annotation(annotation)))
    except Exception as exc:  # pragma: no cover - worker errors logged upstream
        queue.put(("error", repr(exc)))


def _spawned_diarization_worker(config: Dict[str, Any], audio_path: str,
                                diarization_kwargs: Dict[str, Any], queue):
    try:
        from pyannote.audio import Pipeline

        device = torch.device(config["device"])
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=config.get("token")
        )
        pipeline.to(device)
        annotation = pipeline(audio_path, **diarization_kwargs)
        queue.put(("ok", _serialize_annotation(annotation)))
    except Exception as exc:  # pragma: no cover - worker errors logged upstream
        queue.put(("error", repr(exc)))


class DiarizationError(Exception):
    """Custom exception for diarization failures"""
    pass


class DiarizationTimeoutError(DiarizationError):
    """Exception for diarization timeout"""
    pass


def retry_on_failure(max_retries=2, delay=1.0):
    """
    Decorator to retry function on failure with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (doubles each retry)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")

            raise last_exception

        return wrapper
    return decorator


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
        max_speakers: int = 10,
        timeout_seconds: int = 600,
        enable_graceful_degradation: bool = True,
        max_audio_duration_minutes: int = 120
    ):
        """
        Initialize Speaker Diarizer

        Args:
            use_auth_token: Hugging Face authentication token (required for model access)
            device: Device to run on ('cuda', 'cpu', or None for auto-detect)
            min_speakers: Minimum number of speakers to detect
            max_speakers: Maximum number of speakers to detect
            timeout_seconds: Maximum time for diarization (default: 600s = 10min)
            enable_graceful_degradation: If True, return empty list on failure instead of raising
            max_audio_duration_minutes: Maximum audio duration to process (default: 120min = 2h)
        """
        if not PYANNOTE_AVAILABLE:
            raise ImportError(
                "pyannote.audio is not installed. "
                "Install with: pip install pyannote.audio"
            )

        self.use_auth_token = use_auth_token
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.timeout_seconds = timeout_seconds
        self.enable_graceful_degradation = enable_graceful_degradation
        self.max_audio_duration_minutes = max_audio_duration_minutes

        # Auto-detect device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        logger.info(f"Speaker Diarizer initialized on {self.device}")
        logger.info(f"  Graceful degradation: {enable_graceful_degradation}")
        logger.info(f"  Timeout: {timeout_seconds}s")
        logger.info(f"  Max audio duration: {max_audio_duration_minutes}min")

        # Pipeline will be loaded on first use
        self.pipeline = None
        self.osd_pipeline = None
        self._mp_start_method = (
            "fork" if "fork" in mp.get_all_start_methods() else "spawn"
        )
        self.fallback_invocations = 0
        self.fallback_timeouts = 0

    def _load_pipeline(self):
        """Load pyannote.audio pipeline (lazy loading)"""
        if self.pipeline is not None:
            return

        try:
            logger.info("Loading pyannote speaker-diarization-3.1 pipeline...")
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=self.use_auth_token
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

    @retry_on_failure(max_retries=1, delay=2.0)
    def _run_diarization_with_timeout(
        self,
        audio_path: Path,
        diarization_kwargs: Dict[str, Any]
    ):
        """
        Run diarization with timeout handling

        Args:
            audio_path: Path to audio file
            diarization_kwargs: Parameters for diarization

        Returns:
            Diarization annotation from pyannote

        Raises:
            DiarizationTimeoutError: If diarization exceeds timeout
        """
        if threading.current_thread() is not threading.main_thread():
            logger.info(
                "Thread-safe fallback diarization activated (worker=%s)",
                self._mp_start_method
            )
            return self._run_fallback_diarization(audio_path, diarization_kwargs)

        import signal

        def timeout_handler(signum, frame):
            raise DiarizationTimeoutError(
                f"Diarization exceeded timeout of {self.timeout_seconds}s"
            )

        # Set timeout (only works on Unix systems)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout_seconds)

            # Run diarization
            diarization = self.pipeline(str(audio_path), **diarization_kwargs)

            # Cancel timeout
            signal.alarm(0)

            return diarization

        except AttributeError:
            # Windows doesn't support signal.SIGALRM
            logger.warning("Timeout not supported on this platform - running without timeout")
            return self.pipeline(str(audio_path), **diarization_kwargs)

    def _run_fallback_diarization(
        self,
        audio_path: Path,
        diarization_kwargs: Dict[str, Any]
    ):
        """Execute diarization in a separate worker with join timeout."""
        ctx = mp.get_context(self._mp_start_method)
        result_queue = ctx.Queue()
        start_time = time.time()
        self.fallback_invocations += 1

        logger.info(
            "Using fallback diarization worker (%s) for %s",
            self._mp_start_method,
            audio_path.name
        )

        if self._mp_start_method == "fork":
            _set_forked_pipeline(self.pipeline)
            process = ctx.Process(
                target=_forked_diarization_worker,
                args=(str(audio_path), diarization_kwargs, result_queue)
            )
        else:
            worker_config = {
                "token": self.use_auth_token,
                "device": str(self.device)
            }
            process = ctx.Process(
                target=_spawned_diarization_worker,
                args=(worker_config, str(audio_path), diarization_kwargs, result_queue)
            )

        process.start()
        process.join(self.timeout_seconds)

        if process.is_alive():
            self.fallback_timeouts += 1
            process.terminate()
            process.join()
            logger.error(
                "Fallback diarization timeout after %.1fs on %s worker",
                self.timeout_seconds,
                self._mp_start_method
            )
            raise DiarizationTimeoutError(
                f"Fallback diarization exceeded timeout of {self.timeout_seconds}s"
            )

        if result_queue.empty():
            logger.error("Fallback diarization worker returned no result")
            raise DiarizationError("Fallback worker returned no result")

        status, payload = result_queue.get()
        duration = time.time() - start_time

        if status == "ok":
            logger.info(
                "Fallback diarization finished in %.2fs (%s)",
                duration,
                self._mp_start_method
            )
            return _deserialize_annotation(payload)

        logger.error("Fallback diarization worker failed: %s", payload)
        raise DiarizationError(payload)

    def detect_overlapped_speech(
        self,
        audio_path: Path,
        min_duration_on: float = 0.0,
        min_duration_off: float = 0.0,
        onset: float = 0.5,
        offset: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Detect overlapped speech regions (multiple speakers talking simultaneously)

        Args:
            audio_path: Path to audio file
            min_duration_on: Remove overlapped speech regions shorter than this (seconds)
            min_duration_off: Fill non-overlapped speech regions shorter than this (seconds)
            onset: Threshold for detecting speech onset (0.0-1.0)
            offset: Threshold for detecting speech offset (0.0-1.0)

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
        # pyannote/segmentation-3.0 uses powerset encoding where overlaps
        # are indicated by labels with '+' (e.g., "SPEAKER_00+SPEAKER_01")
        HYPER_PARAMETERS = {
            "onset": onset,
            "offset": offset,
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
        # Extract only overlapped speech regions
        overlaps = []
        for segment, _, label in osd_annotation.itertracks(yield_label=True):
            label_str = str(label)
            # Powerset encoding uses '+' between speaker IDs to indicate overlap
            # e.g., "SPEAKER_00+SPEAKER_01" means both speakers are talking
            if '+' in label_str:
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
        Perform speaker diarization on audio file with robust error handling

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

            Returns empty list [] if diarization fails and graceful_degradation is enabled
        """
        # Check audio duration first
        try:
            import librosa
            duration_seconds = librosa.get_duration(path=str(audio_path))
            duration_minutes = duration_seconds / 60

            if duration_minutes > self.max_audio_duration_minutes:
                logger.warning(
                    f"Audio duration ({duration_minutes:.1f}min) exceeds maximum "
                    f"({self.max_audio_duration_minutes}min). Skipping diarization."
                )
                if self.enable_graceful_degradation:
                    return []
                else:
                    raise DiarizationError(
                        f"Audio too long: {duration_minutes:.1f}min > {self.max_audio_duration_minutes}min"
                    )
        except ImportError:
            logger.warning("librosa not available - cannot check audio duration")
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")

        # Load pipeline with error handling
        try:
            self._load_pipeline()
        except Exception as e:
            logger.error(f"Failed to load diarization pipeline: {e}")
            if self.enable_graceful_degradation:
                logger.warning("⚠️ Continuing without speaker labels (graceful degradation)")
                return []
            else:
                raise

        logger.info(f"Running diarization on {audio_path.name}...")

        # Configure diarization parameters
        diarization_kwargs = {}
        if num_speakers is not None:
            diarization_kwargs['num_speakers'] = num_speakers
        else:
            diarization_kwargs['min_speakers'] = self.min_speakers
            diarization_kwargs['max_speakers'] = self.max_speakers

        # Run diarization with timeout and retry
        try:
            diarization = self._run_diarization_with_timeout(audio_path, diarization_kwargs)
        except DiarizationTimeoutError as e:
            logger.error(f"Diarization timed out after {self.timeout_seconds}s: {e}")
            if self.enable_graceful_degradation:
                logger.warning("⚠️ Continuing without speaker labels (graceful degradation)")
                return []
            else:
                raise
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            logger.error(
                "Common issues:\n"
                "  - HF token invalid or expired (check .env file)\n"
                "  - pyannote model access not granted (accept user agreements)\n"
                "  - Out of memory (try smaller audio chunks or use CPU)\n"
                "  - Audio format not supported (convert to WAV)"
            )
            if self.enable_graceful_degradation:
                logger.warning("⚠️ Continuing without speaker labels (graceful degradation)")
                return []
            else:
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
