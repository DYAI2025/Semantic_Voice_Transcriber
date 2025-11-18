# Current SVT Architecture Overview

## Entry Points & Runtime Flow
- `svt.py` hosts the Tkinter GUI, queues background transcription jobs, and triggers the psychoanalysis dashboard workflow.
- Audio processing uses `auto_transcriber_v4_emotion.py`, which chains Whisper inference, prosody extraction, speaker diarization, semantic marker detection, and file export.
- The dashboard path loads the latest `_transkript.prosody.json`, prepares `pipeline_input`, and calls `PsychoanalysisPipeline` before rendering via `dashboard_generator.py`.

## LLM Usage
- `PsychoanalysisPipeline` selects between:
  - `PsychoanalysisAPI` (OpenAI chat completions) using `.env` keys and `config/psychoanalysis_config.yaml`.
  - `OllamaPsychoanalysisAPI` (local REST at `http://localhost:11434`).
- Responses must include `utterance_states`, `ued_metrics`, and `marker_summary`; missing keys currently crash the dashboard.
- No abstraction layer exists: switching providers requires editing config/env vars.

## Diarization & Prosody
- `speaker_diarizer.py` wraps pyannote with Hugging Face tokens; runs in worker threads and uses SIGALRM-based timeouts.
- Prosody extraction uses `prosody_extractor.py` (Parselmouth/librosa) and writes results into the transcription JSON.
- There is no CPU-only fallback; Hugging Face access is mandatory when diarization is enabled.

## Configuration & Secrets
- `.env` controls OpenAI + Hugging Face tokens; `.env.example` only documents `HF_TOKEN`.
- Psychoanalysis behavior is defined in `config/psychoanalysis_config.yaml` (provider, models, retry parameters, cache directory).
- Other modules read environment vars ad-hoc (e.g., `OPENAI_API_KEY`). There is no centralized config loader for provider settings.

## Distribution / Installation Today
- Developers install dependencies manually via `pip install -r requirements.txt` and manage Ollama, Whisper models, and Hugging Face tokens themselves.
- No provisioning script or installer exists; health checks are not run before GUI launch.
- End users need CLI experience to configure `.env`, run Ollama, and accept pyannote licenses.

## Pain Points
- Provider coupling: LLM-specific logic is embedded directly in `PsychoanalysisPipeline` without a unified interface or fallback.
- Pyannote dependency requires HF tokens; SIGALRM fails in worker threads, causing repeated warnings.
- On machines without Ollama/OpenAI configured, the dashboard crashes with `KeyError` when analysis responses lack required keys.
- Installation requires multiple manual steps (Python runtime, pip deps, model downloads) and is unsuitable for non-technical users.
