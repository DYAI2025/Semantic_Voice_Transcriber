# IMPLEMENTATION PLAN V5: Professional Therapeutic Transcription System

**Date:** 2025-11-12
**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc
**Project:** Super Semantic Whisper - Professional Grade Enhancement
**Branch:** `feat/professional-quality-enhancement`

---

## 🎯 EXECUTIVE SUMMARY

This plan implements a **professional-grade therapeutic transcription system** with the following unique differentiators:

1. **Turning Points with Scientific Evidence** - The core differentiator
2. **Multi-Model Speech Recognition** - Highest possible accuracy
3. **Professional Speaker Representation** - Crystal-clear visual separation
4. **PDF Export with Premium Layout** - Publication-ready documents
5. **Transparent Confidence System** - Full traceability

---

## 📊 PRIORITY MATRIX

| Priority | Feature | Impact | Effort | Status |
|----------|---------|--------|--------|--------|
| **P1** | Speaker Separation & Display | HIGH | MEDIUM | ⏳ Pending |
| **P2** | Speech Recognition Quality | HIGH | HIGH | ⏳ Pending |
| **P3** | PDF Export Professional | HIGH | MEDIUM | ⏳ Pending |
| **P4** | Confidence Transparency | MEDIUM | LOW | ⏳ Pending |
| **P5** | System Clarity (UI/UX) | MEDIUM | LOW | ⏳ Pending |

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   SVT GUI    │  │  Web UI      │  │  CLI Tool    │     │
│  │  (Tkinter)   │  │  (Flask)     │  │  (Argparse)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                             │
│                                                               │
│  transcription_orchestrator.py                               │
│  - Manages multi-model transcription                         │
│  - Coordinates all processing layers                         │
│  - Handles result merging and validation                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 1: SPEECH RECOGNITION                        │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Whisper large-v3 │  │ ElevenLabs       │               │
│  │  (Primary)        │  │ Scrive v2 API    │               │
│  │                   │  │ (Fallback)       │               │
│  └──────────────────┘  └──────────────────┘               │
│            ↓                      ↓                          │
│       consensus_merger.py                                    │
│       - Compares results                                     │
│       - Selects best segments                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 2: SPEAKER DIARIZATION                       │
│                                                               │
│  speaker_diarizer_v2.py                                      │
│  - Pyannote.audio 3.0                                        │
│  - Speaker embeddings                                        │
│  - Voice profile matching                                    │
│  - Editable speaker names                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 3: PROSODY ANALYSIS                          │
│                                                               │
│  prosody_extractor.py (Enhanced)                             │
│  - Pitch, tempo, energy extraction                           │
│  - HNR, jitter, shimmer                                      │
│  - Baseline calculation per speaker                          │
│  - Deviation scoring                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 4: TURNING POINTS DETECTION                  │
│                            ★ UNIQUE DIFFERENTIATOR ★         │
│  turning_points_detector_v2.py                               │
│  - CoSD (Co-Emergent Semantic Drift) algorithm              │
│  - Prosody evidence collection                               │
│  - Semantic marker transitions                               │
│  - Scientific transparency logging                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 5: POST-PROCESSING                           │
│                                                               │
│  transcript_corrector.py                                     │
│  - LLM-based contextual correction                           │
│  - Custom therapeutic dictionary                             │
│  - Confidence-based selective correction                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 6: OUTPUT GENERATION                         │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Markdown        │  │  PDF Export       │               │
│  │  Generator       │  │  (ReportLab)      │               │
│  └──────────────────┘  └──────────────────┘               │
│            ↓                      ↓                          │
│  professional_pdf_generator.py                               │
│  - Premium layout templates                                  │
│  - Turning point visualization                               │
│  - Speaker color coding                                      │
│  - Metadata page with quality metrics                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 DETAILED TASK BREAKDOWN

### **PHASE 1: SPEAKER SYSTEM ENHANCEMENT** (Priority 1)

#### **Task 1.1: Upgrade Speaker Diarization**
**File:** `speaker_diarizer_v2.py`

**Requirements:**
- Upgrade to pyannote.audio 3.0
- Implement speaker embedding extraction
- Create persistent speaker database
- Add voice profile matching

**Implementation Details:**
```python
class SpeakerDiarizerV2:
    """Enhanced speaker diarization with persistent profiles"""

    def __init__(self):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.0",
            use_auth_token=HF_TOKEN
        )
        self.speaker_db = SpeakerDatabase("Memory/speaker_profiles.db")
        self.embeddings_model = Model.from_pretrained(
            "pyannote/embedding",
            use_auth_token=HF_TOKEN
        )

    def diarize_with_identification(self, audio_path: str) -> Dict:
        """
        Perform diarization and match against known speakers

        Returns:
            {
                'segments': [
                    {
                        'start': 0.0,
                        'end': 5.2,
                        'speaker_id': 'SPEAKER_00',
                        'speaker_name': 'Dr. Schmidt',  # Matched or None
                        'confidence': 0.89,
                        'embedding': [...]  # 512-dim vector
                    }
                ]
            }
        """
        # 1. Run diarization
        diarization = self.pipeline(audio_path)

        # 2. Extract embeddings for each segment
        # 3. Match against database
        # 4. Return with identified speakers
        pass

    def update_speaker_name(self, speaker_id: str, new_name: str):
        """Allow user to edit speaker names"""
        self.speaker_db.update_name(speaker_id, new_name)
```

**Verification:**
```bash
python3 -m pytest tests/test_speaker_diarizer_v2.py -v
```

**Acceptance Criteria:**
- ✅ Diarization accuracy > 90% on test set
- ✅ Speaker matching works with known voices
- ✅ Editable names persist across sessions
- ✅ New speakers auto-added to database

---

#### **Task 1.2: Create Speaker Name Editor GUI**
**File:** `speaker_editor_dialog.py`

**Requirements:**
- Tkinter dialog for editing speaker names
- Real-time preview of changes
- Color picker for speaker colors
- Save/Cancel functionality

**Implementation Details:**
```python
class SpeakerEditorDialog(tk.Toplevel):
    """Dialog for editing speaker names and colors"""

    def __init__(self, parent, speakers: List[Dict]):
        super().__init__(parent)
        self.title("Edit Speaker Names")
        self.speakers = speakers

        # Create entry fields for each speaker
        for i, speaker in enumerate(speakers):
            frame = tk.Frame(self)
            frame.pack(fill='x', padx=5, pady=5)

            # Speaker ID (read-only)
            tk.Label(frame, text=f"Speaker {i+1}:").pack(side='left')

            # Name entry
            name_var = tk.StringVar(value=speaker.get('name', f'Speaker {i+1}'))
            tk.Entry(frame, textvariable=name_var).pack(side='left', expand=True)

            # Color picker button
            color_btn = tk.Button(
                frame,
                bg=speaker.get('color', '#4A90E2'),
                command=lambda s=speaker: self.pick_color(s)
            )
            color_btn.pack(side='right')

    def pick_color(self, speaker: Dict):
        """Open color picker for speaker"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(
            initialcolor=speaker.get('color', '#4A90E2'),
            title="Choose Speaker Color"
        )
        if color[1]:
            speaker['color'] = color[1]
```

**Verification:**
- Manual GUI testing
- Screenshot comparison with design mockups

**Acceptance Criteria:**
- ✅ All speakers editable
- ✅ Colors visible and changeable
- ✅ Changes saved to database
- ✅ Preview shows updated names/colors

---

#### **Task 1.3: Enhanced Speaker Visualization**
**File:** `speaker_visualizer_v2.py`

**Requirements:**
- Color-coded speaker blocks
- Icons/Avatars before each speaker
- Horizontal divider lines between speakers
- Indentation for better readability

**Implementation Details:**
```python
class SpeakerVisualizerV2:
    """Professional speaker visualization with all visual elements"""

    SPEAKER_ICONS = {
        0: "👤", 1: "👨", 2: "👩", 3: "🧑",
        4: "👴", 5: "👵", 6: "🧔", 7: "👱"
    }

    def format_transcript(self, segments: List[Dict], format: str = 'markdown') -> str:
        """
        Format transcript with enhanced speaker visualization

        Args:
            segments: List of transcript segments with speaker info
            format: 'markdown', 'html', or 'plain'

        Returns:
            Formatted transcript string
        """
        output = []
        previous_speaker = None

        for segment in segments:
            speaker_id = segment['speaker_id']
            speaker_name = segment.get('speaker_name', f'Speaker {speaker_id}')
            speaker_color = segment.get('color', '#4A90E2')
            text = segment['text']

            # Add divider line if speaker changed
            if speaker_id != previous_speaker and previous_speaker is not None:
                if format == 'markdown':
                    output.append('\n---\n')
                elif format == 'html':
                    output.append('<hr class="speaker-divider"/>')

            # Add speaker header with icon
            icon = self.SPEAKER_ICONS.get(hash(speaker_id) % 8, "👤")

            if format == 'markdown':
                header = f"\n{icon} **{speaker_name}** [{segment['start']:.1f}s - {segment['end']:.1f}s]\n"
                content = f"> {text}\n"  # Blockquote for indentation
            elif format == 'html':
                header = f'''
                <div class="speaker-block" style="border-left: 4px solid {speaker_color};">
                    <div class="speaker-header">
                        <span class="speaker-icon">{icon}</span>
                        <span class="speaker-name">{speaker_name}</span>
                        <span class="timestamp">[{segment['start']:.1f}s - {segment['end']:.1f}s]</span>
                    </div>
                    <div class="speaker-content" style="margin-left: 20px;">
                        {text}
                    </div>
                </div>
                '''
                content = header

            output.append(header if format == 'markdown' else '')
            output.append(content)

            previous_speaker = speaker_id

        return ''.join(output)
```

**CSS for HTML output:**
```css
.speaker-block {
    margin: 15px 0;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 8px;
}

.speaker-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-weight: bold;
}

.speaker-icon {
    font-size: 24px;
}

.speaker-content {
    line-height: 1.6;
    padding-left: 35px;
}

.speaker-divider {
    margin: 20px 0;
    border: none;
    border-top: 2px solid #dee2e6;
}
```

**Verification:**
```bash
python3 -m pytest tests/test_speaker_visualizer_v2.py -v
# Visual verification of generated HTML/Markdown
```

**Acceptance Criteria:**
- ✅ Each speaker has unique color
- ✅ Icons displayed correctly
- ✅ Divider lines between speakers
- ✅ Content properly indented
- ✅ Responsive layout in HTML

---

### **PHASE 2: SPEECH RECOGNITION QUALITY** (Priority 2)

#### **Task 2.1: Integrate Whisper large-v3**
**File:** `whisper_transcriber_v3.py`

**Requirements:**
- Upgrade from medium to large-v3 model
- Optimize memory usage for large model
- Add model caching
- Performance monitoring

**Implementation Details:**
```python
class WhisperTranscriberV3:
    """Whisper large-v3 integration with optimization"""

    def __init__(self, device: str = "auto"):
        """
        Initialize Whisper large-v3

        Args:
            device: 'cpu', 'cuda', or 'auto'
        """
        import torch

        # Auto-detect best device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load model with FP16 for GPU (2x faster, half memory)
        if device == "cuda":
            self.model = whisper.load_model("large-v3", device=device)
            self.compute_type = "float16"
        else:
            # Use INT8 quantization for CPU (faster, less memory)
            self.model = whisper.load_model("large-v3", device=device)
            self.compute_type = "int8"

        self.device = device

    def transcribe(
        self,
        audio_path: str,
        language: str = "de",
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio with large-v3

        Returns:
            {
                'text': str,
                'segments': List[Dict],
                'language': str,
                'model': 'large-v3',
                'processing_time': float,
                'memory_used_mb': float
            }
        """
        import time
        import psutil
        import torch

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Transcribe with optimal settings
        result = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            fp16=(self.device == "cuda"),  # FP16 for GPU only
            verbose=False,
            # Beam search for better quality
            beam_size=5,
            best_of=5,
            # VAD settings
            condition_on_previous_text=True,
            # Temperature fallback for low confidence
            temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        )

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Add metadata
        result['model'] = 'large-v3'
        result['processing_time'] = end_time - start_time
        result['memory_used_mb'] = end_memory - start_memory
        result['device'] = self.device

        # Convert segments to enhanced format
        result['segments'] = self._enhance_segments(result['segments'])

        return result

    def _enhance_segments(self, segments: List[Dict]) -> List[Dict]:
        """Add confidence scores to segments"""
        enhanced = []
        for seg in segments:
            enhanced.append({
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text'],
                'confidence': self._calculate_confidence(seg),
                'avg_logprob': seg.get('avg_logprob', 0),
                'no_speech_prob': seg.get('no_speech_prob', 0),
            })
        return enhanced

    def _calculate_confidence(self, segment: Dict) -> float:
        """
        Calculate confidence score (0-1)

        Based on:
        - avg_logprob: How confident the model is
        - no_speech_prob: Probability of silence
        """
        import math

        avg_logprob = segment.get('avg_logprob', -1.0)
        no_speech_prob = segment.get('no_speech_prob', 0.5)

        # Convert logprob to probability
        prob = math.exp(avg_logprob)

        # Adjust by speech detection
        confidence = prob * (1 - no_speech_prob)

        return min(max(confidence, 0.0), 1.0)
```

**Memory Optimization:**
```python
# For systems with limited RAM/VRAM
def transcribe_with_batching(self, audio_path: str, chunk_duration: int = 300):
    """
    Transcribe long audio in chunks to save memory

    Args:
        audio_path: Path to audio file
        chunk_duration: Seconds per chunk (default 5 minutes)
    """
    import librosa

    # Load audio
    audio, sr = librosa.load(audio_path, sr=16000)

    # Split into chunks
    chunk_samples = chunk_duration * sr
    chunks = [audio[i:i+chunk_samples]
              for i in range(0, len(audio), chunk_samples)]

    # Transcribe each chunk
    all_segments = []
    time_offset = 0

    for i, chunk in enumerate(chunks):
        # Save chunk to temp file
        temp_path = f"/tmp/chunk_{i}.wav"
        sf.write(temp_path, chunk, sr)

        # Transcribe
        result = self.transcribe(temp_path)

        # Adjust timestamps
        for seg in result['segments']:
            seg['start'] += time_offset
            seg['end'] += time_offset
            all_segments.append(seg)

        time_offset += len(chunk) / sr

        # Cleanup
        os.remove(temp_path)

    return {
        'segments': all_segments,
        'text': ' '.join(seg['text'] for seg in all_segments)
    }
```

**Verification:**
```bash
python3 -m pytest tests/test_whisper_v3.py -v
python3 benchmark_whisper_v3.py  # Compare with medium model
```

**Acceptance Criteria:**
- ✅ Model loads successfully on both CPU and GPU
- ✅ WER (Word Error Rate) < 5% on German test set
- ✅ Processing time < 10x real-time on GPU
- ✅ Memory usage < 8GB on GPU, < 16GB on CPU
- ✅ Confidence scores correlate with actual accuracy

---

#### **Task 2.2: Integrate ElevenLabs Scrive v2 API**
**File:** `elevenlabs_transcriber.py`

**Requirements:**
- API client for ElevenLabs Scrive v2
- Error handling and retry logic
- Cost tracking
- Fallback to Whisper if API unavailable

**Implementation Details:**
```python
import requests
import time
from typing import Dict, Optional

class ElevenLabsTranscriber:
    """ElevenLabs Scrive v2 API integration"""

    API_URL = "https://api.elevenlabs.io/v1/speech-to-text"

    def __init__(self, api_key: str):
        """
        Initialize ElevenLabs client

        Args:
            api_key: Your ElevenLabs API key
        """
        self.api_key = api_key
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.total_cost = 0.0

    def transcribe(
        self,
        audio_path: str,
        language: str = "de",
        model: str = "scribe-v2"
    ) -> Optional[Dict]:
        """
        Transcribe audio using ElevenLabs Scrive v2

        Args:
            audio_path: Path to audio file
            language: Language code (de, en, etc.)
            model: Model to use (scribe-v2, scribe-v2-realtime)

        Returns:
            Dict with transcription or None if failed
        """
        try:
            # Upload audio file
            with open(audio_path, 'rb') as f:
                files = {'audio': f}
                data = {
                    'model': model,
                    'language': language
                }

                response = requests.post(
                    self.API_URL,
                    headers={'xi-api-key': self.api_key},
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout
                )

            response.raise_for_status()
            result = response.json()

            # Track cost
            duration_seconds = result.get('duration', 0)
            cost = self._calculate_cost(duration_seconds)
            self.total_cost += cost

            # Convert to standard format
            return {
                'text': result['text'],
                'segments': self._parse_segments(result.get('words', [])),
                'language': result.get('detected_language', language),
                'model': model,
                'provider': 'elevenlabs',
                'confidence': result.get('confidence', 0.9),
                'cost_usd': cost
            }

        except requests.exceptions.RequestException as e:
            print(f"ElevenLabs API error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def _parse_segments(self, words: List[Dict]) -> List[Dict]:
        """Convert word-level timestamps to segment-level"""
        if not words:
            return []

        segments = []
        current_segment = {
            'start': words[0]['start'],
            'words': [],
            'text': ''
        }

        # Group words into segments (sentences or ~30 words)
        for i, word in enumerate(words):
            current_segment['words'].append(word)
            current_segment['text'] += word['text'] + ' '

            # End segment on sentence boundary or every 30 words
            is_sentence_end = word['text'].endswith(('.', '!', '?'))
            is_max_length = len(current_segment['words']) >= 30
            is_last_word = i == len(words) - 1

            if is_sentence_end or is_max_length or is_last_word:
                current_segment['end'] = word['end']
                current_segment['text'] = current_segment['text'].strip()
                current_segment['confidence'] = sum(
                    w.get('confidence', 0.9) for w in current_segment['words']
                ) / len(current_segment['words'])

                segments.append(current_segment)

                if not is_last_word:
                    current_segment = {
                        'start': words[i+1]['start'],
                        'words': [],
                        'text': ''
                    }

        return segments

    def _calculate_cost(self, duration_seconds: float) -> float:
        """
        Calculate cost based on duration

        Scrive v2 pricing: ~$0.10 per minute
        """
        minutes = duration_seconds / 60.0
        return minutes * 0.10

    def is_available(self) -> bool:
        """Check if API is available"""
        try:
            response = requests.get(
                "https://api.elevenlabs.io/v1/user",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
```

**Configuration:**
```yaml
# config/api_keys.yaml
elevenlabs:
  api_key: "your_api_key_here"
  enabled: true
  fallback_to_whisper: true
  max_cost_per_file_usd: 5.0
```

**Verification:**
```bash
python3 -m pytest tests/test_elevenlabs_transcriber.py -v
python3 test_api_connectivity.py  # Check API availability
```

**Acceptance Criteria:**
- ✅ API calls successful with valid key
- ✅ Error handling for network issues
- ✅ Cost tracking accurate
- ✅ Fallback to Whisper works
- ✅ Results in standard format compatible with pipeline

---

#### **Task 2.3: Consensus Merger for Multi-Model Results**
**File:** `consensus_merger.py`

**Requirements:**
- Compare results from Whisper and ElevenLabs
- Select best segments based on confidence
- Handle timing mismatches
- Generate merged transcript

**Implementation Details:**
```python
from typing import List, Dict
import difflib

class ConsensusMerger:
    """Merge transcription results from multiple models"""

    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize merger

        Args:
            confidence_threshold: Minimum confidence to trust a segment
        """
        self.confidence_threshold = confidence_threshold

    def merge(
        self,
        whisper_result: Dict,
        elevenlabs_result: Dict
    ) -> Dict:
        """
        Merge results from two transcription models

        Strategy:
        1. Align segments by timestamp
        2. Compare text similarity
        3. Select segment with higher confidence
        4. If confidence similar, use majority vote on words

        Args:
            whisper_result: Result from Whisper
            elevenlabs_result: Result from ElevenLabs

        Returns:
            Merged transcription with best segments
        """
        whisper_segments = whisper_result['segments']
        elevenlabs_segments = elevenlabs_result['segments']

        # Align segments by timestamp
        aligned = self._align_segments(whisper_segments, elevenlabs_segments)

        # Select best segments
        merged_segments = []
        for whisper_seg, elevenlabs_seg in aligned:
            best_seg = self._select_best_segment(whisper_seg, elevenlabs_seg)
            merged_segments.append(best_seg)

        return {
            'text': ' '.join(seg['text'] for seg in merged_segments),
            'segments': merged_segments,
            'source_models': ['whisper-large-v3', 'elevenlabs-scribe-v2'],
            'merge_strategy': 'confidence_based'
        }

    def _align_segments(
        self,
        segments_a: List[Dict],
        segments_b: List[Dict]
    ) -> List[tuple]:
        """
        Align segments from two transcriptions by timestamp overlap

        Returns:
            List of (segment_a, segment_b) pairs
        """
        aligned = []
        j = 0

        for seg_a in segments_a:
            # Find overlapping segment in B
            best_overlap = 0
            best_seg_b = None

            for seg_b in segments_b[j:]:
                overlap = self._calculate_overlap(seg_a, seg_b)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_seg_b = seg_b
                elif overlap == 0 and best_seg_b:
                    # No more overlaps, move on
                    break

            aligned.append((seg_a, best_seg_b))

        return aligned

    def _calculate_overlap(self, seg_a: Dict, seg_b: Dict) -> float:
        """Calculate temporal overlap between two segments"""
        start = max(seg_a['start'], seg_b['start'])
        end = min(seg_a['end'], seg_b['end'])
        overlap = max(0, end - start)

        # Normalize by average duration
        avg_duration = (
            (seg_a['end'] - seg_a['start']) +
            (seg_b['end'] - seg_b['start'])
        ) / 2.0

        return overlap / avg_duration if avg_duration > 0 else 0

    def _select_best_segment(
        self,
        seg_whisper: Dict,
        seg_elevenlabs: Optional[Dict]
    ) -> Dict:
        """
        Select best segment from two options

        Priority:
        1. If one is None, use the other
        2. If confidence difference > 0.2, use higher confidence
        3. If text very similar, average confidence
        4. If text different, use word-level voting
        """
        if seg_elevenlabs is None:
            return {**seg_whisper, 'source': 'whisper'}

        conf_whisper = seg_whisper.get('confidence', 0.5)
        conf_elevenlabs = seg_elevenlabs.get('confidence', 0.5)

        # Clear winner by confidence
        if abs(conf_whisper - conf_elevenlabs) > 0.2:
            if conf_whisper > conf_elevenlabs:
                return {**seg_whisper, 'source': 'whisper'}
            else:
                return {**seg_elevenlabs, 'source': 'elevenlabs'}

        # Check text similarity
        text_whisper = seg_whisper['text'].strip()
        text_elevenlabs = seg_elevenlabs['text'].strip()

        similarity = difflib.SequenceMatcher(
            None,
            text_whisper.lower(),
            text_elevenlabs.lower()
        ).ratio()

        if similarity > 0.9:
            # Very similar, use average confidence
            avg_confidence = (conf_whisper + conf_elevenlabs) / 2.0
            return {
                **seg_whisper,
                'confidence': avg_confidence,
                'source': 'consensus',
                'similarity': similarity
            }
        else:
            # Different texts, use word-level voting
            merged_text = self._merge_words(
                text_whisper,
                text_elevenlabs,
                conf_whisper,
                conf_elevenlabs
            )
            return {
                'start': seg_whisper['start'],
                'end': seg_whisper['end'],
                'text': merged_text,
                'confidence': (conf_whisper + conf_elevenlabs) / 2.0,
                'source': 'word_voting',
                'similarity': similarity,
                'whisper_text': text_whisper,
                'elevenlabs_text': text_elevenlabs
            }

    def _merge_words(
        self,
        text_a: str,
        text_b: str,
        conf_a: float,
        conf_b: float
    ) -> str:
        """
        Merge two different texts word-by-word

        Uses difflib to align words, then selects best option
        """
        words_a = text_a.split()
        words_b = text_b.split()

        matcher = difflib.SequenceMatcher(None, words_a, words_b)
        merged_words = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Words match, use them
                merged_words.extend(words_a[i1:i2])
            elif tag == 'replace':
                # Words differ, use version from higher confidence model
                if conf_a > conf_b:
                    merged_words.extend(words_a[i1:i2])
                else:
                    merged_words.extend(words_b[j1:j2])
            elif tag == 'delete':
                # Only in A, include if A has higher confidence
                if conf_a > conf_b:
                    merged_words.extend(words_a[i1:i2])
            elif tag == 'insert':
                # Only in B, include if B has higher confidence
                if conf_b > conf_a:
                    merged_words.extend(words_b[j1:j2])

        return ' '.join(merged_words)
```

**Verification:**
```bash
python3 -m pytest tests/test_consensus_merger.py -v
python3 compare_models.py --audio test.wav  # Visual comparison
```

**Acceptance Criteria:**
- ✅ Segments aligned correctly by timestamp
- ✅ Best segments selected based on confidence
- ✅ Word-level voting works for differing texts
- ✅ Final WER better than either model alone
- ✅ Merge strategy documented in output

---

#### **Task 2.4: LLM-Based Post-Processing**
**File:** `transcript_corrector.py`

**Requirements:**
- Use Claude/GPT for contextual correction
- Focus on low-confidence segments
- Apply custom therapeutic dictionary
- Preserve timestamps and structure

**Implementation Details:**
```python
import anthropic
from typing import List, Dict

class TranscriptCorrector:
    """LLM-based post-processing for transcription errors"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize corrector with Claude API

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.dictionary = self._load_dictionary()

    def _load_dictionary(self) -> Dict[str, str]:
        """Load custom therapeutic term dictionary"""
        return {
            # Common errors
            "tragen": "fragen",  # "wenn ich tragen darf" -> "wenn ich fragen darf"
            "Ego Start": "Ego State",
            "Trauma tar": "Traumata",
            "Dis Asso": "Dissoziation",

            # Therapeutic terms
            "Anker": "Anker (anchoring technique)",
            "Flash": "Flash-Technik",
            "EMDR": "EMDR (Eye Movement Desensitization)",

            # Add more as needed
        }

    def correct(
        self,
        segments: List[Dict],
        confidence_threshold: float = 0.7,
        context: str = "therapeutic conversation"
    ) -> List[Dict]:
        """
        Correct transcript segments using LLM

        Args:
            segments: List of transcript segments
            confidence_threshold: Only correct segments below this
            context: Context description for LLM

        Returns:
            Corrected segments with original preserved
        """
        corrected = []

        for seg in segments:
            if seg.get('confidence', 1.0) < confidence_threshold:
                # Low confidence, apply correction
                corrected_seg = self._correct_segment(seg, context)
                corrected.append(corrected_seg)
            else:
                # High confidence, keep as-is
                corrected.append(seg)

        return corrected

    def _correct_segment(self, segment: Dict, context: str) -> Dict:
        """Correct a single segment using LLM"""
        text = segment['text']

        # Step 1: Apply dictionary corrections
        text_dict = self._apply_dictionary(text)

        # Step 2: LLM correction if still low confidence
        if segment.get('confidence', 0.5) < 0.5:
            text_llm = self._correct_with_llm(text_dict, context)
        else:
            text_llm = text_dict

        return {
            **segment,
            'text': text_llm,
            'original_text': text,
            'corrected_by': 'dictionary+llm' if text_llm != text_dict else 'dictionary',
            'corrections_applied': text != text_llm
        }

    def _apply_dictionary(self, text: str) -> str:
        """Apply custom dictionary corrections"""
        corrected = text
        for wrong, correct in self.dictionary.items():
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(wrong), re.IGNORECASE)
            corrected = pattern.sub(correct, corrected)
        return corrected

    def _correct_with_llm(self, text: str, context: str) -> str:
        """Use LLM to correct text based on context"""
        prompt = f"""You are a German language expert specializing in therapeutic transcriptions.

Context: This text is from a {context}.

Please correct any obvious transcription errors in the following German text.
Focus on:
1. Common ASR errors (like "tragen" instead of "fragen")
2. Therapeutic terminology
3. Grammar and context

IMPORTANT:
- Only fix clear errors
- Preserve the speaker's original meaning and style
- Do not add or remove content
- If the text seems correct, return it unchanged

Text to correct:
"{text}"

Return ONLY the corrected text, no explanations."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            corrected = message.content[0].text.strip()

            # Safety check: Don't accept if too different
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, text, corrected).ratio()

            if similarity < 0.6:
                # Too different, might be hallucination
                print(f"⚠️ LLM correction rejected (similarity {similarity:.2f})")
                return text

            return corrected

        except Exception as e:
            print(f"LLM correction failed: {e}")
            return text  # Return original on error
```

**Cost Control:**
```python
def estimate_correction_cost(segments: List[Dict], confidence_threshold: float = 0.7) -> float:
    """Estimate cost of correcting transcript"""
    low_conf_segments = [s for s in segments if s.get('confidence', 1.0) < confidence_threshold]

    total_tokens = sum(len(s['text'].split()) * 1.3 for s in low_conf_segments)  # ~1.3 tokens per word
    prompt_tokens = total_tokens * 1.5  # Prompt overhead

    # Claude Sonnet pricing: $3 per million input tokens, $15 per million output tokens
    input_cost = (prompt_tokens / 1_000_000) * 3
    output_cost = (total_tokens / 1_000_000) * 15

    return input_cost + output_cost
```

**Verification:**
```bash
python3 -m pytest tests/test_transcript_corrector.py -v
python3 test_correction_quality.py --dataset test_errors.json
```

**Acceptance Criteria:**
- ✅ Dictionary corrections work correctly
- ✅ LLM corrections improve accuracy without hallucinations
- ✅ Cost stays under $0.50 per hour of audio
- ✅ Original text preserved for comparison
- ✅ Correction process logged

---

### **PHASE 3: PDF EXPORT WITH PROFESSIONAL LAYOUT** (Priority 3)

#### **Task 3.1: PDF Generator with ReportLab**
**File:** `professional_pdf_generator.py`

**Requirements:**
- Multi-page PDF generation
- Professional layout templates
- Speaker color coding
- Turning point visualization
- Metadata summary page

**Implementation Details:**

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import List, Dict
import os

class ProfessionalPDFGenerator:
    """Generate professional PDF reports for transcriptions"""

    def __init__(self, output_path: str):
        """
        Initialize PDF generator

        Args:
            output_path: Where to save the PDF
        """
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Register custom fonts (if available)
        self._register_fonts()

        # Create styles
        self.styles = self._create_styles()

        # Story (content) accumulator
        self.story = []

    def _register_fonts(self):
        """Register custom fonts for better typography"""
        try:
            # Try to use system fonts
            pdfmetrics.registerFont(
                TTFont('OpenSans', '/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf')
            )
            pdfmetrics.registerFont(
                TTFont('OpenSans-Bold', '/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf')
            )
            self.font_family = 'OpenSans'
        except:
            # Fallback to Helvetica
            self.font_family = 'Helvetica'

    def _create_styles(self) -> Dict:
        """Create paragraph styles for different elements"""
        styles = getSampleStyleSheet()

        custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                fontName=f'{self.font_family}-Bold' if self.font_family == 'OpenSans' else 'Helvetica-Bold',
                alignment=TA_CENTER
            ),
            'Heading1': ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#34495E'),
                spaceAfter=12,
                spaceBefore=12,
                fontName=f'{self.font_family}-Bold' if self.font_family == 'OpenSans' else 'Helvetica-Bold'
            ),
            'Heading2': ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#7F8C8D'),
                spaceAfter=8,
                spaceBefore=8,
                fontName=f'{self.font_family}-Bold' if self.font_family == 'OpenSans' else 'Helvetica-Bold'
            ),
            'Normal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                textColor=colors.HexColor('#2C3E50'),
                fontName=self.font_family
            ),
            'SpeakerName': ParagraphStyle(
                'SpeakerName',
                fontSize=12,
                textColor=colors.HexColor('#2C3E50'),
                fontName=f'{self.font_family}-Bold' if self.font_family == 'OpenSans' else 'Helvetica-Bold',
                spaceAfter=6
            ),
            'SpeakerText': ParagraphStyle(
                'SpeakerText',
                fontSize=11,
                leading=16,
                leftIndent=20,
                textColor=colors.HexColor('#34495E'),
                fontName=self.font_family,
                spaceAfter=12
            ),
            'Timestamp': ParagraphStyle(
                'Timestamp',
                fontSize=9,
                textColor=colors.HexColor('#95A5A6'),
                fontName=self.font_family
            ),
            'TurningPoint': ParagraphStyle(
                'TurningPoint',
                fontSize=10,
                textColor=colors.HexColor('#E74C3C'),
                fontName=f'{self.font_family}-Bold' if self.font_family == 'OpenSans' else 'Helvetica-Bold',
                leftIndent=15,
                spaceAfter=8
            )
        }

        return custom_styles

    def add_metadata_page(self, metadata: Dict):
        """
        Add metadata summary page

        Args:
            metadata: Dict with keys:
                - title: str
                - date: datetime
                - duration: float (seconds)
                - speakers: List[Dict]
                - quality: float
                - turning_points_count: int
                - model: str
        """
        # Title
        self.story.append(Paragraph(
            "THERAPEUTIC TRANSCRIPTION REPORT",
            self.styles['Title']
        ))
        self.story.append(Spacer(1, 0.5*cm))

        # Logo placeholder (if you have one)
        # logo_path = "assets/logo.png"
        # if os.path.exists(logo_path):
        #     img = Image(logo_path, width=4*cm, height=2*cm)
        #     self.story.append(img)
        #     self.story.append(Spacer(1, 1*cm))

        # Metadata section
        self.story.append(Paragraph("📋 METADATA", self.styles['Heading1']))
        self.story.append(Spacer(1, 0.3*cm))

        metadata_table = [
            ["Date:", metadata.get('date', datetime.now()).strftime("%d.%m.%Y %H:%M")],
            ["Duration:", self._format_duration(metadata.get('duration', 0))],
            ["Speakers:", f"{len(metadata.get('speakers', []))} detected"],
            ["Overall Quality:", f"{metadata.get('quality', 0.0):.0%}"],
            ["Model:", metadata.get('model', 'Whisper large-v3')],
            ["Turning Points:", str(metadata.get('turning_points_count', 0))]
        ]

        t = Table(metadata_table, colWidths=[4*cm, 12*cm])
        t.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), f'{self.font_family}-Bold' if self.font_family == 'OpenSans' else 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), self.font_family, 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        self.story.append(t)
        self.story.append(Spacer(1, 1*cm))

        # Speaker list
        self.story.append(Paragraph("👥 SPEAKERS", self.styles['Heading1']))
        self.story.append(Spacer(1, 0.3*cm))

        speakers = metadata.get('speakers', [])
        if speakers:
            speaker_data = [["#", "Name", "Duration", "Segments"]]
            for i, speaker in enumerate(speakers, 1):
                speaker_data.append([
                    str(i),
                    speaker.get('name', f'Speaker {i}'),
                    self._format_duration(speaker.get('total_duration', 0)),
                    str(speaker.get('segment_count', 0))
                ])

            st = Table(speaker_data, colWidths=[1*cm, 7*cm, 4*cm, 3*cm])
            st.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), f'{self.font_family}-Bold' if self.font_family == 'OpenSans' else 'Helvetica-Bold', 11),
                # Data rows
                ('FONT', (0, 1), (-1, -1), self.font_family, 10),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))

            self.story.append(st)

        self.story.append(Spacer(1, 1*cm))

        # Turning points summary
        if metadata.get('turning_points_count', 0) > 0:
            self.story.append(Paragraph("🔄 KEY TURNING POINTS SUMMARY", self.styles['Heading1']))
            self.story.append(Spacer(1, 0.3*cm))

            tp_list = metadata.get('turning_points', [])
            for i, tp in enumerate(tp_list[:5], 1):  # Top 5
                time_str = self._format_time(tp.get('timestamp', 0))
                tp_type = tp.get('type', 'unknown').replace('_', ' ').title()
                confidence = tp.get('confidence', 0.0)

                tp_text = f"{i}. [{time_str}] <b>{tp_type}</b> (Confidence: {confidence:.0%})"
                self.story.append(Paragraph(tp_text, self.styles['TurningPoint']))

            self.story.append(Spacer(1, 0.5*cm))

        # Page break before transcript
        self.story.append(PageBreak())

    def add_transcript_page(self, segments: List[Dict]):
        """
        Add transcript with speaker visualization

        Args:
            segments: List of transcript segments with speaker info
        """
        self.story.append(Paragraph("💬 FULL TRANSCRIPT WITH ANNOTATIONS", self.styles['Heading1']))
        self.story.append(Spacer(1, 0.5*cm))

        previous_speaker = None

        for seg in segments:
            speaker_id = seg.get('speaker_id', 'unknown')
            speaker_name = seg.get('speaker_name', f'Speaker {speaker_id}')
            speaker_color = seg.get('color', '#4A90E2')
            text = seg['text']
            start = seg['start']
            end = seg['end']
            confidence = seg.get('confidence', 1.0)

            # Add divider line if speaker changed
            if speaker_id != previous_speaker and previous_speaker is not None:
                self.story.append(HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor('#BDC3C7'),
                    spaceAfter=0.3*cm,
                    spaceBefore=0.3*cm
                ))

            # Speaker header with icon and color bar
            icon = self._get_speaker_icon(hash(speaker_id) % 8)
            time_str = f"[{self._format_time(start)} - {self._format_time(end)}]"

            # Create colored table for speaker header
            header_data = [[
                Paragraph(f"{icon} <b>{speaker_name}</b>", self.styles['SpeakerName']),
                Paragraph(time_str, self.styles['Timestamp'])
            ]]

            header_table = Table(header_data, colWidths=[12*cm, 5*cm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(speaker_color + '20')),  # 20% opacity
                ('LEFTPADDING', (0, 0), (0, -1), 10),
                ('RIGHTPADDING', (-1, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, -1), 3, colors.HexColor(speaker_color)),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            self.story.append(header_table)
            self.story.append(Spacer(1, 0.2*cm))

            # Speaker text with confidence indicator
            if confidence < 0.7:
                text_with_conf = f"{text} <font color='#E67E22'>[⚠️ Low confidence: {confidence:.0%}]</font>"
            else:
                text_with_conf = text

            self.story.append(Paragraph(text_with_conf, self.styles['SpeakerText']))

            # Check if segment has turning point
            if seg.get('has_turning_point'):
                tp = seg['turning_point']
                self._add_turning_point_box(tp)

            previous_speaker = speaker_id

    def _add_turning_point_box(self, tp: Dict):
        """Add a highlighted box for a turning point"""
        tp_type = tp.get('type', 'unknown').replace('_', ' ').title()
        confidence = tp.get('confidence', 0.0)

        # Header
        tp_header = f"🔄 <b>TURNING POINT DETECTED: {tp_type}</b> (Confidence: {confidence:.0%})"
        self.story.append(Paragraph(tp_header, self.styles['TurningPoint']))

        # Prosody evidence
        prosody = tp.get('prosody_evidence', {})
        if prosody:
            evidence_data = [
                ["📊 Prosody Evidence:", ""],
                ["• Pitch:", f"+{prosody.get('pitch_change', 0):.1f}% ({prosody.get('pitch_from', 0):.1f} Hz → {prosody.get('pitch_to', 0):.1f} Hz)"],
                ["• Tempo:", f"+{prosody.get('tempo_change', 0):.1f}% ({prosody.get('tempo_from', 0):.1f} WPM → {prosody.get('tempo_to', 0):.1f} WPM)"],
                ["• Energy:", f"+{prosody.get('energy_change', 0):.1f}% ({prosody.get('energy_from', 0):.4f} → {prosody.get('energy_to', 0):.4f} RMS)"],
                ["• CoSD Score:", f"{prosody.get('cosd_score', 0):.2f} (threshold: {prosody.get('cosd_threshold', 0.6):.2f})"]
            ]

            evidence_table = Table(evidence_data, colWidths=[4*cm, 12*cm])
            evidence_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_family, 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#34495E')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF9E6')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F39C12')),
            ]))

            self.story.append(Spacer(1, 0.2*cm))
            self.story.append(evidence_table)
            self.story.append(Spacer(1, 0.3*cm))

    def _get_speaker_icon(self, index: int) -> str:
        """Get emoji icon for speaker"""
        icons = ["👤", "👨", "👩", "🧑", "👴", "👵", "🧔", "👱"]
        return icons[index % len(icons)]

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def _format_time(self, seconds: float) -> str:
        """Format timestamp in seconds to MM:SS"""
        return self._format_duration(seconds)

    def generate(self):
        """Build the PDF document"""
        self.doc.build(self.story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        print(f"✅ PDF generated: {self.output_path}")

    def _add_page_number(self, canvas_obj, doc):
        """Add page number to footer"""
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.saveState()
        canvas_obj.setFont(self.font_family, 9)
        canvas_obj.setFillColor(colors.HexColor('#95A5A6'))
        canvas_obj.drawRightString(A4[0] - 2*cm, 1*cm, text)
        canvas_obj.restoreState()
```

**Usage Example:**
```python
# Generate PDF
pdf = ProfessionalPDFGenerator("output/transcript_2025-11-12.pdf")

# Add metadata page
pdf.add_metadata_page({
    'title': 'Therapeutic Session',
    'date': datetime.now(),
    'duration': 2745,  # 45 minutes 45 seconds
    'speakers': [
        {'name': 'Dr. Schmidt', 'total_duration': 1523, 'segment_count': 45},
        {'name': 'Patient A', 'total_duration': 1222, 'segment_count': 38}
    ],
    'quality': 0.87,
    'turning_points_count': 7,
    'model': 'Whisper large-v3 + ElevenLabs Scrive v2',
    'turning_points': [
        {
            'timestamp': 225,
            'type': 'cognitive_shift',
            'confidence': 0.89
        },
        {
            'timestamp': 750,
            'type': 'emotional_peak',
            'confidence': 0.92
        }
    ]
})

# Add transcript pages
pdf.add_transcript_page(segments)

# Generate file
pdf.generate()
```

**Verification:**
```bash
python3 test_pdf_generator.py
# Manual visual inspection of generated PDFs
```

**Acceptance Criteria:**
- ✅ PDF generates without errors
- ✅ All pages formatted correctly
- ✅ Metadata page includes all information
- ✅ Speaker colors visible and consistent
- ✅ Turning points clearly highlighted with evidence
- ✅ Professional typography and layout
- ✅ File size reasonable (<5MB for 1 hour)

---

## 🔄 INTEGRATION & TESTING

### **Task 4.1: End-to-End Integration Test**
**File:** `tests/test_e2e_professional.py`

**Test Scenario:**
1. Upload test audio file (German therapeutic conversation)
2. Run full pipeline with all enhancements
3. Verify output quality meets all acceptance criteria

**Verification:**
```bash
python3 -m pytest tests/test_e2e_professional.py -v --duration=0
```

---

### **Task 4.2: Performance Benchmarking**
**File:** `benchmark_professional_pipeline.py`

**Metrics to track:**
- Processing time (target: <15x real-time)
- Memory usage (target: <16GB peak)
- Cost per hour of audio (target: <$2.00)
- WER (Word Error Rate) (target: <5%)
- Turning point detection F1-score (target: >0.85)

---

### **Task 4.3: Update GUI with New Features**
**File:** `svt_v2.py`

**New GUI elements:**
1. Model selector (Whisper large-v3, ElevenLabs, Both)
2. Speaker name editor button
3. PDF export options
4. Progress bar with detailed status
5. Cost estimator

---

## 📅 TIMELINE & MILESTONES

| Week | Phase | Deliverable |
|------|-------|-------------|
| Week 1 | Phase 1 | Speaker system enhancement complete |
| Week 2 | Phase 2 | Multi-model transcription working |
| Week 3 | Phase 2-3 | Post-processing + PDF export |
| Week 4 | Phase 3 | Full integration & testing |

---

## 🎯 SUCCESS CRITERIA

### Must Have (P0):
- ✅ Whisper large-v3 integration
- ✅ Speaker name editing
- ✅ Enhanced speaker visualization
- ✅ PDF export with turning points
- ✅ All tests passing

### Should Have (P1):
- ✅ ElevenLabs Scrive v2 integration
- ✅ Multi-model consensus
- ✅ LLM post-processing
- ✅ Cost tracking

### Nice to Have (P2):
- ⏳ Real-time transcription mode
- ⏳ Web-based UI (Flask)
- ⏳ API server mode
- ⏳ Cloud deployment

---

## 📊 QUALITY METRICS

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| WER (German) | ~8% | <5% | 🎯 |
| Speaker Diarization Accuracy | ~85% | >90% | 🎯 |
| Turning Point F1-Score | ~0.78 | >0.85 | 🎯 |
| Processing Speed | ~20x RT | <15x RT | 🎯 |
| PDF Generation Time | N/A | <10s | 🎯 |
| User Satisfaction | N/A | >4.5/5 | 🎯 |

---

## 🔐 SECURITY & PRIVACY

### Data Protection:
- ✅ All processing local (DSGVO compliant)
- ✅ Optional API calls with explicit consent
- ✅ No data retention in cloud services
- ✅ Encrypted speaker database

### API Key Management:
- ✅ Keys stored in .env file (git-ignored)
- ✅ Never logged or printed
- ✅ Rotation supported

---

## 📚 DOCUMENTATION UPDATES

### Files to Update:
1. `CLAUDE.md` - Architecture and usage
2. `README.md` - Installation and quick start
3. `docs/USER_GUIDE.md` - Step-by-step tutorials
4. `docs/API.md` - Developer API reference
5. `docs/TURNING_POINTS.md` - Scientific documentation

---

## 🚀 DEPLOYMENT STRATEGY

### Local Installation:
```bash
# 1. Update repository
git pull origin feat/professional-quality-enhancement

# 2. Install new dependencies
pip3 install -r requirements.txt

# 3. Download models
python3 scripts/download_models.py

# 4. Configure API keys (optional)
cp .env.example .env
# Edit .env with your keys

# 5. Run tests
python3 -m pytest tests/ -v

# 6. Launch application
python3 svt_v2.py
```

---

## 💰 COST ANALYSIS

### Per Hour of Audio:

| Component | Cost | Notes |
|-----------|------|-------|
| Whisper large-v3 | $0.00 | Local, free |
| ElevenLabs Scrive v2 | $6.00 | $0.10/min |
| LLM Post-Processing | $0.30 | ~100K tokens |
| **Total (all features)** | **$6.30** | |
| **Total (Whisper only)** | **$0.30** | Recommended default |

**Recommendation:** Use Whisper large-v3 by default, ElevenLabs as optional upgrade for critical sessions.

---

## ✅ NEXT STEPS

1. **Review this plan with stakeholders**
2. **Set up development environment**
3. **Start with Phase 1 (Speaker System)**
4. **Weekly progress reviews**
5. **Iterate based on user feedback**

---

**Plan Created:** 2025-11-12
**Plan Version:** 5.0
**Estimated Completion:** 4 weeks
**Priority:** HIGH - Core Differentiator Implementation
