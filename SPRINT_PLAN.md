# Speaker Separation Improvement - Sprint Plans

**Project:** Semantic Voice Transcriber
**Branch:** claude/test-speaker-separation-01Ez1hVdjtqBpv7fGpnvqSqZ
**Duration:** 2 Wochen (10 Arbeitstage)

---

## Sprint 1: Genauigkeit & Stabilität Foundation (Week 1)

**Ziel:** Baseline-Messung etablieren, Confidence Integration, Stabilität erhöhen

### Tag 1-2: Ground Truth & Baseline (8 Stunden)

#### Task 1.1: Ground Truth Test Set erstellen (4h)
**Deliverable:** `tests/fixtures/ground_truth/`
- [ ] Erstelle 5 synthetische Test-Audiodateien:
  - `test_2speakers_clear.wav` (2 Speaker, klar, kein Overlap)
  - `test_2speakers_overlap.wav` (2 Speaker mit Überlappungen)
  - `test_3speakers_clear.wav` (3 Speaker, sequenziell)
  - `test_2speakers_noisy.wav` (2 Speaker, niedriger SNR)
  - `test_single_speaker.wav` (1 Speaker, Edge Case)
- [ ] Erstelle manuelle Annotationen im JSON-Format:
  ```json
  {
    "audio_file": "test_2speakers_clear.wav",
    "duration": 30.0,
    "speakers": ["Speaker A", "Speaker B"],
    "segments": [
      {"start": 0.0, "end": 5.0, "speaker": "Speaker A"},
      {"start": 5.5, "end": 10.0, "speaker": "Speaker B"},
      ...
    ]
  }
  ```
- [ ] Validiere Annotationen manuell (Audacity Labels Check)

#### Task 1.2: Evaluation Framework implementieren (3h)
**Deliverable:** `tests/test_diarization_accuracy.py`
- [ ] Implementiere DER (Diarization Error Rate) Berechnung:
  - False Alarm (FA): Speaker detektiert, aber keiner spricht
  - Missed Detection (MD): Speaker spricht, aber nicht detektiert
  - Speaker Error (SE): Falscher Speaker zugewiesen
  - DER = (FA + MD + SE) / Total Speech Time
- [ ] Implementiere Precision, Recall, F1 pro Speaker
- [ ] Implementiere Confusion Matrix Visualization
- [ ] Output: Detailed HTML report mit Grafiken

#### Task 1.3: Baseline-Messung durchführen (1h)
**Deliverable:** `baseline_results.json`
- [ ] Führe aktuelles System gegen Ground Truth aus
- [ ] Dokumentiere Baseline-Metriken:
  - DER: ?%
  - Speaker ID Accuracy: ?%
  - Precision/Recall/F1 pro Szenario
- [ ] Identifiziere Schwachstellen (welche Szenarien versagen?)

---

### Tag 3-4: Confidence Integration & Adaptive Alignment (7h)

#### Task 2.1: Confidence Score Extraction (2h)
**File:** `svt_core/audio/diarization.py`
- [ ] Research: Wie extrahiere ich Confidence aus pyannote.Annotation?
  - Prüfe pyannote.core.Annotation API
  - Alternative: Segmentation Model scores nutzen
- [ ] Extend `diarize()` Return-Format:
  ```python
  {
    'start': 5.2,
    'end': 7.8,
    'speaker': 'Speaker A',
    'speaker_id': 'SPEAKER_00',
    'confidence': 0.87  # NEW
  }
  ```
- [ ] Add Confidence Logging für Debugging

#### Task 2.2: Adaptive Alignment mit Confidence (2h)
**File:** `svt_core/audio/diarization.py:559-609`
- [ ] Rewrite `align_with_transcription()`:
  ```python
  def align_with_transcription(dia_segs, trans_segs):
      for trans_seg in trans_segs:
          candidates = []
          for dia_seg in dia_segs:
              overlap = calculate_overlap(trans_seg, dia_seg)
              confidence = dia_seg['confidence']
              score = 0.7 * overlap + 0.3 * confidence  # Weighted
              candidates.append((score, dia_seg))

          best = max(candidates, key=lambda x: x[0])
          trans_seg['speaker'] = best[1]['speaker']
  ```
- [ ] Unit Tests für Edge Cases:
  - Gleiche Overlaps, unterschiedliche Confidence
  - Kein Overlap, aber hohe Confidence
  - Multiple Candidates

#### Task 2.3: Re-Test gegen Ground Truth (1h)
- [ ] Führe Tests erneut aus mit neuer Alignment-Logik
- [ ] Vergleiche mit Baseline:
  - DER Verbesserung: Baseline → New
  - Speaker ID Accuracy: Baseline → New
- [ ] Dokumentiere Improvement in `results_sprint1_day4.json`

#### Task 2.4: Confidence-basierte Warnings (2h)
**File:** `output_formatter.py`
- [ ] Add Confidence Threshold Warnings:
  - Low Confidence (<0.6): `[UNSICHER:SPEAKER]` Marker
  - Medium Confidence (0.6-0.8): Gelbes Highlighting in HTML
  - High Confidence (>0.8): Grünes Highlighting
- [ ] Update Therapeutic Transcript Format:
  ```markdown
  ### **Therapeut** | 00:05 - 00:12 | ⚠️ Confidence: 0.65
  ```
- [ ] Add to JSON output: `"speaker_confidence": 0.87`

---

### Tag 5: Stabilität - HF Token & Memory Monitoring (4h)

#### Task 3.1: HF Token Pre-Validation (1h)
**File:** `svt_core/audio/diarization.py:200-224`
- [ ] Implementiere `_validate_hf_token()`:
  ```python
  def _validate_hf_token(self, token: str) -> bool:
      """Pre-validate HF token before expensive pipeline load"""
      if not token or not token.startswith('hf_'):
          return False

      try:
          import requests
          response = requests.get(
              "https://huggingface.co/api/whoami-v2",
              headers={"Authorization": f"Bearer {token}"},
              timeout=5
          )
          if response.status_code == 200:
              logger.info("✅ HF token validated successfully")
              return True
          else:
              logger.error(f"❌ HF token invalid: {response.status_code}")
              return False
      except Exception as e:
          logger.warning(f"HF token validation failed: {e}")
          return False  # Don't block on network errors
  ```
- [ ] Call in `__init__()` vor Pipeline Load
- [ ] Add user-friendly error mit Setup-Link:
  ```python
  if not self._validate_hf_token(token):
      raise ValueError(
          "Invalid HF token. Setup instructions:\n"
          "1. Create account: https://huggingface.co/join\n"
          "2. Accept agreements:\n"
          "   - https://huggingface.co/pyannote/segmentation-3.0\n"
          "   - https://huggingface.co/pyannote/speaker-diarization-3.1\n"
          "3. Create token: https://huggingface.co/settings/tokens\n"
          "4. Add to .env: HF_TOKEN=hf_YourTokenHere"
      )
  ```

#### Task 3.2: Memory Monitor Integration (2h)
**File:** `svt_core/audio/diarization.py:439-557`
- [ ] Add psutil dependency check:
  ```python
  try:
      import psutil
      PSUTIL_AVAILABLE = True
  except ImportError:
      PSUTIL_AVAILABLE = False
  ```
- [ ] Implementiere `_check_memory()` vor Diarization:
  ```python
  def _check_memory(self, audio_path: Path) -> str:
      """Check available memory and recommend mode"""
      if not PSUTIL_AVAILABLE:
          return "gpu"  # Default

      mem = psutil.virtual_memory()
      available_gb = mem.available / (1024**3)

      # Estimate memory needed (rough heuristic)
      audio_duration = librosa.get_duration(path=str(audio_path))
      estimated_mb = audio_duration * 50  # ~50MB per minute

      if mem.percent > 85:
          logger.warning(
              f"⚠️ High RAM usage: {mem.percent:.1f}% "
              f"(Available: {available_gb:.1f}GB)"
          )
          if mem.percent > 90:
              logger.warning("Switching to CPU fallback to prevent OOM")
              return "cpu"

      return "gpu" if torch.cuda.is_available() else "cpu"
  ```
- [ ] Integrate in `diarize()`:
  ```python
  recommended_device = self._check_memory(audio_path)
  if recommended_device == "cpu" and self.device.type == "cuda":
      logger.info("Auto-switching to CPU fallback due to memory constraints")
      # Use CPUDiarizer instead
  ```

#### Task 3.3: Progressive Degradation Levels (1h)
**File:** `svt_core/audio/diarization.py`
- [ ] Implementiere 3-Level Degradation:
  ```python
  class DiarizationMode(Enum):
      OPTIMAL = "pyannote.audio (GPU)"
      FALLBACK = "pyannote.audio (CPU)"
      MINIMAL = "CPU energy-based"
      NONE = "Single speaker assumption"
  ```
- [ ] Auto-Select basierend auf:
  - RAM availability (>85% → FALLBACK)
  - GPU availability (No GPU → FALLBACK)
  - HF token validity (Invalid → MINIMAL)
  - Pipeline load failure (→ MINIMAL)
  - Audio duration (>120min → MINIMAL or chunked)
- [ ] Log selected mode: `logger.info(f"Diarization mode: {mode.value}")`

---

### Tag 6-7: Speaker Embedding System Foundation (10h)

#### Task 4.1: Speaker Embedding Research & API Design (2h)
**Deliverable:** `docs/speaker_embeddings_design.md`
- [ ] Research pyannote Embedding Extraction:
  - Option 1: Extract from segmentation model
  - Option 2: Use separate `pyannote.audio.Model.from_pretrained("pyannote/embedding")`
  - Option 3: Use `pyannote.audio.pipelines.SpeakerEmbedding`
- [ ] Design Embedding Schema:
  ```python
  @dataclass
  class SpeakerEmbedding:
      speaker_id: str                    # e.g., "SPEAKER_00"
      embedding: np.ndarray              # Shape: (512,) or (768,)
      timestamp: datetime
      audio_file: str
      confidence: float
      metadata: Dict[str, Any]
  ```
- [ ] Design Database Schema (SQLite):
  ```sql
  CREATE TABLE speaker_embeddings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      speaker_label VARCHAR(255),        -- "Therapeut", "Patient A"
      embedding BLOB,                    -- Numpy array serialized
      embedding_dim INTEGER,             -- 512 or 768
      timestamp DATETIME,
      audio_file VARCHAR(512),
      segment_start FLOAT,
      segment_end FLOAT,
      confidence FLOAT,
      metadata JSON
  );

  CREATE INDEX idx_speaker_label ON speaker_embeddings(speaker_label);
  CREATE INDEX idx_timestamp ON speaker_embeddings(timestamp);
  ```

#### Task 4.2: Embedding Extraction Implementation (4h)
**File:** `svt_core/audio/speaker_embeddings.py` (NEW)
- [ ] Create new module:
  ```python
  class SpeakerEmbeddingExtractor:
      """Extract and manage speaker embeddings from audio"""

      def __init__(self, use_auth_token: str):
          self.model = Model.from_pretrained(
              "pyannote/embedding",
              token=use_auth_token
          )

      def extract_embedding(
          self,
          audio_path: Path,
          start: float,
          end: float
      ) -> np.ndarray:
          """Extract embedding for audio segment"""
          # Load audio segment
          waveform, sr = torchaudio.load(audio_path)
          segment = waveform[:, int(start*sr):int(end*sr)]

          # Extract embedding
          embedding = self.model({"waveform": segment, "sample_rate": sr})
          return embedding.numpy()

      def extract_from_diarization(
          self,
          audio_path: Path,
          diarization_segments: List[Dict]
      ) -> List[SpeakerEmbedding]:
          """Extract embeddings for all speaker segments"""
          embeddings = []

          for seg in diarization_segments:
              # Average embeddings from multiple segments per speaker
              # to get more robust representation
              emb = self.extract_embedding(
                  audio_path,
                  seg['start'],
                  seg['end']
              )

              embeddings.append(SpeakerEmbedding(
                  speaker_id=seg['speaker_id'],
                  embedding=emb,
                  timestamp=datetime.now(),
                  audio_file=str(audio_path),
                  confidence=seg.get('confidence', 1.0)
              ))

          return embeddings
  ```

#### Task 4.3: Embedding Database Layer (2h)
**File:** `svt_core/audio/speaker_embedding_db.py` (NEW)
- [ ] Implementiere CRUD Operations:
  ```python
  class SpeakerEmbeddingDB:
      """Manage speaker embeddings in SQLite database"""

      def __init__(self, db_path: Path = Path("Memory/speaker_embeddings.db")):
          self.conn = sqlite3.connect(db_path)
          self._create_tables()

      def save_embedding(self, embedding: SpeakerEmbedding):
          """Save embedding to database"""
          cursor = self.conn.cursor()
          cursor.execute("""
              INSERT INTO speaker_embeddings (
                  speaker_label, embedding, embedding_dim,
                  timestamp, audio_file, segment_start, segment_end,
                  confidence, metadata
              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          """, (
              embedding.speaker_id,
              embedding.embedding.tobytes(),
              len(embedding.embedding),
              embedding.timestamp,
              embedding.audio_file,
              0.0,  # TODO: Add segment times
              0.0,
              embedding.confidence,
              json.dumps(embedding.metadata)
          ))
          self.conn.commit()

      def get_embeddings_by_speaker(
          self,
          speaker_label: str
      ) -> List[SpeakerEmbedding]:
          """Retrieve all embeddings for a speaker"""
          cursor = self.conn.cursor()
          cursor.execute("""
              SELECT * FROM speaker_embeddings
              WHERE speaker_label = ?
              ORDER BY timestamp DESC
          """, (speaker_label,))

          results = []
          for row in cursor.fetchall():
              emb = np.frombuffer(row[2], dtype=np.float32)
              results.append(SpeakerEmbedding(
                  speaker_id=row[1],
                  embedding=emb,
                  timestamp=row[4],
                  audio_file=row[5],
                  confidence=row[8]
              ))
          return results

      def get_all_speakers(self) -> List[str]:
          """Get list of all known speakers"""
          cursor = self.conn.cursor()
          cursor.execute("""
              SELECT DISTINCT speaker_label FROM speaker_embeddings
          """)
          return [row[0] for row in cursor.fetchall()]
  ```

#### Task 4.4: Integration in Diarization Pipeline (2h)
**File:** `svt_core/audio/diarization.py`
- [ ] Add embedding extraction parameter:
  ```python
  def __init__(
      self,
      use_auth_token: str,
      enable_embedding_extraction: bool = True,  # NEW
      ...
  ):
      self.enable_embedding_extraction = enable_embedding_extraction
      if enable_embedding_extraction:
          from svt_core.audio.speaker_embeddings import SpeakerEmbeddingExtractor
          self.embedding_extractor = SpeakerEmbeddingExtractor(use_auth_token)
          self.embedding_db = SpeakerEmbeddingDB()
  ```
- [ ] Extract and save embeddings in `diarize()`:
  ```python
  def diarize(self, audio_path: Path, num_speakers: int = None):
      # ... existing diarization code ...

      segments = [...]  # Diarization results

      # Extract and save embeddings
      if self.enable_embedding_extraction:
          logger.info("Extracting speaker embeddings...")
          embeddings = self.embedding_extractor.extract_from_diarization(
              audio_path,
              segments
          )

          for emb in embeddings:
              self.embedding_db.save_embedding(emb)

          logger.info(f"Saved {len(embeddings)} speaker embeddings")

      return segments
  ```

---

## Sprint 2: Advanced Features & Performance (Week 2)

**Ziel:** Cross-Session Speaker Recognition, Speaker-Aware Whisper, Performance Optimization

### Tag 8-9: Speaker Re-Identification (8h)

#### Task 5.1: Cosine Similarity Matching (3h)
**File:** `svt_core/audio/speaker_matching.py` (NEW)
- [ ] Implementiere Speaker Matcher:
  ```python
  class SpeakerMatcher:
      """Match speakers across sessions using embeddings"""

      def __init__(self, db: SpeakerEmbeddingDB, threshold: float = 0.85):
          self.db = db
          self.threshold = threshold

      def match_speaker(
          self,
          new_embedding: np.ndarray,
          candidate_speakers: List[str] = None
      ) -> Optional[Tuple[str, float]]:
          """Match new embedding to known speakers"""
          if candidate_speakers is None:
              candidate_speakers = self.db.get_all_speakers()

          best_match = None
          best_score = -1

          for speaker_label in candidate_speakers:
              known_embeddings = self.db.get_embeddings_by_speaker(speaker_label)

              # Average embeddings for robust matching
              avg_embedding = np.mean([e.embedding for e in known_embeddings], axis=0)

              # Cosine similarity
              similarity = np.dot(new_embedding, avg_embedding) / (
                  np.linalg.norm(new_embedding) * np.linalg.norm(avg_embedding)
              )

              if similarity > best_score:
                  best_score = similarity
                  best_match = speaker_label

          if best_score >= self.threshold:
              return (best_match, best_score)
          else:
              return None  # No match found
  ```

#### Task 5.2: Cross-Session Tests (2h)
**File:** `tests/test_speaker_reidentification.py` (NEW)
- [ ] Create test with same synthetic speakers:
  - Session 1: Speaker A + B (save embeddings)
  - Session 2: Speaker A + C (should recognize A)
  - Session 3: Speaker B + C (should recognize B)
- [ ] Test edge cases:
  - Very similar voices (low similarity threshold)
  - Different recording conditions (noise, microphone)
  - Long time gap between sessions
- [ ] Measure Re-ID Accuracy:
  - True Positive Rate (correct re-identifications)
  - False Positive Rate (wrong re-identifications)
  - False Negative Rate (missed re-identifications)

#### Task 5.3: Integration in SVT Pipeline (3h)
**File:** `auto_transcriber_v4_emotion.py`
- [ ] Add speaker matching step:
  ```python
  def transcribe_with_speaker_matching(
      audio_path: Path,
      enable_speaker_matching: bool = True
  ):
      # Step 1: Diarization (extracts embeddings)
      diarizer = SpeakerDiarizer(...)
      segments = diarizer.diarize(audio_path)

      # Step 2: Match speakers to known profiles
      if enable_speaker_matching:
          matcher = SpeakerMatcher(diarizer.embedding_db)

          for seg in segments:
              embedding = get_embedding_for_segment(seg)  # Helper
              match = matcher.match_speaker(embedding)

              if match:
                  speaker_label, confidence = match
                  seg['matched_speaker'] = speaker_label
                  seg['match_confidence'] = confidence
                  logger.info(
                      f"✅ Matched {seg['speaker']} → {speaker_label} "
                      f"(confidence: {confidence:.2f})"
                  )
              else:
                  seg['matched_speaker'] = None
                  logger.info(f"ℹ️ No match found for {seg['speaker']}")

      return segments
  ```
- [ ] Update output formatter to use matched names:
  ```python
  # In therapeutic transcript
  if seg.get('matched_speaker'):
      speaker_name = seg['matched_speaker']
  else:
      speaker_name = seg['speaker']  # Fallback to A, B, C
  ```

---

### Tag 10-11: Adaptive OSD & Speaker-Aware Whisper (8h)

#### Task 6.1: SNR-based OSD Threshold Tuning (2h)
**File:** `svt_core/audio/diarization.py:366-437`
- [ ] Extend `detect_overlapped_speech()` with adaptive thresholds:
  ```python
  def detect_overlapped_speech(
      self,
      audio_path: Path,
      auto_tune_thresholds: bool = True  # NEW
  ):
      # Analyze audio quality
      if auto_tune_thresholds:
          from audio_quality_analyzer import AudioQualityAnalyzer
          analyzer = AudioQualityAnalyzer()
          quality = analyzer.analyze(audio_path)

          # Adjust thresholds based on SNR
          if quality['snr'] > 20:  # High quality
              onset = 0.5
              offset = 0.5
          elif quality['snr'] > 10:  # Medium quality
              onset = 0.6
              offset = 0.4
          else:  # Low quality (noisy)
              onset = 0.7
              offset = 0.3

          logger.info(
              f"Auto-tuned OSD thresholds based on SNR {quality['snr']:.1f}dB: "
              f"onset={onset}, offset={offset}"
          )
      else:
          onset = 0.5  # Default
          offset = 0.5

      # ... rest of OSD code with tuned thresholds ...
  ```

#### Task 6.2: Speaker-Aware Whisper Prompting (4h)
**File:** `auto_transcriber_v4_emotion.py`
- [ ] Load speaker characteristics from Memory:
  ```python
  def load_speaker_context(speaker_label: str) -> str:
      """Load speaker profile and build context prompt"""
      profile_path = Path(f"Memory/{speaker_label}.yaml")

      if not profile_path.exists():
          return ""  # No context available

      with open(profile_path) as f:
          profile = yaml.safe_load(f)

      # Build context string
      context_parts = []

      if 'characteristics' in profile:
          context_parts.append(f"Speaking style: {', '.join(profile['characteristics'])}")

      if 'topics' in profile:
          top_topics = sorted(profile['topics'].items(), key=lambda x: x[1], reverse=True)[:3]
          context_parts.append(f"Common topics: {', '.join([t[0] for t in top_topics])}")

      return " | ".join(context_parts)
  ```
- [ ] Pass context to Whisper:
  ```python
  def transcribe_segment_with_context(
      audio_path: Path,
      start: float,
      end: float,
      speaker_label: str,
      model
  ):
      # Extract segment
      segment_audio = extract_audio_segment(audio_path, start, end)

      # Build initial prompt with speaker context
      context = load_speaker_context(speaker_label)
      initial_prompt = f"[{speaker_label}] {context}" if context else None

      # Transcribe with context
      result = model.transcribe(
          segment_audio,
          initial_prompt=initial_prompt,
          language='de'  # Or auto-detect
      )

      logger.debug(f"Transcribed {speaker_label} with context: {context}")

      return result
  ```
- [ ] A/B Testing:
  - Run same audio with/without context
  - Measure WER difference
  - Log results to `speaker_context_impact.json`

#### Task 6.3: Overlap Region Handling (2h)
**File:** `auto_transcriber_v4_emotion.py`
- [ ] Detect overlap regions from OSD:
  ```python
  def handle_overlapped_regions(
      audio_path: Path,
      transcription_segments: List[Dict],
      overlap_regions: List[Dict]
  ):
      """Re-transcribe overlapped regions separately per speaker"""

      for overlap in overlap_regions:
          # Find which speakers are in this overlap
          overlapping_segments = [
              seg for seg in transcription_segments
              if segments_overlap(seg, overlap)
          ]

          speakers_in_overlap = set(seg['speaker'] for seg in overlapping_segments)

          if len(speakers_in_overlap) > 1:
              logger.info(
                  f"Overlap detected at {overlap['start']:.1f}s: "
                  f"{len(speakers_in_overlap)} speakers"
              )

              # TODO: Advanced - Source separation per speaker
              # For now: Mark as [ÜBERLAPPUNG] and keep original transcription
              for seg in overlapping_segments:
                  seg['overlap_detected'] = True
                  seg['overlap_duration'] = overlap['duration']
  ```

---

### Tag 12-13: Performance Optimization (8h)

#### Task 7.1: Model Pre-Caching Setup (2h)
**File:** `svt_core/audio/download_models.py` (NEW)
- [ ] Create model download script:
  ```python
  #!/usr/bin/env python3
  """Pre-download pyannote models to cache"""

  import os
  from pathlib import Path
  from pyannote.audio import Pipeline, Model

  def download_models(hf_token: str = None):
      """Download all required models"""

      if hf_token is None:
          hf_token = os.getenv('HF_TOKEN')

      if not hf_token:
          print("⚠️ HF_TOKEN not set. Set in .env or pass as argument")
          return False

      models = [
          "pyannote/speaker-diarization-3.1",
          "pyannote/segmentation-3.0",
          "pyannote/embedding"
      ]

      for model_name in models:
          print(f"Downloading {model_name}...")
          try:
              if "diarization" in model_name:
                  Pipeline.from_pretrained(model_name, token=hf_token)
              else:
                  Model.from_pretrained(model_name, token=hf_token)

              print(f"✅ {model_name} downloaded")
          except Exception as e:
              print(f"❌ Failed to download {model_name}: {e}")
              return False

      print("\n✅ All models downloaded successfully!")
      return True

  if __name__ == "__main__":
      import sys
      token = sys.argv[1] if len(sys.argv) > 1 else None
      download_models(token)
  ```
- [ ] Update `INSTALLATION.md`:
  ```bash
  # After installing requirements
  python3 -m svt_core.audio.download_models
  ```
- [ ] Add to `svt_core/health_check.py`:
  ```python
  def check_models_cached() -> bool:
      """Check if models are cached locally"""
      cache_dir = Path.home() / ".cache" / "torch" / "pyannote"
      return cache_dir.exists() and len(list(cache_dir.glob("*"))) >= 3
  ```

#### Task 7.2: Chunked Processing für lange Audio (4h)
**File:** `svt_core/audio/chunked_diarization.py` (NEW)
- [ ] Implementiere Chunking Strategy:
  ```python
  class ChunkedDiarizer:
      """Diarize very long audio by chunking"""

      def __init__(
          self,
          diarizer: SpeakerDiarizer,
          chunk_duration: float = 900.0,  # 15 minutes
          overlap: float = 30.0            # 30 seconds overlap
      ):
          self.diarizer = diarizer
          self.chunk_duration = chunk_duration
          self.overlap = overlap

      def diarize_chunked(
          self,
          audio_path: Path
      ) -> List[Dict[str, Any]]:
          """Diarize audio in chunks and merge results"""

          # Get audio duration
          import librosa
          duration = librosa.get_duration(path=str(audio_path))

          if duration <= self.chunk_duration:
              # No chunking needed
              return self.diarizer.diarize(audio_path)

          logger.info(
              f"Audio duration {duration/60:.1f}min exceeds chunk size. "
              f"Processing in chunks of {self.chunk_duration/60:.1f}min..."
          )

          # Split into chunks
          chunks = []
          start = 0
          chunk_idx = 0

          while start < duration:
              end = min(start + self.chunk_duration, duration)

              # Extract chunk
              chunk_path = self._extract_chunk(
                  audio_path,
                  start,
                  end,
                  chunk_idx
              )

              # Diarize chunk
              chunk_segments = self.diarizer.diarize(chunk_path)

              # Adjust timestamps
              for seg in chunk_segments:
                  seg['start'] += start
                  seg['end'] += start

              chunks.append({
                  'chunk_idx': chunk_idx,
                  'start': start,
                  'end': end,
                  'segments': chunk_segments
              })

              # Move to next chunk (with overlap)
              start = end - self.overlap
              chunk_idx += 1

          # Merge chunks
          merged_segments = self._merge_chunks(chunks)

          logger.info(
              f"Chunked diarization complete: {len(chunks)} chunks, "
              f"{len(merged_segments)} total segments"
          )

          return merged_segments

      def _merge_chunks(self, chunks: List[Dict]) -> List[Dict]:
          """Merge overlapping chunk segments using speaker embeddings"""

          all_segments = []

          for chunk in chunks:
              all_segments.extend(chunk['segments'])

          # Sort by time
          all_segments.sort(key=lambda x: x['start'])

          # TODO: Advanced - Use speaker embeddings to merge
          # same speakers across chunks
          # For now: Simple time-based merge

          return all_segments
  ```

#### Task 7.3: Batch GPU Processing (2h)
**File:** `svt_core/audio/batch_diarizer.py` (NEW)
- [ ] Implementiere Batch Processing:
  ```python
  class BatchDiarizer:
      """Process multiple short audio files in batches"""

      def __init__(self, diarizer: SpeakerDiarizer, batch_size: int = 4):
          self.diarizer = diarizer
          self.batch_size = batch_size

      def diarize_batch(
          self,
          audio_files: List[Path]
      ) -> Dict[Path, List[Dict]]:
          """Diarize multiple files efficiently"""

          results = {}

          # Group by duration (process similar lengths together)
          grouped = self._group_by_duration(audio_files)

          for duration_bucket, files in grouped.items():
              logger.info(
                  f"Processing {len(files)} files of ~{duration_bucket}s duration"
              )

              # Process in batches
              for i in range(0, len(files), self.batch_size):
                  batch = files[i:i+self.batch_size]

                  # TODO: Parallel processing on GPU
                  # For now: Sequential
                  for audio_file in batch:
                      results[audio_file] = self.diarizer.diarize(audio_file)

          return results
  ```

---

### Tag 14: Testing & Documentation (4h)

#### Task 8.1: End-to-End Integration Tests (2h)
**File:** `tests/test_e2e_speaker_separation.py` (NEW)
- [ ] Test complete pipeline:
  - Diarization → Embedding Extraction → Speaker Matching → Whisper → Output
- [ ] Test all degradation levels:
  - Optimal (GPU + HF Token)
  - Fallback (CPU)
  - Minimal (Energy-based)
- [ ] Test cross-session recognition:
  - Session 1: Extract embeddings
  - Session 2: Match speakers
  - Validate: Correct re-identification

#### Task 8.2: Performance Benchmarking (1h)
**File:** `benchmark_speaker_separation.py` (NEW)
- [ ] Measure:
  - Diarization speed (Realtime Factor)
  - Memory usage (peak RAM)
  - Accuracy metrics (DER, F1)
- [ ] Compare:
  - Baseline vs. Sprint 1 improvements
  - GPU vs. CPU performance
  - Chunked vs. full processing

#### Task 8.3: Documentation Updates (1h)
- [ ] Update `SPEAKER_DIARIZATION.md`:
  - Add speaker embedding section
  - Add cross-session recognition guide
  - Add performance tuning tips
- [ ] Update `CLAUDE.md`:
  - Document new features
  - Update architecture diagram
- [ ] Update `INSTALLATION.md`:
  - Add model pre-download step
- [ ] Create `SPEAKER_EMBEDDINGS_GUIDE.md`:
  - Explain embedding system
  - Usage examples
  - Troubleshooting

---

## Success Criteria

### Sprint 1 (Week 1):
- [ ] DER measured and < 15% on ground truth
- [ ] Confidence scores integrated and logged
- [ ] HF Token validation working
- [ ] Memory monitor preventing OOM
- [ ] Speaker embeddings extracting and saving
- [ ] All tests passing

### Sprint 2 (Week 2):
- [ ] Cross-session Re-ID accuracy > 70%
- [ ] Speaker-aware Whisper showing +3% WER improvement
- [ ] Chunked processing working for 120min audio
- [ ] Model pre-download script working
- [ ] Full E2E tests passing
- [ ] Documentation complete

---

## Rollback Plan

If critical issues arise:
1. **Branch Protection:** All work on feature branch `claude/test-speaker-separation-*`
2. **Backward Compatibility:** Keep deprecated `speaker_diarizer.py` wrapper
3. **Feature Flags:** All new features optional (enable_embedding_extraction, enable_speaker_matching)
4. **Fallback Modes:** System continues without new features if they fail

---

**Next Step:** Start Sprint 1, Tag 1 - Ground Truth Test Set Creation
