# SVT Microservices Architecture

**Last Updated:** 2025-11-28 | **Status:** Planning Phase

## Executive Summary

This document describes the decomposition of the Semantic Voice Transcriber (SVT) monolithic application into a microservices architecture. The primary goal is to create independent, scalable services that can be deployed and consumed separately, with the **Transcription Service** as the foundational component offering highest precision speech-to-text capabilities.

### Key Objectives

1. **Service Independence**: Each service can be deployed, scaled, and updated independently
2. **Transcription First**: Pure transcription service with the highest precision, speaker separation, and word recognition
3. **Composability**: Services can consume other services while maintaining functional independence
4. **API-Driven**: RESTful APIs with OpenAPI/Swagger documentation
5. **Scalability**: Horizontal scaling for compute-intensive services (transcription, prosody, diarization)
6. **Fault Tolerance**: Circuit breakers, retry logic, graceful degradation

---

## Microservices Overview

### Service Architecture Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Orchestrator                  │
│              (Request Routing, Auth, Rate Limiting)              │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────────────┐   ┌▼────────────────┐
│ CORE SERVICES  │   │  ANALYSIS       │
│                │   │  SERVICES       │
│ 1. Transcription│  │ 4. Prosody      │
│ 2. Audio Proc  │   │ 5. Emotion      │
│ 3. Diarization │   │ 6. Semantic     │
└────────────────┘   └─────────────────┘
         │                    │
         └────────┬───────────┘
                  │
    ┌─────────────▼──────────────┐
    │   SUPPORT SERVICES         │
    │                            │
    │ 7. Memory/Profile          │
    │ 8. LLM Provider            │
    │ 9. Output Formatting       │
    │ 10. Health Monitoring      │
    └────────────────────────────┘
```

---

## 1. Transcription Service (CORE)

**Priority:** P0 (Highest) - Foundational Service
**Status:** To be extracted from monolith
**Dependencies:** None (fully independent)

### Description

Pure speech-to-text transcription service with highest precision. This is the **core service** that all other services build upon. It provides:
- Multi-model Whisper STT (tiny → large)
- Intelligent quality-based model selection
- Confidence scoring per segment
- Language detection
- Timestamp alignment
- Format support: opus, m4a, wav, mp3, ogg

### Functional Requirements

**Core Capabilities:**
- Accept audio file upload (REST API)
- Automatic quality analysis → optimal Whisper model selection
- Return timestamped segments with confidence scores
- Support for long audio files (chunking with overlap)
- Language auto-detection (100+ languages)
- Low confidence segment flagging

**Quality Guarantees:**
- Word Error Rate (WER) < 5% for high-quality audio
- Confidence scores > 0.85 for 95% of segments
- Processing time < 0.3x real-time for medium model

### API Contract

#### POST /api/v1/transcribe

**Request:**
```json
{
  "audio_file": "base64_encoded_audio OR multipart/form-data",
  "model": "auto|tiny|base|small|medium|large",
  "language": "auto|de|en|...",
  "options": {
    "enable_timestamps": true,
    "min_confidence": 0.5,
    "chunk_duration": 300.0
  }
}
```

**Response:**
```json
{
  "transcription_id": "uuid-string",
  "status": "completed",
  "language": "de",
  "model_used": "medium",
  "duration_seconds": 120.5,
  "processing_time_seconds": 28.3,
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Guten Tag, wie geht es Ihnen?",
      "confidence": 0.92,
      "language_probability": 0.98
    }
  ],
  "metadata": {
    "audio_format": "opus",
    "sample_rate": 16000,
    "channels": 1,
    "quality_score": 0.87
  }
}
```

### Technology Stack

- **Framework:** FastAPI (Python 3.12+)
- **STT Engine:** OpenAI Whisper (openai-whisper)
- **Audio Processing:** FFmpeg, librosa, soundfile
- **Queue:** Celery + Redis (for async processing)
- **Storage:** S3-compatible (MinIO/AWS S3) for audio files
- **Monitoring:** Prometheus metrics

### Deployment Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Nginx LB   │─────▶│  FastAPI     │─────▶│  Celery      │
│   (SSL/TLS)  │      │  (API)       │      │  Workers     │
└──────────────┘      └──────────────┘      └──────────────┘
                             │                      │
                             ▼                      ▼
                      ┌──────────────┐      ┌──────────────┐
                      │   Redis      │      │  MinIO       │
                      │   (Queue)    │      │  (Audio)     │
                      └──────────────┘      └──────────────┘
```

### Scalability Considerations

- **Horizontal Scaling:** Add Celery workers for parallel processing
- **GPU Support:** Optional CUDA-enabled workers for large model
- **Caching:** Redis cache for repeated audio files (hash-based)
- **Rate Limiting:** 100 requests/minute per API key

### Migration Path

**Phase 1:** Extract core transcription logic
- Move `auto_transcriber_v4_emotion.py` → `transcription_service/`
- Extract `audio_quality_analyzer.py` → `transcription_service/analyzer/`
- Create FastAPI endpoints
- Add Celery task queue

**Phase 2:** Containerization
- Create Dockerfile with Whisper models
- Docker Compose for local dev
- Kubernetes manifests for production

**Phase 3:** Testing & Validation
- Unit tests for API endpoints
- Integration tests with sample audio
- Load testing (100+ concurrent requests)
- WER benchmarking against ground truth

---

## 2. Audio Processing Service

**Priority:** P1 (High)
**Status:** To be extracted
**Dependencies:** None

### Description

Preprocessing service for audio enhancement and quality analysis. Prepares audio for optimal transcription.

### Functional Requirements

- **Noise Reduction:** Spectral subtraction, Wiener filtering
- **Normalization:** Loudness normalization (LUFS)
- **Format Conversion:** All formats → WAV (16kHz, mono)
- **Quality Analysis:** SNR, zero-crossing rate, energy distribution
- **Chunking:** Split long audio with overlap
- **Voice Activity Detection (VAD):** Remove silence segments

### API Contract

#### POST /api/v1/audio/preprocess

**Request:**
```json
{
  "audio_file": "base64_encoded OR file_url",
  "operations": ["noise_reduction", "normalize", "convert"],
  "target_format": {
    "sample_rate": 16000,
    "channels": 1,
    "format": "wav"
  }
}
```

**Response:**
```json
{
  "processed_audio_url": "s3://bucket/processed/uuid.wav",
  "quality_metrics": {
    "snr_db": 18.5,
    "zero_crossing_rate": 0.042,
    "recommended_model": "medium"
  },
  "operations_applied": ["noise_reduction", "normalize", "convert"]
}
```

### Technology Stack

- **Framework:** FastAPI
- **Audio Libraries:** librosa, soundfile, pydub, noisereduce
- **Processing:** FFmpeg
- **Storage:** S3-compatible

---

## 3. Speaker Diarization Service

**Priority:** P1 (High)
**Status:** To be extracted
**Dependencies:** Audio Processing Service (optional)

### Description

Automatic speaker segmentation and labeling. Identifies "who spoke when" with overlap detection.

### Functional Requirements

- **Speaker Segmentation:** pyannote.audio 3.1
- **Speaker Labels:** A, B, C... (no name assignment)
- **Overlapped Speech Detection (OSD):** Track simultaneous speakers
- **Clustering:** Group segments by speaker
- **Timeline Output:** Speaker turns with timestamps

### API Contract

#### POST /api/v1/diarization/process

**Request:**
```json
{
  "audio_file_url": "s3://bucket/audio.wav",
  "num_speakers": "auto|2|3|...",
  "enable_overlap_detection": true
}
```

**Response:**
```json
{
  "diarization_id": "uuid",
  "speakers": ["A", "B", "C"],
  "segments": [
    {
      "speaker": "A",
      "start": 0.0,
      "end": 3.5,
      "overlap": false
    },
    {
      "speaker": "B",
      "start": 3.2,
      "end": 5.1,
      "overlap": true,
      "overlap_duration": 0.3,
      "overlap_with": ["A"]
    }
  ]
}
```

### Technology Stack

- **Framework:** FastAPI
- **Diarization:** pyannote.audio 3.1
- **Authentication:** Hugging Face token (for model access)
- **Compute:** GPU-enabled for faster processing

---

## 4. Prosody Analysis Service

**Priority:** P1 (High)
**Status:** To be extracted
**Dependencies:** Transcription Service (for segment alignment)

### Description

Extracts the "Big 4" prosodic features: Tempo, Pitch, Energy, Pauses. Detects deviations from baseline.

### Functional Requirements

- **Tempo Extraction:** WPM, syllables/sec (librosa)
- **Pitch Analysis:** F0 extraction, jitter, shimmer (Parselmouth/Praat)
- **Energy Measurement:** RMS, dB levels
- **Pause Detection:** Silence segments > 1000ms
- **Baseline Calculation:** Global means for deviation detection
- **Marker Generation:** `[TEMPO↑]`, `[PITCH↓]`, etc.

### API Contract

#### POST /api/v1/prosody/analyze

**Request:**
```json
{
  "audio_file_url": "s3://bucket/audio.wav",
  "segments": [
    {"start": 0.0, "end": 3.5, "text": "..."}
  ],
  "thresholds": {
    "tempo_deviation": 0.20,
    "pitch_deviation": 0.15,
    "energy_deviation": 0.25,
    "pause_threshold_ms": 1000
  }
}
```

**Response:**
```json
{
  "prosody_id": "uuid",
  "baseline": {
    "mean_pitch_hz": 147.8,
    "mean_tempo_wpm": 118.5,
    "mean_energy_rms": 0.045
  },
  "segments": [
    {
      "segment_id": 0,
      "start": 0.0,
      "end": 3.5,
      "prosody": {
        "pitch": {"mean": 162.3, "std": 12.4, "deviation": "+15.2%"},
        "tempo": {"wpm": 95.2, "deviation": "-19.6%"},
        "energy": {"rms": 0.038, "db": -28.4, "deviation": "-15.6%"},
        "pauses": []
      },
      "markers": ["PITCH↑", "TEMPO↓"]
    }
  ]
}
```

### Technology Stack

- **Framework:** FastAPI
- **Prosody Libraries:** Parselmouth (Praat), librosa
- **Audio:** soundfile, scipy

---

## 5. Emotion Detection Service

**Priority:** P2 (Medium)
**Status:** To be extracted
**Dependencies:** Transcription Service, Prosody Service (optional)

### Description

Multi-modal emotion analysis combining text sentiment and audio features. Provides VAD dimensions and discrete emotions.

### Functional Requirements

- **Text Sentiment:** TextBlob for polarity/subjectivity
- **Audio Features:** Spectral features, MFCCs
- **VAD Dimensions:** Valence, Arousal, Dominance
- **Discrete Emotions:** Joy, Sadness, Anger, Fear, Disgust, Surprise
- **UED Metrics:** Home Base, Variability, Instability, Inertia
- **Turnpoint Detection:** Emotion trajectory changes

### API Contract

#### POST /api/v1/emotion/analyze

**Request:**
```json
{
  "segments": [
    {
      "text": "Ich bin so glücklich!",
      "audio_features": {
        "pitch_mean": 180.2,
        "energy_mean": 0.052
      }
    }
  ],
  "enable_ued": true
}
```

**Response:**
```json
{
  "emotion_analysis_id": "uuid",
  "segments": [
    {
      "segment_id": 0,
      "sentiment": {
        "polarity": 0.85,
        "subjectivity": 0.72
      },
      "vad": {
        "valence": 0.82,
        "arousal": 0.64,
        "dominance": 0.58
      },
      "discrete_emotions": {
        "joy": 0.89,
        "sadness": 0.05,
        "anger": 0.02
      }
    }
  ],
  "ued_metrics": {
    "home_base": {"valence": 0.52, "arousal": 0.48},
    "variability": 0.34,
    "instability": 0.21
  }
}
```

### Technology Stack

- **Framework:** FastAPI
- **NLP:** TextBlob, NLTK
- **ML:** scikit-learn, transformers (optional)
- **Audio Features:** librosa

---

## 6. Semantic Marker Service

**Priority:** P2 (Medium)
**Status:** To be extracted
**Dependencies:** Transcription Service, Emotion Service (optional)

### Description

Detects semantic and behavioral patterns using the LeanDeep 3.5 marker system (ATO → SEM → CLU → MEMA).

### Functional Requirements

- **ATO Detection:** 63+ atomic markers (regex, tokens)
- **SEM Composition:** Combine ATOs into semantic units
- **CLU Aggregation:** Thematic clusters over windows
- **MEMA Patterns:** Meta-analysis of emergent patterns
- **Therapeutic Markers:** 40 curated clinical markers
- **Correlation Analysis:** Marker co-occurrence

### API Contract

#### POST /api/v1/markers/detect

**Request:**
```json
{
  "segments": [
    {
      "text": "Ich habe Angst davor...",
      "prosody_markers": ["PITCH↑", "PAUSE"],
      "emotion": "fear"
    }
  ],
  "marker_sets": ["ATO_EMOTIONS", "ATO_THERAPEUTIC"],
  "enable_hierarchy": true
}
```

**Response:**
```json
{
  "marker_analysis_id": "uuid",
  "segments": [
    {
      "segment_id": 0,
      "ato_markers": ["ATO_FEAR", "ATO_HESITATION"],
      "sem_markers": ["SEM_ANXIETY_PATTERN"],
      "clu_markers": ["CLU_RESISTANCE"],
      "confidence": 0.82
    }
  ],
  "correlations": [
    {
      "markers": ["ATO_FEAR", "PITCH↑"],
      "correlation": 0.76
    }
  ]
}
```

### Technology Stack

- **Framework:** FastAPI
- **Pattern Matching:** regex, YAML marker definitions
- **Storage:** PostgreSQL for marker definitions
- **Cache:** Redis for compiled patterns

---

## 7. Memory/Profile Service

**Priority:** P2 (Medium)
**Status:** To be extracted
**Dependencies:** Prosody Service, Emotion Service

### Description

Persistent speaker profiles with learning capabilities. Stores prosody baselines, speech statistics, and interaction history.

### Functional Requirements

- **Profile Management:** CRUD for speaker profiles
- **Prosody Baselines:** Running averages (pitch, tempo, energy)
- **Speech Statistics:** Sentence length, sentiment ratios
- **Topic Tracking:** Keyword extraction, topic frequencies
- **Interaction History:** Last 50 transcriptions with timestamps
- **Learning:** Update profiles with new data

### API Contract

#### GET /api/v1/profiles/{speaker_id}

**Response:**
```json
{
  "speaker_id": "uuid",
  "name": "Patient_A",
  "prosody_baselines": {
    "mean_pitch_hz": 147.8,
    "mean_tempo_wpm": 118.5,
    "mean_energy_rms": 0.045
  },
  "statistics": {
    "avg_sentence_length": 15.3,
    "sentiment_ratio": 5.25
  },
  "topics": {
    "technology": 15,
    "personal": 23
  },
  "last_updated": "2025-11-28T10:30:00Z"
}
```

#### PUT /api/v1/profiles/{speaker_id}

**Request:**
```json
{
  "update_prosody": {
    "pitch_samples": [145.2, 150.3, 149.1],
    "tempo_samples": [115, 120, 118]
  },
  "new_topics": ["health"],
  "interaction_timestamp": "2025-11-28T10:30:00Z"
}
```

### Technology Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (profiles), SQLite (backup)
- **YAML:** Profile export/import
- **Cache:** Redis for frequently accessed profiles

---

## 8. LLM Provider Service

**Priority:** P2 (Medium)
**Status:** To be extracted
**Dependencies:** None

### Description

Abstraction layer for multiple LLM providers (OpenAI, Ollama, Anthropic, etc.). Provides unified interface.

### Functional Requirements

- **Multi-Provider Support:** OpenAI, Ollama, Anthropic, Google, Grok
- **Health Checks:** Provider availability and API key validation
- **Response Caching:** Redis-based cache
- **Retry Logic:** Exponential backoff for rate limits
- **Usage Tracking:** Token consumption per provider
- **Failover:** Automatic fallback to alternative provider

### API Contract

#### POST /api/v1/llm/generate

**Request:**
```json
{
  "provider": "openai|ollama|anthropic",
  "prompt": "Analyze this transcript...",
  "model": "gpt-4-turbo-preview",
  "options": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Response:**
```json
{
  "response_id": "uuid",
  "provider_used": "openai",
  "model_used": "gpt-4-turbo-preview",
  "text": "Analysis result...",
  "usage": {
    "prompt_tokens": 350,
    "completion_tokens": 500,
    "total_tokens": 850
  },
  "cached": false
}
```

### Technology Stack

- **Framework:** FastAPI
- **LLM SDKs:** openai, anthropic, ollama-python
- **Cache:** Redis with TTL
- **Monitoring:** Usage metrics

---

## 9. Output Formatting Service

**Priority:** P3 (Low)
**Status:** To be extracted
**Dependencies:** All analysis services

### Description

Converts analysis results into various output formats (MD, JSON, HTML, PDF, CSV, Dashboard).

### Functional Requirements

- **Markdown:** Therapeutic format with metadata sidebars
- **JSON:** Structured data for system processing
- **HTML:** Color-coded speakers, interactive
- **PDF:** Professional layout for printing
- **CSV:** Data export for analysis
- **Dashboard:** Interactive HTML with Chart.js

### API Contract

#### POST /api/v1/output/format

**Request:**
```json
{
  "transcription": {...},
  "prosody": {...},
  "diarization": {...},
  "emotions": {...},
  "markers": {...},
  "format": "markdown|json|html|pdf|csv|dashboard",
  "options": {
    "speaker_mode": "anonymous|letters|names",
    "include_metadata": true
  }
}
```

**Response:**
```json
{
  "output_url": "s3://bucket/output/file.md",
  "format": "markdown",
  "size_bytes": 12548
}
```

### Technology Stack

- **Framework:** FastAPI
- **Templates:** Jinja2
- **PDF:** WeasyPrint
- **Visualization:** Chart.js, Cytoscape.js

---

## 10. API Gateway / Orchestration Service

**Priority:** P1 (High)
**Status:** New service
**Dependencies:** All services

### Description

Central API gateway for request routing, authentication, rate limiting, and service orchestration.

### Functional Requirements

- **Request Routing:** Route to appropriate microservice
- **Authentication:** JWT-based API keys
- **Rate Limiting:** Per-user quotas
- **Circuit Breaker:** Fault tolerance for failed services
- **Orchestration:** Coordinate multi-service workflows
- **Health Monitoring:** Aggregate service health
- **Logging:** Centralized request/response logs

### API Contract

#### POST /api/v1/orchestrate/full-analysis

**Request:**
```json
{
  "audio_file": "base64_encoded",
  "pipeline": {
    "transcription": {"model": "auto"},
    "diarization": {"enabled": true},
    "prosody": {"enabled": true},
    "emotion": {"enabled": true},
    "markers": {"sets": ["ATO_EMOTIONS"]},
    "output": ["markdown", "json"]
  }
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 0.45,
  "services_completed": ["transcription", "diarization"],
  "services_pending": ["prosody", "emotion"],
  "estimated_completion_seconds": 120
}
```

### Technology Stack

- **Framework:** FastAPI
- **Gateway:** Kong or Nginx (reverse proxy)
- **Auth:** JWT (PyJWT)
- **Rate Limiting:** Redis
- **Circuit Breaker:** pybreaker
- **Orchestration:** Celery workflows

---

## Inter-Service Communication

### Communication Patterns

1. **Synchronous (REST API):**
   - API Gateway → Individual Services
   - Simple request/response (< 5s response time)

2. **Asynchronous (Message Queue):**
   - Long-running tasks (transcription, prosody)
   - Celery + Redis/RabbitMQ
   - Event-driven workflows

3. **Service Mesh (Optional):**
   - Istio or Linkerd for advanced routing
   - mTLS for secure communication
   - Observability (distributed tracing)

### Data Flow Example: Full Analysis Pipeline

```
1. User uploads audio → API Gateway
2. Gateway → Transcription Service (async)
3. Transcription → Audio Processing Service (preprocessing)
4. Transcription complete → Event published
5. Event triggers parallel processing:
   - Diarization Service
   - Prosody Service
   - Emotion Service
6. Prosody + Emotion complete → Semantic Marker Service
7. All analysis complete → Output Formatting Service
8. Gateway returns download URLs to user
```

---

## Data Storage Strategy

### Service-Specific Databases

| Service | Storage Type | Purpose |
|---------|-------------|---------|
| Transcription | S3 + PostgreSQL | Audio files, transcription metadata |
| Audio Processing | S3 | Processed audio cache |
| Diarization | PostgreSQL | Diarization results |
| Prosody | PostgreSQL | Prosody features |
| Emotion | PostgreSQL | Emotion analysis |
| Markers | PostgreSQL + YAML | Marker definitions, detections |
| Memory/Profile | PostgreSQL + SQLite | Speaker profiles, baselines |
| LLM Provider | Redis | Response cache |
| Gateway | PostgreSQL | API keys, usage logs |

### Shared Data

- **Audio Files:** MinIO/S3 (shared across services)
- **Redis Cache:** Shared for caching and queues
- **PostgreSQL:** Separate schemas per service (shared instance for dev)

---

## Deployment Strategy

### Containerization

Each service packaged as Docker container:

```yaml
# Example: transcription-service/Dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  api-gateway:
    build: ./api-gateway
    ports: ["8000:8000"]

  transcription-service:
    build: ./transcription-service
    depends_on: [redis, postgres]

  prosody-service:
    build: ./prosody-service

  redis:
    image: redis:7-alpine

  postgres:
    image: postgres:15

  minio:
    image: minio/minio
```

### Kubernetes (Production)

- **Namespaces:** `svt-core`, `svt-analysis`, `svt-support`
- **Deployments:** StatefulSets for databases, Deployments for services
- **Services:** ClusterIP (internal), LoadBalancer (API Gateway)
- **Ingress:** Nginx Ingress Controller with TLS
- **Autoscaling:** HPA based on CPU/memory
- **Storage:** Persistent Volume Claims for databases

---

## Security Considerations

### Authentication & Authorization

- **API Gateway:** JWT-based authentication
- **Service-to-Service:** mTLS certificates or service tokens
- **Secrets Management:** Kubernetes Secrets or HashiCorp Vault

### Data Privacy

- **Audio Files:** Encrypted at rest (S3 encryption)
- **Transcripts:** PII detection and masking (optional)
- **GDPR Compliance:** Data retention policies, right to deletion

### Network Security

- **Firewall Rules:** Only API Gateway exposed externally
- **TLS/SSL:** All external communication encrypted
- **Rate Limiting:** Prevent abuse and DDoS

---

## Monitoring & Observability

### Metrics (Prometheus + Grafana)

- **Service Metrics:** Request rate, latency, error rate
- **Business Metrics:** Transcriptions/hour, average WER
- **Resource Metrics:** CPU, memory, disk usage

### Logging (ELK Stack)

- **Centralized Logging:** Elasticsearch, Logstash, Kibana
- **Structured Logs:** JSON format with correlation IDs
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

### Tracing (Jaeger)

- **Distributed Tracing:** Track requests across services
- **Performance Analysis:** Identify bottlenecks
- **Error Debugging:** Root cause analysis

---

## Migration & Implementation Plan

### Phase 0: Preparation (Weeks 1-2)

**Objectives:**
- Document current monolith architecture
- Identify service boundaries
- Create API specifications (OpenAPI)
- Set up infrastructure (Kubernetes cluster, CI/CD)

**Deliverables:**
- ✅ This microservices architecture document
- OpenAPI specs for all 10 services
- Infrastructure as Code (Terraform/Helm charts)

**Team Requirements:**
- 1 DevOps Engineer
- 1 Backend Engineer
- 1 Architect

---

### Phase 1: Transcription Service (Weeks 3-6) - **PRIORITY**

**Objectives:**
- Extract transcription logic into standalone service
- Implement FastAPI endpoints
- Set up Celery for async processing
- Deploy to Kubernetes
- Achieve parity with monolith transcription quality

**Tasks:**

**Week 3: Core Extraction**
- [ ] Create `transcription-service/` directory structure
- [ ] Extract `auto_transcriber_v4_emotion.py` → `core/transcriber.py`
- [ ] Extract `audio_quality_analyzer.py` → `core/analyzer.py`
- [ ] Create FastAPI app with `/transcribe` endpoint
- [ ] Implement file upload handling (multipart/form-data)

**Week 4: Async Processing**
- [ ] Set up Celery workers
- [ ] Implement task queue for transcription jobs
- [ ] Add Redis for queue and caching
- [ ] Implement job status tracking
- [ ] Add S3/MinIO for audio file storage

**Week 5: Testing & Optimization**
- [ ] Unit tests for core logic (pytest)
- [ ] Integration tests with sample audio
- [ ] Load testing (Locust): 100 concurrent requests
- [ ] WER benchmarking against ground truth
- [ ] Performance tuning (model loading, caching)

**Week 6: Deployment**
- [ ] Create Dockerfile with Whisper models
- [ ] Docker Compose for local testing
- [ ] Kubernetes manifests (Deployment, Service, Ingress)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Production deployment to K8s cluster

**Success Criteria:**
- ✅ WER < 5% for high-quality audio
- ✅ Processing time < 0.3x real-time (medium model)
- ✅ 99% uptime over 1 week
- ✅ Handles 100+ concurrent requests

**Deliverables:**
- Deployed Transcription Service on Kubernetes
- API documentation (Swagger UI)
- Test suite with 80%+ coverage
- Performance benchmarks

---

### Phase 2: Audio Processing & Diarization Services (Weeks 7-10)

**Objectives:**
- Extract audio preprocessing into standalone service
- Extract speaker diarization into standalone service
- Integrate with Transcription Service

**Week 7: Audio Processing Service**
- [ ] Extract `audio_preprocessor.py` logic
- [ ] Implement noise reduction endpoints
- [ ] Add format conversion and normalization
- [ ] S3 integration for processed audio

**Week 8: Speaker Diarization Service**
- [ ] Extract `speaker_diarizer.py` logic
- [ ] Implement pyannote.audio integration
- [ ] Add overlap detection
- [ ] GPU support for faster processing

**Week 9: Integration**
- [ ] Connect Audio Processing → Transcription
- [ ] Connect Diarization → Transcription
- [ ] Implement service discovery (Consul/K8s DNS)
- [ ] Add circuit breakers

**Week 10: Testing & Deployment**
- [ ] End-to-end testing
- [ ] Deploy both services to K8s
- [ ] Monitor performance

**Success Criteria:**
- ✅ Audio preprocessing reduces noise by 10+ dB SNR
- ✅ Diarization accuracy > 90% (DER < 10%)
- ✅ Integration latency < 500ms

---

### Phase 3: Analysis Services (Weeks 11-14)

**Objectives:**
- Extract Prosody, Emotion, and Semantic Marker services
- Implement parallel processing pipelines

**Week 11: Prosody Service**
- [ ] Extract `prosody_extractor.py`
- [ ] Implement Big 4 features extraction
- [ ] Baseline calculation and deviation detection

**Week 12: Emotion Service**
- [ ] Extract emotion analysis logic
- [ ] Implement text + audio multi-modal analysis
- [ ] UED metrics calculation

**Week 13: Semantic Marker Service**
- [ ] Extract `super_semantic_processor.py`
- [ ] Implement ATO/SEM/CLU/MEMA detection
- [ ] Load 63+ marker definitions from YAML

**Week 14: Integration & Testing**
- [ ] Parallel processing pipeline
- [ ] End-to-end tests
- [ ] Deploy all services

**Success Criteria:**
- ✅ Prosody extraction accuracy > 95%
- ✅ Emotion detection F1-score > 0.80
- ✅ Marker detection precision > 0.85

---

### Phase 4: Support Services (Weeks 15-18)

**Objectives:**
- Extract Memory/Profile, LLM Provider, Output Formatting services
- Complete service ecosystem

**Week 15: Memory/Profile Service**
- [ ] Extract speaker profile logic
- [ ] PostgreSQL schema design
- [ ] CRUD API for profiles
- [ ] Profile learning logic

**Week 16: LLM Provider Service**
- [ ] Extract `svt_core/llm_provider/`
- [ ] Multi-provider abstraction
- [ ] Health checks and failover

**Week 17: Output Formatting Service**
- [ ] Extract `output_formatter.py`
- [ ] Template-based rendering (Jinja2)
- [ ] Multi-format support

**Week 18: Testing & Deployment**
- [ ] Integration tests
- [ ] Deploy all services

---

### Phase 5: API Gateway & Orchestration (Weeks 19-22)

**Objectives:**
- Implement central API Gateway
- Orchestrate multi-service workflows
- Production-ready deployment

**Week 19: API Gateway**
- [ ] Set up Kong or Nginx
- [ ] JWT authentication
- [ ] Rate limiting

**Week 20: Orchestration Service**
- [ ] Implement workflow orchestration
- [ ] Celery workflows for full pipeline
- [ ] Job progress tracking

**Week 21: Monitoring & Observability**
- [ ] Prometheus + Grafana setup
- [ ] ELK stack for logging
- [ ] Jaeger for tracing

**Week 22: Production Deployment**
- [ ] Final integration tests
- [ ] Load testing (1000+ requests/min)
- [ ] Production rollout
- [ ] Documentation

**Success Criteria:**
- ✅ Full pipeline latency < 5 minutes for 30-min audio
- ✅ 99.9% uptime
- ✅ Handles 1000+ transcriptions/day

---

### Phase 6: Optimization & Scaling (Weeks 23-26)

**Objectives:**
- Performance optimization
- Cost reduction
- Advanced features

**Tasks:**
- [ ] Autoscaling based on load
- [ ] GPU optimization for Whisper large model
- [ ] Caching optimization
- [ ] CDN for static assets
- [ ] Cost analysis and optimization

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Transcription WER | < 5% | Benchmark against ground truth |
| Processing Speed | < 0.3x real-time | Median latency for 30-min audio |
| Service Uptime | > 99.9% | Monthly uptime (Prometheus) |
| API Response Time | < 100ms (p95) | Gateway latency |
| Concurrent Requests | 1000+ | Load testing |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Transcriptions/Day | 10,000+ | Usage analytics |
| Cost per Transcription | < $0.05 | AWS billing |
| Customer Satisfaction | > 4.5/5 | User surveys |
| API Adoption | 50+ integrations | Partner count |

---

## Risk Management

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Whisper model size (large file) | High deployment time | Pre-baked Docker images with models |
| GPU availability for diarization | Degraded performance | Fallback to CPU mode with longer processing |
| Service dependencies | Cascading failures | Circuit breakers, retry logic |
| Data loss in async processing | Lost jobs | Persistent queue (Redis AOF) |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cost overruns | Budget exceeded | Cost monitoring, autoscaling limits |
| Security breach | Data leak | Encryption, access controls, audits |
| Vendor lock-in (cloud) | Migration difficulty | Multi-cloud support, abstraction layers |

---

## Cost Estimation (Monthly)

### Infrastructure Costs (AWS Example)

| Resource | Quantity | Monthly Cost |
|----------|----------|--------------|
| EKS Cluster | 1 | $73 |
| EC2 Instances (t3.large) | 5 | $375 |
| EC2 GPU (g4dn.xlarge) | 2 | $600 |
| S3 Storage (1 TB) | 1 | $23 |
| RDS PostgreSQL (db.t3.medium) | 1 | $70 |
| ElastiCache Redis (cache.t3.micro) | 1 | $15 |
| Load Balancer | 1 | $20 |
| Data Transfer (500 GB) | 1 | $45 |
| **Total** | | **~$1,221** |

### Cost Optimizations

- Use Reserved Instances (40% savings)
- Autoscaling for off-peak hours
- S3 Lifecycle policies (archive old audio)
- Spot instances for batch processing

---

## Open Questions

1. **Multi-Tenancy:** How to isolate customers in shared infrastructure?
2. **Real-Time Processing:** Phase 3 live streaming - architecture changes needed?
3. **On-Premise Deployment:** Support for air-gapped environments?
4. **Model Updates:** How to update Whisper models without downtime?
5. **GDPR/HIPAA Compliance:** Additional requirements for healthcare data?

---

## Conclusion

This microservices architecture provides a scalable, maintainable path forward for SVT. The **Transcription Service** as the foundational component enables independent deployment and consumption, while additional services add layers of analysis.

### Key Advantages

1. **Independent Scaling:** Scale transcription separately from analysis
2. **Technology Flexibility:** Use best tool for each service
3. **Development Velocity:** Parallel team development
4. **Fault Isolation:** Failures contained to individual services
5. **Reusability:** Transcription service can be used standalone or integrated

### Next Steps

1. **Review & Approval:** Stakeholder sign-off on architecture
2. **Team Formation:** Assign engineers to Phase 1 (Transcription Service)
3. **Infrastructure Setup:** Provision Kubernetes cluster
4. **Sprint Planning:** Detailed task breakdown for Weeks 1-6

**Project Start Date:** TBD
**Phase 1 Completion Target:** 6 weeks from start

---

**Document Owner:** Architecture Team
**Last Reviewed:** 2025-11-28
**Next Review:** After Phase 1 completion
