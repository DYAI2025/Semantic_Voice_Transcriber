# Transcription Microservice Separation Plan

## Current Components and Coupling
- **Monolithic orchestrator**: `auto_transcriber_v4_emotion.py` loads prosody, diarization, sentiment, and correlation modules in the same runtime, turning optional analytics into hard runtime imports with best-effort fallbacks for missing dependencies (e.g., `ProsodyExtractor`, `SpeakerDiarizer`, TextBlob, ATO correlation engine). The file also controls Whisper inference and speaker-context prompting, so failure in downstream analytics still touches the core transcription entry point. 【F:auto_transcriber_v4_emotion.py†L24-L199】
- **End-to-end pipeline**: The architecture document shows the GUI and `auto_transcriber_v4_emotion.py` orchestrating audio processing → prosody → diarization → Whisper → semantic analysis → interpretation → formatting in a single flow, reinforcing tight coupling between transcription and semantic enrichment. 【F:ARCHITECTURE.md†L34-L134】

## Known Bugs and Fragilities
- **Dependency version blockers (fixed upstream but still risky)**: Historic failures installing `torch==2.9.0` and conflicting `pathlib/pathlib2` packages caused full install breakage across OSes. Although marked as fixed, any reversion to pinned versions would immediately break setup. 【F:CROSS_PLATFORM_BUG_REPORT.md†L28-L102】
- **Platform-specific setup gap**: `setup_environment.py` remains Unix-centric (chmod and Bash launcher creation), still flagged as a moderate unresolved issue for Windows environments. 【F:CROSS_PLATFORM_BUG_REPORT.md†L144-L159】
- **Resilience issues in the orchestrator**: Optional analytics are imported inside `auto_transcriber_v4_emotion.py` rather than run behind interfaces; missing packages only log warnings, but the module remains large and intertwined, making failures harder to isolate and increasing startup time and memory footprint. 【F:auto_transcriber_v4_emotion.py†L24-L199】

## Separation Strategy (Transcription-Only Microservice)
1. **Define a stable transcription contract**
   - Draft a `transcription_service` package exposing `transcribe(audio_path, config) -> Transcript` with strict input validation and structured output (segments, language, confidence, timestamps).
   - Write JSON schema for requests/responses to keep the microservice transport-agnostic.

2. **Extract core Whisper runner**
   - Move Whisper loading, model selection, and chunked inference from `auto_transcriber_v4_emotion.py` into a dedicated module (e.g., `src/transcription/core.py`) with no prosody/semantics imports.
   - Preserve speaker-context prompt loading as an optional hook but gate it behind dependency injection (no direct Memory/ATO access).

3. **Isolate audio preparation**
   - Lift `audio_quality_analyzer.py`, `audio_preprocessor.py`, and `audio_chunker.py` into a lightweight preprocessing layer callable by the service without semantic side effects.
   - Provide clear error codes for unsupported formats or corrupt files instead of logging-only fallbacks.

4. **Abstract optional enrichments**
   - Replace direct imports of prosody, diarization, sentiment, and correlation tools with interface stubs (e.g., `ProsodyFeatureProvider`), and load them only in the legacy monolith or in separate services.
   - Ensure transcription service outputs are enrichable via webhooks/events instead of in-process calls.

5. **Build the microservice shell**
   - Add a FastAPI/Flask wrapper exposing `/health`, `/transcribe`, and `/metrics`. Keep only core dependencies (`ffmpeg`, `whisper`, `numpy`, `pydantic`).
   - Containerize with a slim base image and mount model cache for faster startups.

6. **Refactor GUI and pipelines**
   - Update `svt.py` and `start_super_semantic.py` to call the transcription endpoint first, then hand results to existing prosody/semantic processors as separate steps.
   - Preserve backward compatibility by keeping the current orchestrator as an adapter until all callers migrate.

7. **Testing and hardening**
   - Add unit tests for the new service contract and e2e tests that mock enrichments to ensure transcription continues working when auxiliary services are down.
   - Re-run cross-platform installation checks to verify the reduced dependency footprint eliminates prior install blockers.

## Effort Estimate (Step-by-Step)
- **Scoping & contract**: 0.5–1 day to formalize schemas and acceptance criteria.
- **Core extraction**: 2–3 days to move Whisper + preprocessing into `transcription_service` with tests.
- **Interface abstraction**: 1–2 days to refactor optional analytics behind providers and de-risk imports.
- **Service wrapper & container**: 1–2 days to build API, observability hooks, and Dockerfile.
- **Client refactors**: 2–3 days to update GUI/orchestrator call sites and maintain compatibility.
- **Validation**: 1–2 days for automated tests plus cross-platform smoke runs.

## Expected Outcome
- A minimal, dependency-light transcription microservice that can run independently or alongside existing semantic tooling, reducing startup errors from missing analytics packages and enabling prosody/diarization/semantic analysis to evolve separately without risking core transcription availability.
