# Aktueller Stand & Microservice-Plan (Transcriber Standalone)

## Aktueller Systemstand
- **Pipelines:** GUI-gesteuerter Ablauf orchestriert `auto_transcriber_v4_emotion.py` mit Quality-Checks, Prosodie-Extraktion, Diarisierung und semantischer Auswertung gemäß der Produktarchitektur.【F:ARCHITECTURE.md†L17-L102】
- **Subsysteme:** WhisperSpeakerMatcher, Super Semantic Processor und Prosody Voice Marker System bilden die Kernfunktionen laut Produktübersicht.【F:README.md†L15-L39】
- **Prosodie-Status:** Phase 1 abgeschlossen mit Tempo, Pitch, Energie und Pausen, inklusive Baseline-Berechnung und Multi-Format-Export (MD/JSON/HTML/PDF/CSV).【F:README.md†L49-L104】
- **Export & Validierung:** Post-Processing validiert Sprecher-Labels, Marker-Diversität, Prosodie-Vollständigkeit und erzeugt mehrfache Ausgabeformate (Markdown, HTML, PDF, JSON).【F:ARCHITECTURE.md†L92-L116】
- **Technikrahmen:** Python 3.12 Ziel, modulare Clean-Architecture-Trennung, Tests via `pytest`, Konfiguration per YAML, Geheimnisse über `.env`.【F:AGENTS.md†L20-L46】

## Beobachtete Stärken und Lücken
- **Stärken:** Klar dokumentierte End-to-End-Pipeline mit Fehlerbehandlung, skalierbares Chunking, Caching und ressourcenschonendem Audio-Handling.【F:ARCHITECTURE.md†L9-L54】
- **Lücken Richtung Microservices:**
  - Komponenten sind aktuell primär prozess-intern gekoppelt; klare API-Verträge für eigenständige Services fehlen.
  - Deployment-Angaben fokussieren auf lokale Ausführung; Containerisierung/Orchestrierung nicht spezifiziert.
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
