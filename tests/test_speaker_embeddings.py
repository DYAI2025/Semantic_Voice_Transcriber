#!/usr/bin/env python3
"""
Unit tests for Speaker Embedding System

Tests extraction, storage, and retrieval of speaker embeddings
for cross-session recognition.
"""

import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from svt_core.audio.speaker_embeddings import (
    SpeakerEmbedding,
    SpeakerEmbeddingExtractor
)
from svt_core.audio.speaker_embedding_db import SpeakerEmbeddingDB


# Skip tests if dependencies not available
try:
    import torch
    import torchaudio
    from pyannote.audio import Model
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


@pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="Dependencies not available")
class TestSpeakerEmbedding:
    """Tests for SpeakerEmbedding dataclass"""

    def test_speaker_embedding_creation(self):
        """Test creating a SpeakerEmbedding object"""
        embedding_vec = np.random.randn(512).astype(np.float32)

        emb = SpeakerEmbedding(
            speaker_label="Test Speaker",
            embedding_id=str(uuid.uuid4()),
            embedding=embedding_vec,
            embedding_dim=512,
            timestamp=datetime.now(),
            audio_file="/path/to/audio.wav",
            segment_start=1.0,
            segment_end=3.0,
            confidence=0.85,
            segment_duration=2.0,
            metadata={"test": "value"}
        )

        assert emb.speaker_label == "Test Speaker"
        assert emb.embedding_dim == 512
        assert emb.embedding.shape == (512,)
        assert 0.0 <= emb.confidence <= 1.0
        assert emb.segment_end > emb.segment_start


class TestSpeakerEmbeddingDB:
    """Tests for SpeakerEmbeddingDB database layer"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_embeddings.db"
        db = SpeakerEmbeddingDB(db_path)
        yield db
        db.close()
        # Cleanup
        if db_path.exists():
            db_path.unlink()

    def test_database_creation(self, temp_db):
        """Test database initialization"""
        assert temp_db.db_path.exists()
        assert temp_db.conn is not None

    def test_save_embedding(self, temp_db):
        """Test saving an embedding to database"""
        embedding_vec = np.random.randn(512).astype(np.float32)

        emb = SpeakerEmbedding(
            speaker_label="Speaker A",
            embedding_id=str(uuid.uuid4()),
            embedding=embedding_vec,
            embedding_dim=512,
            timestamp=datetime.now(),
            audio_file="/test/audio.wav",
            segment_start=0.0,
            segment_end=2.0,
            confidence=0.9,
            segment_duration=2.0,
            metadata={}
        )

        row_id = temp_db.save_embedding(emb)
        assert row_id > 0

    def test_get_embeddings_by_speaker(self, temp_db):
        """Test retrieving embeddings for a speaker"""
        # Create multiple embeddings for same speaker
        speaker_label = "Speaker A"

        for i in range(3):
            embedding_vec = np.random.randn(512).astype(np.float32)
            emb = SpeakerEmbedding(
                speaker_label=speaker_label,
                embedding_id=str(uuid.uuid4()),
                embedding=embedding_vec,
                embedding_dim=512,
                timestamp=datetime.now(),
                audio_file=f"/test/audio{i}.wav",
                segment_start=float(i),
                segment_end=float(i + 2),
                confidence=0.8 + i * 0.05,
                segment_duration=2.0,
                metadata={}
            )
            temp_db.save_embedding(emb)

        # Retrieve embeddings
        embeddings = temp_db.get_embeddings_by_speaker(speaker_label)

        assert len(embeddings) == 3
        assert all(emb.speaker_label == speaker_label for emb in embeddings)
        assert all(emb.embedding.shape == (512,) for emb in embeddings)

    def test_get_all_speakers(self, temp_db):
        """Test getting list of all speakers"""
        speakers = ["Speaker A", "Speaker B", "Speaker C"]

        for speaker in speakers:
            embedding_vec = np.random.randn(512).astype(np.float32)
            emb = SpeakerEmbedding(
                speaker_label=speaker,
                embedding_id=str(uuid.uuid4()),
                embedding=embedding_vec,
                embedding_dim=512,
                timestamp=datetime.now(),
                audio_file="/test/audio.wav",
                segment_start=0.0,
                segment_end=2.0,
                confidence=0.9,
                segment_duration=2.0,
                metadata={}
            )
            temp_db.save_embedding(emb)

        all_speakers = temp_db.get_all_speakers()

        assert len(all_speakers) == 3
        assert set(all_speakers) == set(speakers)

    def test_get_speaker_profile(self, temp_db):
        """Test retrieving speaker profile"""
        speaker_label = "Speaker A"

        # Add multiple embeddings
        for i in range(5):
            embedding_vec = np.random.randn(512).astype(np.float32)
            emb = SpeakerEmbedding(
                speaker_label=speaker_label,
                embedding_id=str(uuid.uuid4()),
                embedding=embedding_vec,
                embedding_dim=512,
                timestamp=datetime.now(),
                audio_file=f"/test/audio{i}.wav",
                segment_start=0.0,
                segment_end=2.0,
                confidence=0.8,
                segment_duration=2.0,
                metadata={}
            )
            temp_db.save_embedding(emb)

        # Get profile
        profile = temp_db.get_speaker_profile(speaker_label)

        assert profile is not None
        assert profile['speaker_label'] == speaker_label
        assert profile['total_embeddings'] == 5
        assert profile['avg_confidence'] == pytest.approx(0.8, abs=0.01)
        assert profile['total_audio_duration'] == pytest.approx(10.0, abs=0.1)

    def test_delete_speaker(self, temp_db):
        """Test deleting all data for a speaker"""
        speaker_label = "Speaker A"

        # Add embeddings
        for i in range(3):
            embedding_vec = np.random.randn(512).astype(np.float32)
            emb = SpeakerEmbedding(
                speaker_label=speaker_label,
                embedding_id=str(uuid.uuid4()),
                embedding=embedding_vec,
                embedding_dim=512,
                timestamp=datetime.now(),
                audio_file=f"/test/audio{i}.wav",
                segment_start=0.0,
                segment_end=2.0,
                confidence=0.9,
                segment_duration=2.0,
                metadata={}
            )
            temp_db.save_embedding(emb)

        # Delete speaker
        deleted_count = temp_db.delete_speaker(speaker_label)

        assert deleted_count == 3

        # Verify deletion
        embeddings = temp_db.get_embeddings_by_speaker(speaker_label)
        assert len(embeddings) == 0

        profile = temp_db.get_speaker_profile(speaker_label)
        assert profile is None

    def test_get_statistics(self, temp_db):
        """Test database statistics"""
        # Add embeddings for multiple speakers
        for speaker in ["Speaker A", "Speaker B"]:
            for i in range(3):
                embedding_vec = np.random.randn(512).astype(np.float32)
                emb = SpeakerEmbedding(
                    speaker_label=speaker,
                    embedding_id=str(uuid.uuid4()),
                    embedding=embedding_vec,
                    embedding_dim=512,
                    timestamp=datetime.now(),
                    audio_file=f"/test/audio{i}.wav",
                    segment_start=0.0,
                    segment_end=2.0,
                    confidence=0.85,
                    segment_duration=2.0,
                    metadata={}
                )
                temp_db.save_embedding(emb)

        stats = temp_db.get_statistics()

        assert stats['total_embeddings'] == 6
        assert stats['total_speakers'] == 2
        assert stats['avg_confidence'] == pytest.approx(0.85, abs=0.01)
        assert stats['total_audio_duration_seconds'] == pytest.approx(12.0, abs=0.1)
        assert stats['database_size_mb'] > 0


@pytest.mark.skipif(
    not DEPENDENCIES_AVAILABLE or not os.getenv('HF_TOKEN'),
    reason="Dependencies or HF_TOKEN not available"
)
class TestSpeakerEmbeddingExtractor:
    """Tests for SpeakerEmbeddingExtractor (requires HF_TOKEN)"""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance"""
        hf_token = os.getenv('HF_TOKEN')
        return SpeakerEmbeddingExtractor(use_auth_token=hf_token, device='cpu')

    @pytest.fixture
    def synthetic_audio(self):
        """Create synthetic audio file for testing"""
        # Generate 2 seconds of sine wave
        sample_rate = 16000
        duration = 2.0
        frequency = 440.0  # A4 note

        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        import soundfile as sf
        sf.write(temp_file.name, audio, sample_rate)

        yield Path(temp_file.name)

        # Cleanup
        Path(temp_file.name).unlink()

    def test_extractor_initialization(self, extractor):
        """Test extractor initialization"""
        assert extractor.model is None  # Lazy loading
        assert extractor.device is not None

    def test_extract_embedding(self, extractor, synthetic_audio):
        """Test extracting embedding from audio segment"""
        embedding = extractor.extract_embedding(
            synthetic_audio,
            start=0.0,
            end=1.0
        )

        assert embedding.shape == (512,)
        assert embedding.dtype == np.float32 or embedding.dtype == np.float64

        # Check L2-normalization
        norm = np.linalg.norm(embedding)
        assert pytest.approx(norm, abs=0.01) == 1.0

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        # Create two similar embeddings
        emb1 = np.random.randn(512)
        emb1 = emb1 / np.linalg.norm(emb1)

        emb2 = emb1 + 0.1 * np.random.randn(512)
        emb2 = emb2 / np.linalg.norm(emb2)

        similarity = SpeakerEmbeddingExtractor.cosine_similarity(emb1, emb2)

        assert -1.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should be fairly similar

    def test_compute_average_embedding(self, extractor):
        """Test computing average embedding"""
        # Create multiple embeddings
        embeddings = [np.random.randn(512) for _ in range(5)]

        avg_embedding = extractor.compute_average_embedding(embeddings)

        assert avg_embedding.shape == (512,)

        # Check L2-normalization
        norm = np.linalg.norm(avg_embedding)
        assert pytest.approx(norm, abs=0.01) == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
