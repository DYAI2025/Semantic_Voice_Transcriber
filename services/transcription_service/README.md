# Transcription Service - Standalone Speech-to-Text with Speaker Detection

**Version:** 1.0.0 | **Last Updated:** 2025-12-07

## Overview

This is a standalone transcription microservice that provides high-precision speech-to-text using OpenAI Whisper, with optional speaker detection and recognition via pyannote.audio.

### Key Features

✅ **Pure Transcription** - No dependencies on prosody, emotion, or semantic analysis
✅ **Speaker Detection** - Optional speaker diarization via adapter pattern
✅ **Multi-Model Support** - 5 Whisper models (tiny → large) with intelligent selection
✅ **REST API** - FastAPI endpoints for independent deployment
✅ **Backward Compatible** - Legacy function wrappers for smooth migration
✅ **Dockerized** - Ready for containerized deployment

---

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies
pip install openai-whisper fastapi uvicorn numpy librosa soundfile pydantic

# Optional: Speaker diarization
pip install pyannote.audio torch
```

### 2. Basic Usage (Python)

```python
from services.transcription_service import (
    TranscriptionService,
    TranscriptionRequest,
    ModelProfile
)
from pathlib import Path

# Initialize service
service = TranscriptionService()

# Transcribe audio
request = TranscriptionRequest(
    audio_path=Path("recording.opus"),
    language="de",
    model_profile=ModelProfile(name="medium")
)

response = service.transcribe(request)

print(f"Transcription: {response.text}")
print(f"Confidence: {response.confidence_scores['overall_confidence']:.1%}")
```

### 3. REST API

**Start server:**
```bash
cd services/transcription_service
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Call API:**
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@recording.opus" \
  -F "language=de" \
  -F "model_profile=medium"
```

**Response:**
```json
{
  "text": "Full transcription text...",
  "segments": [...],
  "confidence_scores": {
    "overall_confidence": 0.87,
    "total_segments": 42
  },
  "marked_text": "Text with [UNSICHER:0.42] markers..."
}
```

---

## Adding Speaker Detection

### Setup

1. **Install pyannote.audio:**
   ```bash
   pip install pyannote.audio torch
   ```

2. **Get Hugging Face token:**
   - Sign up: https://huggingface.co/join
   - Accept agreements:
     - https://huggingface.co/pyannote/segmentation-3.0
     - https://huggingface.co/pyannote/speaker-diarization-3.1
   - Create token: https://huggingface.co/settings/tokens
   - Add to `.env`:
     ```
     HF_TOKEN=hf_YourTokenHere
     ```

### Usage with Speaker Detection

```python
import os
from services.transcription_service import TranscriptionService
from svt_core.audio.diarization import SpeakerDiarizer

# Create diarization adapter
class DiarizationAdapter:
    def __init__(self, hf_token):
        self.diarizer = SpeakerDiarizer(hf_token=hf_token)

    def attach(self, raw_result, request):
        # Run speaker diarization
        diarization = self.diarizer.diarize_audio(
            str(request.audio_path),
            num_speakers="auto"
        )

        # Merge speaker labels with transcription
        for segment in raw_result.get("segments", []):
            for spk_seg in diarization["segments"]:
                if spk_seg["start"] <= segment["start"] < spk_seg["end"]:
                    segment["speaker"] = spk_seg["speaker"]
                    break

        return diarization

# Initialize service with adapter
service = TranscriptionService(
    diarization_adapter=DiarizationAdapter(os.getenv("HF_TOKEN"))
)

# Transcribe with speaker detection
response = service.transcribe(request)

# Print results with speakers
for segment in response.segments:
    speaker = segment.get("speaker", "Unknown")
    print(f"[{speaker}] {segment['text']}")
```

---

## Architecture

### Service Structure

```
services/transcription_service/
├── __init__.py              # Public API exports
├── transcription_service.py # Core service logic
├── model_manager.py         # Whisper model loading
├── config.py                # Configuration management
├── api.py                   # FastAPI REST endpoints
├── cli.py                   # Command-line interface
├── adapters.py              # Optional feature adapters
├── pipeline_integration.py  # Legacy integration
├── Dockerfile               # Container definition
└── README.md                # This file
```

### Dependency Layers

```
┌─────────────────────────────────────┐
│    Transcription Service (Core)     │
│  - Whisper STT                      │
│  - Confidence scoring               │
│  - Model management                 │
└────────────┬────────────────────────┘
             │
             ├──> Optional: Prosody Adapter
             ├──> Optional: Diarization Adapter
             └──> Optional: Custom Adapters
```

**Core Dependencies (Required):**
- `openai-whisper` - STT engine
- `fastapi` - REST API framework
- `numpy` - Numerical operations
- `librosa`, `soundfile` - Audio processing

**Optional Dependencies:**
- `pyannote.audio` - Speaker diarization
- `torch` - PyTorch for diarization models

---

## Configuration

### Environment Variables

```bash
# Base paths
SVT_BASE_PATH=/path/to/transcriber
SVT_INPUT_DIR=${SVT_BASE_PATH}/Eingang
SVT_OUTPUT_DIR=${SVT_BASE_PATH}/Transkripte_LLM
SVT_LOG_DIR=${SVT_BASE_PATH}/logs

# Model cache
SVT_MODEL_CACHE=${HOME}/.cache/whisper

# Speaker diarization (optional)
HF_TOKEN=hf_YourTokenHere
```

### Config File (YAML)

```yaml
# config/transcription.yaml
input_dir: Eingang
output_dir: Transkripte_LLM
log_dir: logs
cache_dir: /path/to/model/cache
```

**Load config:**
```python
from services.transcription_service import TranscriptionConfig

# From environment
config = TranscriptionConfig.from_env()

# From file
from pathlib import Path
config = TranscriptionConfig.from_file(Path("config/transcription.yaml"))
```

---

## API Reference

### POST /transcribe

**Request (multipart/form-data):**
- `file` (required): Audio file
- `language` (optional): "de" | "en" | "auto" (default: "de")
- `model_profile` (optional): "tiny" | "base" | "small" | "medium" | "large" (default: "base")
- `initial_prompt` (optional): Context prompt for Whisper

**Response (JSON):**
```json
{
  "text": "Full transcription text",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Segment text",
      "confidence": 0.92,
      "avg_logprob": -0.18,
      "no_speech_prob": 0.02
    }
  ],
  "confidence_scores": {
    "overall_confidence": 0.87,
    "total_segments": 42,
    "low_confidence_segments": []
  },
  "marked_text": "Text with [UNSICHER:0.42] markers",
  "source": "recording.opus"
}
```

### GET /health

**Response:**
```json
{
  "status": "ok"
}
```

---

## Docker Deployment

### Build Image

```bash
docker build -t svt-transcription -f Dockerfile .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e HF_TOKEN=${HF_TOKEN} \
  -v $(pwd)/audio:/audio \
  svt-transcription
```

### Docker Compose

```yaml
version: '3.8'
services:
  transcription:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HF_TOKEN=${HF_TOKEN}
    volumes:
      - ./Eingang:/app/Eingang
      - ./Transkripte_LLM:/app/Transkripte_LLM
```

---

## Migration from Monolith

### Backward Compatibility

**Old code (still works):**
```python
from auto_transcriber_v4_emotion import transcribe_audio_whisper

result = transcribe_audio_whisper(
    audio_path="recording.opus",
    model_size="medium",
    language="de"
)
```

**New code (recommended):**
```python
from services.transcription_service import transcribe_with_whisper

result = transcribe_with_whisper(
    audio_path="recording.opus",
    model_size="medium",
    language="de"
)
```

---

## Testing

```bash
# Unit tests
pytest tests/test_transcription_service_unit.py -v

# Integration tests
pytest tests/test_pipeline_integration_adapter.py -v

# API tests
pytest tests/test_transcription_service_api.py -v

# Standalone tests
pytest tests/test_standalone_transcriber.py -v
```

---

## Performance

| Model | WER (German) | Processing Speed | Memory |
|-------|-------------|-----------------|--------|
| tiny | ~12% | 0.05x RT | 1 GB |
| base | ~8% | 0.10x RT | 1.5 GB |
| small | ~6% | 0.15x RT | 2 GB |
| medium | ~4.2% | 0.25x RT | 4 GB |
| large | ~3.5% | 0.40x RT | 8 GB |

**RT = Real-time** (e.g., 0.25x RT = 30-min audio in 7.5 min)

---

## Limitations

1. **No async job queue** - Long audio blocks API (use Celery for production)
2. **No persistent storage** - Results not auto-saved (add PostgreSQL/S3)
3. **No rate limiting** - Can be overwhelmed (add API gateway)
4. **Diarization CPU mode slow** - 10x slower than GPU (use GPU if available)

---

## Roadmap

- [ ] Async job queue (Celery + Redis)
- [ ] Persistent storage (PostgreSQL + S3)
- [ ] API gateway with rate limiting
- [ ] Streaming transcription (real-time)
- [ ] Speaker embedding database
- [ ] Cross-session speaker matching

---

## Support

**Documentation:**
- Main status: [../../MICROSERVICE_TRANSCRIBER_STATUS.md](../../MICROSERVICE_TRANSCRIBER_STATUS.md)
- Architecture: [../../docs/microservices_architecture.md](../../docs/microservices_architecture.md)
- Speaker diarization: [../../SPEAKER_DIARIZATION.md](../../SPEAKER_DIARIZATION.md)

**Issues:**
- GitHub: https://github.com/DYAI2025/Semantic_Voice_Transcriber/issues

---

**Maintained By:** SVT Development Team
**License:** See parent repository
**Last Updated:** 2025-12-07
