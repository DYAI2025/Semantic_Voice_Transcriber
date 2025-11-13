"""
Speaker Database for Persistent Speaker Profiles

This module manages a SQLite database of speaker profiles including:
- Voice embeddings (512-dimensional vectors)
- Speaker names (user-editable)
- Visual attributes (colors, icons)
- Usage statistics and metadata
"""

import sqlite3
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SpeakerDatabase:
    """Persistent database for speaker profiles"""

    def __init__(self, db_path: str = "Memory/speaker_profiles.db"):
        """
        Initialize speaker database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()

        self._create_tables()

    def _create_tables(self):
        """Create database schema if not exists"""
        # Speakers table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS speakers (
                speaker_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                color TEXT DEFAULT '#4A90E2',
                icon_index INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                total_duration_seconds REAL DEFAULT 0.0,
                total_segments INTEGER DEFAULT 0,
                notes TEXT
            )
        """)

        # Embeddings table (one-to-many with speakers)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                speaker_id TEXT NOT NULL,
                embedding BLOB NOT NULL,
                recorded_at TEXT NOT NULL,
                audio_file TEXT,
                confidence REAL DEFAULT 1.0,
                FOREIGN KEY (speaker_id) REFERENCES speakers(speaker_id)
            )
        """)

        # Sessions table (track transcription sessions)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                audio_file TEXT NOT NULL,
                started_at TEXT NOT NULL,
                duration_seconds REAL,
                speakers_detected INTEGER,
                quality_score REAL
            )
        """)

        # Session speakers (many-to-many)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_speakers (
                session_id TEXT NOT NULL,
                speaker_id TEXT NOT NULL,
                duration_seconds REAL DEFAULT 0.0,
                segment_count INTEGER DEFAULT 0,
                PRIMARY KEY (session_id, speaker_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                FOREIGN KEY (speaker_id) REFERENCES speakers(speaker_id)
            )
        """)

        # Create indices for faster queries
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embeddings_speaker
            ON embeddings(speaker_id)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_speakers_session
            ON session_speakers(session_id)
        """)

        self.conn.commit()

    def add_speaker(
        self,
        speaker_id: str,
        name: str = None,
        color: str = None,
        icon_index: int = 0
    ) -> str:
        """
        Add a new speaker to the database

        Args:
            speaker_id: Unique identifier for speaker
            name: Display name (default: "Speaker {id}")
            color: Hex color code (default: auto-assigned)
            icon_index: Icon index for visualization

        Returns:
            speaker_id of created speaker
        """
        if name is None:
            name = f"Speaker {speaker_id}"

        if color is None:
            # Auto-assign color from palette
            color = self._get_next_color()

        now = datetime.now().isoformat()

        try:
            self.cursor.execute("""
                INSERT INTO speakers (
                    speaker_id, name, color, icon_index,
                    created_at, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (speaker_id, name, color, icon_index, now, now))

            self.conn.commit()
            logger.info(f"Added new speaker: {speaker_id} ({name})")
            return speaker_id

        except sqlite3.IntegrityError:
            logger.warning(f"Speaker {speaker_id} already exists")
            return speaker_id

    def get_speaker(self, speaker_id: str) -> Optional[Dict]:
        """
        Get speaker profile

        Args:
            speaker_id: Speaker identifier

        Returns:
            Dict with speaker data or None if not found
        """
        self.cursor.execute("""
            SELECT * FROM speakers WHERE speaker_id = ?
        """, (speaker_id,))

        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None

    def update_speaker_name(self, speaker_id: str, new_name: str):
        """
        Update speaker display name

        Args:
            speaker_id: Speaker identifier
            new_name: New display name
        """
        self.cursor.execute("""
            UPDATE speakers
            SET name = ?, last_seen = ?
            WHERE speaker_id = ?
        """, (new_name, datetime.now().isoformat(), speaker_id))

        self.conn.commit()
        logger.info(f"Updated speaker {speaker_id} name to: {new_name}")

    def update_speaker_color(self, speaker_id: str, new_color: str):
        """
        Update speaker color

        Args:
            speaker_id: Speaker identifier
            new_color: Hex color code
        """
        self.cursor.execute("""
            UPDATE speakers
            SET color = ?
            WHERE speaker_id = ?
        """, (new_color, speaker_id))

        self.conn.commit()
        logger.info(f"Updated speaker {speaker_id} color to: {new_color}")

    def add_embedding(
        self,
        speaker_id: str,
        embedding: np.ndarray,
        audio_file: str = None,
        confidence: float = 1.0
    ):
        """
        Add a voice embedding for a speaker

        Args:
            speaker_id: Speaker identifier
            embedding: 512-dim numpy array
            audio_file: Source audio file
            confidence: Embedding quality score
        """
        # Convert numpy array to bytes
        embedding_bytes = embedding.tobytes()

        now = datetime.now().isoformat()

        self.cursor.execute("""
            INSERT INTO embeddings (
                speaker_id, embedding, recorded_at,
                audio_file, confidence
            ) VALUES (?, ?, ?, ?, ?)
        """, (speaker_id, embedding_bytes, now, audio_file, confidence))

        self.conn.commit()
        logger.debug(f"Added embedding for speaker {speaker_id}")

    def get_embeddings(self, speaker_id: str) -> List[np.ndarray]:
        """
        Get all embeddings for a speaker

        Args:
            speaker_id: Speaker identifier

        Returns:
            List of numpy arrays (512-dim each)
        """
        self.cursor.execute("""
            SELECT embedding FROM embeddings
            WHERE speaker_id = ?
            ORDER BY confidence DESC
        """, (speaker_id,))

        rows = self.cursor.fetchall()

        embeddings = []
        for row in rows:
            # Convert bytes back to numpy array
            embedding = np.frombuffer(row['embedding'], dtype=np.float32)
            embeddings.append(embedding)

        return embeddings

    def find_matching_speaker(
        self,
        query_embedding: np.ndarray,
        threshold: float = 0.75
    ) -> Optional[Tuple[str, float]]:
        """
        Find speaker that matches query embedding

        Args:
            query_embedding: 512-dim numpy array to match
            threshold: Minimum cosine similarity (0-1)

        Returns:
            Tuple of (speaker_id, similarity) or None if no match
        """
        # Get all speakers with embeddings
        self.cursor.execute("""
            SELECT DISTINCT speaker_id FROM embeddings
        """)

        speaker_ids = [row['speaker_id'] for row in self.cursor.fetchall()]

        best_match = None
        best_similarity = threshold

        for speaker_id in speaker_ids:
            embeddings = self.get_embeddings(speaker_id)

            for emb in embeddings:
                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, emb)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = speaker_id

        if best_match:
            logger.info(f"Matched speaker {best_match} with similarity {best_similarity:.3f}")
            return (best_match, best_similarity)

        return None

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def get_all_speakers(self) -> List[Dict]:
        """
        Get all speakers in database

        Returns:
            List of speaker dicts
        """
        self.cursor.execute("""
            SELECT * FROM speakers
            ORDER BY last_seen DESC
        """)

        return [dict(row) for row in self.cursor.fetchall()]

    def update_speaker_stats(
        self,
        speaker_id: str,
        duration_seconds: float,
        segment_count: int
    ):
        """
        Update speaker usage statistics

        Args:
            speaker_id: Speaker identifier
            duration_seconds: Duration to add
            segment_count: Number of segments to add
        """
        self.cursor.execute("""
            UPDATE speakers
            SET
                total_duration_seconds = total_duration_seconds + ?,
                total_segments = total_segments + ?,
                last_seen = ?
            WHERE speaker_id = ?
        """, (duration_seconds, segment_count, datetime.now().isoformat(), speaker_id))

        self.conn.commit()

    def create_session(
        self,
        session_id: str,
        audio_file: str,
        duration_seconds: float = None,
        quality_score: float = None
    ):
        """
        Create a transcription session record

        Args:
            session_id: Unique session identifier
            audio_file: Path to audio file
            duration_seconds: Total audio duration
            quality_score: Overall quality score
        """
        now = datetime.now().isoformat()

        self.cursor.execute("""
            INSERT INTO sessions (
                session_id, audio_file, started_at,
                duration_seconds, quality_score
            ) VALUES (?, ?, ?, ?, ?)
        """, (session_id, audio_file, now, duration_seconds, quality_score))

        self.conn.commit()
        logger.info(f"Created session: {session_id}")

    def add_session_speaker(
        self,
        session_id: str,
        speaker_id: str,
        duration_seconds: float,
        segment_count: int
    ):
        """
        Associate speaker with session

        Args:
            session_id: Session identifier
            speaker_id: Speaker identifier
            duration_seconds: Speaker's duration in this session
            segment_count: Number of segments
        """
        self.cursor.execute("""
            INSERT OR REPLACE INTO session_speakers (
                session_id, speaker_id, duration_seconds, segment_count
            ) VALUES (?, ?, ?, ?)
        """, (session_id, speaker_id, duration_seconds, segment_count))

        self.conn.commit()

        # Also update speaker's total stats
        self.update_speaker_stats(speaker_id, duration_seconds, segment_count)

    def get_speaker_history(self, speaker_id: str, limit: int = 10) -> List[Dict]:
        """
        Get recent sessions for a speaker

        Args:
            speaker_id: Speaker identifier
            limit: Maximum number of sessions to return

        Returns:
            List of session dicts
        """
        self.cursor.execute("""
            SELECT s.*, ss.duration_seconds as speaker_duration,
                   ss.segment_count as speaker_segments
            FROM sessions s
            JOIN session_speakers ss ON s.session_id = ss.session_id
            WHERE ss.speaker_id = ?
            ORDER BY s.started_at DESC
            LIMIT ?
        """, (speaker_id, limit))

        return [dict(row) for row in self.cursor.fetchall()]

    def _get_next_color(self) -> str:
        """Get next color from palette for new speaker"""
        palette = [
            '#4A90E2',  # Blue
            '#7B68EE',  # Purple
            '#50C878',  # Green
            '#FF6B6B',  # Red
            '#FFA500',  # Orange
            '#20B2AA',  # Teal
            '#FF69B4',  # Pink
            '#FFD700',  # Gold
        ]

        # Count existing speakers
        self.cursor.execute("SELECT COUNT(*) as count FROM speakers")
        count = self.cursor.fetchone()['count']

        return palette[count % len(palette)]

    def export_speakers(self, output_path: str):
        """
        Export all speakers to JSON

        Args:
            output_path: Where to save JSON file
        """
        speakers = self.get_all_speakers()

        # Convert to JSON-serializable format
        for speaker in speakers:
            # Get embedding count
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM embeddings
                WHERE speaker_id = ?
            """, (speaker['speaker_id'],))
            speaker['embedding_count'] = self.cursor.fetchone()['count']

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(speakers, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(speakers)} speakers to {output_path}")

    def delete_speaker(self, speaker_id: str):
        """
        Delete a speaker and all associated data

        Args:
            speaker_id: Speaker to delete
        """
        # Delete embeddings
        self.cursor.execute("""
            DELETE FROM embeddings WHERE speaker_id = ?
        """, (speaker_id,))

        # Delete session associations
        self.cursor.execute("""
            DELETE FROM session_speakers WHERE speaker_id = ?
        """, (speaker_id,))

        # Delete speaker
        self.cursor.execute("""
            DELETE FROM speakers WHERE speaker_id = ?
        """, (speaker_id,))

        self.conn.commit()
        logger.info(f"Deleted speaker: {speaker_id}")

    def get_statistics(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dict with counts and summaries
        """
        stats = {}

        # Total speakers
        self.cursor.execute("SELECT COUNT(*) as count FROM speakers")
        stats['total_speakers'] = self.cursor.fetchone()['count']

        # Total embeddings
        self.cursor.execute("SELECT COUNT(*) as count FROM embeddings")
        stats['total_embeddings'] = self.cursor.fetchone()['count']

        # Total sessions
        self.cursor.execute("SELECT COUNT(*) as count FROM sessions")
        stats['total_sessions'] = self.cursor.fetchone()['count']

        # Total duration
        self.cursor.execute("""
            SELECT SUM(total_duration_seconds) as total FROM speakers
        """)
        stats['total_duration_hours'] = (self.cursor.fetchone()['total'] or 0) / 3600

        # Most active speaker
        self.cursor.execute("""
            SELECT speaker_id, name, total_duration_seconds
            FROM speakers
            ORDER BY total_duration_seconds DESC
            LIMIT 1
        """)
        row = self.cursor.fetchone()
        if row:
            stats['most_active_speaker'] = {
                'id': row['speaker_id'],
                'name': row['name'],
                'duration_hours': row['total_duration_seconds'] / 3600
            }

        return stats

    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create/open database
    with SpeakerDatabase("Memory/speaker_profiles.db") as db:
        # Add some test speakers
        db.add_speaker("SPEAKER_00", "Dr. Schmidt", "#4A90E2")
        db.add_speaker("SPEAKER_01", "Patient A", "#7B68EE")

        # Add dummy embedding
        dummy_embedding = np.random.randn(512).astype(np.float32)
        db.add_embedding("SPEAKER_00", dummy_embedding)

        # Get all speakers
        speakers = db.get_all_speakers()
        print(f"\n📊 Found {len(speakers)} speakers:")
        for speaker in speakers:
            print(f"  - {speaker['name']} ({speaker['speaker_id']})")

        # Get statistics
        stats = db.get_statistics()
        print(f"\n📈 Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
