# SVT Transcription Microservice - Implementation Plan

**Last Updated:** 2025-11-28 | **Status:** Planning Phase
**Priority:** P0 (Critical Path - Foundation for all other services)

## Executive Summary

This document provides a focused implementation plan for extracting the **Transcription Service** from the SVT monolith. This is the **first and most critical step** in the microservices migration, as all other analysis services depend on high-quality transcription output.

### Goals

1. **Pure Transcription Service:** Standalone API for Whisper-based STT
2. **Highest Precision:** WER < 5% for high-quality audio
3. **Speaker Separation:** Integration with diarization service
4. **Word Recognition:** Confidence scoring per segment
5. **Production Ready:** 99%+ uptime, handles 1000+ requests/day

---

## Current Architecture Analysis

### Components and Coupling

- **Monolithic orchestrator**: `auto_transcriber_v4_emotion.py` loads prosody, diarization, sentiment, and correlation modules in the same runtime, turning optional analytics into hard runtime imports with best-effort fallbacks for missing dependencies (e.g., `ProsodyExtractor`, `SpeakerDiarizer`, TextBlob, ATO correlation engine). The file also controls Whisper inference and speaker-context prompting, so failure in downstream analytics still touches the core transcription entry point.

- **End-to-end pipeline**: The architecture document shows the GUI and `auto_transcriber_v4_emotion.py` orchestrating audio processing → prosody → diarization → Whisper → semantic analysis → interpretation → formatting in a single flow, reinforcing tight coupling between transcription and semantic enrichment.

### Known Issues and Risks

- **Dependency version blockers**: Historic failures installing `torch==2.9.0` and conflicting `pathlib/pathlib2` packages caused full install breakage across OSes. Although marked as fixed, any reversion to pinned versions would immediately break setup.

- **Platform-specific setup gap**: `setup_environment.py` remains Unix-centric (chmod and Bash launcher creation), still flagged as a moderate unresolved issue for Windows environments.

- **Resilience issues**: Optional analytics are imported inside `auto_transcriber_v4_emotion.py` rather than run behind interfaces; missing packages only log warnings, but the module remains large and intertwined, making failures harder to isolate and increasing startup time and memory footprint.

---

## Service Overview

### Core Capabilities

```
INPUT:  Audio file (opus, m4a, wav, mp3, ogg)
        ↓
PROCESSING:
- Quality analysis → Model selection (tiny/base/small/medium/large)
- Whisper STT → Timestamped segments
- Confidence scoring (avg_logprob, no_speech_prob)
- Language detection (100+ languages)
        ↓
OUTPUT: JSON with segments, timestamps, confidence scores
```

### Key Features

- ✅ Multi-model support (5 Whisper models)
- ✅ Intelligent model selection based on audio quality
- ✅ Long audio support (chunking with overlap)
- ✅ Async processing (Celery + Redis)
- ✅ RESTful API (FastAPI)
- ✅ S3-compatible storage
- ✅ GPU acceleration (optional)

---

## Architecture

### System Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────────┐
│     Nginx Load Balancer             │
│     (SSL Termination)               │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│     FastAPI Application             │
│  ┌────────────────────────────────┐ │
│  │ POST /api/v1/transcribe        │ │
│  │ GET  /api/v1/jobs/{id}         │ │
│  │ GET  /api/v1/health            │ │
│  └────────────────────────────────┘ │
└──────┬──────────────────────────────┘
       │
       ├──▶ Redis (Task Queue)
       │       ▲
       │       │
       ▼       │
┌──────────────┴──────────────────────┐
│    Celery Workers (3-5 instances)   │
│  ┌────────────────────────────────┐ │
│  │ 1. Load audio from S3          │ │
│  │ 2. Quality analysis            │ │
│  │ 3. Select Whisper model        │ │
│  │ 4. Transcribe (chunked)        │ │
│  │ 5. Confidence scoring          │ │
│  │ 6. Store result in PostgreSQL  │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
       │
       ├──▶ MinIO/S3 (Audio Storage)
       │
       └──▶ PostgreSQL (Metadata)
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI 0.100+ | REST endpoints, async support |
| STT Engine | openai-whisper | Speech-to-text |
| Task Queue | Celery 5.3.4 | Async job processing |
| Message Broker | Redis 7.x | Queue backend |
| Storage | MinIO/S3 | Audio file storage |
| Database | PostgreSQL 15 | Transcription metadata |
| Audio Processing | FFmpeg, librosa | Format conversion, analysis |
| Containerization | Docker, Kubernetes | Deployment |
| Monitoring | Prometheus, Grafana | Metrics and alerts |

---

## API Specification

### POST /api/v1/transcribe

**Purpose:** Submit audio file for transcription

**Request:**
```bash
curl -X POST https://transcription-api.example.com/api/v1/transcribe \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "audio_file=@recording.opus" \
  -F "model=auto" \
  -F "language=de" \
  -F "options={\"min_confidence\": 0.5}"
```

**Request Body (JSON alternative):**
```json
{
  "audio_file": "base64_encoded_audio_data",
  "model": "auto|tiny|base|small|medium|large",
  "language": "auto|de|en|fr|es|...",
  "options": {
    "enable_timestamps": true,
    "min_confidence": 0.5,
    "chunk_duration": 300.0,
    "beam_size": 5,
    "best_of": 5
  }
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "queued",
  "created_at": "2025-11-28T10:30:00Z",
  "status_url": "/api/v1/jobs/f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

---

### GET /api/v1/jobs/{job_id}

**Purpose:** Check transcription job status

**Response (Processing):**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "processing",
  "progress": 0.45,
  "created_at": "2025-11-28T10:30:00Z",
  "started_at": "2025-11-28T10:30:05Z",
  "estimated_completion": "2025-11-28T10:32:00Z"
}
```

**Response (Completed):**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "created_at": "2025-11-28T10:30:00Z",
  "started_at": "2025-11-28T10:30:05Z",
  "completed_at": "2025-11-28T10:31:45Z",
  "processing_time_seconds": 100.2,
  "result": {
    "language": "de",
    "language_probability": 0.98,
    "model_used": "medium",
    "duration_seconds": 120.5,
    "segments": [
      {
        "id": 0,
        "start": 0.0,
        "end": 3.52,
        "text": "Guten Tag, wie geht es Ihnen heute?",
        "tokens": [50364, 42833, 3834, 11, 1326, 48065, 1279, 286, 25084, 11037, 30, 50540],
        "temperature": 0.0,
        "avg_logprob": -0.18,
        "compression_ratio": 1.54,
        "no_speech_prob": 0.02,
        "confidence": 0.92
      },
      {
        "id": 1,
        "start": 3.52,
        "end": 6.84,
        "text": "Mir geht es sehr gut, vielen Dank.",
        "tokens": [50540, 14322, 48065, 1279, 15040, 5697, 11, 371, 42043, 3801, 74, 13, 50706],
        "temperature": 0.0,
        "avg_logprob": -0.15,
        "compression_ratio": 1.48,
        "no_speech_prob": 0.01,
        "confidence": 0.94
      }
    ],
    "metadata": {
      "audio_format": "opus",
      "sample_rate": 48000,
      "channels": 1,
      "bitrate": 64000,
      "quality_score": 0.87,
      "snr_db": 18.5
    }
  }
}
```

---

### GET /api/v1/health

**Purpose:** Service health check

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "ok",
    "celery_workers": {"total": 5, "active": 3, "idle": 2},
    "redis": "ok",
    "postgres": "ok",
    "minio": "ok"
  },
  "models_loaded": ["tiny", "base", "small", "medium", "large"],
  "queue_size": 12,
  "avg_processing_time_seconds": 95.4
}
```

---

## Separation Strategy

### 1. Define Stable Transcription Contract

**Objective:** Create a clean interface between transcription and other services

**Tasks:**
- [ ] Draft `transcription_service` package exposing `transcribe(audio_path, config) -> Transcript`
- [ ] Write JSON schema for requests/responses (transport-agnostic)
- [ ] Define strict input validation (Pydantic models)
- [ ] Define structured output format (segments, language, confidence, timestamps)

**Deliverables:**
- `schemas/transcription_request.json`
- `schemas/transcription_response.json`
- Pydantic models in `api/models.py`

---

### 2. Extract Core Whisper Runner

**Objective:** Isolate Whisper inference from analytics dependencies

**Tasks:**
- [ ] Move Whisper loading, model selection from `auto_transcriber_v4_emotion.py` → `transcription_service/core/transcriber.py`
- [ ] Remove prosody/semantics imports
- [ ] Preserve speaker-context prompt loading as optional hook (dependency injection)
- [ ] Implement model caching for faster startups

**Before (Monolith):**
```python
# auto_transcriber_v4_emotion.py
from prosody_extractor import ProsodyExtractor
from speaker_diarizer import SpeakerDiarizer
from psychoanalysis_pipeline import analyze_emotions
# ... 20+ imports

def transcribe_and_analyze(audio_path):
    # Whisper + prosody + diarization + emotion
    ...
```

**After (Service):**
```python
# transcription_service/core/transcriber.py
import whisper
from .analyzer import AudioQualityAnalyzer

def transcribe(audio_path: str, config: TranscriptionConfig) -> Transcript:
    # ONLY Whisper STT
    model = whisper.load_model(config.model)
    result = model.transcribe(audio_path)
    return Transcript.from_whisper_result(result)
```

**Deliverables:**
- `transcription_service/core/transcriber.py`
- Unit tests for model loading and inference
- No analytics dependencies

---

### 3. Isolate Audio Preparation

**Objective:** Lightweight preprocessing without semantic side effects

**Tasks:**
- [ ] Lift `audio_quality_analyzer.py` → `transcription_service/core/analyzer.py`
- [ ] Lift `audio_preprocessor.py` → `transcription_service/core/preprocessor.py`
- [ ] Lift `audio_chunker.py` → `transcription_service/core/chunker.py`
- [ ] Provide clear error codes for unsupported formats (no silent fallbacks)

**Deliverables:**
- `transcription_service/core/analyzer.py`
- `transcription_service/core/preprocessor.py`
- `transcription_service/core/chunker.py`
- Error code enum (e.g., `UNSUPPORTED_FORMAT`, `CORRUPT_FILE`)

---

### 4. Abstract Optional Enrichments

**Objective:** Decouple transcription from analytics

**Tasks:**
- [ ] Replace direct imports with interface stubs (e.g., `ProsodyFeatureProvider`)
- [ ] Load enrichments only in legacy monolith or separate services
- [ ] Enable webhook-based enrichment (event-driven architecture)

**Example Interface:**
```python
# transcription_service/interfaces.py
from abc import ABC, abstractmethod

class TranscriptionEnrichmentProvider(ABC):
    @abstractmethod
    def enrich(self, transcript: Transcript) -> EnrichedTranscript:
        pass

# Implementations in other services
class ProsodyEnrichmentProvider(TranscriptionEnrichmentProvider):
    ...

class EmotionEnrichmentProvider(TranscriptionEnrichmentProvider):
    ...
```

**Deliverables:**
- Interface definitions
- Webhook system for async enrichment
- Event bus integration (optional: Kafka, RabbitMQ)

---

### 5. Build Microservice Shell

**Objective:** Standalone service with minimal dependencies

**Tasks:**
- [ ] Add FastAPI wrapper with `/health`, `/transcribe`, `/metrics`
- [ ] Keep only core dependencies (`ffmpeg`, `whisper`, `numpy`, `pydantic`)
- [ ] Containerize with slim base image
- [ ] Mount model cache for faster startups

**Dependencies (requirements.txt):**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
celery==5.3.4
redis==5.0.1
psycopg2-binary==2.9.9
boto3==1.29.7
openai-whisper==20231117
librosa==0.10.1
soundfile==0.12.1
pydantic==2.5.0
python-multipart==0.0.6
```

**No longer required:**
- TextBlob, nltk (emotion analysis)
- parselmouth (prosody)
- pyannote.audio (diarization)
- All marker/semantic dependencies

**Deliverables:**
- FastAPI application (`main.py`)
- Dockerfile with slim base
- `requirements.txt` (minimal)

---

### 6. Refactor GUI and Pipelines

**Objective:** Update clients to use new service

**Tasks:**
- [ ] Update `svt.py` to call transcription endpoint first
- [ ] Pass results to existing prosody/semantic processors as separate steps
- [ ] Preserve backward compatibility with adapter pattern

**Before (Monolith):**
```python
# svt.py
result = auto_transcriber_v4_emotion.process(audio_path)
# result contains transcription + prosody + emotion + markers
```

**After (Microservices):**
```python
# svt.py
transcript = transcription_service.transcribe(audio_path)
prosody = prosody_service.analyze(transcript)
emotion = emotion_service.analyze(transcript)
markers = marker_service.detect(transcript, prosody, emotion)
```

**Deliverables:**
- Updated `svt.py` with service calls
- Adapter for backward compatibility
- Migration guide for other clients

---

### 7. Testing and Hardening

**Objective:** Ensure service reliability

**Tasks:**
- [ ] Unit tests for service contract
- [ ] E2E tests with mocked enrichments
- [ ] Verify transcription works when auxiliary services are down
- [ ] Re-run cross-platform installation checks
- [ ] Load testing (100+ concurrent requests)

**Test Scenarios:**
- Transcription-only (no prosody/emotion)
- Long audio files (60+ minutes)
- Low-quality audio (graceful degradation)
- Unsupported formats (clear error messages)
- Network failures (S3, PostgreSQL)

**Deliverables:**
- Test suite with 80%+ coverage
- Load testing report
- Cross-platform verification (Windows, macOS, Linux)

---

## Implementation Roadmap

### Week 1: Project Setup & Core Extraction

**Days 1-2: Repository Setup**
- [ ] Create `transcription-service/` directory
- [ ] Initialize Git repository
- [ ] Set up Python virtual environment (Python 3.13)  <!-- Updated to latest stable; verify openai-whisper compatibility -->
- [ ] Create minimal `requirements.txt`
- [ ] Create Docker development environment

**Days 3-5: Core Logic Extraction**
- [ ] Extract transcription logic → `transcription_service/core/transcriber.py`
- [ ] Extract quality analyzer → `transcription_service/core/analyzer.py`
- [ ] Extract audio chunker → `transcription_service/core/chunker.py`
- [ ] Remove all analytics dependencies
- [ ] Unit tests for core logic

**Deliverables:**
- ✅ Python project structure
- ✅ Core transcription modules (no analytics)
- ✅ Unit tests with pytest

---

### Week 2: FastAPI Application & Storage

**Days 1-3: API Development**
- [ ] Create FastAPI app with 3 endpoints
- [ ] Implement file upload handling
- [ ] Implement request validation (Pydantic)
- [ ] Add API key authentication (JWT)

**Days 4-5: Storage Integration**
- [ ] Set up MinIO (local S3)
- [ ] Implement S3 client for audio upload/download
- [ ] Set up PostgreSQL database
- [ ] Create database schema for jobs
- [ ] Implement SQLAlchemy models

**Deliverables:**
- ✅ FastAPI app with `/transcribe`, `/jobs/{id}`, `/health`
- ✅ S3 storage integration
- ✅ PostgreSQL database

---

### Week 3: Celery Task Queue & Async Processing

**Days 1-2: Celery Setup**
- [ ] Install Redis
- [ ] Configure Celery app
- [ ] Create transcription task

**Days 3-4: Integration**
- [ ] Connect API endpoints to Celery tasks
- [ ] Implement job progress tracking
- [ ] Add error handling and retry logic

**Day 5: Testing**
- [ ] Integration tests with sample audio
- [ ] Test long audio files (30+ minutes)
- [ ] Test concurrent processing

**Deliverables:**
- ✅ Celery task queue operational
- ✅ Async transcription
- ✅ Job tracking

---

### Week 4: Containerization & Local Deployment

**Days 1-2: Docker Images**
- [ ] Create Dockerfile for API
- [ ] Create Dockerfile for Celery worker
- [ ] Preload Whisper models

**Days 3-4: Docker Compose**
- [ ] Create `docker-compose.yml`
- [ ] Test local deployment

**Day 5: Testing**
- [ ] End-to-end testing in Docker
- [ ] Verify service communication

**Deliverables:**
- ✅ Dockerized application
- ✅ Docker Compose for local dev
- ✅ Working local deployment

---

### Week 5: Testing, Optimization & Documentation

**Days 1-2: Comprehensive Testing**
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests (various formats, languages)
- [ ] Load testing (Locust: 100 concurrent users)

**Days 3-4: Performance Optimization**
- [ ] Caching (Redis)
- [ ] Model preloading
- [ ] Database optimization
- [ ] Prometheus metrics

**Day 5: Documentation**
- [ ] API documentation (Swagger)
- [ ] README with setup instructions
- [ ] Architecture diagram
- [ ] Deployment guide

**Deliverables:**
- ✅ Test suite (80%+ coverage)
- ✅ Load testing results
- ✅ Performance optimizations
- ✅ Complete documentation

---

### Week 6: Kubernetes Deployment & Production Readiness

**Days 1-2: Kubernetes Manifests**
- [ ] Create namespace
- Create ConfigMaps and Secrets
- Create Deployments (API, Celery)
- Create Services
- Create Ingress

**Days 3-4: CI/CD Pipeline**
- Create GitHub Actions workflow
- Automated testing
- Docker image builds
- Kubernetes deployment

**Day 5: Production Deployment**
- Deploy to Kubernetes
- Configure monitoring (Prometheus + Grafana)
- Set up alerts
- Load testing in production
- Smoke tests

**Deliverables:**
- ✅ Production Kubernetes deployment
- ✅ CI/CD pipeline
- ✅ Monitoring and alerting
- ✅ Production-ready service

---

## Effort Estimate Summary

| Phase | Duration | Team |
|-------|----------|------|
| Scoping & contract | 0.5-1 day | 1 Backend Engineer |
| Core extraction | 2-3 days | 1 Backend Engineer |
| Interface abstraction | 1-2 days | 1 Backend Engineer |
| Service wrapper & container | 1-2 days | 1 DevOps Engineer |
| Client refactors | 2-3 days | 1 Backend Engineer |
| Validation | 1-2 days | 1 QA Engineer |
| **Total** | **7-12 days** | **2-3 Engineers** |

With dedicated team (2 engineers):
- **Best case:** 1.5 weeks
- **Realistic:** 6 weeks (with testing, documentation, deployment)
- **Conservative:** 8 weeks (with contingency)

---

## Success Criteria

### Performance Benchmarks

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Word Error Rate (WER) | < 5% | LibriSpeech, Tuda-De datasets |
| Processing Speed | < 0.3x real-time | Median latency (30-min audio, medium model) |
| Confidence Accuracy | > 90% | Segments with confidence > 0.85 should have WER < 3% |
| API Response Time | < 100ms (p95) | Prometheus metrics |
| Concurrent Requests | 100+ | Load testing (Locust) |
| Uptime | > 99% | Weekly uptime monitoring |

### Quality Benchmarks

- [ ] **German audio:** WER < 5% on Tuda-De dataset
- [ ] **English audio:** WER < 4% on LibriSpeech
- [ ] **Low-quality audio:** WER < 15% (graceful degradation)
- [ ] **Long audio (60+ min):** No OOM errors

### Functional Requirements

- [ ] 5 Whisper models supported
- [ ] 5 audio formats (opus, m4a, wav, mp3, ogg)
- [ ] 100+ languages (auto-detection)
- [ ] Per-segment confidence scoring
- [ ] Long audio chunking
- [ ] Async processing
- [ ] Job status tracking
- [ ] Error handling with retry logic

---

## Expected Outcome

A minimal, dependency-light transcription microservice that can run independently or alongside existing semantic tooling, reducing startup errors from missing analytics packages and enabling prosody/diarization/semantic analysis to evolve separately without risking core transcription availability.

### Key Benefits

1. **Reduced Dependencies:** Core service has ~10 dependencies vs. 40+ in monolith
2. **Faster Startup:** No loading of prosody/emotion/marker modules
3. **Better Isolation:** Failures in analytics don't affect transcription
4. **Easier Testing:** Mock enrichments in tests
5. **Independent Scaling:** Scale transcription separately from analytics
6. **Cleaner Code:** Clear separation of concerns

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Whisper model size (large Docker images) | High | Medium | Pre-bake models, use registry cache |
| Breaking changes in client code | Medium | High | Adapter pattern for backward compatibility |
| Performance regression | Low | Medium | Benchmark before/after, optimize as needed |
| Missing dependencies in new environment | Medium | Medium | Comprehensive testing across platforms |

---

## Next Steps

1. ✅ **Review Plan:** Stakeholder approval
2. **Team Assignment:** Assign backend + DevOps engineers
3. **Sprint Planning:** Break down Week 1 into daily tasks
4. **Kick-off:** Start implementation

**Target Start Date:** TBD
**Target Completion:** 6 weeks from start
**Status:** ✅ Ready for Implementation

---

**Document Owner:** Transcription Service Team
**Reviewed By:** Architecture Team
**Approval Status:** Pending Review
**Last Updated:** 2025-11-28

---

## See Also

- **Full Microservices Architecture:** [docs/microservices_architecture.md](./microservices_architecture.md)
- **Current Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md)
- **Cross-Platform Issues:** [CROSS_PLATFORM_BUG_REPORT.md](../CROSS_PLATFORM_BUG_REPORT.md)
