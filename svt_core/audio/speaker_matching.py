#!/usr/bin/env python3
"""
Speaker Matching Module for Cross-Session Recognition

Matches speakers across sessions using embedding similarity.
Enables automatic re-identification of known speakers.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

import numpy as np

from svt_core.audio.speaker_embeddings import SpeakerEmbeddingExtractor
from svt_core.audio.speaker_embedding_db import SpeakerEmbeddingDB


logger = logging.getLogger(__name__)


@dataclass
class SpeakerMatch:
    """Represents a speaker match result"""
    matched_speaker_label: str
    similarity_score: float
    confidence: float
    num_embeddings_used: int
    matched_embedding_ids: List[str]
    metadata: Dict[str, Any]


class SpeakerMatcher:
    """
    Match speakers across sessions using embedding similarity

    Uses cosine similarity between speaker embeddings to identify
    known speakers in new audio files.
    """

    def __init__(
        self,
        embedding_db: SpeakerEmbeddingDB,
        similarity_threshold: float = 0.85,
        min_embeddings_for_match: int = 1,
        use_average_embedding: bool = True
    ):
        """
        Initialize Speaker Matcher

        Args:
            embedding_db: Database with stored speaker embeddings
            similarity_threshold: Minimum cosine similarity for match (0.0-1.0)
            min_embeddings_for_match: Minimum number of embeddings required
            use_average_embedding: If True, use average embedding for robust matching
        """
        self.embedding_db = embedding_db
        self.similarity_threshold = similarity_threshold
        self.min_embeddings_for_match = min_embeddings_for_match
        self.use_average_embedding = use_average_embedding

        logger.info(f"Speaker Matcher initialized:")
        logger.info(f"  Similarity threshold: {similarity_threshold}")
        logger.info(f"  Min embeddings: {min_embeddings_for_match}")
        logger.info(f"  Use average: {use_average_embedding}")

    def match_speaker(
        self,
        new_embedding: np.ndarray,
        candidate_speakers: Optional[List[str]] = None,
        min_confidence: float = 0.6
    ) -> Optional[SpeakerMatch]:
        """
        Match a new embedding to known speakers

        Args:
            new_embedding: Embedding vector to match (512-dim)
            candidate_speakers: List of speaker labels to consider (None = all)
            min_confidence: Minimum confidence threshold for stored embeddings

        Returns:
            SpeakerMatch if match found, None otherwise
        """
        if candidate_speakers is None:
            candidate_speakers = self.embedding_db.get_all_speakers()

        if not candidate_speakers:
            logger.debug("No candidate speakers in database")
            return None

        best_match = None
        best_score = -1

        for speaker_label in candidate_speakers:
            # Get embeddings for this speaker
            known_embeddings = self.embedding_db.get_embeddings_by_speaker(
                speaker_label,
                limit=50,  # Use top 50 most recent
                min_confidence=min_confidence
            )

            if len(known_embeddings) < self.min_embeddings_for_match:
                logger.debug(
                    f"Skipping {speaker_label}: only {len(known_embeddings)} embeddings "
                    f"(min required: {self.min_embeddings_for_match})"
                )
                continue

            # Extract embedding vectors
            embedding_vectors = [emb.embedding for emb in known_embeddings]

            # Calculate similarity
            if self.use_average_embedding:
                # Use average embedding for robust matching
                avg_embedding = np.mean(embedding_vectors, axis=0)
                # L2-normalize
                norm = np.linalg.norm(avg_embedding)
                if norm > 0:
                    avg_embedding = avg_embedding / norm

                similarity = self._cosine_similarity(new_embedding, avg_embedding)
            else:
                # Use maximum similarity across all embeddings
                similarities = [
                    self._cosine_similarity(new_embedding, emb_vec)
                    for emb_vec in embedding_vectors
                ]
                similarity = max(similarities)

            logger.debug(
                f"Similarity to {speaker_label}: {similarity:.3f} "
                f"({len(known_embeddings)} embeddings)"
            )

            if similarity > best_score:
                best_score = similarity
                best_match = SpeakerMatch(
                    matched_speaker_label=speaker_label,
                    similarity_score=similarity,
                    confidence=np.mean([emb.confidence for emb in known_embeddings]),
                    num_embeddings_used=len(known_embeddings),
                    matched_embedding_ids=[emb.embedding_id for emb in known_embeddings[:5]],
                    metadata={
                        'matching_method': 'average' if self.use_average_embedding else 'max',
                        'candidate_count': len(candidate_speakers)
                    }
                )

        # Check if best match exceeds threshold
        if best_match and best_match.similarity_score >= self.similarity_threshold:
            logger.info(
                f"✅ Speaker match found: {best_match.matched_speaker_label} "
                f"(similarity: {best_match.similarity_score:.3f})"
            )
            return best_match
        else:
            if best_match:
                logger.info(
                    f"❌ No match: best similarity {best_match.similarity_score:.3f} "
                    f"< threshold {self.similarity_threshold}"
                )
            return None

    def match_multiple_speakers(
        self,
        embeddings: Dict[str, List[np.ndarray]],
        min_confidence: float = 0.6
    ) -> Dict[str, Optional[SpeakerMatch]]:
        """
        Match multiple speakers at once

        Args:
            embeddings: Dict mapping temporary speaker_id to list of embedding vectors
            min_confidence: Minimum confidence for stored embeddings

        Returns:
            Dict mapping temporary speaker_id to SpeakerMatch (or None if no match)
        """
        results = {}

        for temp_speaker_id, embedding_list in embeddings.items():
            if not embedding_list:
                results[temp_speaker_id] = None
                continue

            # Use average embedding if multiple segments
            if len(embedding_list) > 1:
                avg_embedding = np.mean(embedding_list, axis=0)
                norm = np.linalg.norm(avg_embedding)
                if norm > 0:
                    avg_embedding = avg_embedding / norm
                test_embedding = avg_embedding
            else:
                test_embedding = embedding_list[0]

            # Match this speaker
            match = self.match_speaker(
                test_embedding,
                min_confidence=min_confidence
            )

            results[temp_speaker_id] = match

        # Log summary
        matched_count = sum(1 for m in results.values() if m is not None)
        logger.info(
            f"Matched {matched_count}/{len(results)} speakers "
            f"(threshold: {self.similarity_threshold})"
        )

        return results

    def get_similar_speakers(
        self,
        embedding: np.ndarray,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Get top-k most similar speakers to an embedding

        Useful for debugging and finding potential matches.

        Args:
            embedding: Embedding vector to compare
            top_k: Number of top matches to return
            min_similarity: Minimum similarity to include

        Returns:
            List of (speaker_label, similarity) tuples, sorted by similarity (descending)
        """
        all_speakers = self.embedding_db.get_all_speakers()

        similarities = []

        for speaker_label in all_speakers:
            known_embeddings = self.embedding_db.get_embeddings_by_speaker(
                speaker_label,
                limit=50
            )

            if not known_embeddings:
                continue

            # Use average embedding
            embedding_vectors = [emb.embedding for emb in known_embeddings]
            avg_embedding = np.mean(embedding_vectors, axis=0)
            norm = np.linalg.norm(avg_embedding)
            if norm > 0:
                avg_embedding = avg_embedding / norm

            similarity = self._cosine_similarity(embedding, avg_embedding)

            if similarity >= min_similarity:
                similarities.append((speaker_label, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def update_speaker_label(
        self,
        old_label: str,
        new_label: str
    ) -> int:
        """
        Rename a speaker (useful for manual correction)

        Args:
            old_label: Current speaker label
            new_label: New speaker label

        Returns:
            Number of embeddings updated
        """
        # Get all embeddings for old speaker
        embeddings = self.embedding_db.get_embeddings_by_speaker(old_label)

        if not embeddings:
            logger.warning(f"No embeddings found for {old_label}")
            return 0

        # Update each embedding
        # Note: This is a simplified implementation
        # In production, you'd want a proper UPDATE query
        logger.info(f"Renaming speaker: {old_label} → {new_label}")

        # For now, we delete old and re-insert with new label
        self.embedding_db.delete_speaker(old_label)

        for emb in embeddings:
            emb.speaker_label = new_label
            self.embedding_db.save_embedding(emb)

        logger.info(f"Updated {len(embeddings)} embeddings")

        return len(embeddings)

    @staticmethod
    def _cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Assumes embeddings are L2-normalized.

        Args:
            emb1: First embedding vector
            emb2: Second embedding vector

        Returns:
            Cosine similarity in range [-1, 1]
        """
        # For L2-normalized vectors, cosine similarity = dot product
        similarity = np.dot(emb1, emb2)

        # Clamp to valid range (numerical stability)
        similarity = np.clip(similarity, -1.0, 1.0)

        return float(similarity)

    def get_matching_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about speaker matching performance

        Returns:
            Dict with matching statistics
        """
        db_stats = self.embedding_db.get_statistics()

        return {
            'total_speakers': db_stats['total_speakers'],
            'total_embeddings': db_stats['total_embeddings'],
            'avg_embeddings_per_speaker': (
                db_stats['total_embeddings'] / db_stats['total_speakers']
                if db_stats['total_speakers'] > 0 else 0
            ),
            'similarity_threshold': self.similarity_threshold,
            'min_embeddings_for_match': self.min_embeddings_for_match,
            'database_size_mb': db_stats['database_size_mb']
        }


class CrossSessionRecognizer:
    """
    High-level API for cross-session speaker recognition

    Combines diarization + embedding extraction + speaker matching
    into a single workflow.
    """

    def __init__(
        self,
        diarizer,  # SpeakerDiarizer instance
        matcher: SpeakerMatcher
    ):
        """
        Initialize Cross-Session Recognizer

        Args:
            diarizer: SpeakerDiarizer instance (with embedding extraction enabled)
            matcher: SpeakerMatcher instance
        """
        self.diarizer = diarizer
        self.matcher = matcher

        logger.info("Cross-Session Recognizer initialized")

    def process_audio(
        self,
        audio_path,
        auto_match: bool = True
    ) -> Dict[str, Any]:
        """
        Process audio with cross-session speaker recognition

        Args:
            audio_path: Path to audio file
            auto_match: If True, automatically match speakers to known profiles

        Returns:
            Dict with diarization results and speaker matches
        """
        logger.info(f"Processing audio with cross-session recognition: {audio_path.name}")

        # Run diarization (this also extracts embeddings if enabled)
        segments = self.diarizer.diarize(audio_path)

        if not segments:
            logger.warning("No segments detected")
            return {
                'segments': [],
                'matches': {},
                'new_speakers': []
            }

        # Get unique speakers
        speaker_ids = list(set(seg['speaker_id'] for seg in segments))

        logger.info(f"Detected {len(speaker_ids)} speakers: {speaker_ids}")

        # Match speakers if enabled
        matches = {}
        if auto_match and self.diarizer.enable_embedding_extraction:
            logger.info("Matching speakers to known profiles...")

            for speaker_id in speaker_ids:
                # Get segments for this speaker
                speaker_segments = [s for s in segments if s['speaker_id'] == speaker_id]

                if not speaker_segments:
                    continue

                # Get embeddings for this speaker (from database)
                speaker_label = speaker_segments[0]['speaker']
                embeddings = self.diarizer.embedding_db.get_embeddings_by_speaker(
                    speaker_label,
                    limit=10
                )

                if not embeddings:
                    logger.warning(f"No embeddings found for {speaker_label}")
                    continue

                # Use first embedding for matching (or average)
                test_embedding = embeddings[0].embedding

                # Match to known speakers
                match = self.matcher.match_speaker(test_embedding)

                if match:
                    matches[speaker_id] = match
                    logger.info(
                        f"  {speaker_label} → {match.matched_speaker_label} "
                        f"(similarity: {match.similarity_score:.3f})"
                    )

        # Update segments with matched speaker labels
        updated_segments = []
        new_speakers = []

        for seg in segments:
            seg_copy = seg.copy()

            if seg['speaker_id'] in matches:
                # Update to matched speaker
                match = matches[seg['speaker_id']]
                seg_copy['matched_speaker'] = match.matched_speaker_label
                seg_copy['match_confidence'] = match.similarity_score
                seg_copy['is_known_speaker'] = True
            else:
                # New speaker
                seg_copy['matched_speaker'] = None
                seg_copy['match_confidence'] = 0.0
                seg_copy['is_known_speaker'] = False

                if seg['speaker'] not in new_speakers:
                    new_speakers.append(seg['speaker'])

            updated_segments.append(seg_copy)

        # Summary
        logger.info(
            f"Cross-session recognition complete: "
            f"{len(matches)} matched, {len(new_speakers)} new speakers"
        )

        return {
            'segments': updated_segments,
            'matches': matches,
            'new_speakers': new_speakers,
            'statistics': {
                'total_speakers': len(speaker_ids),
                'matched_speakers': len(matches),
                'new_speakers': len(new_speakers),
                'match_rate': len(matches) / len(speaker_ids) if speaker_ids else 0.0
            }
        }
