# Aktueller Stand & Microservice-Plan (Transcriber Standalone)

**Last Updated:** 2025-12-07 | **Verified against commit:** c5ef26a

> **📋 See detailed status:** [MICROSERVICE_TRANSCRIBER_STATUS.md](MICROSERVICE_TRANSCRIBER_STATUS.md)

## ✅ Completed: Core Transcription Service (Phase 1)

**PR #41, Commit 2f4c869** - Successfully extracted standalone transcription microservice

### What's Done
- **Isolated Whisper Service:** Pure STT engine in `services/transcription_service/`
  - No dependencies on prosody, emotion, or semantic analysis
  - Clean API boundaries with adapter pattern
  - FastAPI REST endpoints (`/transcribe`, `/health`)
  - Backward-compatible wrappers for legacy code

- **Speaker Diarization Integration:** Optional add-on in `svt_core/audio/`
  - pyannote.audio 3.1 for automatic speaker segmentation
  - CPU-optimized processing (no GPU required)
  - Overlapped Speech Detection (OSD)
  - Robust error handling with graceful degradation

- **Production-Ready Features:**
  - ✅ 5 Whisper models (tiny → large) with intelligent selection
  - ✅ Confidence scoring per segment
  - ✅ 100+ language support with auto-detection
  - ✅ Long audio support (chunking with overlap)
  - ✅ Docker containerization
  - ✅ Environment-based configuration
  - ✅ Comprehensive test coverage

### Deployment Modes
1. **Python Library:** Import and use programmatically
2. **REST API:** FastAPI service at `http://localhost:8000`
3. **CLI:** Command-line tool for batch processing
4. **Docker:** Containerized standalone service

## Aktueller Systemstand
- **Pipelines:** GUI-gesteuerter Ablauf orchestriert `auto_transcriber_v4_emotion.py` mit Quality-Checks, Prosodie-Extraktion, Diarisierung und semantischer Auswertung gemäß der Produktarchitektur.
- **Transcription Service:** Standalone-Mikroservice in `services/transcription_service/` mit FastAPI REST-Endpunkten, vollständiger Rückwärtskompatibilität und optionalen Adaptern für Prosodie/Diarisierung.
- **Subsysteme:** WhisperSpeakerMatcher (jetzt als Service extrahiert), Super Semantic Processor und Prosody Voice Marker System bilden die Kernfunktionen.
- **Prosodie-Status:** Phase 1 abgeschlossen mit Tempo, Pitch, Energie und Pausen, inklusive Baseline-Berechnung und Multi-Format-Export (MD/JSON/HTML/PDF/CSV).
- **Export & Validierung:** Post-Processing validiert Sprecher-Labels, Marker-Diversität, Prosodie-Vollständigkeit und erzeugt mehrfache Ausgabeformate (Markdown, HTML, PDF, JSON).
- **Technikrahmen:** Python 3.12 Ziel, modulare Clean-Architecture-Trennung, Tests via `pytest`, Konfiguration per YAML, Geheimnisse über `.env`.

## Beobachtete Stärken und erreichte Meilensteine
- **Stärken:** Klar dokumentierte End-to-End-Pipeline mit Fehlerbehandlung, skalierbares Chunking, Caching und ressourcenschonendem Audio-Handling.
- **✅ Transcription Service extrahiert:** Vollständig unabhängiger Dienst mit REST API, keine Zwangskopplung an Semantic/Emotion-Analysen
- **✅ Adapter-Pattern implementiert:** Optionale Integration von Prosodie/Diarisierung via Dependency Injection
- **✅ Containerisierung:** Docker-Images mit Whisper-Modellen, docker-compose-ready
- **Verbleibende Lücken Richtung vollständiger Microservices:**
  - Async Job Queue (Celery + Redis) noch nicht produktiv
  - Persistent Storage (PostgreSQL/S3) noch nicht integriert
  - API Gateway mit Rate Limiting ausstehend
  - Emotionale Dynamik (zeitliche Verlaufserkennung), Arousal-Modellierung und explizite Wendepunkt-Erkennung sind nicht als getrennte Dienste definiert.

## Iterativer Weg zur Microservice-Architektur (Transcriber Standalone)
1. **Service-Schnittstellen definieren (Iteration 0)**
   - Gemeinsames Contract-Schema (JSON/Protobuf) für Audio-Metadaten, Segmentlisten und Prosodie-Features.
   - Events: `audio.ingested`, `prosody.extracted`, `emotion.stream`, `turningpoint.detected`.
2. **Prosody-Service extrahieren (Iteration 1)**
   - Endpunkt: `/prosody/analyze` nimmt Audio-Chunk-IDs + Speicherpfad entgegen, liefert Big-4-Features + Baselines.
   - Persistenz: Feature-Cache (Redis/SQLite) pro Segment; Rückkanal via Message-Bus (NATS/Kafka leichtgewichtig).
3. **Emotion Dynamics & Arousal-Service (Iteration 2)**
   - Input: Transkript + Prosodie-Zeitreihe; Output: gleitende Emotionen (valence/arousal), Change-Points.
   - Streaming-Fähigkeit: WebSocket/gRPC-Streaming für fortlaufende Segmente.
   - Modell-Adapter-Schicht erlaubt Austausch zwischen Heuristik (TextBlob) und Deep-Model (HF/Local LLM).
4. **Turningpoint-Detection-Service (Iteration 3)**
   - Konsumiert Emotion-Dynamik + Prosodie-Deviationen; Regeln + ML-Hybrid.
   - API: `/turningpoint/evaluate` gibt Zeitstempel, Sprecher, Evidenzmarker (Prosody + SEM/ATO IDs) zurück.
5. **Transcriber Orchestrator als dünner Gateway (Iteration 4)**
   - Verantwortlich für Orchestration, Idempotenz, Retries, SLA-Überwachung (Timeouts, Circuit Breaker).
   - Konvertiert GUI-Requests in Service-Calls; persistiert Run-Graph (z. B. in SQLite/PG) für Replays.
6. **Deployment & Observability (Iteration 5)**
   - Container-Blueprints pro Service (Dockerfiles, healthchecks), Compose-Stack für lokale Iterationen.
   - Observability: strukturierte Logs + OpenTelemetry-Traces, Metriken (Latenz/Queue-Länge), Dead-Letter-Queues.
7. **Hardening & ML Ops (Iteration 6)**
   - Model Registry für Prosody/Emotion/Arousal; Version-Pins in Configmaps.
   - Batch-Reprocessing Jobs für historische Audios; Canary-Rollouts für neue Modelle.

## Modularisierungsleitplanken (Prosody, Emotion Dynamics, Arousal, Turningpoint)
- **Prosody-Service:** CPU-optimiert, optional GPU-Flag; verantwortet Chunking, Big-4-Features, Baseline-Berechnung, Quality-Score-Rückmeldung.
- **Emotion Dynamics-Service:** Fokus auf zeitlichen Verlauf; kombiniert Text + Prosodie; liefert Valence/Arousal-Kurven und Wechselpunkte.
- **Arousal-Service:** Spezialisierte Ableitung aus Energie/Pitch/Tempo; kann als Submodul oder eigenständiger Pfad laufen, liefert Arousal-Score pro Segment.
- **Turningpoint-Service:** Fusioniert Emotion-Dynamik, Arousal-Peaks und SEM/ATO-Marker zu Wendepunkt-Ereignissen; stellt Evidenz-Objekte für UI/Formatter bereit.
- **Gemeinsame Verträge:** Einheitliche Segment-IDs, Zeitstempel-Granularität, Sprecher-Mapping; Responses enthalten Confidence + Herkunft (audio/text/model).

## Nächste konkrete Schritte (2-Wochen-Horizont)
1. Contract-Entwurf und Beispielpayloads in `docs/api/` festhalten.
2. Dockerfile + Compose-Skelett für Prosody-Service erstellen; Healthcheck + Sample-Request testen.
3. Message-Bus-Auswahl prototypisch evaluieren (NATS vs. Kafka) mit Minimal-Event-Flow `audio.ingested → prosody.extracted`.
4. Thin-Orchestrator-Refactor: `auto_transcriber_v4_emotion.py` an Service-Clients anbinden (Feature-Flags, Fallback auf lokalen Modus).
