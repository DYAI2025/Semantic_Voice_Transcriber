# Repository Guidelines

## Project Structure & Module Organization
`svt.py` orchestrates the GUI workflow, while `auto_transcriber_v4_emotion.py`, `prosody_extractor.py`, `speaker_diarizer.py`, and `super_semantic_processor.py` anchor transcription, prosody, diarization, and semantic fusion. Source audio belongs in `Eingang/`, derived transcripts land in `Transkripte_LLM/`, and regression fixtures live in `fixtures/`. Persist long-term therapeutic memory inside `Memory/` (YAML plus SQLite), and keep marker grammars within `VP_ATO/` and `Marker_LD3.5_SSoTh/`. Reference docs stay under `docs/`, with fusion specs inside `FusionEngine_ProjectSpec.md/`.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` – core runtime deps; append `requirements_emotion.txt` for prosody/emotion experiments.
- `python3 svt.py` – production launcher; `python3 start_super_semantic.py` opens the interactive pipeline controller.
- `python3 auto_transcriber_v4_emotion.py --audio Eingang/Patient/demo.wav` – drives ingest → diarization → semantic emit end-to-end.
- `python3 -m pytest tests -v` – primary regression harness; add focused runs like `python3 test_prosody_pipeline.py` or `python3 -m pytest tests/test_full_integration.py -v` when touching cross-layer flows.

## Coding Style & Naming Conventions
Target Python 3.12, 4-space indentation, and type hints on every public function. Docstrings must capture therapeutic intent rather than pure mechanics. Modules stay `snake_case.py`, classes use `CamelCase`, and YAML markers follow the `ATO_*`/`SEM_*` prefixes already present. Centralize reusable helpers (e.g., `audio_preprocessor.normalize_levels`) and keep critical thresholds or config constants near the top of each module.

## Testing Guidelines
Prefer `pytest` plus the supplied fixtures; mirror any new audio samples inside `fixtures/` instead of `Eingang/`. Add regression tests whenever you modify prosody thresholds, diarization heuristics, or YAML schemas, and assert required keys as shown in `tests/test_yaml_structure.py`. Multi-layer edits require at least one integration test (`tests/test_full_integration.py`) before merging.

## Commit & Pull Request Guidelines
Write short, imperative commits (`feat:`, `fix:`, `chore:`) and branch by work type (`feat/<topic>`). Every PR must cite the relevant spec or issue, summarize UX impact, call out config/env updates, and paste the exact test commands plus outcomes. Include screenshots or transcript snippets whenever UI elements, Markdown exports, or JSON payloads change.

## Security & Configuration Tips
Load OpenAI/Hugging Face tokens from `.env` via `os.getenv` and keep the file untracked. Never commit PHI: stash patient media under `Eingang/` or `Output/` locally and scrub them before pushing. Redact speaker identifiers and marker payloads in logs, and spot-check sensitive YAML within `VP_ATO/` for inadvertent PII before publishing.
