# Speaker Embeddings System - Design Document

**Datum:** 2025-11-22
**Sprint:** 1, Tag 5
**Autor:** Claude
**Status:** Design Phase

---

## 📋 Übersicht

Das Speaker Embeddings System ermöglicht **Cross-Session Speaker Recognition** durch Extraktion und Persistierung von Speaker-spezifischen akustischen Merkmalen (Embeddings).

**Ziel:** Speaker aus früheren Sessions automatisch wiedererkennen → Kontinuität über Sitzungen hinweg.

---

## 🎯 Use Cases

### Primary Use Case: Therapeutische Sitzungen
- **Session 1:** Patient A + Therapeut B → Embeddings gespeichert
- **Session 2:** Patient A + Therapeut B → Automatische Wiedererkennung
- **Session 3:** Patient A + Therapeut C → Patient wiedererkannt, Therapeut neu

**Business Value:**
- Kontinuität in Therapie-Transkripten
- Automatische Patient-Zuordnung
- Langzeit-Analyse über Sessions hinweg

### Secondary Use Case: Multi-Session Meetings
- Wiederkehrende Teilnehmer automatisch identifizieren
- Konsistente Sprecherlabels über Meetings hinweg

---

## 🏗️ Architektur

### Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                   Diarization Pipeline                      │
│  ┌──────────────┐    ┌─────────────────┐                  │
│  │ Audio Input  │───▶│ pyannote.audio  │                  │
│  └──────────────┘    │  Diarization    │                  │
│                      └────────┬─────────┘                  │
│                               │                             │
│                               ▼                             │
│                      ┌─────────────────┐                   │
│                      │ Speaker Segments│                   │
│                      │ [A, B, C, ...]  │                   │
│                      └────────┬─────────┘                   │
└─────────────────────────────┼─────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Speaker Embedding System (NEW)                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SpeakerEmbeddingExtractor                           │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ extract_embedding(audio, start, end)           │  │  │
│  │  │  ├─ Load audio segment                         │  │  │
│  │  │  ├─ Run pyannote.audio.Model("embedding")      │  │  │
│  │  │  └─ Return 512-dim vector                      │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ extract_from_diarization(audio, segments)      │  │  │
│  │  │  ├─ For each speaker segment                   │  │  │
│  │  │  ├─ Extract embedding                          │  │  │
│  │  │  └─ Average multiple segments per speaker      │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                               ▼                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SpeakerEmbeddingDB                                  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ save_embedding(speaker, embedding, metadata)   │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ get_embeddings_by_speaker(label)               │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ get_all_speakers()                             │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                               │                             │
│                               ▼                             │
│                    ┌─────────────────────┐                 │
│                    │  SQLite Database    │                 │
│                    │  Memory/            │                 │
│                    │  speaker_           │                 │
│                    │  embeddings.db      │                 │
│                    └─────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 pyannote.audio Embedding Extraction

### Option 1: Segmentation Model Embeddings (CHOSEN)
```python
from pyannote.audio import Model

# Load embedding model
model = Model.from_pretrained(
    "pyannote/embedding",
    token=hf_token
)

# Extract embedding for audio segment
embedding = model({"waveform": audio_segment, "sample_rate": sr})
# Returns: torch.Tensor of shape (1, 512)
```

**Pros:**
- ✅ Official pyannote.audio embedding model
- ✅ Optimized for speaker recognition (512-dim)
- ✅ Trained on VoxCeleb dataset (speaker verification)
- ✅ State-of-the-art performance

**Cons:**
- ⚠️ Requires separate model download (~50MB)
- ⚠️ Additional inference time per segment

### Option 2: Use Diarization Pipeline Embeddings (REJECTED)
```python
# Extract from diarization pipeline's internal embeddings
# Problem: Not exposed in pyannote.audio 3.1 API
```

**Decision:** Use Option 1 (dedicated embedding model)

---

## 📊 Data Model

### SpeakerEmbedding Dataclass

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
import numpy as np

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
    # Example metadata:
    # {
    #   "session_id": "2025-01-15_session_01",
    #   "recording_quality": "high",
    #   "prosody_features": {...},
    #   "device": "cuda"
    # }
```

### SQLite Database Schema

```sql
-- Main embeddings table
CREATE TABLE speaker_embeddings (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Speaker identification
    speaker_label VARCHAR(255) NOT NULL,      -- "Therapeut", "Patient A"
    embedding_id VARCHAR(36) NOT NULL UNIQUE, -- UUID

    -- Embedding data (stored as BLOB)
    embedding BLOB NOT NULL,                  -- Numpy array serialized with tobytes()
    embedding_dim INTEGER NOT NULL DEFAULT 512,

    -- Temporal metadata
    timestamp DATETIME NOT NULL,              -- ISO format
    audio_file VARCHAR(512) NOT NULL,         -- Path to source audio
    segment_start REAL NOT NULL,              -- Seconds
    segment_end REAL NOT NULL,                -- Seconds

    -- Quality metrics
    confidence REAL NOT NULL,                 -- 0.0-1.0
    segment_duration REAL NOT NULL,           -- Seconds

    -- Additional metadata (JSON)
    metadata TEXT,                            -- JSON string

    -- Constraints
    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    CHECK (segment_start >= 0.0),
    CHECK (segment_end > segment_start),
    CHECK (embedding_dim > 0)
);

-- Indexes for fast lookups
CREATE INDEX idx_speaker_label ON speaker_embeddings(speaker_label);
CREATE INDEX idx_timestamp ON speaker_embeddings(timestamp DESC);
CREATE INDEX idx_audio_file ON speaker_embeddings(audio_file);
CREATE INDEX idx_confidence ON speaker_embeddings(confidence DESC);

-- Speaker profiles table (aggregated info)
CREATE TABLE speaker_profiles (
    speaker_label VARCHAR(255) PRIMARY KEY,
    first_seen DATETIME NOT NULL,
    last_seen DATETIME NOT NULL,
    total_embeddings INTEGER NOT NULL DEFAULT 0,
    avg_confidence REAL NOT NULL DEFAULT 0.0,
    total_audio_duration REAL NOT NULL DEFAULT 0.0,  -- Seconds
    metadata TEXT  -- JSON string with profile info
);

-- Trigger to update speaker_profiles on insert
CREATE TRIGGER update_speaker_profile_on_insert
AFTER INSERT ON speaker_embeddings
FOR EACH ROW
BEGIN
    INSERT INTO speaker_profiles (
        speaker_label,
        first_seen,
        last_seen,
        total_embeddings,
        avg_confidence,
        total_audio_duration
    )
    VALUES (
        NEW.speaker_label,
        NEW.timestamp,
        NEW.timestamp,
        1,
        NEW.confidence,
        NEW.segment_duration
    )
    ON CONFLICT(speaker_label) DO UPDATE SET
        last_seen = NEW.timestamp,
        total_embeddings = total_embeddings + 1,
        avg_confidence = (avg_confidence * total_embeddings + NEW.confidence) / (total_embeddings + 1),
        total_audio_duration = total_audio_duration + NEW.segment_duration;
END;
```

---

## 🔧 API Design

### SpeakerEmbeddingExtractor

```python
class SpeakerEmbeddingExtractor:
    """Extract speaker embeddings from audio using pyannote.audio"""

    def __init__(self, use_auth_token: str, device: str = None):
        """
        Initialize embedding extractor

        Args:
            use_auth_token: Hugging Face token
            device: 'cuda', 'cpu', or None (auto-detect)
        """
        self.use_auth_token = use_auth_token
        self.device = torch.device(device) if device else torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu'
        )
        self.model = None  # Lazy loading

    def _load_model(self):
        """Load pyannote embedding model (lazy loading)"""
        if self.model is None:
            logger.info("Loading pyannote embedding model...")
            self.model = Model.from_pretrained(
                "pyannote/embedding",
                token=self.use_auth_token
            )
            self.model.to(self.device)
            logger.info("Embedding model loaded successfully")

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
            Numpy array of shape (512,) with embedding vector
        """
        self._load_model()

        # Load audio segment
        import torchaudio
        waveform, sr = torchaudio.load(str(audio_path))

        # Extract segment (convert seconds to samples)
        start_sample = int(start * sr)
        end_sample = int(end * sr)
        segment = waveform[:, start_sample:end_sample]

        # Resample if needed (pyannote expects 16kHz)
        if sr != 16000:
            resampler = torchaudio.transforms.Resample(sr, 16000)
            segment = resampler(segment)
            sr = 16000

        # Extract embedding
        with torch.no_grad():
            embedding = self.model({
                "waveform": segment.to(self.device),
                "sample_rate": sr
            })

        # Convert to numpy and flatten
        return embedding.cpu().numpy().flatten()

    def extract_from_diarization(
        self,
        audio_path: Path,
        diarization_segments: List[Dict[str, Any]]
    ) -> Dict[str, List[SpeakerEmbedding]]:
        """
        Extract embeddings for all speakers from diarization segments

        Averages multiple segments per speaker for robust representation.

        Args:
            audio_path: Path to audio file
            diarization_segments: Diarization output with speaker labels

        Returns:
            Dict mapping speaker_id to list of embeddings
        """
        self._load_model()

        embeddings_by_speaker = {}

        # Group segments by speaker
        from collections import defaultdict
        speaker_segments = defaultdict(list)

        for seg in diarization_segments:
            speaker_segments[seg['speaker_id']].append(seg)

        # Extract embeddings per speaker
        for speaker_id, segments in speaker_segments.items():
            speaker_embeddings = []

            for seg in segments:
                # Only extract for segments >0.5s (more reliable)
                if (seg['end'] - seg['start']) < 0.5:
                    continue

                try:
                    embedding_vec = self.extract_embedding(
                        audio_path,
                        seg['start'],
                        seg['end']
                    )

                    # Create SpeakerEmbedding object
                    emb = SpeakerEmbedding(
                        speaker_label=seg['speaker'],
                        embedding_id=str(uuid.uuid4()),
                        embedding=embedding_vec,
                        embedding_dim=len(embedding_vec),
                        timestamp=datetime.now(),
                        audio_file=str(audio_path),
                        segment_start=seg['start'],
                        segment_end=seg['end'],
                        confidence=seg.get('confidence', 0.5),
                        segment_duration=seg['end'] - seg['start'],
                        metadata={}
                    )

                    speaker_embeddings.append(emb)

                except Exception as e:
                    logger.warning(
                        f"Failed to extract embedding for {speaker_id} "
                        f"at {seg['start']:.1f}s: {e}"
                    )
                    continue

            embeddings_by_speaker[speaker_id] = speaker_embeddings

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
```

### SpeakerEmbeddingDB

```python
class SpeakerEmbeddingDB:
    """Manage speaker embeddings in SQLite database"""

    def __init__(self, db_path: Path = Path("Memory/speaker_embeddings.db")):
        """
        Initialize embedding database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Main embeddings table (see schema above)
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
                CHECK (segment_end > segment_start)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_speaker_label
            ON speaker_embeddings(speaker_label)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON speaker_embeddings(timestamp DESC)
        """)

        # Speaker profiles table
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

    def save_embedding(self, embedding: SpeakerEmbedding) -> int:
        """
        Save embedding to database

        Args:
            embedding: SpeakerEmbedding object

        Returns:
            Database row ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO speaker_embeddings (
                speaker_label, embedding_id, embedding, embedding_dim,
                timestamp, audio_file, segment_start, segment_end,
                confidence, segment_duration, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            embedding.speaker_label,
            embedding.embedding_id,
            embedding.embedding.tobytes(),
            embedding.embedding_dim,
            embedding.timestamp.isoformat(),
            embedding.audio_file,
            embedding.segment_start,
            embedding.segment_end,
            embedding.confidence,
            embedding.segment_duration,
            json.dumps(embedding.metadata)
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_embeddings_by_speaker(
        self,
        speaker_label: str,
        limit: int = None
    ) -> List[SpeakerEmbedding]:
        """
        Retrieve all embeddings for a speaker

        Args:
            speaker_label: Speaker label to query
            limit: Maximum number of embeddings to return

        Returns:
            List of SpeakerEmbedding objects
        """
        cursor = self.conn.cursor()

        query = """
            SELECT * FROM speaker_embeddings
            WHERE speaker_label = ?
            ORDER BY timestamp DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (speaker_label,))

        embeddings = []
        for row in cursor.fetchall():
            emb = SpeakerEmbedding(
                speaker_label=row[1],
                embedding_id=row[2],
                embedding=np.frombuffer(row[3], dtype=np.float32).reshape(-1),
                embedding_dim=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                audio_file=row[6],
                segment_start=row[7],
                segment_end=row[8],
                confidence=row[9],
                segment_duration=row[10],
                metadata=json.loads(row[11]) if row[11] else {}
            )
            embeddings.append(emb)

        return embeddings

    def get_all_speakers(self) -> List[str]:
        """Get list of all known speakers"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT speaker_label FROM speaker_embeddings
        """)
        return [row[0] for row in cursor.fetchall()]

    def get_speaker_profile(self, speaker_label: str) -> Dict[str, Any]:
        """Get aggregated speaker profile"""
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
```

---

## 🔄 Integration Flow

### Diarization Pipeline Integration

```python
# In SpeakerDiarizer.__init__()
def __init__(
    self,
    use_auth_token: str,
    enable_embedding_extraction: bool = True,  # NEW
    ...
):
    self.enable_embedding_extraction = enable_embedding_extraction

    if enable_embedding_extraction:
        from svt_core.audio.speaker_embeddings import SpeakerEmbeddingExtractor
        from svt_core.audio.speaker_embedding_db import SpeakerEmbeddingDB

        self.embedding_extractor = SpeakerEmbeddingExtractor(use_auth_token)
        self.embedding_db = SpeakerEmbeddingDB()

# In SpeakerDiarizer.diarize()
def diarize(self, audio_path: Path, num_speakers: int = None):
    # ... existing diarization code ...

    segments = [...]  # Diarization results

    # Extract and save embeddings
    if self.enable_embedding_extraction:
        logger.info("Extracting speaker embeddings...")

        embeddings_by_speaker = self.embedding_extractor.extract_from_diarization(
            audio_path,
            segments
        )

        # Save to database
        for speaker_id, embeddings in embeddings_by_speaker.items():
            for emb in embeddings:
                self.embedding_db.save_embedding(emb)

        total_saved = sum(len(embs) for embs in embeddings_by_speaker.values())
        logger.info(f"Saved {total_saved} speaker embeddings to database")

    return segments
```

---

## 📊 Performance Considerations

### Memory Footprint
- **Single embedding**: 512 floats × 4 bytes = 2 KB
- **100 embeddings/speaker**: 200 KB
- **10 speakers × 100 sessions**: ~2 MB in RAM

**Conclusion:** Very lightweight, no memory concerns.

### Inference Time
- **pyannote/embedding**: ~50-100ms per segment (GPU), ~200-400ms (CPU)
- **Average diarization**: 10-50 segments
- **Total overhead**: 0.5-5 seconds (GPU), 2-20 seconds (CPU)

**Mitigation:** Parallel extraction (future optimization)

### Storage
- **Database size**: ~2 KB per embedding
- **1000 sessions × 20 segments/session**: 40 MB
- **10 years**: ~400 MB

**Conclusion:** Negligible storage requirements.

---

## ✅ Implementation Checklist

- [ ] Create `svt_core/audio/speaker_embeddings.py`
- [ ] Create `svt_core/audio/speaker_embedding_db.py`
- [ ] Implement `SpeakerEmbeddingExtractor`
- [ ] Implement `SpeakerEmbeddingDB`
- [ ] Integrate into `SpeakerDiarizer.diarize()`
- [ ] Add unit tests (`tests/test_speaker_embeddings.py`)
- [ ] Add integration tests
- [ ] Document in `SPEAKER_DIARIZATION.md`

---

## 🔜 Next Steps (Sprint 2)

Once embeddings are extracted and stored, Sprint 2 will implement:

1. **Speaker Matching**: Cosine similarity-based speaker re-identification
2. **Cross-Session Recognition**: Match new speakers to existing profiles
3. **Confidence Scoring**: Use embedding similarity as confidence metric
4. **Speaker Clustering**: Merge similar speakers across sessions

---

## 📚 References

- [pyannote.audio Embedding Model](https://huggingface.co/pyannote/embedding)
- [VoxCeleb Dataset](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/)
- [Speaker Verification with pyannote.audio](https://github.com/pyannote/pyannote-audio/blob/develop/tutorials/speaker_verification.ipynb)
