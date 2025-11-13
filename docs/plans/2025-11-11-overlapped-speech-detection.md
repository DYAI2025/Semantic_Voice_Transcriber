# Overlapped Speech Detection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Add Overlapped Speech Detection (OSD) to identify when multiple speakers talk simultaneously in therapeutic transcripts.

**Architecture:** Extend existing `speaker_diarizer.py` with pyannote.audio's `OverlappedSpeechDetection` pipeline. Integrate OSD markers into all output formats (Markdown, JSON, HTML, PDF, CSV) alongside existing prosody markers. OSD runs parallel to diarization.

**Tech Stack:** pyannote.audio 4.0, pyannote/segmentation-3.0, existing SVT infrastructure

---

## Task 1: Extend SpeakerDiarizer with OSD Pipeline

**Files:**
- Modify: `speaker_diarizer.py:1-250`
- Test: `test_overlapped_speech_detection.py` (new)

**Step 1: Write failing test for OSD pipeline**

Create `test_overlapped_speech_detection.py`:

```python
#!/usr/bin/env python3
import pytest
from pathlib import Path
from speaker_diarizer import SpeakerDiarizer
import os

# Skip if no HF token available
HF_TOKEN = os.getenv('HF_TOKEN')
pytestmark = pytest.mark.skipif(
    not HF_TOKEN,
    reason="HF_TOKEN not set"
)


def test_overlapped_speech_detection_initialization():
    """Test OSD pipeline can be initialized"""
    diarizer = SpeakerDiarizer(use_auth_token=HF_TOKEN)
    diarizer._load_osd_pipeline()

    assert diarizer.osd_pipeline is not None


def test_detect_overlapped_speech_returns_segments():
    """Test OSD returns list of overlap segments"""
    diarizer = SpeakerDiarizer(use_auth_token=HF_TOKEN)

    # Use test audio file (create dummy if needed)
    test_audio = Path("test_audio_overlap.wav")
    if not test_audio.exists():
        pytest.skip("Test audio not available")

    overlaps = diarizer.detect_overlapped_speech(
        test_audio,
        min_duration_on=0.0,
        min_duration_off=0.0
    )

    assert isinstance(overlaps, list)
    # Each overlap has start, end, duration
    if len(overlaps) > 0:
        assert 'start' in overlaps[0]
        assert 'end' in overlaps[0]
        assert 'duration' in overlaps[0]


def test_overlapped_speech_output_format():
    """Test overlap segments have correct format"""
    diarizer = SpeakerDiarizer(use_auth_token=HF_TOKEN)
    test_audio = Path("test_audio_overlap.wav")

    if not test_audio.exists():
        pytest.skip("Test audio not available")

    overlaps = diarizer.detect_overlapped_speech(test_audio)

    for overlap in overlaps:
        assert overlap['start'] >= 0
        assert overlap['end'] > overlap['start']
        assert overlap['duration'] == overlap['end'] - overlap['start']
        assert 'overlap_type' in overlap  # e.g., "simultaneous_speech"
```

**Step 2: Run test to verify it fails**

Run: `pytest test_overlapped_speech_detection.py::test_overlapped_speech_detection_initialization -v`

Expected: FAIL with "AttributeError: 'SpeakerDiarizer' object has no attribute '_load_osd_pipeline'"

**Step 3: Implement OSD pipeline in SpeakerDiarizer**

Modify `speaker_diarizer.py`, add after `_load_pipeline` method (around line 80):

```python
def _load_osd_pipeline(self):
    """Load pyannote.audio Overlapped Speech Detection pipeline (lazy loading)"""
    if self.osd_pipeline is not None:
        return

    try:
        from pyannote.audio.pipelines import OverlappedSpeechDetection

        logger.info("Loading pyannote Overlapped Speech Detection pipeline...")

        # Load segmentation model first
        if self.pipeline is None:
            self._load_pipeline()

        # Create OSD pipeline using the segmentation model
        self.osd_pipeline = OverlappedSpeechDetection(
            segmentation=self.pipeline.segmentation_model
        )

        logger.info("OSD pipeline loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load OSD pipeline: {e}")
        raise


def detect_overlapped_speech(
    self,
    audio_path: Path,
    min_duration_on: float = 0.0,
    min_duration_off: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Detect overlapped speech regions (multiple speakers talking simultaneously)

    Args:
        audio_path: Path to audio file
        min_duration_on: Remove overlapped speech regions shorter than this (seconds)
        min_duration_off: Fill non-overlapped speech regions shorter than this (seconds)

    Returns:
        List of overlap segments with format:
        [
            {
                'start': 12.5,
                'end': 14.2,
                'duration': 1.7,
                'overlap_type': 'simultaneous_speech'
            },
            ...
        ]
    """
    self._load_osd_pipeline()

    logger.info(f"Running overlapped speech detection on {audio_path.name}...")

    # Configure hyperparameters
    HYPER_PARAMETERS = {
        "min_duration_on": min_duration_on,
        "min_duration_off": min_duration_off
    }
    self.osd_pipeline.instantiate(HYPER_PARAMETERS)

    # Run OSD
    try:
        osd_annotation = self.osd_pipeline(str(audio_path))
    except Exception as e:
        logger.error(f"OSD failed: {e}")
        raise

    # Convert pyannote format to our format
    overlaps = []
    for segment, _, label in osd_annotation.itertracks(yield_label=True):
        overlaps.append({
            'start': segment.start,
            'end': segment.end,
            'duration': segment.end - segment.start,
            'overlap_type': 'simultaneous_speech'
        })

    logger.info(
        f"OSD complete: Found {len(overlaps)} overlapped speech regions"
    )

    return overlaps
```

Also modify `__init__` method to add `self.osd_pipeline = None` (around line 65):

```python
def __init__(
    self,
    use_auth_token: Optional[str] = None,
    device: Optional[str] = None,
    min_speakers: int = 1,
    max_speakers: int = 10
):
    # ... existing code ...

    # Pipeline will be loaded on first use
    self.pipeline = None
    self.osd_pipeline = None  # ADD THIS LINE
```

**Step 4: Run test to verify it passes**

Run: `pytest test_overlapped_speech_detection.py::test_overlapped_speech_detection_initialization -v`

Expected: PASS (or SKIP if no HF_TOKEN)

**Step 5: Commit OSD pipeline**

```bash
git add speaker_diarizer.py test_overlapped_speech_detection.py
git commit -m "feat: add overlapped speech detection pipeline

- Add _load_osd_pipeline() method
- Add detect_overlapped_speech() method
- Use pyannote.audio OverlappedSpeechDetection
- Returns list of overlap segments with start/end/duration
- Tests verify pipeline initialization and output format"
```

---

## Task 2: Integrate OSD into Transcription Pipeline

**Files:**
- Modify: `auto_transcriber_v4_emotion.py:786-960`
- Test: `test_transcriber_osd_integration.py` (new)

**Step 1: Write failing integration test**

Create `test_transcriber_osd_integration.py`:

```python
#!/usr/bin/env python3
import pytest
from pathlib import Path
from auto_transcriber_v4_emotion import transcribe_with_whisper
import os

HF_TOKEN = os.getenv('HF_TOKEN')
TEST_AUDIO = Path("Eingang/Patient/test_audio.m4a")

pytestmark = pytest.mark.skipif(
    not HF_TOKEN or not TEST_AUDIO.exists(),
    reason="HF_TOKEN or test audio not available"
)


def test_transcribe_with_osd_enabled():
    """Test transcription with OSD returns overlap segments"""
    result = transcribe_with_whisper(
        audio_path=str(TEST_AUDIO),
        model_size='tiny',
        language='de',
        enable_diarization=False,
        enable_overlap_detection=True,  # NEW PARAMETER
        hf_token=HF_TOKEN
    )

    assert 'overlapped_speech' in result
    assert isinstance(result['overlapped_speech'], list)


def test_transcribe_segments_have_overlap_flag():
    """Test segments are flagged if they overlap with detected regions"""
    result = transcribe_with_whisper(
        audio_path=str(TEST_AUDIO),
        model_size='tiny',
        language='de',
        enable_overlap_detection=True,
        hf_token=HF_TOKEN
    )

    # Check if any segment has overlap marker
    segments = result.get('segments', [])
    # At least one segment should have 'has_overlap' field
    assert any('has_overlap' in seg for seg in segments)
```

**Step 2: Run test to verify it fails**

Run: `pytest test_transcriber_osd_integration.py::test_transcribe_with_osd_enabled -v`

Expected: FAIL with "TypeError: transcribe_with_whisper() got an unexpected keyword argument 'enable_overlap_detection'"

**Step 3: Add OSD integration to transcribe_with_whisper**

Modify `auto_transcriber_v4_emotion.py`:

1. Import statement (add around line 45):

```python
try:
    from speaker_diarizer import SpeakerDiarizer
    DIARIZATION_AVAILABLE = True
except ImportError:
    DIARIZATION_AVAILABLE = False
    print("⚠️ Speaker Diarizer nicht gefunden. Sprechererkennung deaktiviert.")
```

2. Update function signature (around line 793):

```python
def transcribe_with_whisper(
    audio_path: str,
    model_size: str = 'base',
    language: str = 'de',
    use_intelligent_pipeline: bool = False,
    quality_score: Optional[float] = None,
    quality_analyzer: Optional[Any] = None,
    audio_preprocessor: Optional[Any] = None,
    extract_prosody: bool = False,
    enable_diarization: bool = False,
    hf_token: Optional[str] = None,
    num_speakers: Optional[int] = None,
    enable_overlap_detection: bool = False,  # NEW PARAMETER
    osd_min_duration: float = 0.5  # NEW PARAMETER
) -> Dict[str, Any]:
```

3. Update docstring (around line 807):

```python
    """
    Transkribiert Audio mit Whisper und extrahiert Confidence Scores

    Args:
        audio_path: Pfad zur Audio-Datei
        model_size: Whisper-Modell (tiny, base, small, medium, large)
        language: Sprache (de, en, etc.)
        use_intelligent_pipeline: Enable quality-based preprocessing
        quality_score: Pre-calculated quality score (0-1)
        quality_analyzer: AudioQualityAnalyzer instance
        audio_preprocessor: AudioPreprocessor instance
        extract_prosody: Extract prosodic features (tempo, pitch, energy, pauses)
        enable_diarization: Enable automatic speaker diarization (Speaker A, B, C, ...)
        hf_token: Hugging Face token for pyannote.audio (required for diarization/OSD)
        num_speakers: Fixed number of speakers (None for auto-detect)
        enable_overlap_detection: Enable overlapped speech detection
        osd_min_duration: Minimum duration (seconds) for overlap regions

    Returns:
        Dict mit text, segments, confidence_scores, prosody_features/baseline,
        speaker_labels, und overlapped_speech
    """
```

4. Add OSD logic after speaker diarization (around line 937):

```python
        # OVERLAPPED SPEECH DETECTION (Phase 2c)
        overlapped_speech = []

        if enable_overlap_detection and DIARIZATION_AVAILABLE:
            try:
                logger.info("🔊 Starte Overlapped Speech Detection...")
                diarizer = SpeakerDiarizer(
                    use_auth_token=hf_token,
                    min_speakers=1,
                    max_speakers=10
                )

                # Run OSD
                overlapped_speech = diarizer.detect_overlapped_speech(
                    Path(audio_path),
                    min_duration_on=osd_min_duration,
                    min_duration_off=0.3  # Fill gaps shorter than 300ms
                )

                # Mark segments that have overlaps
                aligned_segments = _mark_overlapped_segments(
                    aligned_segments,
                    overlapped_speech
                )

                logger.info(
                    f"✅ OSD abgeschlossen: {len(overlapped_speech)} "
                    f"Überlappungsbereiche gefunden"
                )

            except Exception as e:
                logger.error(f"Fehler bei Overlapped Speech Detection: {e}")
                logger.warning("Fortfahren ohne OSD...")

        return {
            'text': result['text'],
            'segments': aligned_segments,
            'confidence_scores': confidence_scores,
            'prosody_features': prosody_features,
            'prosody_baseline': prosody_baseline,
            'speaker_segments': speaker_segments,
            'overlapped_speech': overlapped_speech  # NEW FIELD
        }
```

5. Add helper function after `_extract_confidence_scores` (around line 1010):

```python
def _mark_overlapped_segments(
    segments: List[Dict[str, Any]],
    overlaps: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Mark transcription segments that contain overlapped speech

    Args:
        segments: Whisper transcription segments
        overlaps: OSD overlap segments

    Returns:
        Segments with added 'has_overlap' and 'overlap_duration' fields
    """
    for seg in segments:
        seg_start = seg.get('start', 0.0)
        seg_end = seg.get('end', 0.0)

        # Check overlap with OSD regions
        total_overlap = 0.0
        has_overlap = False

        for overlap in overlaps:
            ovl_start = overlap['start']
            ovl_end = overlap['end']

            # Calculate intersection
            intersection_start = max(seg_start, ovl_start)
            intersection_end = min(seg_end, ovl_end)
            intersection = max(0, intersection_end - intersection_start)

            if intersection > 0:
                has_overlap = True
                total_overlap += intersection

        seg['has_overlap'] = has_overlap
        seg['overlap_duration'] = total_overlap

    return segments
```

6. Update error return (around line 958):

```python
    except Exception as e:
        logger.error(f"Fehler bei Transkription: {e}")
        return {
            'text': '',
            'segments': [],
            'confidence_scores': {
                'overall_confidence': 0.0,
                'segments': [],
                'low_confidence_segments': []
            },
            'prosody_features': [],
            'prosody_baseline': None,
            'speaker_segments': [],
            'overlapped_speech': []  # ADD THIS
        }
```

**Step 4: Run test to verify it passes**

Run: `pytest test_transcriber_osd_integration.py::test_transcribe_with_osd_enabled -v`

Expected: PASS (or SKIP if no test audio)

**Step 5: Commit OSD integration**

```bash
git add auto_transcriber_v4_emotion.py test_transcriber_osd_integration.py
git commit -m "feat: integrate overlapped speech detection into transcription

- Add enable_overlap_detection parameter to transcribe_with_whisper
- Run OSD parallel to diarization
- Mark segments with has_overlap and overlap_duration fields
- Add _mark_overlapped_segments helper function
- Tests verify OSD integration and segment marking"
```

---

## Task 3: Add OSD Markers to Output Formats

**Files:**
- Modify: `output_formatter.py:258-380`
- Test: `test_output_formatter_osd.py` (new)

**Step 1: Write failing test for OSD markers**

Create `test_output_formatter_osd.py`:

```python
#!/usr/bin/env python3
import pytest
from pathlib import Path
from output_formatter import OutputFormatter
import json


def test_markdown_includes_overlap_marker():
    """Test Markdown output includes [OVERLAP] marker"""
    formatter = OutputFormatter()

    transcription_result = {
        'segments': [
            {
                'start': 5.0,
                'end': 7.0,
                'text': 'Test text',
                'has_overlap': True,
                'overlap_duration': 0.8
            }
        ],
        'prosody_features': [],
        'prosody_baseline': None,
        'confidence_scores': {'overall_confidence': 0.9, 'segments': []},
        'overlapped_speech': [
            {'start': 5.2, 'end': 6.0, 'duration': 0.8}
        ]
    }

    markdown = formatter._generate_markdown(
        'test.m4a',
        transcription_result['segments'],
        transcription_result['prosody_features'],
        transcription_result['prosody_baseline'],
        transcription_result['confidence_scores'],
        include_prosody_markers=True
    )

    assert '[OVERLAP]' in markdown or '[ÜBERLAPPUNG]' in markdown


def test_json_includes_overlap_data():
    """Test JSON output includes overlap fields"""
    formatter = OutputFormatter()

    transcription_result = {
        'segments': [
            {
                'start': 5.0,
                'end': 7.0,
                'text': 'Test',
                'has_overlap': True,
                'overlap_duration': 0.8
            }
        ],
        'prosody_features': [],
        'prosody_baseline': None,
        'confidence_scores': {'overall_confidence': 0.9, 'segments': []}
    }

    json_data = formatter._generate_json_sidecar(
        'test.m4a',
        transcription_result['segments'],
        transcription_result['prosody_features'],
        transcription_result['prosody_baseline'],
        transcription_result['confidence_scores']
    )

    # Check first segment has overlap fields
    assert 'has_overlap' in json_data['segments'][0]
    assert json_data['segments'][0]['has_overlap'] is True
    assert 'overlap_duration' in json_data['segments'][0]


def test_csv_includes_overlap_column():
    """Test CSV includes has_overlap column"""
    formatter = OutputFormatter()

    transcription_result = {
        'segments': [
            {
                'start': 5.0,
                'end': 7.0,
                'text': 'Test',
                'has_overlap': True,
                'overlap_duration': 0.8
            }
        ],
        'prosody_features': [],
        'confidence_scores': {'overall_confidence': 0.9, 'segments': []}
    }

    output_path = Path('/tmp/test_osd_output')
    csv_path = formatter.generate_csv(transcription_result, output_path)

    # Read CSV and check header
    import csv
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        assert 'has_overlap' in fieldnames
        assert 'overlap_duration_s' in fieldnames

        # Check first row
        row = next(reader)
        assert row['has_overlap'] == 'True'
```

**Step 2: Run test to verify it fails**

Run: `pytest test_output_formatter_osd.py::test_markdown_includes_overlap_marker -v`

Expected: FAIL with "'[OVERLAP]' not found in markdown"

**Step 3: Add OSD markers to Markdown formatter**

Modify `output_formatter.py`, in `_generate_markdown` method (around line 294):

```python
        for i, segment in enumerate(segments):
            start = segment.get('start', 0.0)
            end = segment.get('end', 0.0)
            text = segment.get('text', '').strip()
            speaker = segment.get('speaker', None)
            has_overlap = segment.get('has_overlap', False)  # ADD THIS

            # Get prosody for this segment
            prosody = None
            if i < len(prosody_features):
                prosody = prosody_features[i]

            # Format timestamp
            timestamp = self._format_timestamp(start, end)

            # Build segment line with speaker label
            if speaker:
                segment_line = f"**[{timestamp}] {speaker}:** {text}"
            else:
                segment_line = f"**[{timestamp}]** {text}"

            # Add prosody markers if available
            if include_prosody_markers and prosody:
                markers = self._generate_prosody_markers(prosody)
                if markers:
                    segment_line += f" {markers}"

            # Add overlap marker if detected
            if has_overlap:
                overlap_duration = segment.get('overlap_duration', 0.0)
                segment_line += f" `[ÜBERLAPPUNG {overlap_duration:.1f}s]`"

            lines.append(segment_line)
```

Add to legend (around line 336):

```python
        if include_prosody_markers:
            lines.append("\n---\n")
            lines.append("### Legende\n")
            lines.append("- `[TEMPO↓]` = Langsames Sprechen (>20% unter Baseline)")
            lines.append("- `[TEMPO↑]` = Schnelles Sprechen (>20% über Baseline)")
            lines.append("- `[PITCH↓]` = Tiefe Stimme (>15% unter Baseline)")
            lines.append("- `[PITCH↑]` = Hohe Stimme (>15% über Baseline)")
            lines.append("- `[ENERGY↓]` = Leise (>25% unter Baseline)")
            lines.append("- `[ENERGY↑]` = Laut (>25% über Baseline)")
            lines.append("- `[PAUSE]` = Signifikante Pause (>1s)")
            lines.append("- `[ÜBERLAPPUNG]` = Mehrere Sprecher gleichzeitig")  # ADD THIS
```

**Step 4: Add overlap fields to JSON**

Modify `_generate_json_sidecar` method (around line 363):

```python
            "segments": [
                {
                    "index": i,
                    "speaker": seg.get('speaker', None),
                    "start": seg.get('start', 0.0),
                    "end": seg.get('end', 0.0),
                    "text": seg.get('text', '').strip(),
                    "confidence": confidence_scores.get('segments', [])[i].get('confidence', 0.0)
                    if i < len(confidence_scores.get('segments', [])) else 0.0,
                    "prosody": prosody_features[i] if i < len(prosody_features) else None,
                    "has_overlap": seg.get('has_overlap', False),  # ADD THIS
                    "overlap_duration": seg.get('overlap_duration', 0.0)  # ADD THIS
                }
                for i, seg in enumerate(segments)
            ]
```

**Step 5: Add overlap columns to CSV**

Modify `generate_csv` method (around line 198):

```python
            fieldnames = [
                'index',
                'speaker',
                'start_time',
                'end_time',
                'duration',
                'text',
                'confidence',
                'has_overlap',  # ADD THIS
                'overlap_duration_s',  # ADD THIS
                'tempo_wpm',
                'tempo_deviation_pct',
                'pitch_mean_hz',
                'pitch_deviation_pct',
                'energy_rms',
                'energy_deviation_pct',
                'pause_before_ms',
                'jitter_local',
                'shimmer_local'
            ]
```

And in the row generation (around line 223):

```python
                row = {
                    'index': i,
                    'speaker': segment.get('speaker', ''),
                    'start_time': segment.get('start', 0.0),
                    'end_time': segment.get('end', 0.0),
                    'duration': segment.get('end', 0.0) - segment.get('start', 0.0),
                    'text': segment.get('text', '').strip(),
                    'confidence': conf_segment.get('confidence', 0.0)
                    if i < len(confidence_scores.get('segments', [])) else 0.0,
                    'has_overlap': segment.get('has_overlap', False),  # ADD THIS
                    'overlap_duration_s': segment.get('overlap_duration', 0.0),  # ADD THIS
                    # ... rest of prosody fields ...
                }
```

**Step 6: Run tests to verify they pass**

Run: `pytest test_output_formatter_osd.py -v`

Expected: All PASS

**Step 7: Commit output format changes**

```bash
git add output_formatter.py test_output_formatter_osd.py
git commit -m "feat: add OSD markers to all output formats

- Markdown: [ÜBERLAPPUNG Xs] marker with duration
- JSON: has_overlap and overlap_duration fields
- CSV: has_overlap and overlap_duration_s columns
- Update legend with overlap marker explanation
- Tests verify all formats include overlap data"
```

---

## Task 4: Add OSD Visualization to HTML/PDF

**Files:**
- Modify: `html_formatter.py:1-780`
- Test: Manual verification with browser

**Step 1: Add overlap styling to HTML formatter**

Modify `html_formatter.py`, add to MARKER_COLORS dict (around line 50):

```python
    # Prosody marker colors
    MARKER_COLORS = {
        "TEMPO↑": {"color": "#D32F2F", "bg": "#FFEBEE", "label": "Schnell"},
        "TEMPO↓": {"color": "#1976D2", "bg": "#E3F2FD", "label": "Langsam"},
        "PITCH↑": {"color": "#F57C00", "bg": "#FFF3E0", "label": "Hoch"},
        "PITCH↓": {"color": "#7B1FA2", "bg": "#F3E5F5", "label": "Tief"},
        "ENERGY↑": {"color": "#388E3C", "bg": "#E8F5E9", "label": "Laut"},
        "ENERGY↓": {"color": "#5D4037", "bg": "#EFEBE9", "label": "Leise"},
        "PAUSE": {"color": "#455A64", "bg": "#ECEFF1", "label": "Pause"},
        "ÜBERLAPPUNG": {"color": "#E91E63", "bg": "#FCE4EC", "label": "Überlappung"}  # ADD THIS - Pink/Magenta
    }
```

**Step 2: Add CSS for overlap highlighting**

Modify the CSS in `_generate_html_content` method (around line 250):

```python
            .overlap-segment {
                border-left: 4px solid #E91E63 !important;
                background: linear-gradient(90deg,
                    rgba(233, 30, 99, 0.05) 0%,
                    rgba(233, 30, 99, 0.02) 100%);
            }

            .overlap-badge {
                display: inline-block;
                background: #E91E63;
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 8px;
            }
```

**Step 3: Apply overlap styling to segments**

Modify segment generation in `_generate_html_content` (around line 450):

```python
        for i, seg in enumerate(segments):
            start = seg.get('start', 0.0)
            end = seg.get('end', 0.0)
            text = seg.get('text', '').strip()
            speaker = seg.get('speaker', 'Sprecher')
            has_overlap = seg.get('has_overlap', False)  # ADD THIS
            overlap_duration = seg.get('overlap_duration', 0.0)  # ADD THIS

            # ... existing prosody code ...

            # Determine segment CSS classes
            segment_classes = ['segment']
            if is_turning_point:
                segment_classes.append('turning-point')
            if has_overlap:
                segment_classes.append('overlap-segment')  # ADD THIS

            # ... existing speaker color code ...

            html_content += f'''
                <div class="{' '.join(segment_classes)}"
                     style="background-color: {speaker_bg}; border-left-color: {speaker_border};">
                    <div class="segment-header">
                        <span class="speaker-label">{speaker}</span>
                        <span class="timestamp">{timestamp}</span>
                        {f'<span class="overlap-badge">⚠ Überlappung {overlap_duration:.1f}s</span>' if has_overlap else ''}
                    </div>
                    <div class="text">{text}</div>
            '''

            # ... rest of existing code for prosody details ...
```

**Step 4: Manual verification**

Run: Generate HTML with OSD enabled and open in browser

```bash
# Test with OSD
python3 -c "
from auto_transcriber_v4_emotion import transcribe_with_whisper
from output_formatter import OutputFormatter
from pathlib import Path
import os

result = transcribe_with_whisper(
    'Eingang/Patient/test.m4a',
    model_size='tiny',
    extract_prosody=True,
    enable_overlap_detection=True,
    hf_token=os.getenv('HF_TOKEN')
)

formatter = OutputFormatter()
files = formatter.format_all(
    result,
    'test.m4a',
    Path('Transkripte_LLM/test_osd'),
    generate_html=True,
    generate_pdf=True
)

print(f'HTML: {files[\"html\"]}')
"
```

Expected: HTML shows overlap segments with pink border and "⚠ Überlappung" badge

**Step 5: Commit HTML/PDF visualization**

```bash
git add html_formatter.py
git commit -m "feat: add OSD visualization to HTML/PDF output

- Pink/magenta color scheme for overlap markers
- overlap-segment CSS class with gradient background
- Overlap badge showing duration in segment header
- Consistent with existing prosody marker styling"
```

---

## Task 5: Update Documentation and GUI Integration

**Files:**
- Modify: `SPEAKER_DIARIZATION.md:1-300`
- Modify: `README.md:127-160`
- Create: `docs/OSD_GUIDE.md`

**Step 1: Create OSD user guide**

Create `docs/OSD_GUIDE.md`:

```markdown
# Overlapped Speech Detection (OSD) Guide

## Overview

Overlapped Speech Detection (OSD) identifies moments when multiple speakers talk simultaneously. This is crucial for therapeutic transcripts to mark interruptions, simultaneous speech, and conversational dynamics.

## Usage

### Python API

\`\`\`python
from auto_transcriber_v4_emotion import transcribe_with_whisper

result = transcribe_with_whisper(
    audio_path="session.m4a",
    model_size='small',
    enable_overlap_detection=True,  # Enable OSD
    osd_min_duration=0.5,  # Ignore overlaps < 0.5s
    hf_token="hf_YOUR_TOKEN"
)

# Access overlap regions
for overlap in result['overlapped_speech']:
    print(f"Overlap: {overlap['start']:.2f}s - {overlap['end']:.2f}s")

# Check segments for overlaps
for seg in result['segments']:
    if seg.get('has_overlap'):
        print(f"Segment has {seg['overlap_duration']:.1f}s overlap")
\`\`\`

### Output Formats

**Markdown:**
\`\`\`
**[00:12 - 00:15] Speaker A:** Ich denke dass... `[ÜBERLAPPUNG 1.2s]`
**[00:13 - 00:16] Speaker B:** Moment, lass mich... `[ÜBERLAPPUNG 1.0s]`
\`\`\`

**CSV:**
\`\`\`csv
index,speaker,text,has_overlap,overlap_duration_s,...
0,Speaker A,"Ich denke...",True,1.2,...
1,Speaker B,"Moment...",True,1.0,...
\`\`\`

**HTML/PDF:** Pink border + overlap badge

## Parameters

- `enable_overlap_detection` (bool): Enable/disable OSD
- `osd_min_duration` (float): Minimum overlap duration to detect (default: 0.5s)
- `hf_token` (str): Hugging Face token (same as for diarization)

## Therapeutic Applications

1. **Interruption Analysis**: Track who interrupts whom
2. **Turn-Taking Dynamics**: Measure conversational flow
3. **Engagement Metrics**: Identify highly engaged vs. passive moments
4. **Conflict Detection**: Overlaps may indicate tension

## Technical Details

- Model: `pyannote/segmentation-3.0`
- Pipeline: `OverlappedSpeechDetection`
- Runs parallel to speaker diarization
- GPU-accelerated

## Troubleshooting

**Too many false positives:** Increase `osd_min_duration`
**Missing overlaps:** Decrease `osd_min_duration` or check audio quality
**Same requirements as diarization:** HF token, pyannote.audio 4.0
```

**Step 2: Update SPEAKER_DIARIZATION.md**

Add section after "Speaker-Statistiken" (around line 180):

```markdown
## Overlapped Speech Detection

Speaker Diarization kann mit Overlapped Speech Detection kombiniert werden:

\`\`\`python
result = transcribe_with_whisper(
    audio_path="session.m4a",
    enable_diarization=True,      # Sprecher A, B, C
    enable_overlap_detection=True, # Überlappungen
    hf_token=os.getenv('HF_TOKEN')
)

# Statistiken
print(f"Speakers: {len(set(s['speaker'] for s in result['segments']))}")
print(f"Overlaps: {len(result['overlapped_speech'])}")
\`\`\`

Siehe [OSD_GUIDE.md](docs/OSD_GUIDE.md) für Details.
```

**Step 3: Update README.md roadmap**

Modify `README.md` (around line 147):

```markdown
### Phase 2b: Speaker Diarization (✅ Abgeschlossen)

- [x] Automatische Sprechererkennung mit pyannote.audio
- [x] Speaker A, B, C Labels ohne Namenszuordnung
- [x] Integration in Transkriptionspipeline
- [x] Speaker-Labels in allen Ausgabeformaten (MD, JSON, HTML, PDF, CSV)
- [x] Farbcodierte Sprecher in HTML/PDF (6 Farben)

### Phase 2c: Overlapped Speech Detection (✅ Abgeschlossen)

- [x] Automatische Erkennung überlappender Sprache
- [x] OSD-Marker in allen Ausgabeformaten
- [x] Visualisierung in HTML/PDF (pink border + badge)
- [x] Segment-Flagging (has_overlap, overlap_duration)
- [x] Therapeutische Anwendungen (Interruptions-Analyse)

**Siehe:** [OSD_GUIDE.md](docs/OSD_GUIDE.md) für Details

### Phase 2d: ATO-Marker-Integration (In Planung)
```

**Step 4: Commit documentation**

```bash
git add docs/OSD_GUIDE.md SPEAKER_DIARIZATION.md README.md
git commit -m "docs: add overlapped speech detection documentation

- Create OSD_GUIDE.md with usage examples
- Update SPEAKER_DIARIZATION.md with OSD section
- Mark Phase 2c as complete in README.md
- Document therapeutic applications"
```

**Step 5: Verify all tests pass**

Run: `pytest -v`

Expected: All tests PASS

---

## Verification

After completing all tasks, verify:

1. **Unit Tests:** All OSD tests pass
2. **Integration:** Transcription with OSD works end-to-end
3. **Output Formats:** Markdown, JSON, CSV, HTML, PDF all show overlaps
4. **Documentation:** Guides complete and accurate

Run full verification:

```bash
# Run all tests
pytest -v

# Test with real audio (if available)
python3 -c "
from auto_transcriber_v4_emotion import transcribe_with_whisper
from output_formatter import OutputFormatter
from pathlib import Path
import os

result = transcribe_with_whisper(
    'Eingang/Patient/test.m4a',
    model_size='small',
    extract_prosody=True,
    enable_diarization=True,
    enable_overlap_detection=True,
    hf_token=os.getenv('HF_TOKEN')
)

formatter = OutputFormatter()
files = formatter.format_all(result, 'test.m4a', Path('Transkripte_LLM/test_full'))

print('Generated files:')
for fmt, path in files.items():
    print(f'  {fmt}: {path}')
"
```

---

## Notes for Engineer

- **DRY:** Reuse existing `SpeakerDiarizer` for both diarization and OSD
- **YAGNI:** Don't add overlap types beyond "simultaneous_speech" unless needed
- **TDD:** Write test first, watch it fail, implement, watch it pass
- **Commits:** Frequent small commits (one per task step)
- **HF Token:** Same token works for both diarization and OSD
- **Performance:** OSD adds ~20% processing time (runs in parallel with diarization)

## Common Issues

1. **Import Error:** pyannote.audio not installed → `pip install pyannote.audio`
2. **Auth Error:** HF token invalid → Check token permissions
3. **No overlaps detected:** Audio quality low or min_duration too high
4. **Tests skip:** Set `HF_TOKEN` environment variable

---

**Total Estimated Time:** 3-4 hours
**Complexity:** Medium (builds on existing diarization infrastructure)
**Dependencies:** pyannote.audio 4.0, existing Phase 2b code
