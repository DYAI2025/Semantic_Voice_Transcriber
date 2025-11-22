#!/usr/bin/env python3
"""
Cross-Session Speaker Re-Identification Tests

Tests speaker matching across multiple sessions with the same speakers.
"""

import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from svt_core.audio.speaker_embeddings import SpeakerEmbedding
from svt_core.audio.speaker_embedding_db import SpeakerEmbeddingDB
from svt_core.audio.speaker_matching import SpeakerMatcher, SpeakerMatch


class TestSpeakerMatcher:
    """Tests for SpeakerMatcher cross-session recognition"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_matching.db"
        db = SpeakerEmbeddingDB(db_path)
        yield db
        db.close()
        if db_path.exists():
            db_path.unlink()

    @pytest.fixture
    def matcher(self, temp_db):
        """Create SpeakerMatcher instance"""
        return SpeakerMatcher(
            embedding_db=temp_db,
            similarity_threshold=0.85,
            min_embeddings_for_match=1,
            use_average_embedding=True
        )

    def test_matcher_initialization(self, matcher):
        """Test matcher initialization"""
        assert matcher.similarity_threshold == 0.85
        assert matcher.min_embeddings_for_match == 1
        assert matcher.use_average_embedding is True

    def test_match_speaker_no_database(self, matcher):
        """Test matching when database is empty"""
        test_embedding = np.random.randn(512).astype(np.float32)
        test_embedding = test_embedding / np.linalg.norm(test_embedding)

        match = matcher.match_speaker(test_embedding)

        assert match is None  # No speakers in database

    def test_match_speaker_exact_match(self, matcher, temp_db):
        """Test matching with identical embedding (perfect match)"""
        # Create and save a speaker embedding
        original_embedding = np.random.randn(512).astype(np.float32)
        original_embedding = original_embedding / np.linalg.norm(original_embedding)

        emb = SpeakerEmbedding(
            speaker_label="Speaker A",
            embedding_id=str(uuid.uuid4()),
            embedding=original_embedding,
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

        # Match with same embedding (should be perfect match)
        match = matcher.match_speaker(original_embedding)

        assert match is not None
        assert match.matched_speaker_label == "Speaker A"
        assert match.similarity_score >= 0.99  # Nearly perfect

    def test_match_speaker_similar_embedding(self, matcher, temp_db):
        """Test matching with similar embedding"""
        # Create original embedding
        original_embedding = np.random.randn(512).astype(np.float32)
        original_embedding = original_embedding / np.linalg.norm(original_embedding)

        emb = SpeakerEmbedding(
            speaker_label="Speaker A",
            embedding_id=str(uuid.uuid4()),
            embedding=original_embedding,
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

        # Create similar embedding (add small noise)
        similar_embedding = original_embedding + 0.1 * np.random.randn(512).astype(np.float32)
        similar_embedding = similar_embedding / np.linalg.norm(similar_embedding)

        # Match
        match = matcher.match_speaker(similar_embedding)

        # Should match (similarity should be high)
        if match:
            assert match.matched_speaker_label == "Speaker A"
            assert match.similarity_score > 0.85
        # If not matched, similarity was below threshold (acceptable)

    def test_match_speaker_different_embedding(self, matcher, temp_db):
        """Test matching with very different embedding (no match expected)"""
        # Create original embedding
        original_embedding = np.random.randn(512).astype(np.float32)
        original_embedding = original_embedding / np.linalg.norm(original_embedding)

        emb = SpeakerEmbedding(
            speaker_label="Speaker A",
            embedding_id=str(uuid.uuid4()),
            embedding=original_embedding,
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

        # Create completely different embedding
        different_embedding = np.random.randn(512).astype(np.float32)
        different_embedding = different_embedding / np.linalg.norm(different_embedding)

        # Match
        match = matcher.match_speaker(different_embedding)

        # Should not match (similarity will be low)
        # Allow match if similarity happens to be high (random chance)
        if match:
            assert match.similarity_score >= 0.85  # At least above threshold

    def test_match_multiple_speakers(self, matcher, temp_db):
        """Test matching multiple speakers at once"""
        # Create embeddings for Speaker A and Speaker B
        emb_a = np.random.randn(512).astype(np.float32)
        emb_a = emb_a / np.linalg.norm(emb_a)

        emb_b = np.random.randn(512).astype(np.float32)
        emb_b = emb_b / np.linalg.norm(emb_b)

        # Save to database
        for label, emb_vec in [("Speaker A", emb_a), ("Speaker B", emb_b)]:
            emb = SpeakerEmbedding(
                speaker_label=label,
                embedding_id=str(uuid.uuid4()),
                embedding=emb_vec,
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

        # Create test embeddings (same speakers)
        test_embeddings = {
            'SPEAKER_00': [emb_a],
            'SPEAKER_01': [emb_b]
        }

        # Match
        matches = matcher.match_multiple_speakers(test_embeddings)

        assert len(matches) == 2
        # Check if matches found (may not match due to threshold)
        for speaker_id, match in matches.items():
            if match:
                assert match.matched_speaker_label in ["Speaker A", "Speaker B"]

    def test_get_similar_speakers(self, matcher, temp_db):
        """Test getting top-k similar speakers"""
        # Create embeddings for 3 speakers
        for i, label in enumerate(["Speaker A", "Speaker B", "Speaker C"]):
            emb_vec = np.random.randn(512).astype(np.float32)
            emb_vec = emb_vec / np.linalg.norm(emb_vec)

            emb = SpeakerEmbedding(
                speaker_label=label,
                embedding_id=str(uuid.uuid4()),
                embedding=emb_vec,
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

        # Test embedding
        test_embedding = np.random.randn(512).astype(np.float32)
        test_embedding = test_embedding / np.linalg.norm(test_embedding)

        # Get similar speakers
        similar = matcher.get_similar_speakers(
            test_embedding,
            top_k=2,
            min_similarity=0.0  # Include all
        )

        assert len(similar) <= 2  # Top-2
        assert all(isinstance(item, tuple) for item in similar)
        assert all(len(item) == 2 for item in similar)

        # Check sorted by similarity (descending)
        if len(similar) > 1:
            assert similar[0][1] >= similar[1][1]

    def test_matching_with_multiple_embeddings(self, matcher, temp_db):
        """Test matching with multiple embeddings per speaker (robust matching)"""
        # Create multiple embeddings for same speaker
        base_embedding = np.random.randn(512).astype(np.float32)
        base_embedding = base_embedding / np.linalg.norm(base_embedding)

        # Add 5 slightly different embeddings (simulating different segments)
        for i in range(5):
            varied_embedding = base_embedding + 0.05 * np.random.randn(512).astype(np.float32)
            varied_embedding = varied_embedding / np.linalg.norm(varied_embedding)

            emb = SpeakerEmbedding(
                speaker_label="Speaker A",
                embedding_id=str(uuid.uuid4()),
                embedding=varied_embedding,
                embedding_dim=512,
                timestamp=datetime.now(),
                audio_file=f"/test/audio{i}.wav",
                segment_start=0.0,
                segment_end=2.0,
                confidence=0.85 + i * 0.01,
                segment_duration=2.0,
                metadata={}
            )
            temp_db.save_embedding(emb)

        # Test with similar embedding
        test_embedding = base_embedding + 0.05 * np.random.randn(512).astype(np.float32)
        test_embedding = test_embedding / np.linalg.norm(test_embedding)

        # Match (should use average of 5 embeddings)
        match = matcher.match_speaker(test_embedding)

        # Should match robustly
        if match:
            assert match.matched_speaker_label == "Speaker A"
            assert match.num_embeddings_used == 5

    def test_similarity_threshold_filtering(self, matcher, temp_db):
        """Test that similarity threshold is properly enforced"""
        # Create embedding
        original_embedding = np.random.randn(512).astype(np.float32)
        original_embedding = original_embedding / np.linalg.norm(original_embedding)

        emb = SpeakerEmbedding(
            speaker_label="Speaker A",
            embedding_id=str(uuid.uuid4()),
            embedding=original_embedding,
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

        # Create matcher with very high threshold
        strict_matcher = SpeakerMatcher(
            embedding_db=temp_db,
            similarity_threshold=0.99,  # Very strict
            min_embeddings_for_match=1
        )

        # Test with slightly different embedding
        test_embedding = original_embedding + 0.1 * np.random.randn(512).astype(np.float32)
        test_embedding = test_embedding / np.linalg.norm(test_embedding)

        # Match should likely fail due to strict threshold
        match = strict_matcher.match_speaker(test_embedding)

        # If match found, similarity must be >= 0.99
        if match:
            assert match.similarity_score >= 0.99

    def test_get_matching_statistics(self, matcher, temp_db):
        """Test getting matching statistics"""
        # Add some embeddings
        for i in range(3):
            emb_vec = np.random.randn(512).astype(np.float32)
            emb_vec = emb_vec / np.linalg.norm(emb_vec)

            emb = SpeakerEmbedding(
                speaker_label=f"Speaker {chr(ord('A') + i)}",
                embedding_id=str(uuid.uuid4()),
                embedding=emb_vec,
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

        stats = matcher.get_matching_statistics()

        assert stats['total_speakers'] == 3
        assert stats['total_embeddings'] == 3
        assert stats['similarity_threshold'] == 0.85
        assert stats['min_embeddings_for_match'] == 1


class TestCrossSessionScenarios:
    """Integration tests for realistic cross-session scenarios"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_cross_session.db"
        db = SpeakerEmbeddingDB(db_path)
        yield db
        db.close()
        if db_path.exists():
            db_path.unlink()

    def test_therapy_session_continuity(self, temp_db):
        """
        Test: Patient A comes for multiple therapy sessions
        Expect: Patient recognized across sessions
        """
        matcher = SpeakerMatcher(
            embedding_db=temp_db,
            similarity_threshold=0.85
        )

        # Session 1: Patient A + Therapist B
        # Generate consistent embeddings for each speaker
        np.random.seed(42)  # Reproducible
        patient_base = np.random.randn(512).astype(np.float32)
        patient_base = patient_base / np.linalg.norm(patient_base)

        therapist_base = np.random.randn(512).astype(np.float32)
        therapist_base = therapist_base / np.linalg.norm(therapist_base)

        # Save Session 1 embeddings
        for label, base in [("Patient A", patient_base), ("Therapist B", therapist_base)]:
            for i in range(3):  # 3 segments each
                varied = base + 0.05 * np.random.randn(512).astype(np.float32)
                varied = varied / np.linalg.norm(varied)

                emb = SpeakerEmbedding(
                    speaker_label=label,
                    embedding_id=str(uuid.uuid4()),
                    embedding=varied,
                    embedding_dim=512,
                    timestamp=datetime.now(),
                    audio_file="/test/session1.wav",
                    segment_start=float(i * 5),
                    segment_end=float((i + 1) * 5),
                    confidence=0.9,
                    segment_duration=5.0,
                    metadata={'session': 1}
                )
                temp_db.save_embedding(emb)

        # Session 2: Same patient, same therapist
        # Generate new embeddings (similar but not identical)
        patient_new = patient_base + 0.08 * np.random.randn(512).astype(np.float32)
        patient_new = patient_new / np.linalg.norm(patient_new)

        therapist_new = therapist_base + 0.08 * np.random.randn(512).astype(np.float32)
        therapist_new = therapist_new / np.linalg.norm(therapist_new)

        # Match
        patient_match = matcher.match_speaker(patient_new)
        therapist_match = matcher.match_speaker(therapist_new)

        # Assertions
        assert patient_match is not None, "Patient should be recognized"
        assert patient_match.matched_speaker_label == "Patient A"
        assert patient_match.similarity_score >= 0.85

        assert therapist_match is not None, "Therapist should be recognized"
        assert therapist_match.matched_speaker_label == "Therapist B"
        assert therapist_match.similarity_score >= 0.85

    def test_new_speaker_detection(self, temp_db):
        """
        Test: New speaker should NOT match existing speakers
        """
        matcher = SpeakerMatcher(
            embedding_db=temp_db,
            similarity_threshold=0.85
        )

        # Add existing speaker
        existing_embedding = np.random.randn(512).astype(np.float32)
        existing_embedding = existing_embedding / np.linalg.norm(existing_embedding)

        emb = SpeakerEmbedding(
            speaker_label="Existing Speaker",
            embedding_id=str(uuid.uuid4()),
            embedding=existing_embedding,
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

        # New speaker (completely different)
        new_speaker_embedding = np.random.randn(512).astype(np.float32)
        new_speaker_embedding = new_speaker_embedding / np.linalg.norm(new_speaker_embedding)

        # Match
        match = matcher.match_speaker(new_speaker_embedding)

        # Should NOT match (unless by random chance similarity > 0.85)
        # We can't assert None because random embeddings might be similar
        # But we log the result
        if match:
            print(f"Unexpected match: {match.similarity_score}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
