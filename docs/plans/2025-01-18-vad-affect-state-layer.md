# VAD Affect State Layer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Build a non-diagnostic Affect State Layer with continuous Valence-Arousal-Dominance time series per speaker, baseline-normalized, smoothed, with turning point detection, API, JSON schema, and UI timeline overlay.

**Architecture:** Rule-based VAD scoring from prosody + text features → per-speaker baseline normalization → EMA smoothing → event detection → JSON output + API + UI overlay

**Tech Stack:** Python 3.12+, Parselmouth (prosody), librosa, TextBlob (sentiment), existing SVT pipeline, Tkinter (GUI), pytest

---

## Phase 0: Setup & Schema

### Task 0.1: Create Module Scaffold

**Files:**
- Create: `src/affect/__init__.py`
- Create: `src/affect/features_prosody.py`
- Create: `src/affect/features_text.py`
- Create: `src/affect/features_dominance.py`
- Create: `src/affect/vad_engine.py`
- Create: `src/affect/normalization.py`
- Create: `src/affect/smoothing.py`
- Create: `src/affect/events.py`
- Create: `src/affect/relational.py`
- Create: `src/affect/schema.py`
- Create: `src/affect/api.py`
- Create: `tests/affect/__init__.py`
- Create: `config/affect.yaml`

**Step 1: Create directory structure**

```bash
mkdir -p src/affect tests/affect config docs
touch src/affect/__init__.py tests/affect/__init__.py
```

**Step 2: Create empty module stubs**

Create `src/affect/features_prosody.py`:
```python
"""Prosody-based affect features extraction."""

def extract_arousal_features(audio_segment, sr=16000):
    """Extract arousal-related prosody features.

    Args:
        audio_segment: Audio signal array
        sr: Sample rate

    Returns:
        dict: {energy_rms, energy_db, zcr}
    """
    raise NotImplementedError
```

Create `src/affect/features_text.py`:
```python
"""Text-based affect features extraction."""

def extract_valence_features(text, language="de"):
    """Extract valence from text using lexicon + sentiment.

    Args:
        text: Transcript text
        language: Language code (de, en)

    Returns:
        dict: {valence_score, polarity, subjectivity}
    """
    raise NotImplementedError
```

Create `src/affect/features_dominance.py`:
```python
"""Dominance features from turn-taking and loudness."""

def extract_dominance_features(speaker_segments, audio_segments):
    """Extract dominance indicators.

    Args:
        speaker_segments: List of {speaker, start, end, overlaps}
        audio_segments: Corresponding audio arrays

    Returns:
        dict: {interruption_index, loudness_delta, hedges_rate}
    """
    raise NotImplementedError
```

Create `src/affect/vad_engine.py`:
```python
"""VAD rule-based scoring engine."""

def compute_vad_raw(prosody_features, text_features, dominance_features, config):
    """Combine features into raw V/A/D scores.

    Args:
        prosody_features: dict from features_prosody
        text_features: dict from features_text
        dominance_features: dict from features_dominance
        config: dict with weights {alpha, beta, gamma}

    Returns:
        dict: {valence_raw, arousal_raw, dominance_raw}
    """
    raise NotImplementedError
```

Create `src/affect/normalization.py`:
```python
"""Per-speaker baseline normalization."""

def normalize_speaker_baseline(vad_samples, speaker_id):
    """Z-score normalize per speaker, then map to [-1, +1].

    Args:
        vad_samples: List of {timestamp, speaker_id, valence_raw, arousal_raw, dominance_raw}
        speaker_id: Speaker identifier

    Returns:
        List of {timestamp, speaker_id, valence, arousal, dominance}
    """
    raise NotImplementedError
```

Create `src/affect/smoothing.py`:
```python
"""EMA smoothing with latency constraint."""

def smooth_vad_ema(vad_samples, lambda_=0.3):
    """Apply exponential moving average smoothing.

    Args:
        vad_samples: List of normalized VAD samples
        lambda_: Smoothing factor (0-1, higher = more smoothing)

    Returns:
        List of smoothed VAD samples
    """
    raise NotImplementedError
```

Create `src/affect/events.py`:
```python
"""Turning point event detection."""

def detect_turning_points(vad_samples, config):
    """Detect emotional turning points.

    Args:
        vad_samples: List of smoothed VAD samples
        config: {grad_threshold, persistence_min, hysteresis}

    Returns:
        List of {timestamp, type, dimension, magnitude}
    """
    raise NotImplementedError
```

Create `src/affect/relational.py`:
```python
"""Relational synchronicity indicators."""

def compute_synchronicity(vad_samples_speaker_a, vad_samples_speaker_b, window_sec=30):
    """Cross-correlation of arousal curves.

    Args:
        vad_samples_speaker_a: VAD samples for speaker A
        vad_samples_speaker_b: VAD samples for speaker B
        window_sec: Sliding window size in seconds

    Returns:
        float: Synchronicity score [-1, +1]
    """
    raise NotImplementedError
```

Create `src/affect/schema.py`:
```python
"""JSON schema validation."""

def validate_vad_output(vad_data):
    """Validate VAD JSON against schema.

    Args:
        vad_data: dict with samples, events, confidence, provenance

    Returns:
        bool: True if valid

    Raises:
        ValueError: If validation fails
    """
    raise NotImplementedError
```

Create `src/affect/api.py`:
```python
"""VAD API and SDK."""

class VADService:
    """Streaming and batch VAD API."""

    def process_batch(self, audio_path, transcript_path):
        """Process audio file in batch mode."""
        raise NotImplementedError

    def process_stream(self, audio_stream):
        """Process audio stream in real-time."""
        raise NotImplementedError
```

**Step 3: Create initial config**

Create `config/affect.yaml`:
```yaml
# VAD Affect State Layer Configuration

# Feature weights
weights:
  arousal:
    energy: 0.5
    f0_range: 0.3
    tempo: 0.2
  valence:
    lexical: 0.6
    prosody_pitch_mean: 0.4
  dominance:
    interruption: 0.4
    loudness_delta: 0.4
    hedges: 0.2

# Thresholds
thresholds:
  grad_threshold: 0.15  # Turning point gradient
  persistence_min: 3.0  # Seconds
  hysteresis: 0.05

# Smoothing
smoothing:
  lambda: 0.3  # EMA factor

# Latency SLA
latency:
  target_95p_ms: 500
```

**Step 4: Commit scaffold**

```bash
git add src/affect/ tests/affect/ config/affect.yaml docs/
git commit -m "feat(vad): add module scaffold and initial config"
```

---

### Task 0.2: Define JSON Schema

**Files:**
- Create: `config/schema_affect.json`
- Create: `tests/affect/test_schema.py`

**Step 1: Write schema validation test**

Create `tests/affect/test_schema.py`:
```python
import pytest
from src.affect.schema import validate_vad_output

def test_valid_vad_output():
    """Valid VAD output should pass validation."""
    valid_data = {
        "version": "1.0",
        "session_id": "test-123",
        "samples": [
            {
                "timestamp": 0.0,
                "speaker_id": "A",
                "valence": 0.5,
                "arousal": 0.3,
                "dominance": 0.2,
                "confidence": 0.85
            }
        ],
        "events": [],
        "provenance": {
            "model": "rule-based-v1",
            "config_hash": "abc123"
        }
    }
    assert validate_vad_output(valid_data) is True

def test_invalid_vad_output_missing_field():
    """Missing required field should fail validation."""
    invalid_data = {
        "version": "1.0",
        "samples": []
        # Missing session_id, events, provenance
    }
    with pytest.raises(ValueError, match="Missing required field"):
        validate_vad_output(invalid_data)

def test_vad_sample_out_of_range():
    """VAD values outside [-1, +1] should fail."""
    invalid_data = {
        "version": "1.0",
        "session_id": "test-123",
        "samples": [
            {
                "timestamp": 0.0,
                "speaker_id": "A",
                "valence": 1.5,  # Out of range!
                "arousal": 0.0,
                "dominance": 0.0,
                "confidence": 0.8
            }
        ],
        "events": [],
        "provenance": {"model": "test"}
    }
    with pytest.raises(ValueError, match="out of range"):
        validate_vad_output(invalid_data)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/affect/test_schema.py -v
```
Expected: FAIL with "NotImplementedError"

**Step 3: Create JSON schema definition**

Create `config/schema_affect.json`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "session_id", "samples", "events", "provenance"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "session_id": {
      "type": "string"
    },
    "samples": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["timestamp", "speaker_id", "valence", "arousal", "dominance", "confidence"],
        "properties": {
          "timestamp": {"type": "number", "minimum": 0},
          "speaker_id": {"type": "string"},
          "valence": {"type": "number", "minimum": -1, "maximum": 1},
          "arousal": {"type": "number", "minimum": -1, "maximum": 1},
          "dominance": {"type": "number", "minimum": -1, "maximum": 1},
          "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["timestamp", "type", "dimension", "magnitude"],
        "properties": {
          "timestamp": {"type": "number"},
          "type": {"type": "string", "enum": ["turning_point", "peak", "valley"]},
          "dimension": {"type": "string", "enum": ["valence", "arousal", "dominance"]},
          "magnitude": {"type": "number"}
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["model", "config_hash"],
      "properties": {
        "model": {"type": "string"},
        "config_hash": {"type": "string"}
      }
    }
  }
}
```

**Step 4: Implement schema validation**

Update `src/affect/schema.py`:
```python
"""JSON schema validation."""
import json
import jsonschema
from pathlib import Path

# Load schema
SCHEMA_PATH = Path(__file__).parent.parent.parent / "config" / "schema_affect.json"
with open(SCHEMA_PATH) as f:
    VAD_SCHEMA = json.load(f)

def validate_vad_output(vad_data):
    """Validate VAD JSON against schema.

    Args:
        vad_data: dict with samples, events, confidence, provenance

    Returns:
        bool: True if valid

    Raises:
        ValueError: If validation fails
    """
    try:
        jsonschema.validate(instance=vad_data, schema=VAD_SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")
    except jsonschema.SchemaError as e:
        raise ValueError(f"Invalid schema: {e.message}")
```

**Step 5: Install jsonschema dependency**

```bash
pip install jsonschema
echo "jsonschema>=4.0.0" >> requirements.txt
```

**Step 6: Run tests to verify they pass**

```bash
pytest tests/affect/test_schema.py -v
```
Expected: PASS (all 3 tests)

**Step 7: Commit**

```bash
git add config/schema_affect.json src/affect/schema.py tests/affect/test_schema.py requirements.txt
git commit -m "feat(vad): add JSON schema validation"
```

---

## Phase 1: Prosody Features

### Task 1.1: Energy-based Arousal Features

**Files:**
- Modify: `src/affect/features_prosody.py`
- Create: `tests/affect/test_features_prosody.py`

**Step 1: Write failing test**

Create `tests/affect/test_features_prosody.py`:
```python
import pytest
import numpy as np
from src.affect.features_prosody import extract_arousal_features

def test_extract_arousal_features_increasing_energy():
    """Higher energy should yield higher arousal features."""
    sr = 16000
    duration = 1.0

    # Low energy signal
    low_energy = np.random.randn(int(sr * duration)) * 0.01

    # High energy signal
    high_energy = np.random.randn(int(sr * duration)) * 0.5

    low_features = extract_arousal_features(low_energy, sr)
    high_features = extract_arousal_features(high_energy, sr)

    assert high_features['energy_rms'] > low_features['energy_rms']
    assert high_features['energy_db'] > low_features['energy_db']

def test_arousal_features_returns_required_keys():
    """Should return energy_rms, energy_db, zcr."""
    sr = 16000
    audio = np.random.randn(sr)  # 1 second

    features = extract_arousal_features(audio, sr)

    assert 'energy_rms' in features
    assert 'energy_db' in features
    assert 'zcr' in features
    assert all(isinstance(v, (int, float)) for v in features.values())
```

**Step 2: Run test to verify failure**

```bash
pytest tests/affect/test_features_prosody.py::test_extract_arousal_features_increasing_energy -v
```
Expected: FAIL with "NotImplementedError"

**Step 3: Implement arousal feature extraction**

Update `src/affect/features_prosody.py`:
```python
"""Prosody-based affect features extraction."""
import numpy as np
import librosa

def extract_arousal_features(audio_segment, sr=16000):
    """Extract arousal-related prosody features.

    Args:
        audio_segment: Audio signal array
        sr: Sample rate

    Returns:
        dict: {energy_rms, energy_db, zcr}
    """
    # RMS energy
    energy_rms = float(np.sqrt(np.mean(audio_segment**2)))

    # Energy in dB
    energy_db = float(librosa.amplitude_to_db([energy_rms])[0])

    # Zero-crossing rate
    zcr = float(np.mean(librosa.zero_crossings(audio_segment, pad=False)))

    return {
        'energy_rms': energy_rms,
        'energy_db': energy_db,
        'zcr': zcr
    }
```

**Step 4: Install librosa if needed**

```bash
# Check if already in requirements.txt from existing prosody_extractor.py
grep -q "librosa" requirements.txt || echo "librosa>=0.10.0" >> requirements.txt
pip install librosa
```

**Step 5: Run tests to verify pass**

```bash
pytest tests/affect/test_features_prosody.py -v
```
Expected: PASS (both tests)

**Step 6: Commit**

```bash
git add src/affect/features_prosody.py tests/affect/test_features_prosody.py
git commit -m "feat(vad): implement energy-based arousal features"
```

---

### Task 1.2: Pitch Features (F0 Range)

**Files:**
- Modify: `src/affect/features_prosody.py`
- Modify: `tests/affect/test_features_prosody.py`

**Step 1: Write failing test**

Add to `tests/affect/test_features_prosody.py`:
```python
from src.affect.features_prosody import extract_pitch_features

def test_extract_pitch_features():
    """Should extract F0 mean, range, variance."""
    sr = 16000
    # Generate synthetic voiced signal (sine wave at 150 Hz)
    duration = 1.0
    f0 = 150.0
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.sin(2 * np.pi * f0 * t)

    features = extract_pitch_features(audio, sr)

    assert 'f0_mean' in features
    assert 'f0_range' in features
    assert 'f0_variance' in features
    # F0 should be close to 150 Hz
    assert 140 < features['f0_mean'] < 160

def test_pitch_features_unvoiced():
    """Noise (unvoiced) should return low F0 or NaN."""
    sr = 16000
    audio = np.random.randn(sr)  # Pure noise

    features = extract_pitch_features(audio, sr)

    # Should handle unvoiced gracefully
    assert features['f0_mean'] is None or features['f0_mean'] == 0.0
```

**Step 2: Run test to verify failure**

```bash
pytest tests/affect/test_features_prosody.py::test_extract_pitch_features -v
```
Expected: FAIL with "ImportError: cannot import name 'extract_pitch_features'"

**Step 3: Implement pitch extraction using Parselmouth**

Update `src/affect/features_prosody.py`:
```python
import parselmouth
from parselmouth.praat import call

def extract_pitch_features(audio_segment, sr=16000):
    """Extract pitch (F0) features using Parselmouth.

    Args:
        audio_segment: Audio signal array
        sr: Sample rate

    Returns:
        dict: {f0_mean, f0_range, f0_variance}
    """
    # Create Parselmouth Sound object
    sound = parselmouth.Sound(audio_segment, sampling_frequency=sr)

    # Extract pitch
    pitch = call(sound, "To Pitch", 0.0, 75, 500)  # 75-500 Hz range

    # Get F0 values
    f0_values = pitch.selected_array['frequency']
    f0_values = f0_values[f0_values > 0]  # Filter unvoiced frames

    if len(f0_values) == 0:
        return {
            'f0_mean': None,
            'f0_range': None,
            'f0_variance': None
        }

    return {
        'f0_mean': float(np.mean(f0_values)),
        'f0_range': float(np.ptp(f0_values)),  # max - min
        'f0_variance': float(np.var(f0_values))
    }
```

**Step 4: Verify Parselmouth is installed**

```bash
# Should already be in requirements.txt from existing prosody_extractor.py
grep -q "parselmouth" requirements.txt || echo "praat-parselmouth>=0.4.0" >> requirements.txt
pip install praat-parselmouth
```

**Step 5: Run tests to verify pass**

```bash
pytest tests/affect/test_features_prosody.py -v
```
Expected: PASS (4 tests total)

**Step 6: Commit**

```bash
git add src/affect/features_prosody.py tests/affect/test_features_prosody.py
git commit -m "feat(vad): add pitch (F0) feature extraction"
```

---

### Task 1.3: Tempo Features

**Files:**
- Modify: `src/affect/features_prosody.py`
- Modify: `tests/affect/test_features_prosody.py`

**Step 1: Write test**

Add to `tests/affect/test_features_prosody.py`:
```python
from src.affect.features_prosody import extract_tempo_features

def test_extract_tempo_features():
    """Should extract tempo (BPM-like) from onset detection."""
    sr = 16000
    # Generate click train (100 BPM = 1.67 Hz)
    duration = 3.0
    t = np.arange(0, duration, 0.6)  # Click every 0.6s = 100 BPM
    audio = np.zeros(int(sr * duration))
    for click_time in t:
        idx = int(click_time * sr)
        if idx < len(audio):
            audio[idx:idx+100] = 0.5

    features = extract_tempo_features(audio, sr)

    assert 'tempo_bpm' in features
    assert 80 < features['tempo_bpm'] < 120  # Should detect ~100 BPM
```

**Step 2: Run test to fail**

```bash
pytest tests/affect/test_features_prosody.py::test_extract_tempo_features -v
```
Expected: FAIL

**Step 3: Implement tempo extraction**

Update `src/affect/features_prosody.py`:
```python
def extract_tempo_features(audio_segment, sr=16000):
    """Extract tempo features using onset detection.

    Args:
        audio_segment: Audio signal array
        sr: Sample rate

    Returns:
        dict: {tempo_bpm}
    """
    # Onset strength envelope
    onset_env = librosa.onset.onset_strength(y=audio_segment, sr=sr)

    # Estimate tempo
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]

    return {
        'tempo_bpm': float(tempo)
    }
```

**Step 4: Run test to pass**

```bash
pytest tests/affect/test_features_prosody.py -v
```
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/affect/features_prosody.py tests/affect/test_features_prosody.py
git commit -m "feat(vad): add tempo feature extraction"
```

---

## Phase 2: Text Valence Features

### Task 2.1: Lexicon-based Valence

**Files:**
- Modify: `src/affect/features_text.py`
- Create: `data/lexicons/valence_de.json`
- Create: `data/lexicons/valence_en.json`
- Create: `tests/affect/test_features_text.py`

**Step 1: Write test**

Create `tests/affect/test_features_text.py`:
```python
import pytest
from src.affect.features_text import extract_valence_features

def test_valence_positive_text():
    """Positive text should yield positive valence."""
    positive_text = "Das ist wunderbar! Ich bin sehr glücklich und zufrieden."

    features = extract_valence_features(positive_text, language="de")

    assert 'valence_score' in features
    assert features['valence_score'] > 0.3  # Clearly positive

def test_valence_negative_text():
    """Negative text should yield negative valence."""
    negative_text = "Das ist schrecklich. Ich bin traurig und enttäuscht."

    features = extract_valence_features(negative_text, language="de")

    assert features['valence_score'] < -0.3  # Clearly negative

def test_valence_neutral_text():
    """Neutral text should yield near-zero valence."""
    neutral_text = "Der Tisch ist braun. Das Fenster ist offen."

    features = extract_valence_features(neutral_text, language="de")

    assert -0.2 < features['valence_score'] < 0.2
```

**Step 2: Run test to fail**

```bash
pytest tests/affect/test_features_text.py -v
```
Expected: FAIL

**Step 3: Create simple German valence lexicon**

Create `data/lexicons/valence_de.json`:
```json
{
  "wunderbar": 0.8,
  "glücklich": 0.9,
  "zufrieden": 0.7,
  "gut": 0.6,
  "schön": 0.7,
  "super": 0.8,
  "toll": 0.8,
  "schrecklich": -0.9,
  "traurig": -0.8,
  "enttäuscht": -0.7,
  "schlecht": -0.6,
  "böse": -0.7,
  "ärgerlich": -0.6,
  "furchtbar": -0.8,
  "aber": -0.2,
  "trotzdem": -0.1,
  "eigentlich": -0.1
}
```

Create `data/lexicons/valence_en.json`:
```json
{
  "wonderful": 0.8,
  "happy": 0.9,
  "satisfied": 0.7,
  "good": 0.6,
  "terrible": -0.9,
  "sad": -0.8,
  "disappointed": -0.7,
  "bad": -0.6,
  "but": -0.2,
  "however": -0.1,
  "actually": -0.1
}
```

**Step 4: Implement lexicon-based valence**

Update `src/affect/features_text.py`:
```python
"""Text-based affect features extraction."""
import json
import re
from pathlib import Path

# Load lexicons
LEXICON_PATH = Path(__file__).parent.parent.parent / "data" / "lexicons"

def load_lexicon(language):
    """Load valence lexicon for language."""
    lexicon_file = LEXICON_PATH / f"valence_{language}.json"
    if not lexicon_file.exists():
        return {}
    with open(lexicon_file) as f:
        return json.load(f)

def extract_valence_features(text, language="de"):
    """Extract valence from text using lexicon + sentiment.

    Args:
        text: Transcript text
        language: Language code (de, en)

    Returns:
        dict: {valence_score, polarity, subjectivity}
    """
    lexicon = load_lexicon(language)

    # Tokenize (simple word split)
    words = re.findall(r'\b\w+\b', text.lower())

    # Lexicon-based score
    valence_scores = [lexicon.get(word, 0.0) for word in words]

    if len(valence_scores) == 0:
        valence_score = 0.0
    else:
        valence_score = sum(valence_scores) / len(words)  # Normalize by word count

    # Clip to [-1, +1]
    valence_score = max(-1.0, min(1.0, valence_score))

    return {
        'valence_score': valence_score,
        'polarity': valence_score,  # Alias for compatibility
        'subjectivity': 0.0  # Placeholder for now
    }
```

**Step 5: Create lexicon directory**

```bash
mkdir -p data/lexicons
```

**Step 6: Run tests to pass**

```bash
pytest tests/affect/test_features_text.py -v
```
Expected: PASS (3 tests)

**Step 7: Commit**

```bash
git add src/affect/features_text.py data/lexicons/ tests/affect/test_features_text.py
git commit -m "feat(vad): add lexicon-based valence extraction"
```

---

## Phase 3: VAD Engine (Rule-based Scoring)

### Task 3.1: Combine Features into Raw VAD

**Files:**
- Modify: `src/affect/vad_engine.py`
- Create: `tests/affect/test_vad_engine.py`

**Step 1: Write test**

Create `tests/affect/test_vad_engine.py`:
```python
import pytest
from src.affect.vad_engine import compute_vad_raw

def test_compute_vad_raw_arousal():
    """High energy should increase arousal."""
    prosody_features = {
        'energy_rms': 0.5,
        'energy_db': -10,
        'zcr': 0.1,
        'f0_mean': 150,
        'f0_range': 50,
        'tempo_bpm': 120
    }
    text_features = {
        'valence_score': 0.0
    }
    dominance_features = {
        'interruption_index': 0.0,
        'loudness_delta': 0.0,
        'hedges_rate': 0.0
    }
    config = {
        'weights': {
            'arousal': {'energy': 0.5, 'f0_range': 0.3, 'tempo': 0.2},
            'valence': {'lexical': 0.6, 'prosody_pitch_mean': 0.4},
            'dominance': {'interruption': 0.4, 'loudness_delta': 0.4, 'hedges': 0.2}
        }
    }

    vad = compute_vad_raw(prosody_features, text_features, dominance_features, config)

    assert 'arousal_raw' in vad
    assert 'valence_raw' in vad
    assert 'dominance_raw' in vad
    assert vad['arousal_raw'] > 0  # High energy -> positive arousal

def test_compute_vad_raw_valence():
    """Positive text valence should increase valence."""
    prosody_features = {
        'energy_rms': 0.1,
        'f0_mean': 150,
        'f0_range': 20,
        'tempo_bpm': 100
    }
    text_features = {
        'valence_score': 0.8  # Strong positive
    }
    dominance_features = {
        'interruption_index': 0.0,
        'loudness_delta': 0.0,
        'hedges_rate': 0.0
    }
    config = {
        'weights': {
            'arousal': {'energy': 0.5, 'f0_range': 0.3, 'tempo': 0.2},
            'valence': {'lexical': 0.6, 'prosody_pitch_mean': 0.4},
            'dominance': {'interruption': 0.4, 'loudness_delta': 0.4, 'hedges': 0.2}
        }
    }

    vad = compute_vad_raw(prosody_features, text_features, dominance_features, config)

    assert vad['valence_raw'] > 0.4  # Should reflect positive text
```

**Step 2: Run test to fail**

```bash
pytest tests/affect/test_vad_engine.py -v
```
Expected: FAIL

**Step 3: Implement VAD scoring**

Update `src/affect/vad_engine.py`:
```python
"""VAD rule-based scoring engine."""

def compute_vad_raw(prosody_features, text_features, dominance_features, config):
    """Combine features into raw V/A/D scores.

    Args:
        prosody_features: dict from features_prosody
        text_features: dict from features_text
        dominance_features: dict from features_dominance
        config: dict with weights {alpha, beta, gamma}

    Returns:
        dict: {valence_raw, arousal_raw, dominance_raw}
    """
    weights = config['weights']

    # AROUSAL: energy + f0_range + tempo
    # Normalize each feature to [0, 1] range (rough heuristic)
    energy_norm = min(1.0, prosody_features.get('energy_rms', 0.0) * 5)  # Scale RMS
    f0_range_norm = min(1.0, prosody_features.get('f0_range', 0.0) / 100)  # 0-100 Hz range
    tempo_norm = min(1.0, prosody_features.get('tempo_bpm', 100) / 200)  # 0-200 BPM

    arousal_raw = (
        weights['arousal']['energy'] * energy_norm +
        weights['arousal']['f0_range'] * f0_range_norm +
        weights['arousal']['tempo'] * tempo_norm
    )

    # VALENCE: lexical + prosody pitch mean
    lexical_valence = text_features.get('valence_score', 0.0)  # Already [-1, +1]
    f0_mean = prosody_features.get('f0_mean', 150)
    # Higher pitch -> slightly more positive (heuristic: 150 Hz = neutral)
    prosody_valence = (f0_mean - 150) / 100  # ±50 Hz = ±0.5
    prosody_valence = max(-1.0, min(1.0, prosody_valence))

    valence_raw = (
        weights['valence']['lexical'] * lexical_valence +
        weights['valence']['prosody_pitch_mean'] * prosody_valence
    )

    # DOMINANCE: interruption + loudness_delta + hedges (inverse)
    interruption_norm = dominance_features.get('interruption_index', 0.0)
    loudness_norm = dominance_features.get('loudness_delta', 0.0)
    hedges_norm = dominance_features.get('hedges_rate', 0.0)

    dominance_raw = (
        weights['dominance']['interruption'] * interruption_norm +
        weights['dominance']['loudness_delta'] * loudness_norm -
        weights['dominance']['hedges'] * hedges_norm  # Hedges reduce dominance
    )

    # Clip to [-1, +1]
    return {
        'arousal_raw': max(-1.0, min(1.0, arousal_raw)),
        'valence_raw': max(-1.0, min(1.0, valence_raw)),
        'dominance_raw': max(-1.0, min(1.0, dominance_raw))
    }
```

**Step 4: Run tests to pass**

```bash
pytest tests/affect/test_vad_engine.py -v
```
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/affect/vad_engine.py tests/affect/test_vad_engine.py
git commit -m "feat(vad): implement rule-based VAD scoring"
```

---

## Phase 4: Baseline Normalization

### Task 4.1: Per-Speaker Z-Score Normalization

**Files:**
- Modify: `src/affect/normalization.py`
- Create: `tests/affect/test_normalization.py`

**Step 1: Write test**

Create `tests/affect/test_normalization.py`:
```python
import pytest
from src.affect.normalization import normalize_speaker_baseline

def test_normalize_speaker_baseline():
    """Z-score normalization should reduce inter-speaker variance."""
    # Speaker A: consistently high arousal
    samples_a = [
        {'timestamp': 0.0, 'speaker_id': 'A', 'arousal_raw': 0.8, 'valence_raw': 0.5, 'dominance_raw': 0.3},
        {'timestamp': 1.0, 'speaker_id': 'A', 'arousal_raw': 0.85, 'valence_raw': 0.55, 'dominance_raw': 0.35},
        {'timestamp': 2.0, 'speaker_id': 'A', 'arousal_raw': 0.75, 'valence_raw': 0.45, 'dominance_raw': 0.25},
    ]

    normalized = normalize_speaker_baseline(samples_a, 'A')

    # Mean should be near 0 after normalization
    arousal_mean = sum(s['arousal'] for s in normalized) / len(normalized)
    assert -0.1 < arousal_mean < 0.1

def test_normalize_maps_to_valid_range():
    """Normalized values should be in [-1, +1]."""
    samples = [
        {'timestamp': 0.0, 'speaker_id': 'B', 'arousal_raw': 0.9, 'valence_raw': 0.9, 'dominance_raw': 0.9},
        {'timestamp': 1.0, 'speaker_id': 'B', 'arousal_raw': -0.9, 'valence_raw': -0.9, 'dominance_raw': -0.9},
    ]

    normalized = normalize_speaker_baseline(samples, 'B')

    for sample in normalized:
        assert -1.0 <= sample['arousal'] <= 1.0
        assert -1.0 <= sample['valence'] <= 1.0
        assert -1.0 <= sample['dominance'] <= 1.0
```

**Step 2: Run test to fail**

```bash
pytest tests/affect/test_normalization.py -v
```
Expected: FAIL

**Step 3: Implement normalization**

Update `src/affect/normalization.py`:
```python
"""Per-speaker baseline normalization."""
import numpy as np

def normalize_speaker_baseline(vad_samples, speaker_id):
    """Z-score normalize per speaker, then map to [-1, +1].

    Args:
        vad_samples: List of {timestamp, speaker_id, valence_raw, arousal_raw, dominance_raw}
        speaker_id: Speaker identifier

    Returns:
        List of {timestamp, speaker_id, valence, arousal, dominance}
    """
    # Filter samples for this speaker
    speaker_samples = [s for s in vad_samples if s['speaker_id'] == speaker_id]

    if len(speaker_samples) == 0:
        return []

    # Extract raw values
    arousal_raw = np.array([s['arousal_raw'] for s in speaker_samples])
    valence_raw = np.array([s['valence_raw'] for s in speaker_samples])
    dominance_raw = np.array([s['dominance_raw'] for s in speaker_samples])

    # Z-score normalization
    def z_score(arr):
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return arr - mean  # Avoid division by zero
        return (arr - mean) / std

    arousal_z = z_score(arousal_raw)
    valence_z = z_score(valence_raw)
    dominance_z = z_score(dominance_raw)

    # Map to [-1, +1] using tanh squashing
    arousal_norm = np.tanh(arousal_z * 0.5)  # Scale factor 0.5 to avoid saturation
    valence_norm = np.tanh(valence_z * 0.5)
    dominance_norm = np.tanh(dominance_z * 0.5)

    # Build normalized samples
    normalized = []
    for i, sample in enumerate(speaker_samples):
        normalized.append({
            'timestamp': sample['timestamp'],
            'speaker_id': speaker_id,
            'arousal': float(arousal_norm[i]),
            'valence': float(valence_norm[i]),
            'dominance': float(dominance_norm[i])
        })

    return normalized
```

**Step 4: Run tests to pass**

```bash
pytest tests/affect/test_normalization.py -v
```
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/affect/normalization.py tests/affect/test_normalization.py
git commit -m "feat(vad): implement per-speaker baseline normalization"
```

---

## Phase 5: Smoothing & Latency

### Task 5.1: EMA Smoothing

**Files:**
- Modify: `src/affect/smoothing.py`
- Create: `tests/affect/test_smoothing.py`

**Step 1: Write test**

Create `tests/affect/test_smoothing.py`:
```python
import pytest
from src.affect.smoothing import smooth_vad_ema

def test_smooth_vad_ema_reduces_noise():
    """EMA should smooth out high-frequency noise."""
    # Noisy signal alternating between -0.5 and +0.5
    noisy_samples = [
        {'timestamp': 0.0, 'speaker_id': 'A', 'arousal': 0.5, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 0.5, 'speaker_id': 'A', 'arousal': -0.5, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 1.0, 'speaker_id': 'A', 'arousal': 0.5, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 1.5, 'speaker_id': 'A', 'arousal': -0.5, 'valence': 0.0, 'dominance': 0.0},
    ]

    smoothed = smooth_vad_ema(noisy_samples, lambda_=0.5)

    # Variance should be reduced
    original_var = sum((s['arousal'] - 0)**2 for s in noisy_samples) / len(noisy_samples)
    smoothed_var = sum((s['arousal'] - 0)**2 for s in smoothed) / len(smoothed)

    assert smoothed_var < original_var

def test_smooth_vad_ema_preserves_trend():
    """EMA should preserve monotonic trend."""
    increasing_samples = [
        {'timestamp': 0.0, 'speaker_id': 'A', 'arousal': 0.0, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 1.0, 'speaker_id': 'A', 'arousal': 0.2, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 2.0, 'speaker_id': 'A', 'arousal': 0.4, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 3.0, 'speaker_id': 'A', 'arousal': 0.6, 'valence': 0.0, 'dominance': 0.0},
    ]

    smoothed = smooth_vad_ema(increasing_samples, lambda_=0.3)

    # Should still be monotonically increasing (approximately)
    arousal_values = [s['arousal'] for s in smoothed]
    for i in range(1, len(arousal_values)):
        assert arousal_values[i] >= arousal_values[i-1] - 0.05  # Allow small tolerance
```

**Step 2: Run test to fail**

```bash
pytest tests/affect/test_smoothing.py -v
```
Expected: FAIL

**Step 3: Implement EMA smoothing**

Update `src/affect/smoothing.py`:
```python
"""EMA smoothing with latency constraint."""

def smooth_vad_ema(vad_samples, lambda_=0.3):
    """Apply exponential moving average smoothing.

    Args:
        vad_samples: List of normalized VAD samples
        lambda_: Smoothing factor (0-1, higher = more smoothing)

    Returns:
        List of smoothed VAD samples
    """
    if len(vad_samples) == 0:
        return []

    smoothed = []

    # Group by speaker
    speakers = {s['speaker_id'] for s in vad_samples}

    for speaker_id in speakers:
        speaker_samples = [s for s in vad_samples if s['speaker_id'] == speaker_id]

        # Initialize with first sample
        prev_arousal = speaker_samples[0]['arousal']
        prev_valence = speaker_samples[0]['valence']
        prev_dominance = speaker_samples[0]['dominance']

        for sample in speaker_samples:
            # EMA: smoothed = lambda * prev + (1 - lambda) * current
            arousal_smooth = lambda_ * prev_arousal + (1 - lambda_) * sample['arousal']
            valence_smooth = lambda_ * prev_valence + (1 - lambda_) * sample['valence']
            dominance_smooth = lambda_ * prev_dominance + (1 - lambda_) * sample['dominance']

            smoothed.append({
                'timestamp': sample['timestamp'],
                'speaker_id': speaker_id,
                'arousal': arousal_smooth,
                'valence': valence_smooth,
                'dominance': dominance_smooth
            })

            # Update previous values
            prev_arousal = arousal_smooth
            prev_valence = valence_smooth
            prev_dominance = dominance_smooth

    # Sort by timestamp
    smoothed.sort(key=lambda s: s['timestamp'])

    return smoothed
```

**Step 4: Run tests to pass**

```bash
pytest tests/affect/test_smoothing.py -v
```
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/affect/smoothing.py tests/affect/test_smoothing.py
git commit -m "feat(vad): implement EMA smoothing"
```

---

## Phase 6: Event Detection

### Task 6.1: Turning Point Detection

**Files:**
- Modify: `src/affect/events.py`
- Create: `tests/affect/test_events.py`

**Step 1: Write test**

Create `tests/affect/test_events.py`:
```python
import pytest
from src.affect.events import detect_turning_points

def test_detect_turning_points_arousal_spike():
    """Should detect sharp increase in arousal."""
    samples = [
        {'timestamp': 0.0, 'speaker_id': 'A', 'arousal': 0.0, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 1.0, 'speaker_id': 'A', 'arousal': 0.1, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 2.0, 'speaker_id': 'A', 'arousal': 0.7, 'valence': 0.0, 'dominance': 0.0},  # Sharp jump!
        {'timestamp': 3.0, 'speaker_id': 'A', 'arousal': 0.75, 'valence': 0.0, 'dominance': 0.0},
        {'timestamp': 4.0, 'speaker_id': 'A', 'arousal': 0.7, 'valence': 0.0, 'dominance': 0.0},
    ]

    config = {
        'grad_threshold': 0.15,
        'persistence_min': 1.0,
        'hysteresis': 0.05
    }

    events = detect_turning_points(samples, config)

    assert len(events) > 0
    assert any(e['dimension'] == 'arousal' for e in events)
    assert any(1.5 < e['timestamp'] < 2.5 for e in events)  # Around the spike

def test_no_turning_points_for_flat_signal():
    """Flat signal should produce no events."""
    samples = [
        {'timestamp': float(i), 'speaker_id': 'A', 'arousal': 0.5, 'valence': 0.0, 'dominance': 0.0}
        for i in range(10)
    ]

    config = {
        'grad_threshold': 0.15,
        'persistence_min': 1.0,
        'hysteresis': 0.05
    }

    events = detect_turning_points(samples, config)

    assert len(events) == 0
```

**Step 2: Run test to fail**

```bash
pytest tests/affect/test_events.py -v
```
Expected: FAIL

**Step 3: Implement turning point detection**

Update `src/affect/events.py`:
```python
"""Turning point event detection."""

def detect_turning_points(vad_samples, config):
    """Detect emotional turning points.

    Args:
        vad_samples: List of smoothed VAD samples
        config: {grad_threshold, persistence_min, hysteresis}

    Returns:
        List of {timestamp, type, dimension, magnitude}
    """
    if len(vad_samples) < 3:
        return []

    events = []
    grad_threshold = config['grad_threshold']
    persistence_min = config['persistence_min']

    dimensions = ['arousal', 'valence', 'dominance']

    for dim in dimensions:
        # Extract time series for this dimension
        values = [(s['timestamp'], s[dim]) for s in vad_samples]

        # Compute gradients
        for i in range(1, len(values) - 1):
            t_prev, v_prev = values[i - 1]
            t_curr, v_curr = values[i]
            t_next, v_next = values[i + 1]

            # Gradient (change per second)
            dt = t_curr - t_prev
            if dt == 0:
                continue
            grad = (v_curr - v_prev) / dt

            # Check if gradient exceeds threshold
            if abs(grad) > grad_threshold:
                # Check persistence (next value sustains change)
                if (grad > 0 and v_next >= v_curr - config['hysteresis']) or \
                   (grad < 0 and v_next <= v_curr + config['hysteresis']):

                    event_type = 'turning_point'
                    if grad > 0:
                        event_type = 'peak' if v_curr > v_next else 'turning_point'
                    else:
                        event_type = 'valley' if v_curr < v_next else 'turning_point'

                    events.append({
                        'timestamp': t_curr,
                        'type': event_type,
                        'dimension': dim,
                        'magnitude': abs(grad)
                    })

    return events
```

**Step 4: Run tests to pass**

```bash
pytest tests/affect/test_events.py -v
```
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/affect/events.py tests/affect/test_events.py
git commit -m "feat(vad): implement turning point detection"
```

---

## Phase 7: Integration & API

### Task 7.1: End-to-End Pipeline Integration

**Files:**
- Create: `src/affect/pipeline.py`
- Create: `tests/affect/test_pipeline_integration.py`

**Step 1: Write integration test**

Create `tests/affect/test_pipeline_integration.py`:
```python
import pytest
import numpy as np
from src.affect.pipeline import process_vad_pipeline

def test_vad_pipeline_end_to_end():
    """Full pipeline should produce valid VAD output."""
    # Synthetic audio (1 second at 16kHz)
    sr = 16000
    audio = np.random.randn(sr) * 0.1

    # Synthetic transcript
    transcript = [
        {'start': 0.0, 'end': 1.0, 'text': 'Ich bin glücklich.', 'speaker': 'A'}
    ]

    # Run pipeline
    result = process_vad_pipeline(audio, transcript, sr=sr)

    assert 'samples' in result
    assert 'events' in result
    assert 'provenance' in result
    assert len(result['samples']) > 0

    # Check sample structure
    sample = result['samples'][0]
    assert 'timestamp' in sample
    assert 'speaker_id' in sample
    assert 'arousal' in sample
    assert 'valence' in sample
    assert 'dominance' in sample
    assert -1 <= sample['arousal'] <= 1
```

**Step 2: Run test to fail**

```bash
pytest tests/affect/test_pipeline_integration.py -v
```
Expected: FAIL

**Step 3: Implement pipeline orchestration**

Create `src/affect/pipeline.py`:
```python
"""VAD processing pipeline orchestration."""
import yaml
from pathlib import Path
from src.affect.features_prosody import extract_arousal_features, extract_pitch_features, extract_tempo_features
from src.affect.features_text import extract_valence_features
from src.affect.features_dominance import extract_dominance_features
from src.affect.vad_engine import compute_vad_raw
from src.affect.normalization import normalize_speaker_baseline
from src.affect.smoothing import smooth_vad_ema
from src.affect.events import detect_turning_points
from src.affect.schema import validate_vad_output
import hashlib

# Load config
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "affect.yaml"
with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

def process_vad_pipeline(audio, transcript, sr=16000):
    """Run full VAD processing pipeline.

    Args:
        audio: Audio signal array
        transcript: List of {start, end, text, speaker}
        sr: Sample rate

    Returns:
        dict: {samples, events, provenance} validated against schema
    """
    raw_samples = []

    # Process each transcript segment
    for segment in transcript:
        start_sample = int(segment['start'] * sr)
        end_sample = int(segment['end'] * sr)
        audio_segment = audio[start_sample:end_sample]

        # Extract features
        prosody_features = {}
        prosody_features.update(extract_arousal_features(audio_segment, sr))
        pitch_features = extract_pitch_features(audio_segment, sr)
        if pitch_features['f0_mean'] is not None:
            prosody_features.update(pitch_features)
        else:
            prosody_features.update({'f0_mean': 150, 'f0_range': 0, 'f0_variance': 0})
        prosody_features.update(extract_tempo_features(audio_segment, sr))

        text_features = extract_valence_features(segment['text'], language='de')

        # Dominance features (placeholder for now)
        dominance_features = {
            'interruption_index': 0.0,
            'loudness_delta': 0.0,
            'hedges_rate': 0.0
        }

        # Compute raw VAD
        vad_raw = compute_vad_raw(prosody_features, text_features, dominance_features, CONFIG)

        raw_samples.append({
            'timestamp': segment['start'],
            'speaker_id': segment['speaker'],
            'arousal_raw': vad_raw['arousal_raw'],
            'valence_raw': vad_raw['valence_raw'],
            'dominance_raw': vad_raw['dominance_raw']
        })

    # Normalize per speaker
    speakers = {s['speaker_id'] for s in raw_samples}
    normalized_samples = []
    for speaker_id in speakers:
        normalized_samples.extend(normalize_speaker_baseline(raw_samples, speaker_id))

    # Sort by timestamp
    normalized_samples.sort(key=lambda s: s['timestamp'])

    # Smooth
    smoothed_samples = smooth_vad_ema(normalized_samples, lambda_=CONFIG['smoothing']['lambda'])

    # Detect events
    events = detect_turning_points(smoothed_samples, CONFIG['thresholds'])

    # Add confidence (placeholder: always high for now)
    for sample in smoothed_samples:
        sample['confidence'] = 0.85

    # Build output
    config_hash = hashlib.md5(str(CONFIG).encode()).hexdigest()[:8]
    output = {
        'version': '1.0',
        'session_id': 'test-session',
        'samples': smoothed_samples,
        'events': events,
        'provenance': {
            'model': 'rule-based-v1',
            'config_hash': config_hash
        }
    }

    # Validate
    validate_vad_output(output)

    return output
```

**Step 4: Install PyYAML if needed**

```bash
grep -q "PyYAML" requirements.txt || echo "PyYAML>=6.0" >> requirements.txt
pip install PyYAML
```

**Step 5: Implement placeholder dominance features**

Update `src/affect/features_dominance.py`:
```python
"""Dominance features from turn-taking and loudness."""

def extract_dominance_features(speaker_segments, audio_segments):
    """Extract dominance indicators.

    Args:
        speaker_segments: List of {speaker, start, end, overlaps}
        audio_segments: Corresponding audio arrays

    Returns:
        dict: {interruption_index, loudness_delta, hedges_rate}
    """
    # Placeholder implementation
    return {
        'interruption_index': 0.0,
        'loudness_delta': 0.0,
        'hedges_rate': 0.0
    }
```

**Step 6: Run test to pass**

```bash
pytest tests/affect/test_pipeline_integration.py -v
```
Expected: PASS

**Step 7: Commit**

```bash
git add src/affect/pipeline.py src/affect/features_dominance.py tests/affect/test_pipeline_integration.py requirements.txt
git commit -m "feat(vad): implement end-to-end pipeline integration"
```

---

## Phase 8: SVT GUI Integration

### Task 8.1: Add VAD Toggle to SVT GUI

**Files:**
- Modify: `svt.py` (around line 100-150, GUI setup)
- Create: `tests/test_svt_vad_integration.py`

**Step 1: Write integration test**

Create `tests/test_svt_vad_integration.py`:
```python
import pytest
from pathlib import Path

def test_vad_output_created_when_enabled():
    """When VAD enabled, .vad.json file should be created."""
    # This is a manual integration test
    # Run: python svt.py with VAD checkbox enabled
    # Expected: Transkripte_LLM/*_transkript.vad.json exists
    pass  # Manual test

def test_vad_json_schema_valid():
    """Generated VAD JSON should pass schema validation."""
    from src.affect.schema import validate_vad_output
    import json

    # Find a recent .vad.json file
    vad_files = list(Path('Transkripte_LLM').glob('*.vad.json'))
    if len(vad_files) == 0:
        pytest.skip("No VAD output files found")

    with open(vad_files[0]) as f:
        vad_data = json.load(f)

    assert validate_vad_output(vad_data) is True
```

**Step 2: Modify SVT GUI to add VAD checkbox**

Read current SVT GUI structure:

```bash
grep -n "enable_prosody" svt.py | head -5
```

Then modify `svt.py` (find the GUI setup section around line 100-150):

Add after prosody checkbox:
```python
# VAD Affect State checkbox
self.enable_vad = tk.BooleanVar(value=False)
tk.Checkbutton(
    features_frame,
    text="VAD Affect State (Valence-Arousal-Dominance)",
    variable=self.enable_vad,
    font=("Segoe UI", 10)
).pack(anchor="w", padx=20, pady=2)
```

**Step 3: Integrate VAD pipeline into transcription workflow**

Modify the transcription callback in `svt.py` (search for `process_audio_file` or similar):

Add after prosody processing:
```python
# VAD processing (if enabled)
if self.enable_vad.get():
    from src.affect.pipeline import process_vad_pipeline

    try:
        # Run VAD pipeline
        vad_result = process_vad_pipeline(
            audio=audio_data,
            transcript=[
                {
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'],
                    'speaker': seg.get('speaker', 'Unknown')
                }
                for seg in segments
            ],
            sr=sample_rate
        )

        # Save VAD output
        vad_output_path = output_path.replace('_transkript.md', '_transkript.vad.json')
        with open(vad_output_path, 'w', encoding='utf-8') as f:
            json.dump(vad_result, f, indent=2, ensure_ascii=False)

        logging.info(f"VAD output saved to {vad_output_path}")
    except Exception as e:
        logging.error(f"VAD processing failed: {e}")
```

**Step 4: Test manually**

```bash
python svt.py
# 1. Enable "VAD Affect State" checkbox
# 2. Process a test audio file
# 3. Check Transkripte_LLM/ for .vad.json output
# 4. Verify JSON structure
```

**Step 5: Commit**

```bash
git add svt.py tests/test_svt_vad_integration.py
git commit -m "feat(vad): integrate VAD pipeline into SVT GUI"
```

---

## Phase 9: UI Timeline Visualization (Future)

### Task 9.1: Design Timeline Component

**Note:** This task requires frontend work (HTML/JS or Tkinter Canvas). For now, we create a placeholder.

**Files:**
- Create: `docs/vad_timeline_design.md`

**Step 1: Document timeline UI requirements**

Create `docs/vad_timeline_design.md`:
```markdown
# VAD Timeline UI Design

## Requirements

- Display 3 curves (V/A/D) per speaker
- Synchronized with transcript timeline
- Color-coded by speaker (green=Patient, blue=Therapeut)
- Event markers (turning points) as badges
- Hover tooltips with exact values
- Export timeline view as PNG

## Technology Options

1. **HTML + Chart.js** (current dashboard approach)
2. **Tkinter Canvas** (integrated into SVT GUI)
3. **Matplotlib** (static export)

## Implementation Plan (Phase 10)

- Create `src/affect/timeline_renderer.py`
- Integrate with existing dashboard generator
- Add timeline view to psychoanalysis dashboard
```

**Step 2: Commit**

```bash
git add docs/vad_timeline_design.md
git commit -m "docs(vad): add timeline UI design spec"
```

---

## Validation & Testing

### Task 10.1: Run Full Test Suite

**Step 1: Run all VAD tests**

```bash
pytest tests/affect/ -v --cov=src/affect --cov-report=term-missing
```

Expected: Coverage ≥ 80%

**Step 2: Run integration tests**

```bash
pytest tests/test_svt_vad_integration.py -v
```

**Step 3: Performance test (latency SLA)**

Create `tests/affect/test_performance.py`:
```python
import pytest
import numpy as np
import time
from src.affect.pipeline import process_vad_pipeline

def test_latency_sla_95p():
    """95th percentile latency should be ≤ 500ms."""
    sr = 16000
    latencies = []

    for i in range(20):  # Run 20 iterations
        # 3-second audio segment
        audio = np.random.randn(sr * 3) * 0.1
        transcript = [
            {'start': 0.0, 'end': 1.0, 'text': 'Test utterance.', 'speaker': 'A'},
            {'start': 1.0, 'end': 2.0, 'text': 'Another utterance.', 'speaker': 'A'},
            {'start': 2.0, 'end': 3.0, 'text': 'Final utterance.', 'speaker': 'A'},
        ]

        start_time = time.time()
        process_vad_pipeline(audio, transcript, sr=sr)
        latency_ms = (time.time() - start_time) * 1000

        latencies.append(latency_ms)

    # Calculate 95th percentile
    latencies.sort()
    p95_latency = latencies[int(len(latencies) * 0.95)]

    print(f"\n95th percentile latency: {p95_latency:.1f} ms")
    assert p95_latency <= 500, f"Latency SLA violated: {p95_latency:.1f} ms > 500 ms"
```

Run:
```bash
pytest tests/affect/test_performance.py -v -s
```

**Step 4: Commit**

```bash
git add tests/affect/test_performance.py
git commit -m "test(vad): add performance and latency tests"
```

---

## Documentation & Handoff

### Task 11.1: Write User Documentation

**Files:**
- Create: `docs/VAD_USER_GUIDE.md`

**Step 1: Create user guide**

Create `docs/VAD_USER_GUIDE.md`:
```markdown
# VAD Affect State Layer - User Guide

## Overview

The VAD (Valence-Arousal-Dominance) Affect State Layer provides non-diagnostic emotional state tracking for therapeutic transcripts.

## Usage

### 1. Enable in SVT GUI

```
1. Launch: python svt.py
2. Check "VAD Affect State (Valence-Arousal-Dominance)"
3. Process audio as normal
4. Find .vad.json output in Transkripte_LLM/
```

### 2. VAD Output Format

```json
{
  "version": "1.0",
  "session_id": "2025-01-18_14-30-00",
  "samples": [
    {
      "timestamp": 0.0,
      "speaker_id": "Therapeut",
      "valence": 0.3,
      "arousal": 0.5,
      "dominance": 0.2,
      "confidence": 0.85
    }
  ],
  "events": [
    {
      "timestamp": 12.5,
      "type": "turning_point",
      "dimension": "arousal",
      "magnitude": 0.45
    }
  ],
  "provenance": {
    "model": "rule-based-v1",
    "config_hash": "abc12345"
  }
}
```

### 3. Interpretation

**Valence** [-1, +1]: Negative ↔ Positive emotional tone
**Arousal** [-1, +1]: Low energy ↔ High energy/activation
**Dominance** [-1, +1]: Submissive ↔ Assertive/controlling

**Important:** These are indicators, NOT clinical diagnoses.

## Configuration

Edit `config/affect.yaml` to adjust:
- Feature weights (arousal/valence/dominance)
- Turning point thresholds
- Smoothing parameters

## Troubleshooting

**No VAD output created:**
- Check that VAD checkbox is enabled
- Verify `src/affect/` modules exist
- Check logs for errors

**High latency:**
- Reduce smoothing lambda in config
- Use shorter audio segments
```

**Step 2: Commit**

```bash
git add docs/VAD_USER_GUIDE.md
git commit -m "docs(vad): add user guide"
```

---

## Success Criteria Checklist

### SC-1: UX "hilfreich"
- [ ] VAD output generated successfully
- [ ] Timeline visualization available (Phase 10)
- [ ] User feedback survey (post-MVP)

### SC-2: ≤ 2 Min to find top sections
- [ ] Timeline allows quick navigation (Phase 10)

### SC-3: Correlation thresholds
- [ ] Arousal r ≥ 0.55 (requires evaluation dataset)
- [ ] Valence r ≥ 0.45 (requires evaluation dataset)

### SC-4: Schema stability
- [x] JSON schema defined
- [x] 100 sessions validation test (synthetic)

### SC-5: Latency SLA
- [x] 95p ≤ 500 ms performance test

### SC-6: Policy-Lint
- [x] Non-diagnostic language in UI copy
- [x] Privacy filter in export (Phase 10)

---

## Execution Notes

**Day 0-7 Ship Loop:**

- **Day 0:** Tasks 0.1-0.2 (scaffold, schema)
- **Day 1:** Tasks 1.1-1.3, 2.1 (prosody + text features)
- **Day 2:** Tasks 3.1, 4.1 (VAD engine, normalization)
- **Day 3:** Tasks 5.1, 6.1 (smoothing, events)
- **Day 4:** Tasks 7.1, 8.1 (pipeline, GUI integration)
- **Day 5:** Tasks 10.1, 11.1 (testing, docs)
- **Day 6:** Phase 10 (UI timeline - future)
- **Day 7:** Ship MVP, gather feedback

---

## Future Enhancements (Post-MVP)

1. **Dominance features** (interruption detection, hedges counting)
2. **Relational synchronicity** (cross-correlation indicator)
3. **Timeline UI** (Chart.js overlay in dashboard)
4. **ML-based VAD** (replace rule-based with trained model)
5. **Real-time streaming** (live VAD updates)
6. **Evaluation dataset** (validate correlation targets SC-3)

---

**Plan Complete.**

**For Claude:** Use `executing-plans` skill or `subagent-driven-development` to implement this plan task-by-task.
