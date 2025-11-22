#!/usr/bin/env python3
"""
Speaker Embeddings Extraction Module

Extracts speaker-specific acoustic embeddings using pyannote.audio
for cross-session speaker recognition.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

import numpy as np
import torch

try:
    import torchaudio
    TORCHAUDIO_AVAILABLE = True
except ImportError:
    TORCHAUDIO_AVAILABLE = False
    logging.warning("torchaudio not available - speaker embeddings disabled")

try:
    from pyannote.audio import Model
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    logging.warning("pyannote.audio not available - speaker embeddings disabled")


logger = logging.getLogger(__name__)


@dataclass
class SpeakerEmbedding:
    """Represents a speaker embedding vector with metadata"""

    # Identifiers
    speaker_label: str          # e.g., "Therapeut", "Patient A"
    embedding_id: str           # UUID for this specific embedding

    # Embedding data
    embedding: np.ndarray       # Shape: (512,) - embedding vector
    embedding_dim: int          # 512 (constant for pyannote/embedding)

    # Temporal metadata
    timestamp: datetime         # When embedding was extracted
    audio_file: str             # Source audio file path
    segment_start: float        # Start time in audio (seconds)
    segment_end: float          # End time in audio (seconds)

    # Quality metrics
    confidence: float           # Diarization confidence (0.0-1.0)
    segment_duration: float     # Duration of audio segment (seconds)

    # Additional metadata
    metadata: Dict[str, Any]    # Extensible metadata field


class SpeakerEmbeddingExtractor:
    """
    Extract speaker embeddings from audio using pyannote.audio

    Uses the pyannote/embedding model to extract 512-dimensional
    speaker-specific acoustic features for cross-session recognition.
    """

    def __init__(self, use_auth_token: str, device: str = None):
        """
        Initialize embedding extractor

        Args:
            use_auth_token: Hugging Face authentication token
            device: 'cuda', 'cpu', or None for auto-detect
        """
        if not PYANNOTE_AVAILABLE:
            raise ImportError(
                "pyannote.audio is not installed. "
                "Install with: pip install pyannote.audio"
            )

        if not TORCHAUDIO_AVAILABLE:
            raise ImportError(
                "torchaudio is not installed. "
                "Install with: pip install torchaudio"
            )

        self.use_auth_token = use_auth_token

        # Auto-detect device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        logger.info(f"Speaker Embedding Extractor initialized on {self.device}")

        # Model will be loaded on first use (lazy loading)
        self.model = None

    def _load_model(self):
        """Load pyannote embedding model (lazy loading)"""
        if self.model is not None:
            return

        try:
            logger.info("Loading pyannote/embedding model...")
            self.model = Model.from_pretrained(
                "pyannote/embedding",
                token=self.use_auth_token
            )
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            logger.error(
                "You may need to:\n"
                "1. Accept pyannote/embedding user agreement at: "
                "https://huggingface.co/pyannote/embedding\n"
                "2. Verify your HF token is valid\n"
                "3. Check internet connection for model download"
            )
            raise

    def extract_embedding(
        self,
        audio_path: Path,
        start: float,
        end: float
    ) -> np.ndarray:
        """
        Extract embedding for a single audio segment

        Args:
            audio_path: Path to audio file
            start: Start time in seconds
            end: End time in seconds

        Returns:
            Numpy array of shape (512,) with L2-normalized embedding vector

        Raises:
            ValueError: If segment is too short (<0.1s)
            RuntimeError: If embedding extraction fails
        """
        self._load_model()

        # Validate segment duration
        duration = end - start
        if duration < 0.1:
            raise ValueError(f"Segment too short: {duration:.2f}s (minimum: 0.1s)")

        try:
            # Load audio segment
            waveform, sr = torchaudio.load(str(audio_path))

            # Extract segment (convert seconds to samples)
            start_sample = int(start * sr)
            end_sample = int(end * sr)

            # Clamp to valid range
            start_sample = max(0, start_sample)
            end_sample = min(waveform.shape[1], end_sample)

            segment = waveform[:, start_sample:end_sample]

            # Check if segment is empty
            if segment.shape[1] == 0:
                raise ValueError(f"Empty audio segment at {start:.1f}s-{end:.1f}s")

            # Resample if needed (pyannote expects 16kHz)
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(sr, 16000)
                segment = resampler(segment)
                sr = 16000

            # Convert to mono if stereo
            if segment.shape[0] > 1:
                segment = torch.mean(segment, dim=0, keepdim=True)

            # Extract embedding
            with torch.no_grad():
                embedding = self.model({
                    "waveform": segment.to(self.device),
                    "sample_rate": sr
                })

            # Convert to numpy and flatten
            embedding_np = embedding.cpu().numpy().flatten()

            # L2-normalize
            norm = np.linalg.norm(embedding_np)
            if norm > 0:
                embedding_np = embedding_np / norm

            return embedding_np

        except Exception as e:
            logger.error(
                f"Failed to extract embedding from {audio_path.name} "
                f"at {start:.1f}s-{end:.1f}s: {e}"
            )
            raise RuntimeError(f"Embedding extraction failed: {e}") from e

    def extract_from_diarization(
        self,
        audio_path: Path,
        diarization_segments: List[Dict[str, Any]],
        min_segment_duration: float = 0.5,
        max_segments_per_speaker: int = 50
    ) -> Dict[str, List[SpeakerEmbedding]]:
        """
        Extract embeddings for all speakers from diarization segments

        Processes all speaker segments and extracts embeddings.
        Averages multiple segments per speaker for robust representation.

        Args:
            audio_path: Path to audio file
            diarization_segments: Diarization output with speaker labels
            min_segment_duration: Minimum segment duration to process (seconds)
            max_segments_per_speaker: Maximum segments to process per speaker

        Returns:
            Dict mapping speaker_id to list of SpeakerEmbedding objects
        """
        self._load_model()

        logger.info(f"Extracting embeddings from {audio_path.name}...")

        embeddings_by_speaker = {}

        # Group segments by speaker
        speaker_segments = defaultdict(list)

        for seg in diarization_segments:
            speaker_id = seg.get('speaker_id', seg.get('speaker', 'Unknown'))
            speaker_segments[speaker_id].append(seg)

        # Extract embeddings per speaker
        for speaker_id, segments in speaker_segments.items():
            speaker_label = segments[0].get('speaker', speaker_id)
            speaker_embeddings = []

            # Sort segments by confidence (highest first)
            segments_sorted = sorted(
                segments,
                key=lambda s: s.get('confidence', 0.0),
                reverse=True
            )

            # Limit number of segments to process
            segments_to_process = segments_sorted[:max_segments_per_speaker]

            processed = 0
            for seg in segments_to_process:
                seg_duration = seg['end'] - seg['start']

                # Only extract for segments above minimum duration
                if seg_duration < min_segment_duration:
                    logger.debug(
                        f"Skipping short segment for {speaker_label}: {seg_duration:.2f}s"
                    )
                    continue

                try:
                    embedding_vec = self.extract_embedding(
                        audio_path,
                        seg['start'],
                        seg['end']
                    )

                    # Create SpeakerEmbedding object
                    emb = SpeakerEmbedding(
                        speaker_label=speaker_label,
                        embedding_id=str(uuid.uuid4()),
                        embedding=embedding_vec,
                        embedding_dim=len(embedding_vec),
                        timestamp=datetime.now(),
                        audio_file=str(audio_path),
                        segment_start=seg['start'],
                        segment_end=seg['end'],
                        confidence=seg.get('confidence', 0.5),
                        segment_duration=seg_duration,
                        metadata={
                            'speaker_id': speaker_id,
                            'device': str(self.device)
                        }
                    )

                    speaker_embeddings.append(emb)
                    processed += 1

                except Exception as e:
                    logger.warning(
                        f"Failed to extract embedding for {speaker_label} "
                        f"at {seg['start']:.1f}s: {e}"
                    )
                    continue

            embeddings_by_speaker[speaker_id] = speaker_embeddings

            logger.info(
                f"  {speaker_label}: Extracted {len(speaker_embeddings)} embeddings "
                f"from {len(segments)} segments"
            )

        total_embeddings = sum(len(embs) for embs in embeddings_by_speaker.values())
        logger.info(
            f"Embedding extraction complete: {total_embeddings} embeddings "
            f"for {len(embeddings_by_speaker)} speakers"
        )

        return embeddings_by_speaker

    def compute_average_embedding(
        self,
        embeddings: List[np.ndarray]
    ) -> np.ndarray:
        """
        Compute average embedding from multiple segments

        Args:
            embeddings: List of embedding vectors

        Returns:
            Average embedding (L2-normalized)

        Raises:
            ValueError: If embeddings list is empty
        """
        if not embeddings:
            raise ValueError("Cannot compute average of empty embedding list")

        # Stack embeddings
        stacked = np.stack(embeddings, axis=0)

        # Compute mean
        avg_embedding = np.mean(stacked, axis=0)

        # L2-normalize
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm

        return avg_embedding

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            emb1: First embedding vector (normalized)
            emb2: Second embedding vector (normalized)

        Returns:
            Cosine similarity in range [-1, 1]
            (1 = identical, 0 = orthogonal, -1 = opposite)
        """
        # Assuming embeddings are already L2-normalized
        # cosine similarity = dot product
        similarity = np.dot(emb1, emb2)

        return float(similarity)
