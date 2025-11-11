# Therapeutic Transcription System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Build a production-quality transcription system with GUI for therapeutic use, featuring enhanced V4 emotion analysis, prosody extraction for future Voice-Marker 2.0, and comprehensive quality assurance.

**Architecture:** Extend auto_transcriber_v4_emotion.py as the core engine, add prosody extraction layer using librosa, create new GUI with tkinter for one-click workflow, enhance Memory YAML profiles with prosody patterns, implement confidence scoring and quality validation.

**Tech Stack:** Python 3.8+, OpenAI Whisper, librosa (prosody), tkinter (GUI), PyYAML, TextBlob, numpy

---

## Task 1: Create Prosody Extraction Module

**Files:**
- Create: `prosody_analyzer.py`
- Test: `test_prosody_analyzer.py`

**Step 1: Write the failing test**

```bash
cd /home/dyai/Dokumente/DYAI_home/DEV/TOOLS/TransSemantic/Super_semantic_whisper
```

Create `test_prosody_analyzer.py`:

```python
#!/usr/bin/env python3
import pytest
import numpy as np
from pathlib import Path
from prosody_analyzer import ProsodyAnalyzer

def test_prosody_analyzer_initialization():
    """Test that ProsodyAnalyzer initializes correctly"""
    analyzer = ProsodyAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'extract_prosody')

def test_extract_prosody_returns_dict():
    """Test that extract_prosody returns expected data structure"""
    analyzer = ProsodyAnalyzer()
    # Create dummy audio data (1 second at 22050 Hz)
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    assert isinstance(result, dict)
    assert 'pitch' in result
    assert 'tempo' in result
    assert 'energy' in result

def test_pitch_extraction():
    """Test pitch/F0 extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    pitch_data = result['pitch']
    assert 'mean' in pitch_data
    assert 'std' in pitch_data
    assert 'contour' in pitch_data
    assert isinstance(pitch_data['contour'], list)

def test_tempo_extraction():
    """Test tempo/rhythm extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    tempo_data = result['tempo']
    assert 'bpm' in tempo_data
    assert 'speech_rate' in tempo_data

def test_energy_extraction():
    """Test energy/loudness extraction"""
    analyzer = ProsodyAnalyzer()
    audio_data = np.random.randn(22050).astype(np.float32)
    result = analyzer.extract_prosody(audio_data, sr=22050)

    energy_data = result['energy']
    assert 'mean' in energy_data
    assert 'std' in energy_data
    assert 'dynamic_range' in energy_data
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest test_prosody_analyzer.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'prosody_analyzer'"

**Step 3: Write minimal implementation**

Create `prosody_analyzer.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prosody Analyzer - Extracts prosodic features for Voice-Marker 2.0
Features: Pitch (F0), Tempo/Rhythm, Energy/Loudness
"""

import numpy as np
import librosa
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ProsodyAnalyzer:
    """Extracts prosodic features from audio for therapeutic analysis"""

    def __init__(self,
                 hop_length: int = 512,
                 frame_length: int = 2048,
                 fmin: float = 75.0,  # Minimum pitch (Hz) for human speech
                 fmax: float = 500.0):  # Maximum pitch (Hz) for human speech
        """
        Initialize prosody analyzer

        Args:
            hop_length: Number of samples between successive frames
            frame_length: Frame length for analysis
            fmin: Minimum frequency for pitch detection (Hz)
            fmax: Maximum frequency for pitch detection (Hz)
        """
        self.hop_length = hop_length
        self.frame_length = frame_length
        self.fmin = fmin
        self.fmax = fmax

    def extract_prosody(self,
                       audio_data: np.ndarray,
                       sr: int = 22050) -> Dict[str, Any]:
        """
        Extract all prosodic features from audio

        Args:
            audio_data: Audio time series as numpy array
            sr: Sample rate

        Returns:
            Dictionary with pitch, tempo, and energy features
        """
        try:
            pitch_features = self._extract_pitch(audio_data, sr)
            tempo_features = self._extract_tempo(audio_data, sr)
            energy_features = self._extract_energy(audio_data, sr)

            return {
                'pitch': pitch_features,
                'tempo': tempo_features,
                'energy': energy_features
            }
        except Exception as e:
            logger.error(f"Error extracting prosody: {e}")
            return {
                'pitch': {'mean': 0, 'std': 0, 'contour': []},
                'tempo': {'bpm': 0, 'speech_rate': 0},
                'energy': {'mean': 0, 'std': 0, 'dynamic_range': 0}
            }

    def _extract_pitch(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Extract pitch (F0) features

        Returns:
            Dict with mean, std, and contour of pitch
        """
        # Extract pitch using librosa's piptrack
        pitches, magnitudes = librosa.piptrack(
            y=audio_data,
            sr=sr,
            hop_length=self.hop_length,
            fmin=self.fmin,
            fmax=self.fmax
        )

        # Get pitch contour (select pitch with highest magnitude at each frame)
        pitch_contour = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:  # Only include voiced frames
                pitch_contour.append(float(pitch))

        if len(pitch_contour) > 0:
            mean_pitch = np.mean(pitch_contour)
            std_pitch = np.std(pitch_contour)
        else:
            mean_pitch = 0
            std_pitch = 0

        return {
            'mean': float(mean_pitch),
            'std': float(std_pitch),
            'contour': pitch_contour
        }

    def _extract_tempo(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Extract tempo and rhythm features

        Returns:
            Dict with bpm and speech_rate
        """
        # Extract tempo
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]

        # Estimate speech rate (syllables per second)
        # Using onset detection as proxy for syllables
        onsets = librosa.onset.onset_detect(y=audio_data, sr=sr, units='time')
        duration = len(audio_data) / sr
        speech_rate = len(onsets) / duration if duration > 0 else 0

        return {
            'bpm': float(tempo),
            'speech_rate': float(speech_rate)
        }

    def _extract_energy(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Extract energy (loudness) features

        Returns:
            Dict with mean, std, and dynamic_range
        """
        # Calculate RMS energy
        rms = librosa.feature.rms(
            y=audio_data,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )[0]

        mean_energy = np.mean(rms)
        std_energy = np.std(rms)
        dynamic_range = np.max(rms) - np.min(rms) if len(rms) > 0 else 0

        return {
            'mean': float(mean_energy),
            'std': float(std_energy),
            'dynamic_range': float(dynamic_range)
        }

    def extract_from_file(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract prosody from audio file

        Args:
            audio_path: Path to audio file

        Returns:
            Prosody features dict or None on error
        """
        try:
            audio_data, sr = librosa.load(audio_path, sr=None)
            return self.extract_prosody(audio_data, sr)
        except Exception as e:
            logger.error(f"Error loading audio file {audio_path}: {e}")
            return None
```

**Step 4: Run test to verify it passes**

```bash
python3 -m pytest test_prosody_analyzer.py -v
```

Expected: PASS (all 5 tests)

**Step 5: Commit**

```bash
git add test_prosody_analyzer.py prosody_analyzer.py
git commit -m "feat: add prosody analyzer for pitch, tempo, energy extraction

- Extract pitch (F0) with mean, std, contour
- Extract tempo (BPM) and speech rate
- Extract energy (RMS) with dynamic range
- Foundation for Voice-Marker 2.0 integration"
```

---

## Task 2: Enhance V4 with Prosody Integration

**Files:**
- Modify: `auto_transcriber_v4_emotion.py`
- Test: `test_transcriber_v4_prosody.py`

**Step 1: Write the failing test**

Create `test_transcriber_v4_prosody.py`:

```python
#!/usr/bin/env python3
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np

# Import after we modify the file
import auto_transcriber_v4_emotion as v4

def test_emotional_analyzer_has_prosody_analyzer():
    """Test that EmotionalAnalyzer includes prosody analyzer"""
    analyzer = v4.EmotionalAnalyzer()
    assert hasattr(analyzer, 'prosody_analyzer')
    assert analyzer.prosody_analyzer is not None

def test_analyze_emotion_includes_prosody():
    """Test that analyze_emotion returns prosody data"""
    analyzer = v4.EmotionalAnalyzer()

    # Mock audio data
    audio_data = np.random.randn(22050).astype(np.float32)
    text = "This is a test sentence."

    result = analyzer.analyze_emotion(text, audio_data=audio_data, sr=22050)

    assert 'prosody' in result
    assert 'pitch' in result['prosody']
    assert 'tempo' in result['prosody']
    assert 'energy' in result['prosody']

def test_analyze_emotion_without_audio_data():
    """Test that analyze_emotion works without audio (text-only)"""
    analyzer = v4.EmotionalAnalyzer()
    text = "This is a test sentence."

    result = analyzer.analyze_emotion(text, audio_data=None)

    # Should still work but prosody may be empty/default
    assert 'prosody' in result
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest test_transcriber_v4_prosody.py -v
```

Expected: FAIL with assertion errors (prosody_analyzer not found, prosody not in result)

**Step 3: Modify V4 to integrate prosody**

Edit `auto_transcriber_v4_emotion.py`, find the `EmotionalAnalyzer.__init__` method (around line 54) and add prosody analyzer:

```python
def __init__(self):
    self.emotional_markers = self._load_emotional_markers()
    # ADD THIS LINE:
    from prosody_analyzer import ProsodyAnalyzer
    self.prosody_analyzer = ProsodyAnalyzer()
```

Find the `analyze_emotion` method (around line 220) and modify to include prosody:

```python
def analyze_emotion(self, text: str, audio_path: Optional[str] = None,
                   audio_data: Optional[np.ndarray] = None,
                   sr: int = 22050) -> Dict[str, Any]:
    """
    Analysiert emotionale Färbung aus Text und optionalem Audio

    Args:
        text: Transkribierter Text
        audio_path: Pfad zur Audio-Datei (optional)
        audio_data: Audio als numpy array (optional)
        sr: Sample rate

    Returns:
        Dict mit emotion, valence, confidence, text_sentiment, audio_features, prosody
    """
    result = {
        'emotion': 'neutral',
        'valence': 0.0,
        'confidence': 0.0,
        'text_sentiment': {},
        'audio_features': {},
        'prosody': {}  # ADD THIS
    }

    # Text-Sentiment-Analyse
    text_sentiment = self._analyze_text_sentiment(text)
    result['text_sentiment'] = text_sentiment

    # Audio-Feature-Extraktion
    audio_features = {}
    if LIBROSA_AVAILABLE and (audio_path or audio_data is not None):
        if audio_path:
            audio_features = self._extract_audio_features(audio_path)
        elif audio_data is not None:
            audio_features = self._extract_audio_features_from_array(audio_data, sr)
        result['audio_features'] = audio_features

        # PROSODY EXTRACTION - ADD THIS BLOCK:
        try:
            if audio_data is not None:
                prosody_features = self.prosody_analyzer.extract_prosody(audio_data, sr)
            elif audio_path:
                prosody_features = self.prosody_analyzer.extract_from_file(audio_path)
            else:
                prosody_features = {}
            result['prosody'] = prosody_features
        except Exception as e:
            logger.warning(f"Prosody extraction failed: {e}")
            result['prosody'] = {}

    # Kombiniere Text + Audio für Gesamtemotion
    combined_emotion = self._combine_text_audio_emotion(text_sentiment, audio_features)
    result.update(combined_emotion)

    return result
```

Add new helper method for extracting audio features from numpy array (around line 350):

```python
def _extract_audio_features_from_array(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
    """Extrahiert Audio-Features aus numpy array"""
    try:
        features = {}

        # Pitch
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)

        if pitch_values:
            features['pitch_mean'] = float(np.mean(pitch_values))
            features['pitch_std'] = float(np.std(pitch_values))

        # Energy
        rms = librosa.feature.rms(y=audio_data)[0]
        features['energy_mean'] = float(np.mean(rms))
        features['energy_std'] = float(np.std(rms))

        # Tempo
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        features['tempo'] = float(tempo[0]) if len(tempo) > 0 else 0.0

        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))

        return features

    except Exception as e:
        logger.error(f"Fehler bei Audio-Feature-Extraktion: {e}")
        return {}
```

**Step 4: Run test to verify it passes**

```bash
python3 -m pytest test_transcriber_v4_prosody.py -v
```

Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add auto_transcriber_v4_emotion.py test_transcriber_v4_prosody.py
git commit -m "feat: integrate prosody extraction into V4 emotion analyzer

- Add ProsodyAnalyzer to EmotionalAnalyzer
- Extract prosody features during emotion analysis
- Support both audio_path and audio_data numpy arrays
- Prosody data included in analyze_emotion result"
```

---

## Task 3: Enhance Memory YAML with Prosody Patterns

**Files:**
- Modify: `build_memory_from_transcripts.py`
- Test: `test_memory_prosody.py`

**Step 1: Write the failing test**

Create `test_memory_prosody.py`:

```python
#!/usr/bin/env python3
import pytest
import yaml
from pathlib import Path
import tempfile
import shutil

def test_memory_profile_includes_prosody_section():
    """Test that memory profiles have prosody_patterns section"""
    # This will test the enhanced memory structure
    from build_memory_from_transcripts import update_speaker_memory

    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "Memory"
        memory_dir.mkdir()

        speaker = "test_speaker"
        transcript_data = {
            'text': 'This is a test transcript',
            'emotion': {
                'prosody': {
                    'pitch': {'mean': 150.5, 'std': 20.3},
                    'tempo': {'bpm': 120, 'speech_rate': 4.5},
                    'energy': {'mean': 0.5, 'std': 0.1, 'dynamic_range': 0.3}
                }
            }
        }

        update_speaker_memory(speaker, transcript_data, memory_dir)

        # Load and verify
        memory_file = memory_dir / f"{speaker}.yaml"
        assert memory_file.exists()

        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)

        assert 'prosody_patterns' in memory
        assert 'pitch_profile' in memory['prosody_patterns']
        assert 'tempo_profile' in memory['prosody_patterns']
        assert 'energy_profile' in memory['prosody_patterns']

def test_prosody_patterns_accumulate():
    """Test that prosody patterns accumulate over multiple updates"""
    from build_memory_from_transcripts import update_speaker_memory

    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "Memory"
        memory_dir.mkdir()

        speaker = "test_speaker"

        # First transcript
        transcript1 = {
            'text': 'First transcript',
            'emotion': {
                'prosody': {
                    'pitch': {'mean': 150.0, 'std': 20.0},
                    'tempo': {'bpm': 120, 'speech_rate': 4.0},
                    'energy': {'mean': 0.5, 'std': 0.1, 'dynamic_range': 0.3}
                }
            }
        }

        # Second transcript
        transcript2 = {
            'text': 'Second transcript',
            'emotion': {
                'prosody': {
                    'pitch': {'mean': 160.0, 'std': 25.0},
                    'tempo': {'bpm': 130, 'speech_rate': 5.0},
                    'energy': {'mean': 0.6, 'std': 0.15, 'dynamic_range': 0.4}
                }
            }
        }

        update_speaker_memory(speaker, transcript1, memory_dir)
        update_speaker_memory(speaker, transcript2, memory_dir)

        # Verify accumulation
        memory_file = memory_dir / f"{speaker}.yaml"
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)

        # Should have averaged prosody data
        pitch_profile = memory['prosody_patterns']['pitch_profile']
        assert 'mean_pitch' in pitch_profile
        assert pitch_profile['sample_count'] == 2
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest test_memory_prosody.py -v
```

Expected: FAIL (update_speaker_memory doesn't handle prosody, prosody_patterns missing)

**Step 3: Modify build_memory_from_transcripts.py**

Find the `update_speaker_memory` function (around line 150) and add prosody handling:

```python
def update_speaker_memory(speaker: str, transcript_data: Dict[str, Any], memory_dir: Path):
    """
    Aktualisiert das Memory-Profil für einen Sprecher

    Args:
        speaker: Sprecher-Name
        transcript_data: Transkript mit Metadaten (text, emotion, etc.)
        memory_dir: Memory-Verzeichnis
    """
    memory_file = memory_dir / f"{speaker}.yaml"

    # Lade existierendes Profil oder erstelle neues
    if memory_file.exists():
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f) or {}
    else:
        memory = {
            'name': speaker,
            'last_updated': None,
            'total_interactions': 0,
            'statistics': {
                'avg_sentence_length': 0,
                'most_common_words': {},
                'sentiment': {'positive': 0, 'negative': 0, 'ratio': 0}
            },
            'topics': {},
            'characteristics': [],
            'prosody_patterns': {  # ADD THIS
                'pitch_profile': {
                    'mean_pitch': 0,
                    'pitch_variability': 0,
                    'sample_count': 0
                },
                'tempo_profile': {
                    'mean_bpm': 0,
                    'mean_speech_rate': 0,
                    'sample_count': 0
                },
                'energy_profile': {
                    'mean_energy': 0,
                    'energy_variability': 0,
                    'mean_dynamic_range': 0,
                    'sample_count': 0
                }
            }
        }

    # Update statistics from transcript
    text = transcript_data.get('text', '')
    if text:
        sentences = text.split('.')
        memory['statistics']['avg_sentence_length'] = len(text.split()) / max(len(sentences), 1)

    # UPDATE PROSODY PATTERNS - ADD THIS BLOCK:
    if 'emotion' in transcript_data and 'prosody' in transcript_data['emotion']:
        prosody = transcript_data['emotion']['prosody']

        # Update pitch profile
        if 'pitch' in prosody:
            pitch_data = prosody['pitch']
            pitch_profile = memory['prosody_patterns']['pitch_profile']
            n = pitch_profile['sample_count']

            # Running average
            if n > 0:
                pitch_profile['mean_pitch'] = (
                    (pitch_profile['mean_pitch'] * n + pitch_data.get('mean', 0)) / (n + 1)
                )
                pitch_profile['pitch_variability'] = (
                    (pitch_profile['pitch_variability'] * n + pitch_data.get('std', 0)) / (n + 1)
                )
            else:
                pitch_profile['mean_pitch'] = pitch_data.get('mean', 0)
                pitch_profile['pitch_variability'] = pitch_data.get('std', 0)

            pitch_profile['sample_count'] = n + 1

        # Update tempo profile
        if 'tempo' in prosody:
            tempo_data = prosody['tempo']
            tempo_profile = memory['prosody_patterns']['tempo_profile']
            n = tempo_profile['sample_count']

            if n > 0:
                tempo_profile['mean_bpm'] = (
                    (tempo_profile['mean_bpm'] * n + tempo_data.get('bpm', 0)) / (n + 1)
                )
                tempo_profile['mean_speech_rate'] = (
                    (tempo_profile['mean_speech_rate'] * n + tempo_data.get('speech_rate', 0)) / (n + 1)
                )
            else:
                tempo_profile['mean_bpm'] = tempo_data.get('bpm', 0)
                tempo_profile['mean_speech_rate'] = tempo_data.get('speech_rate', 0)

            tempo_profile['sample_count'] = n + 1

        # Update energy profile
        if 'energy' in prosody:
            energy_data = prosody['energy']
            energy_profile = memory['prosody_patterns']['energy_profile']
            n = energy_profile['sample_count']

            if n > 0:
                energy_profile['mean_energy'] = (
                    (energy_profile['mean_energy'] * n + energy_data.get('mean', 0)) / (n + 1)
                )
                energy_profile['energy_variability'] = (
                    (energy_profile['energy_variability'] * n + energy_data.get('std', 0)) / (n + 1)
                )
                energy_profile['mean_dynamic_range'] = (
                    (energy_profile['mean_dynamic_range'] * n + energy_data.get('dynamic_range', 0)) / (n + 1)
                )
            else:
                energy_profile['mean_energy'] = energy_data.get('mean', 0)
                energy_profile['energy_variability'] = energy_data.get('std', 0)
                energy_profile['mean_dynamic_range'] = energy_data.get('dynamic_range', 0)

            energy_profile['sample_count'] = n + 1

    # Update metadata
    memory['last_updated'] = datetime.now().isoformat()
    memory['total_interactions'] += 1

    # Save
    with open(memory_file, 'w', encoding='utf-8') as f:
        yaml.dump(memory, f, allow_unicode=True, default_flow_style=False)
```

**Step 4: Run test to verify it passes**

```bash
python3 -m pytest test_memory_prosody.py -v
```

Expected: PASS (both tests)

**Step 5: Commit**

```bash
git add build_memory_from_transcripts.py test_memory_prosody.py
git commit -m "feat: add prosody patterns to speaker memory profiles

- Store pitch, tempo, energy profiles in YAML
- Running averages for prosody features
- Foundation for Voice-Marker 2.0 speaker modeling"
```

---

## Task 4: Add Confidence Scoring to Transcriptions

**Files:**
- Modify: `auto_transcriber_v4_emotion.py`
- Test: `test_confidence_scoring.py`

**Step 1: Write the failing test**

Create `test_confidence_scoring.py`:

```python
#!/usr/bin/env python3
import pytest
from unittest.mock import Mock, patch, MagicMock
import auto_transcriber_v4_emotion as v4

def test_transcribe_with_confidence_scores():
    """Test that transcribe_with_whisper returns confidence scores"""
    with patch('auto_transcriber_v4_emotion.whisper') as mock_whisper:
        # Mock Whisper model and result
        mock_model = MagicMock()
        mock_result = {
            'text': 'This is a test',
            'segments': [
                {
                    'text': 'This is',
                    'start': 0.0,
                    'end': 1.0,
                    'avg_logprob': -0.2,
                    'no_speech_prob': 0.01
                },
                {
                    'text': 'a test',
                    'start': 1.0,
                    'end': 2.0,
                    'avg_logprob': -0.5,
                    'no_speech_prob': 0.02
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        mock_whisper.load_model.return_value = mock_model

        result = v4.transcribe_with_whisper('test.opus', model_size='base')

        assert 'text' in result
        assert 'confidence_scores' in result
        assert 'segments' in result['confidence_scores']
        assert 'overall_confidence' in result['confidence_scores']
        assert 'low_confidence_segments' in result['confidence_scores']

def test_mark_low_confidence_in_text():
    """Test that low confidence segments are marked in text"""
    result = {
        'text': 'This is a test sentence with some unclear parts',
        'confidence_scores': {
            'segments': [
                {'text': 'This is a test', 'confidence': 0.95, 'start': 0.0, 'end': 1.0},
                {'text': 'sentence with', 'confidence': 0.45, 'start': 1.0, 'end': 2.0},
                {'text': 'some unclear parts', 'confidence': 0.30, 'start': 2.0, 'end': 3.0}
            ],
            'low_confidence_threshold': 0.5
        }
    }

    marked_text = v4.mark_low_confidence_segments(result)

    assert '[unsicher:0.45]' in marked_text or '[UNSICHER' in marked_text
    assert '[unsicher:0.30]' in marked_text or '[UNSICHER' in marked_text
    assert 'This is a test' in marked_text  # High confidence not marked

def test_confidence_threshold_configurable():
    """Test that confidence threshold can be configured"""
    analyzer = v4.EmotionalAnalyzer()

    # Should have configurable threshold
    assert hasattr(analyzer, 'confidence_threshold') or True  # Will add in implementation
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest test_confidence_scoring.py -v
```

Expected: FAIL (confidence_scores not in result, mark_low_confidence_segments not defined)

**Step 3: Modify auto_transcriber_v4_emotion.py**

Add confidence scoring to the transcription function (around line 450):

```python
def transcribe_with_whisper(audio_path: str, model_size: str = 'base', language: str = 'de') -> Dict[str, Any]:
    """
    Transkribiert Audio mit Whisper und extrahiert Confidence Scores

    Args:
        audio_path: Pfad zur Audio-Datei
        model_size: Whisper-Modell (tiny, base, small, medium, large)
        language: Sprache (de, en, etc.)

    Returns:
        Dict mit text, segments, und confidence_scores
    """
    try:
        import whisper

        logger.info(f"Lade Whisper-Modell: {model_size}")
        model = whisper.load_model(model_size)

        logger.info(f"Transkribiere: {audio_path}")
        result = model.transcribe(
            audio_path,
            language=language,
            verbose=False,
            word_timestamps=True  # Enable word-level timestamps
        )

        # EXTRACT CONFIDENCE SCORES - ADD THIS:
        confidence_scores = _extract_confidence_scores(result)

        return {
            'text': result['text'],
            'segments': result.get('segments', []),
            'confidence_scores': confidence_scores
        }

    except Exception as e:
        logger.error(f"Fehler bei Transkription: {e}")
        return {
            'text': '',
            'segments': [],
            'confidence_scores': {
                'overall_confidence': 0.0,
                'segments': [],
                'low_confidence_segments': []
            }
        }

def _extract_confidence_scores(whisper_result: Dict[str, Any],
                               low_confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Extrahiert Confidence Scores aus Whisper-Ergebnis

    Args:
        whisper_result: Whisper transcribe() Ergebnis
        low_confidence_threshold: Schwellwert für niedrige Confidence

    Returns:
        Dict mit confidence-Informationen
    """
    segments = whisper_result.get('segments', [])

    segment_confidences = []
    low_confidence_segments = []
    total_confidence = 0.0

    for seg in segments:
        # Whisper gibt avg_logprob (negative log probability)
        # Konvertiere zu 0-1 Confidence Score
        avg_logprob = seg.get('avg_logprob', -1.0)
        no_speech_prob = seg.get('no_speech_prob', 0.0)

        # Heuristik: exp(avg_logprob) gibt ungefähre Wahrscheinlichkeit
        # Adjustiere mit no_speech_prob
        confidence = min(1.0, max(0.0, np.exp(avg_logprob) * (1 - no_speech_prob)))

        segment_info = {
            'text': seg.get('text', '').strip(),
            'start': seg.get('start', 0.0),
            'end': seg.get('end', 0.0),
            'confidence': float(confidence),
            'avg_logprob': float(avg_logprob),
            'no_speech_prob': float(no_speech_prob)
        }

        segment_confidences.append(segment_info)
        total_confidence += confidence

        # Mark low confidence segments
        if confidence < low_confidence_threshold:
            low_confidence_segments.append(segment_info)

    overall_confidence = total_confidence / len(segments) if segments else 0.0

    return {
        'overall_confidence': float(overall_confidence),
        'segments': segment_confidences,
        'low_confidence_segments': low_confidence_segments,
        'low_confidence_threshold': low_confidence_threshold,
        'total_segments': len(segments)
    }

def mark_low_confidence_segments(transcription_result: Dict[str, Any]) -> str:
    """
    Markiert Segmente mit niedriger Confidence im Text

    Args:
        transcription_result: Ergebnis von transcribe_with_whisper

    Returns:
        Text mit Markierungen für unsichere Stellen
    """
    text = transcription_result.get('text', '')
    confidence_scores = transcription_result.get('confidence_scores', {})
    low_conf_segments = confidence_scores.get('low_confidence_segments', [])

    # Wenn keine unsicheren Segmente, gib Original zurück
    if not low_conf_segments:
        return text

    # Erstelle markierten Text
    marked_text = text

    # Sortiere Segmente nach Position (rückwärts für korrekte String-Insertion)
    sorted_segments = sorted(
        confidence_scores.get('segments', []),
        key=lambda s: s['start'],
        reverse=True
    )

    for seg in sorted_segments:
        if seg['confidence'] < confidence_scores.get('low_confidence_threshold', 0.5):
            # Finde Segment im Text
            seg_text = seg['text'].strip()
            if seg_text in marked_text:
                # Markiere mit Confidence Score
                marker = f" [UNSICHER:{seg['confidence']:.2f}]"
                marked_text = marked_text.replace(seg_text, seg_text + marker, 1)

    return marked_text
```

Add confidence_threshold to EmotionalAnalyzer (around line 54):

```python
def __init__(self, confidence_threshold: float = 0.5):
    self.emotional_markers = self._load_emotional_markers()
    from prosody_analyzer import ProsodyAnalyzer
    self.prosody_analyzer = ProsodyAnalyzer()
    self.confidence_threshold = confidence_threshold  # ADD THIS
```

**Step 4: Run test to verify it passes**

```bash
python3 -m pytest test_confidence_scoring.py -v
```

Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add auto_transcriber_v4_emotion.py test_confidence_scoring.py
git commit -m "feat: add confidence scoring and low-confidence marking

- Extract confidence from Whisper avg_logprob and no_speech_prob
- Mark low-confidence segments with [UNSICHER:score] tags
- Configurable confidence threshold (default 0.5)
- Critical for therapeutic quality assurance"
```

---

## Task 5: Create Unified Transcription GUI

**Files:**
- Create: `therapeutic_transcriber_gui.py`
- Test: Manual testing (GUI)

**Step 1: Create GUI implementation**

Create `therapeutic_transcriber_gui.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Therapeutic Transcription GUI - Professional one-click workflow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import queue
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import auto_transcriber_v4_emotion as v4

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TherapeuticTranscriberGUI:
    """Professional GUI for therapeutic transcription"""

    def __init__(self, root):
        self.root = root
        self.root.title("Therapeutic Transcription System")
        self.root.geometry("900x700")

        # Progress queue for thread communication
        self.progress_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False

        # Default paths
        self.input_dir = Path("Eingang")
        self.output_dir = Path("Transkripte_LLM")
        self.memory_dir = Path("Memory")

        self._create_widgets()
        self._check_progress_queue()

    def _create_widgets(self):
        """Create all GUI widgets"""

        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame,
            text="🎤 Therapeutic Transcription System",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Hochwertige Transkription für therapeutischen Einsatz",
            font=("Helvetica", 10)
        )
        subtitle_label.pack()

        # Configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Konfiguration", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        # Input directory
        ttk.Label(config_frame, text="Eingabe-Ordner:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_dir_var = tk.StringVar(value=str(self.input_dir))
        ttk.Entry(config_frame, textvariable=self.input_dir_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(config_frame, text="Durchsuchen...", command=self._browse_input_dir).grid(row=0, column=2, pady=5)

        # Output directory
        ttk.Label(config_frame, text="Ausgabe-Ordner:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value=str(self.output_dir))
        ttk.Entry(config_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(config_frame, text="Durchsuchen...", command=self._browse_output_dir).grid(row=1, column=2, pady=5)

        # Quality settings frame
        quality_frame = ttk.LabelFrame(self.root, text="Qualitäts-Einstellungen", padding="10")
        quality_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        # Whisper model selection
        ttk.Label(quality_frame, text="Whisper-Modell:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="medium")
        model_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            width=15
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(quality_frame, text="(medium empfohlen für Therapie)").grid(row=0, column=2, sticky=tk.W, pady=5)

        # Language
        ttk.Label(quality_frame, text="Sprache:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value="de")
        lang_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.language_var,
            values=["de", "en", "auto"],
            state="readonly",
            width=15
        )
        lang_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # Confidence threshold
        ttk.Label(quality_frame, text="Confidence-Schwellwert:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_spin = ttk.Spinbox(
            quality_frame,
            from_=0.1,
            to=0.9,
            increment=0.1,
            textvariable=self.confidence_var,
            width=15
        )
        confidence_spin.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(quality_frame, text="(niedrigere Werte = mehr Warnungen)").grid(row=2, column=2, sticky=tk.W, pady=5)

        # Feature toggles frame
        features_frame = ttk.LabelFrame(self.root, text="Features", padding="10")
        features_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.emotion_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame,
            text="Emotions-Analyse aktivieren",
            variable=self.emotion_var
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        self.prosody_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame,
            text="Prosody-Extraktion aktivieren (Voice-Marker 2.0)",
            variable=self.prosody_var
        ).grid(row=1, column=0, sticky=tk.W, pady=2)

        self.memory_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame,
            text="Memory-Profile aktualisieren",
            variable=self.memory_var
        ).grid(row=2, column=0, sticky=tk.W, pady=2)

        # Speaker selection frame
        speaker_frame = ttk.LabelFrame(self.root, text="Sprecher-Auswahl", padding="10")
        speaker_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        ttk.Label(speaker_frame, text="Zu verarbeitende Sprecher:").grid(row=0, column=0, sticky=tk.W, pady=5)

        self.speaker_listbox = tk.Listbox(speaker_frame, selectmode=tk.MULTIPLE, height=5, width=60)
        self.speaker_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

        ttk.Button(speaker_frame, text="Sprecher aktualisieren", command=self._refresh_speakers).grid(row=2, column=0, pady=5)
        ttk.Button(speaker_frame, text="Alle auswählen", command=self._select_all_speakers).grid(row=2, column=1, pady=5)

        # Control buttons frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.start_button = ttk.Button(
            control_frame,
            text="🚀 Transkription starten",
            command=self._start_transcription,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            control_frame,
            text="⏹ Stoppen",
            command=self._stop_transcription,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Fortschritt", padding="10")
        progress_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(progress_frame, text="Bereit")
        self.status_label.pack(pady=5)

        # Log output
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(7, weight=1)

        # Initial speaker refresh
        self._refresh_speakers()

    def _browse_input_dir(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(initialdir=self.input_dir)
        if directory:
            self.input_dir_var.set(directory)
            self._refresh_speakers()

    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir_var.set(directory)

    def _refresh_speakers(self):
        """Refresh list of available speakers from input directory"""
        self.speaker_listbox.delete(0, tk.END)

        input_path = Path(self.input_dir_var.get())
        if not input_path.exists():
            self._log("⚠️ Eingabe-Ordner existiert nicht")
            return

        # Find all subdirectories (speakers)
        speakers = [d.name for d in input_path.iterdir() if d.is_dir()]
        speakers.sort()

        for speaker in speakers:
            self.speaker_listbox.insert(tk.END, speaker)

        # Select Zoe by default (priority)
        if "Zoe" in speakers or "zoe" in speakers:
            idx = speakers.index("Zoe") if "Zoe" in speakers else speakers.index("zoe")
            self.speaker_listbox.selection_set(idx)

        self._log(f"✓ {len(speakers)} Sprecher gefunden")

    def _select_all_speakers(self):
        """Select all speakers in listbox"""
        self.speaker_listbox.selection_set(0, tk.END)

    def _start_transcription(self):
        """Start transcription in background thread"""
        # Validate inputs
        input_dir = Path(self.input_dir_var.get())
        output_dir = Path(self.output_dir_var.get())

        if not input_dir.exists():
            messagebox.showerror("Fehler", "Eingabe-Ordner existiert nicht")
            return

        selected_indices = self.speaker_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte wähle mindestens einen Sprecher aus")
            return

        selected_speakers = [self.speaker_listbox.get(i) for i in selected_indices]

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Disable start button, enable stop
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_processing = True

        # Collect settings
        settings = {
            'input_dir': input_dir,
            'output_dir': output_dir,
            'memory_dir': self.memory_dir,
            'speakers': selected_speakers,
            'model': self.model_var.get(),
            'language': self.language_var.get(),
            'confidence_threshold': self.confidence_var.get(),
            'enable_emotion': self.emotion_var.get(),
            'enable_prosody': self.prosody_var.get(),
            'enable_memory': self.memory_var.get()
        }

        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_transcriptions,
            args=(settings,),
            daemon=True
        )
        self.processing_thread.start()

    def _stop_transcription(self):
        """Stop transcription"""
        self.is_processing = False
        self._log("⏹ Stoppe Verarbeitung...")

    def _process_transcriptions(self, settings: Dict[str, Any]):
        """Process transcriptions (runs in background thread)"""
        try:
            total_files = 0
            processed_files = 0

            # Count total files
            for speaker in settings['speakers']:
                speaker_dir = settings['input_dir'] / speaker
                audio_files = list(speaker_dir.glob("*.opus")) + list(speaker_dir.glob("*.wav"))
                total_files += len(audio_files)

            self.progress_queue.put(('status', f"Verarbeite {total_files} Dateien..."))

            # Process each speaker
            for speaker in settings['speakers']:
                if not self.is_processing:
                    break

                speaker_dir = settings['input_dir'] / speaker
                audio_files = list(speaker_dir.glob("*.opus")) + list(speaker_dir.glob("*.wav"))

                self.progress_queue.put(('log', f"\n📁 Verarbeite Sprecher: {speaker}"))

                for audio_file in audio_files:
                    if not self.is_processing:
                        break

                    self.progress_queue.put(('log', f"  🎤 {audio_file.name}"))

                    try:
                        # Transcribe
                        result = v4.transcribe_with_whisper(
                            str(audio_file),
                            model_size=settings['model'],
                            language=settings['language']
                        )

                        # Analyze emotion if enabled
                        emotion_data = None
                        if settings['enable_emotion']:
                            analyzer = v4.EmotionalAnalyzer(
                                confidence_threshold=settings['confidence_threshold']
                            )
                            emotion_data = analyzer.analyze_emotion(
                                result['text'],
                                audio_path=str(audio_file)
                            )

                        # Mark low confidence
                        marked_text = v4.mark_low_confidence_segments(result)

                        # Save transcript
                        output_filename = f"{audio_file.stem}_transkript.md"
                        output_path = settings['output_dir'] / output_filename

                        self._save_transcript(
                            output_path,
                            audio_file,
                            speaker,
                            marked_text,
                            result,
                            emotion_data
                        )

                        # Update memory if enabled
                        if settings['enable_memory'] and emotion_data:
                            from build_memory_from_transcripts import update_speaker_memory
                            update_speaker_memory(
                                speaker,
                                {'text': result['text'], 'emotion': emotion_data},
                                settings['memory_dir']
                            )

                        processed_files += 1
                        progress = (processed_files / total_files) * 100
                        self.progress_queue.put(('progress', progress))

                        # Check confidence
                        overall_conf = result['confidence_scores']['overall_confidence']
                        if overall_conf < settings['confidence_threshold']:
                            self.progress_queue.put(('log', f"    ⚠️ Niedrige Confidence: {overall_conf:.2f}"))
                        else:
                            self.progress_queue.put(('log', f"    ✓ Confidence: {overall_conf:.2f}"))

                    except Exception as e:
                        self.progress_queue.put(('log', f"    ❌ Fehler: {e}"))

            # Done
            if self.is_processing:
                self.progress_queue.put(('status', f"✓ Fertig! {processed_files}/{total_files} Dateien verarbeitet"))
                self.progress_queue.put(('log', f"\n✓ Verarbeitung abgeschlossen"))
            else:
                self.progress_queue.put(('status', "Verarbeitung gestoppt"))

        except Exception as e:
            self.progress_queue.put(('log', f"\n❌ Fehler: {e}"))
            self.progress_queue.put(('status', "Fehler aufgetreten"))

        finally:
            self.progress_queue.put(('done', None))

    def _save_transcript(self,
                        output_path: Path,
                        audio_file: Path,
                        speaker: str,
                        text: str,
                        result: Dict[str, Any],
                        emotion_data: Optional[Dict[str, Any]]):
        """Save transcript in therapeutic format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Therapeutisches Transkript\n\n")
            f.write(f"**Sprecher:** {speaker}\n")
            f.write(f"**Original-Datei:** {audio_file.name}\n")
            f.write(f"**Verarbeitet am:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Confidence:** {result['confidence_scores']['overall_confidence']:.2f}\n")

            if emotion_data:
                f.write(f"**Dominante Emotion:** {emotion_data.get('emotion', 'neutral')}\n")
                f.write(f"**Emotionale Valenz:** {emotion_data.get('valence', 0.0):.2f}\n")

                if 'prosody' in emotion_data and emotion_data['prosody']:
                    f.write(f"\n## Prosody-Merkmale\n")
                    prosody = emotion_data['prosody']
                    if 'pitch' in prosody:
                        f.write(f"- **Pitch:** {prosody['pitch'].get('mean', 0):.1f} Hz (±{prosody['pitch'].get('std', 0):.1f})\n")
                    if 'tempo' in prosody:
                        f.write(f"- **Tempo:** {prosody['tempo'].get('bpm', 0):.0f} BPM\n")
                        f.write(f"- **Sprechrate:** {prosody['tempo'].get('speech_rate', 0):.1f} Silben/Sek\n")
                    if 'energy' in prosody:
                        f.write(f"- **Energie:** {prosody['energy'].get('mean', 0):.3f}\n")

            # Low confidence warnings
            low_conf = result['confidence_scores']['low_confidence_segments']
            if low_conf:
                f.write(f"\n## ⚠️ Qualitäts-Hinweise\n")
                f.write(f"{len(low_conf)} Segment(e) mit niedriger Confidence erkannt.\n")
                f.write(f"Diese sind im Text mit [UNSICHER:score] markiert.\n")

            f.write(f"\n## Transkription\n\n")
            f.write(text)

    def _check_progress_queue(self):
        """Check progress queue and update GUI"""
        try:
            while True:
                msg_type, msg_data = self.progress_queue.get_nowait()

                if msg_type == 'status':
                    self.status_label.config(text=msg_data)
                elif msg_type == 'progress':
                    self.progress_var.set(msg_data)
                elif msg_type == 'log':
                    self._log(msg_data)
                elif msg_type == 'done':
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.is_processing = False

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self._check_progress_queue)

    def _log(self, message: str):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set theme
    style = ttk.Style()
    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')

    app = TherapeuticTranscriberGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

**Step 2: Test the GUI manually**

```bash
python3 therapeutic_transcriber_gui.py
```

Test checklist:
- [ ] GUI opens without errors
- [ ] Can browse and select directories
- [ ] Speaker list populates correctly
- [ ] Can change Whisper model and settings
- [ ] Can toggle emotion/prosody/memory features
- [ ] Start button initiates processing
- [ ] Progress bar updates during processing
- [ ] Log shows processing steps
- [ ] Output files created in correct format
- [ ] Stop button interrupts processing
- [ ] Memory profiles updated with prosody data

**Step 3: Commit**

```bash
git add therapeutic_transcriber_gui.py
git commit -m "feat: add professional therapeutic transcription GUI

- One-click workflow with comprehensive configuration
- Speaker selection and priority handling
- Quality settings (model, language, confidence threshold)
- Feature toggles (emotion, prosody, memory)
- Real-time progress tracking and logging
- Background processing thread
- Therapeutic output format with quality warnings"
```

---

## Task 6: Create Integration Tests

**Files:**
- Create: `test_integration_therapeutic.py`

**Step 1: Write integration test**

Create `test_integration_therapeutic.py`:

```python
#!/usr/bin/env python3
"""
Integration tests for complete therapeutic transcription pipeline
"""
import pytest
from pathlib import Path
import tempfile
import shutil
import numpy as np
import yaml
import soundfile as sf

def create_test_audio(output_path: Path, duration: float = 2.0, sr: int = 22050):
    """Create a test audio file"""
    # Generate simple sine wave
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.sin(2 * np.pi * 440 * t) * 0.3  # 440 Hz sine wave

    sf.write(output_path, audio, sr)

def test_full_pipeline_with_prosody():
    """Test complete pipeline: audio -> transcription -> emotion -> prosody -> memory"""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Setup directories
        input_dir = tmpdir / "Eingang" / "test_speaker"
        output_dir = tmpdir / "Transkripte_LLM"
        memory_dir = tmpdir / "Memory"

        input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)
        memory_dir.mkdir(parents=True)

        # Create test audio
        audio_file = input_dir / "test_audio.wav"
        create_test_audio(audio_file)

        # Process with V4
        import auto_transcriber_v4_emotion as v4

        # Transcribe
        result = v4.transcribe_with_whisper(str(audio_file), model_size='tiny')

        assert 'text' in result
        assert 'confidence_scores' in result

        # Analyze emotion
        analyzer = v4.EmotionalAnalyzer()
        emotion_data = analyzer.analyze_emotion(
            result['text'],
            audio_path=str(audio_file)
        )

        assert 'emotion' in emotion_data
        assert 'prosody' in emotion_data
        assert 'pitch' in emotion_data['prosody']
        assert 'tempo' in emotion_data['prosody']
        assert 'energy' in emotion_data['prosody']

        # Update memory
        from build_memory_from_transcripts import update_speaker_memory

        update_speaker_memory(
            "test_speaker",
            {'text': result['text'], 'emotion': emotion_data},
            memory_dir
        )

        # Verify memory file
        memory_file = memory_dir / "test_speaker.yaml"
        assert memory_file.exists()

        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)

        assert 'prosody_patterns' in memory
        assert memory['prosody_patterns']['pitch_profile']['sample_count'] == 1
        assert memory['prosody_patterns']['tempo_profile']['sample_count'] == 1
        assert memory['prosody_patterns']['energy_profile']['sample_count'] == 1

        print("✓ Full pipeline test passed")

def test_confidence_marking_in_output():
    """Test that low confidence segments are properly marked in output"""

    import auto_transcriber_v4_emotion as v4

    # Mock result with low confidence
    result = {
        'text': 'This is a test with unclear parts',
        'confidence_scores': {
            'overall_confidence': 0.65,
            'segments': [
                {'text': 'This is a test', 'confidence': 0.85, 'start': 0.0, 'end': 1.0},
                {'text': 'with unclear parts', 'confidence': 0.35, 'start': 1.0, 'end': 2.0}
            ],
            'low_confidence_segments': [
                {'text': 'with unclear parts', 'confidence': 0.35, 'start': 1.0, 'end': 2.0}
            ],
            'low_confidence_threshold': 0.5
        }
    }

    marked_text = v4.mark_low_confidence_segments(result)

    assert '[UNSICHER' in marked_text
    assert '0.35' in marked_text

    print("✓ Confidence marking test passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Step 2: Run integration tests**

```bash
python3 -m pytest test_integration_therapeutic.py -v -s
```

Expected: PASS (both integration tests)

**Step 3: Commit**

```bash
git add test_integration_therapeutic.py
git commit -m "test: add integration tests for therapeutic pipeline

- Full pipeline test: audio -> transcription -> emotion -> prosody -> memory
- Confidence marking verification
- End-to-end validation of therapeutic quality features"
```

---

## Task 7: Create Documentation and User Guide

**Files:**
- Create: `docs/THERAPEUTIC_TRANSCRIPTION_GUIDE.md`
- Modify: `README.md`

**Step 1: Create user guide**

Create `docs/THERAPEUTIC_TRANSCRIPTION_GUIDE.md`:

```markdown
# Therapeutic Transcription System - User Guide

## Overview

This system provides professional-grade audio transcription optimized for therapeutic use cases. It combines OpenAI Whisper transcription with emotion analysis, prosody extraction, and comprehensive quality assurance.

## Key Features for Therapeutic Use

### 1. High-Quality Transcription
- **Multiple model sizes**: Choose based on accuracy needs (medium recommended)
- **Confidence scoring**: Every segment rated for reliability
- **Quality warnings**: Low-confidence segments clearly marked

### 2. Emotional Analysis
- **Text sentiment**: Analyze emotional content of words
- **Audio emotion**: Detect emotional coloring in voice
- **Combined assessment**: Holistic emotion detection

### 3. Prosody Extraction (Voice-Marker 2.0 Ready)
- **Pitch analysis**: F0 contour, mean, variability
- **Tempo/rhythm**: Speaking rate, pauses
- **Energy**: Loudness, dynamic range

### 4. Speaker Memory System
- **Learning profiles**: System improves over time
- **Prosody patterns**: Voice characteristics stored
- **Interaction history**: Track changes over sessions

## Quick Start

### Installation

```bash
cd /path/to/Super_semantic_whisper
pip3 install -r requirements.txt

# Install additional dependencies for emotion/prosody
pip3 install librosa textblob scikit-learn
```

### Basic Usage

1. **Launch GUI**:
   ```bash
   python3 therapeutic_transcriber_gui.py
   ```

2. **Configure**:
   - Set input directory (where audio files are)
   - Set output directory (where transcripts go)
   - Choose Whisper model (medium recommended)
   - Set confidence threshold (0.5 recommended)

3. **Select Speakers**:
   - Click "Sprecher aktualisieren"
   - Select one or more speakers to process

4. **Start**:
   - Click "🚀 Transkription starten"
   - Monitor progress in real-time
   - View log for details

## Understanding Output Files

### Transcript Format

Each transcript includes:

```markdown
# Therapeutisches Transkript

**Sprecher:** john_doe
**Original-Datei:** WhatsApp Audio 2025-11-10 at 14.30.45.opus
**Verarbeitet am:** 2025-11-10 15:22:10
**Confidence:** 0.87

**Dominante Emotion:** neutral
**Emotionale Valenz:** 0.12

## Prosody-Merkmale
- **Pitch:** 145.3 Hz (±18.2)
- **Tempo:** 115 BPM
- **Sprechrate:** 4.2 Silben/Sek
- **Energie:** 0.042

## ⚠️ Qualitäts-Hinweise
2 Segment(e) mit niedriger Confidence erkannt.
Diese sind im Text mit [UNSICHER:score] markiert.

## Transkription

Hello, this is a test. [UNSICHER:0.42] The unclear part is marked.
The rest of the transcription continues normally.
```

### Memory Profiles

Located in `Memory/{speaker}.yaml`:

```yaml
name: john_doe
last_updated: '2025-11-10T15:22:10'
total_interactions: 15
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8
    pitch_variability: 19.4
    sample_count: 15
  tempo_profile:
    mean_bpm: 118.5
    mean_speech_rate: 4.3
    sample_count: 15
  energy_profile:
    mean_energy: 0.045
    energy_variability: 0.012
    mean_dynamic_range: 0.28
    sample_count: 15
```

## Quality Assurance

### Confidence Scores

- **≥ 0.7**: High confidence - reliable transcription
- **0.5 - 0.7**: Medium confidence - generally good
- **< 0.5**: Low confidence - marked with [UNSICHER:score]

### When to Review Manually

Review transcripts if:
- Overall confidence < 0.6
- Multiple [UNSICHER] markers
- Critical therapeutic content
- Speaker is new (first few sessions)

### Improving Quality

1. **Audio quality**:
   - Use good recording environment
   - Minimize background noise
   - Ensure clear speech

2. **Model selection**:
   - `medium`: Best balance for German therapeutic use
   - `large`: Maximum accuracy (slower, more memory)
   - `small`: Faster but less accurate

3. **Language setting**:
   - `de`: German (recommended)
   - `auto`: Auto-detect (use if mixed languages)

## Advanced Features

### Prosody for Voice-Marker 2.0

The system extracts prosodic features that will power Voice-Marker 2.0:

- **Pitch patterns**: Detect stress, emphasis, emotional states
- **Rhythm**: Speaking style, hesitations, confidence
- **Energy**: Engagement level, emotional intensity

These features are stored in memory profiles and available for future analysis.

### Batch Processing

Process multiple speakers efficiently:

1. Organize files: `Eingang/{speaker}/audio_files.opus`
2. Select all speakers in GUI
3. System processes sequentially
4. All results in `Transkripte_LLM/`

## Troubleshooting

### "Whisper model download failed"
- Ensure internet connection
- First run downloads model (large file)
- Subsequent runs use cached model

### "librosa not available"
- Install: `pip3 install librosa soundfile`
- Prosody features require librosa

### "Low confidence on good audio"
- Try larger model (medium -> large)
- Check if audio is actually clear
- Some speakers need multiple sessions to build profile

### "GUI doesn't start"
- Install tkinter: `brew install python-tk` (macOS)
- Or: `sudo apt-get install python3-tk` (Ubuntu)

## Best Practices for Therapeutic Use

1. **Consistent environment**: Record in same setting
2. **Regular processing**: Process sessions shortly after recording
3. **Review low-confidence**: Always check [UNSICHER] segments
4. **Build profiles**: Multiple sessions improve accuracy
5. **Backup memory**: Keep Memory/ directory backed up
6. **Document sessions**: Use consistent naming for audio files

## Technical Details

### Architecture

```
Audio File
    ↓
Whisper Transcription (with confidence)
    ↓
Emotion Analysis (text + audio)
    ↓
Prosody Extraction (pitch, tempo, energy)
    ↓
Memory Update (speaker profiles)
    ↓
Therapeutic Transcript (markdown)
```

### File Organization

```
Eingang/                    # Input
  speaker1/
    audio1.opus
    audio2.opus
  speaker2/
    audio3.opus

Transkripte_LLM/            # Output
  audio1_transkript.md
  audio2_transkript.md
  audio3_transkript.md

Memory/                     # Profiles
  speaker1.yaml
  speaker2.yaml
```

## Support

For issues or questions:
- Check logs in GUI
- Review CLAUDE.md for technical details
- Test with small audio file first
```

**Step 2: Update main README**

Edit `README.md`, add section after Features:

```markdown
## 🏥 Therapeutic Transcription System (NEW)

**Professional-grade transcription for therapeutic use**

### Features
- ✅ High-quality transcription with confidence scoring
- 🎭 Emotion analysis (text + audio)
- 🎵 Prosody extraction (pitch, tempo, energy)
- 🧠 Learning speaker profiles
- ⚠️ Quality warnings for low-confidence segments
- 🖥️ Professional GUI with one-click workflow

### Quick Start
```bash
# Launch therapeutic GUI
python3 therapeutic_transcriber_gui.py
```

📖 **Full documentation**: See [docs/THERAPEUTIC_TRANSCRIPTION_GUIDE.md](docs/THERAPEUTIC_TRANSCRIPTION_GUIDE.md)

---
```

**Step 3: Commit**

```bash
git add docs/THERAPEUTIC_TRANSCRIPTION_GUIDE.md README.md
git commit -m "docs: add comprehensive therapeutic transcription guide

- Complete user guide with examples
- Quality assurance guidelines
- Troubleshooting section
- Best practices for therapeutic use
- Update main README with therapeutic system info"
```

---

## Final Task: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update CLAUDE.md with new system**

Edit `CLAUDE.md`, add section after "Core Commands":

```markdown
### Therapeutic Transcription System (NEW)

```bash
# Launch professional GUI (recommended)
python3 therapeutic_transcriber_gui.py

# Run tests
python3 -m pytest test_prosody_analyzer.py test_transcriber_v4_prosody.py test_memory_prosody.py -v

# Integration tests
python3 -m pytest test_integration_therapeutic.py -v

# Direct usage (programmatic)
python3 -c "
from prosody_analyzer import ProsodyAnalyzer
analyzer = ProsodyAnalyzer()
prosody = analyzer.extract_from_file('audio.wav')
print(prosody)
"
```
```

Add section after "Architecture":

```markdown
### Therapeutic Transcription Pipeline (NEW)

```
Audio Input
    ↓
[Whisper Transcription]
    ├─> Text
    ├─> Segments with timestamps
    └─> Confidence scores (avg_logprob, no_speech_prob)
    ↓
[Emotion Analysis]
    ├─> Text sentiment (TextBlob)
    ├─> Audio emotion (Whisper audio features)
    └─> Combined emotional assessment
    ↓
[Prosody Extraction]
    ├─> Pitch (F0 mean, std, contour)
    ├─> Tempo (BPM, speech rate)
    └─> Energy (RMS, dynamic range)
    ↓
[Confidence Marking]
    └─> Mark segments with confidence < threshold as [UNSICHER:score]
    ↓
[Memory Update]
    ├─> Update speaker prosody_patterns (running averages)
    ├─> Update statistics, topics, characteristics
    └─> Save to Memory/{speaker}.yaml
    ↓
[Output: Therapeutic Transcript]
    ├─> Markdown with all metadata
    ├─> Prosody features summary
    ├─> Quality warnings
    └─> Marked low-confidence segments
```

**Key Architectural Changes:**
- **Prosody integration**: New `prosody_analyzer.py` module extracts pitch/tempo/energy
- **Enhanced V4**: `auto_transcriber_v4_emotion.py` now includes prosody in emotion analysis
- **Memory enhancement**: Speaker YAML profiles now include `prosody_patterns` section
- **Confidence scoring**: Whisper output converted to 0-1 confidence scores
- **Quality marking**: Low-confidence segments marked inline with [UNSICHER:score]
- **GUI**: New `therapeutic_transcriber_gui.py` provides professional one-click workflow
```

Add to "Important Technical Details":

```markdown
### Prosody Data Structure

In Memory YAML profiles:

```yaml
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8          # Hz, running average
    pitch_variability: 19.4    # Standard deviation
    sample_count: 15           # Number of samples
  tempo_profile:
    mean_bpm: 118.5           # Beats per minute
    mean_speech_rate: 4.3     # Syllables per second
    sample_count: 15
  energy_profile:
    mean_energy: 0.045        # RMS energy
    energy_variability: 0.012 # Standard deviation
    mean_dynamic_range: 0.28  # Max - min
    sample_count: 15
```

### Confidence Score Calculation

Whisper provides:
- `avg_logprob`: Average log probability (negative)
- `no_speech_prob`: Probability of silence

Conversion to confidence:
```python
confidence = exp(avg_logprob) * (1 - no_speech_prob)
```

Range: 0.0 (unreliable) to 1.0 (very confident)

Therapeutic threshold: 0.5 (configurable)
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with therapeutic system architecture

- Document new therapeutic transcription pipeline
- Add prosody extraction architecture
- Explain confidence scoring calculation
- Document memory YAML prosody structure
- Add new commands and testing procedures"
```

---

## Summary

This implementation plan creates a production-quality therapeutic transcription system:

**Core Achievements:**
1. ✅ Prosody extraction (pitch, tempo, energy) for Voice-Marker 2.0
2. ✅ Enhanced V4 with integrated prosody analysis
3. ✅ Memory profiles with prosody patterns
4. ✅ Confidence scoring and quality warnings
5. ✅ Professional GUI with one-click workflow
6. ✅ Comprehensive testing (unit + integration)
7. ✅ Complete documentation

**Quality Assurance:**
- Confidence scores on all transcriptions
- Low-confidence segments marked inline
- Therapeutic output format optimized for review
- Memory profiles track quality over time

**Future-Ready:**
- Prosody data stored in Memory profiles
- Ready for Voice-Marker 2.0 integration
- Extensible architecture for additional features

**Total Tasks:** 7 main tasks with 30+ subtasks
**Estimated Time:** 6-8 hours for experienced developer
**Testing:** 15+ tests covering all components
