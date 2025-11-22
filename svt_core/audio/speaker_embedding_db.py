#!/usr/bin/env python3
"""
Speaker Embeddings Database Layer

Manages persistent storage of speaker embeddings in SQLite database
for cross-session speaker recognition.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np

from svt_core.audio.speaker_embeddings import SpeakerEmbedding


logger = logging.getLogger(__name__)


class SpeakerEmbeddingDB:
    """
    Manage speaker embeddings in SQLite database

    Provides CRUD operations for speaker embeddings and aggregated
    speaker profiles.
    """

    def __init__(self, db_path: Path = None):
        """
        Initialize embedding database

        Args:
            db_path: Path to SQLite database file (default: Memory/speaker_embeddings.db)
        """
        if db_path is None:
            db_path = Path("Memory/speaker_embeddings.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing Speaker Embedding DB: {self.db_path}")

        self.conn = sqlite3.connect(str(self.db_path))
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Main embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speaker_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                speaker_label VARCHAR(255) NOT NULL,
                embedding_id VARCHAR(36) NOT NULL UNIQUE,
                embedding BLOB NOT NULL,
                embedding_dim INTEGER NOT NULL DEFAULT 512,
                timestamp DATETIME NOT NULL,
                audio_file VARCHAR(512) NOT NULL,
                segment_start REAL NOT NULL,
                segment_end REAL NOT NULL,
                confidence REAL NOT NULL,
                segment_duration REAL NOT NULL,
                metadata TEXT,
                CHECK (confidence >= 0.0 AND confidence <= 1.0),
                CHECK (segment_start >= 0.0),
                CHECK (segment_end > segment_start),
                CHECK (embedding_dim > 0)
            )
        """)

        # Create indexes for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_speaker_label
            ON speaker_embeddings(speaker_label)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON speaker_embeddings(timestamp DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audio_file
            ON speaker_embeddings(audio_file)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_confidence
            ON speaker_embeddings(confidence DESC)
        """)

        # Speaker profiles table (aggregated info)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speaker_profiles (
                speaker_label VARCHAR(255) PRIMARY KEY,
                first_seen DATETIME NOT NULL,
                last_seen DATETIME NOT NULL,
                total_embeddings INTEGER NOT NULL DEFAULT 0,
                avg_confidence REAL NOT NULL DEFAULT 0.0,
                total_audio_duration REAL NOT NULL DEFAULT 0.0,
                metadata TEXT
            )
        """)

        self.conn.commit()

        logger.debug("Database tables created/verified")

    def save_embedding(self, embedding: SpeakerEmbedding) -> int:
        """
        Save embedding to database

        Args:
            embedding: SpeakerEmbedding object to save

        Returns:
            Database row ID

        Raises:
            sqlite3.IntegrityError: If embedding_id already exists
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO speaker_embeddings (
                    speaker_label, embedding_id, embedding, embedding_dim,
                    timestamp, audio_file, segment_start, segment_end,
                    confidence, segment_duration, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                embedding.speaker_label,
                embedding.embedding_id,
                embedding.embedding.astype(np.float32).tobytes(),
                embedding.embedding_dim,
                embedding.timestamp.isoformat(),
                embedding.audio_file,
                embedding.segment_start,
                embedding.segment_end,
                embedding.confidence,
                embedding.segment_duration,
                json.dumps(embedding.metadata)
            ))

            row_id = cursor.lastrowid

            # Update speaker profile
            self._update_speaker_profile(embedding)

            self.conn.commit()

            logger.debug(
                f"Saved embedding {embedding.embedding_id[:8]}... "
                f"for {embedding.speaker_label}"
            )

            return row_id

        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to save embedding: {e}")
            raise

    def _update_speaker_profile(self, embedding: SpeakerEmbedding):
        """Update or create speaker profile entry"""
        cursor = self.conn.cursor()

        # Check if profile exists
        cursor.execute("""
            SELECT speaker_label, total_embeddings, avg_confidence, total_audio_duration
            FROM speaker_profiles
            WHERE speaker_label = ?
        """, (embedding.speaker_label,))

        row = cursor.fetchone()

        if row:
            # Update existing profile
            current_total = row[1]
            current_avg_conf = row[2]
            current_duration = row[3]

            new_total = current_total + 1
            new_avg_conf = (current_avg_conf * current_total + embedding.confidence) / new_total
            new_duration = current_duration + embedding.segment_duration

            cursor.execute("""
                UPDATE speaker_profiles
                SET last_seen = ?,
                    total_embeddings = ?,
                    avg_confidence = ?,
                    total_audio_duration = ?
                WHERE speaker_label = ?
            """, (
                embedding.timestamp.isoformat(),
                new_total,
                new_avg_conf,
                new_duration,
                embedding.speaker_label
            ))
        else:
            # Create new profile
            cursor.execute("""
                INSERT INTO speaker_profiles (
                    speaker_label, first_seen, last_seen,
                    total_embeddings, avg_confidence, total_audio_duration
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                embedding.speaker_label,
                embedding.timestamp.isoformat(),
                embedding.timestamp.isoformat(),
                1,
                embedding.confidence,
                embedding.segment_duration
            ))

    def get_embeddings_by_speaker(
        self,
        speaker_label: str,
        limit: Optional[int] = None,
        min_confidence: float = 0.0
    ) -> List[SpeakerEmbedding]:
        """
        Retrieve all embeddings for a speaker

        Args:
            speaker_label: Speaker label to query
            limit: Maximum number of embeddings to return (most recent first)
            min_confidence: Minimum confidence threshold (0.0-1.0)

        Returns:
            List of SpeakerEmbedding objects (sorted by timestamp, newest first)
        """
        cursor = self.conn.cursor()

        query = """
            SELECT * FROM speaker_embeddings
            WHERE speaker_label = ? AND confidence >= ?
            ORDER BY timestamp DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (speaker_label, min_confidence))

        embeddings = []
        for row in cursor.fetchall():
            emb = self._row_to_embedding(row)
            embeddings.append(emb)

        logger.debug(
            f"Retrieved {len(embeddings)} embeddings for {speaker_label} "
            f"(limit={limit}, min_conf={min_confidence})"
        )

        return embeddings

    def get_all_speakers(self) -> List[str]:
        """
        Get list of all known speakers

        Returns:
            List of speaker labels
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT speaker_label FROM speaker_embeddings
            ORDER BY speaker_label
        """)
        return [row[0] for row in cursor.fetchall()]

    def get_speaker_profile(self, speaker_label: str) -> Optional[Dict[str, Any]]:
        """
        Get aggregated speaker profile

        Args:
            speaker_label: Speaker label to query

        Returns:
            Dict with profile information or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM speaker_profiles WHERE speaker_label = ?
        """, (speaker_label,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'speaker_label': row[0],
            'first_seen': datetime.fromisoformat(row[1]),
            'last_seen': datetime.fromisoformat(row[2]),
            'total_embeddings': row[3],
            'avg_confidence': row[4],
            'total_audio_duration': row[5],
            'metadata': json.loads(row[6]) if row[6] else {}
        }

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """
        Get all speaker profiles

        Returns:
            List of profile dicts
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM speaker_profiles
            ORDER BY last_seen DESC
        """)

        profiles = []
        for row in cursor.fetchall():
            profiles.append({
                'speaker_label': row[0],
                'first_seen': datetime.fromisoformat(row[1]),
                'last_seen': datetime.fromisoformat(row[2]),
                'total_embeddings': row[3],
                'avg_confidence': row[4],
                'total_audio_duration': row[5],
                'metadata': json.loads(row[6]) if row[6] else {}
            })

        return profiles

    def delete_speaker(self, speaker_label: str) -> int:
        """
        Delete all data for a speaker

        Args:
            speaker_label: Speaker label to delete

        Returns:
            Number of embeddings deleted
        """
        cursor = self.conn.cursor()

        # Delete embeddings
        cursor.execute("""
            DELETE FROM speaker_embeddings WHERE speaker_label = ?
        """, (speaker_label,))
        deleted_count = cursor.rowcount

        # Delete profile
        cursor.execute("""
            DELETE FROM speaker_profiles WHERE speaker_label = ?
        """, (speaker_label,))

        self.conn.commit()

        logger.info(f"Deleted {deleted_count} embeddings for {speaker_label}")

        return deleted_count

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dict with database statistics
        """
        cursor = self.conn.cursor()

        # Count total embeddings
        cursor.execute("SELECT COUNT(*) FROM speaker_embeddings")
        total_embeddings = cursor.fetchone()[0]

        # Count unique speakers
        cursor.execute("SELECT COUNT(DISTINCT speaker_label) FROM speaker_embeddings")
        total_speakers = cursor.fetchone()[0]

        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM speaker_embeddings")
        avg_confidence = cursor.fetchone()[0] or 0.0

        # Total audio duration
        cursor.execute("SELECT SUM(segment_duration) FROM speaker_embeddings")
        total_duration = cursor.fetchone()[0] or 0.0

        # Database file size
        db_size_bytes = self.db_path.stat().st_size if self.db_path.exists() else 0

        return {
            'total_embeddings': total_embeddings,
            'total_speakers': total_speakers,
            'avg_confidence': avg_confidence,
            'total_audio_duration_seconds': total_duration,
            'total_audio_duration_minutes': total_duration / 60,
            'database_size_bytes': db_size_bytes,
            'database_size_mb': db_size_bytes / (1024 * 1024)
        }

    def _row_to_embedding(self, row: tuple) -> SpeakerEmbedding:
        """Convert database row to SpeakerEmbedding object"""
        return SpeakerEmbedding(
            speaker_label=row[1],
            embedding_id=row[2],
            embedding=np.frombuffer(row[3], dtype=np.float32),
            embedding_dim=row[4],
            timestamp=datetime.fromisoformat(row[5]),
            audio_file=row[6],
            segment_start=row[7],
            segment_end=row[8],
            confidence=row[9],
            segment_duration=row[10],
            metadata=json.loads(row[11]) if row[11] else {}
        )

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __del__(self):
        """Destructor"""
        self.close()
