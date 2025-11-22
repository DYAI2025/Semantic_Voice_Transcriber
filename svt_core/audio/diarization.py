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
from typing import Dict, List, Optional, Any, Tuple
import torch
from functools import wraps
from pyannote.core import Annotation, Segment

# Optional psutil for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.debug("psutil not available - memory monitoring disabled")

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

            if last_exception is not None:
                raise last_exception
            else:
                raise RuntimeError(
                    f"{func.__name__} failed after {max_retries + 1} attempts, but no exception was captured."
                )

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

    def _validate_hf_token(self, token: str) -> bool:
        """
        Pre-validate Hugging Face token before expensive pipeline load

        Args:
            token: HF token to validate

        Returns:
            True if token is valid, False otherwise
        """
        if not token or not token.startswith('hf_'):
            logger.error("HF token invalid: must start with 'hf_'")
            return False

        try:
            import requests

            logger.debug("Validating HF token...")
            response = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )

            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"✅ HF token validated successfully (user: {user_info.get('name', 'unknown')})")
                return True
            elif response.status_code == 401:
                logger.error("❌ HF token invalid or expired")
                return False
            else:
                logger.warning(f"HF token validation returned status {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            logger.warning("HF token validation timed out - proceeding without validation")
            return True  # Don't block on network timeout
        except requests.exceptions.RequestException as e:
            logger.warning(f"HF token validation failed (network error): {e}")
            return True  # Don't block on network errors
        except Exception as e:
            logger.warning(f"HF token validation failed: {e}")
            return True  # Don't block on unexpected errors

    def _load_pipeline(self):
        """Load pyannote.audio pipeline (lazy loading)"""
        if self.pipeline is not None:
            return

        # Validate token before expensive pipeline load
        if not self._validate_hf_token(self.use_auth_token):
            error_msg = (
                "Invalid Hugging Face token. Setup instructions:\n\n"
                "1. Create account: https://huggingface.co/join\n"
                "2. Accept model user agreements:\n"
                "   - https://huggingface.co/pyannote/segmentation-3.0\n"
                "   - https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                "3. Create token: https://huggingface.co/settings/tokens (Type: Read)\n"
                "4. Add to .env file: HF_TOKEN=hf_YourTokenHere\n"
                "5. Restart application\n\n"
                "See SPEAKER_DIARIZATION.md for detailed setup guide."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

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
                "Common issues:\n"
                "- Model agreements not accepted (see links above)\n"
                "- Token expired or revoked\n"
                "- Network connection issues\n"
                "- Insufficient disk space for model download (~500MB)"
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

    def _check_memory(self, audio_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Check available memory and recommend processing mode

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (recommended_mode, memory_info)
            where mode is 'gpu', 'cpu', or 'minimal'
        """
        if not PSUTIL_AVAILABLE:
            return 'gpu' if torch.cuda.is_available() else 'cpu', {}

        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024**3)
        percent_used = mem.percent

        # Estimate memory needed (rough heuristic)
        try:
            import librosa
            audio_duration_minutes = librosa.get_duration(path=str(audio_path)) / 60
            # pyannote uses ~50-100MB per minute on CPU, ~200-500MB per minute on GPU
            estimated_mb = audio_duration_minutes * 200  # Conservative estimate
        except Exception:
            estimated_mb = 500  # Default estimate

        memory_info = {
            'total_gb': mem.total / (1024**3),
            'available_gb': available_gb,
            'percent_used': percent_used,
            'estimated_needed_mb': estimated_mb
        }

        # Decision logic
        if percent_used > 90:
            logger.warning(
                f"⚠️ CRITICAL: RAM usage at {percent_used:.1f}% "
                f"(Available: {available_gb:.1f}GB)"
            )
            logger.warning("Switching to MINIMAL mode (CPU energy-based fallback)")
            return 'minimal', memory_info

        elif percent_used > 85:
            logger.warning(
                f"⚠️ HIGH: RAM usage at {percent_used:.1f}% "
                f"(Available: {available_gb:.1f}GB)"
            )
            if self.device.type == 'cuda':
                logger.warning("Switching to CPU mode to reduce memory pressure")
                return 'cpu', memory_info
            else:
                return 'cpu', memory_info

        elif available_gb < estimated_mb / 1024 * 1.5:  # Need 1.5x estimated memory
            logger.warning(
                f"⚠️ Low available memory: {available_gb:.1f}GB "
                f"(Estimated need: {estimated_mb/1024:.1f}GB)"
            )
            logger.warning("Switching to CPU mode")
            return 'cpu', memory_info

        else:
            # Sufficient memory
            logger.info(
                f"Memory check: {percent_used:.1f}% used, "
                f"{available_gb:.1f}GB available"
            )
            return 'gpu' if torch.cuda.is_available() else 'cpu', memory_info

    def _estimate_segment_confidence(self, duration: float) -> float:
        """
        Estimate confidence score for a diarization segment

        Uses heuristics based on segment duration.
        Longer segments generally indicate more confident speaker attribution.

        Note: This is a placeholder until we implement proper embedding-based
        confidence scoring in Sprint 2.

        Args:
            duration: Segment duration in seconds

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Heuristic confidence based on duration
        # Very short segments (<0.5s) are less reliable
        # Optimal segments (2-10s) have high confidence
        # Very long segments (>30s) might be multiple turns

        if duration < 0.5:
            # Very short - low confidence
            confidence = 0.5 + (duration / 0.5) * 0.2  # 0.5-0.7
        elif duration < 2.0:
            # Short - medium confidence
            confidence = 0.7 + ((duration - 0.5) / 1.5) * 0.15  # 0.7-0.85
        elif duration < 10.0:
            # Optimal - high confidence
            confidence = 0.85 + ((duration - 2.0) / 8.0) * 0.10  # 0.85-0.95
        elif duration < 30.0:
            # Long - slightly decreasing confidence
            confidence = 0.95 - ((duration - 10.0) / 20.0) * 0.10  # 0.95-0.85
        else:
            # Very long - medium confidence (might be multiple turns)
            confidence = 0.80

        return round(confidence, 3)

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

        # Check memory and select processing mode
        recommended_mode, memory_info = self._check_memory(audio_path)

        if recommended_mode == 'minimal':
            # Use CPU energy-based fallback
            logger.warning(
                "⚠️ Insufficient memory - using CPU energy-based diarization fallback"
            )
            if self.enable_graceful_degradation:
                from svt_core.audio.diarization_cpu import CPUDiarizer
                cpu_diarizer = CPUDiarizer()
                logger.info("Using CPUDiarizer (energy-based segmentation)")
                return cpu_diarizer.diarize(audio_path, num_speakers=num_speakers)
            else:
                raise DiarizationError(
                    f"Insufficient memory: {memory_info['percent_used']:.1f}% used, "
                    f"{memory_info['available_gb']:.1f}GB available"
                )

        elif recommended_mode == 'cpu' and self.device.type == 'cuda':
            # Switch from GPU to CPU
            logger.info("Switching from GPU to CPU mode due to memory constraints")
            self.device = torch.device('cpu')

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

            # Calculate confidence score heuristic
            # Note: pyannote.audio 3.1 doesn't provide per-segment confidence directly
            # We use a heuristic based on segment duration and consistency
            segment_duration = turn.end - turn.start
            confidence = self._estimate_segment_confidence(segment_duration)

            segments.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker_mapping[speaker],
                'speaker_id': speaker,
                'confidence': confidence  # NEW: Confidence score (0.0-1.0)
            })

        # Calculate average confidence
        avg_confidence = sum(seg['confidence'] for seg in segments) / len(segments) if segments else 0.0
        low_conf_count = sum(1 for seg in segments if seg['confidence'] < 0.7)

        logger.info(
            f"Diarization complete: Found {len(speaker_mapping)} speakers, "
            f"{len(segments)} segments"
        )
        logger.info(
            f"  Confidence: avg={avg_confidence:.2f}, "
            f"low_conf_segments={low_conf_count} (<0.7)"
        )

        # Log per-speaker confidence
        for speaker, label in speaker_mapping.items():
            speaker_segs = [s for s in segments if s['speaker_id'] == speaker]
            speaker_conf = sum(s['confidence'] for s in speaker_segs) / len(speaker_segs)
            logger.debug(
                f"  {label}: {len(speaker_segs)} segments, "
                f"avg_confidence={speaker_conf:.2f}"
            )

        return segments

    def align_with_transcription(
        self,
        diarization_segments: List[Dict[str, Any]],
        transcription_segments: List[Dict[str, Any]],
        overlap_weight: float = 0.7,
        confidence_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Align speaker diarization with Whisper transcription segments

        Uses weighted scoring: overlap duration + confidence score
        to select the best matching speaker for each transcription segment.

        Args:
            diarization_segments: Output from diarize() with 'confidence' field
            transcription_segments: Whisper segments with 'start', 'end', 'text'
            overlap_weight: Weight for overlap duration in scoring (default: 0.7)
            confidence_weight: Weight for confidence score in scoring (default: 0.3)

        Returns:
            Transcription segments with added 'speaker' and 'speaker_confidence' fields
        """
        aligned = []

        for trans_seg in transcription_segments:
            trans_start = trans_seg['start']
            trans_end = trans_seg['end']
            trans_duration = trans_end - trans_start
            trans_mid = (trans_start + trans_end) / 2

            # Find best matching speaker using weighted scoring
            best_speaker = "Speaker A"  # Default fallback
            best_speaker_id = None
            best_score = -1
            best_confidence = 0.5

            # Score all overlapping diarization segments
            for dia_seg in diarization_segments:
                dia_start = dia_seg['start']
                dia_end = dia_seg['end']

                # Calculate overlap
                overlap_start = max(trans_start, dia_start)
                overlap_end = min(trans_end, dia_end)
                overlap_duration = max(0, overlap_end - overlap_start)

                if overlap_duration > 0:
                    # Normalize overlap by transcription duration (0.0-1.0)
                    overlap_ratio = overlap_duration / trans_duration

                    # Get confidence score (0.0-1.0)
                    dia_confidence = dia_seg.get('confidence', 0.5)

                    # Weighted score
                    score = (overlap_weight * overlap_ratio) + (confidence_weight * dia_confidence)

                    if score > best_score:
                        best_score = score
                        best_speaker = dia_seg['speaker']
                        best_speaker_id = dia_seg['speaker_id']
                        best_confidence = dia_confidence

            # Fallback: Check midpoint (backward compatibility)
            if best_score < 0.3:  # Very low score, try midpoint
                for dia_seg in diarization_segments:
                    if dia_seg['start'] <= trans_mid <= dia_seg['end']:
                        best_speaker = dia_seg['speaker']
                        best_speaker_id = dia_seg['speaker_id']
                        best_confidence = dia_seg.get('confidence', 0.5)
                        logger.debug(
                            f"Used midpoint fallback for segment at {trans_start:.1f}s"
                        )
                        break

            # Add speaker to transcription segment
            aligned_seg = trans_seg.copy()
            aligned_seg['speaker'] = best_speaker
            aligned_seg['speaker_id'] = best_speaker_id
            aligned_seg['speaker_confidence'] = round(best_confidence, 3)
            aligned_seg['alignment_score'] = round(best_score, 3)
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
