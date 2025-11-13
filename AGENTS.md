# Repository Guidelines

## Project Structure & Module Organization
`svt.py` launches the main GUI orchestration, while `auto_transcriber_v4_emotion.py`, `prosody_extractor.py`, `speaker_diarizer.py`, and `super_semantic_processor.py` host the audio, prosody, diarization, and semantic layers. Keep ingest assets inside `Eingang/` (source audio), persist results in `Transkripte_LLM/`, and never commit raw PHI. Long-lived knowledge lives in `Memory/` (YAML + SQLite), while marker grammars reside in `VP_ATO/` and `Marker_LD3.5_SSoTh/`. Docs live in `docs/` and the fusion specs under `FusionEngine_ProjectSpec.md/`.

## Build, Test, and Development Commands
Use `python3 svt.py` for the production workflow, or `python3 start_super_semantic.py` to launch the interactive launcher when debugging pipelines. `python3 auto_transcriber_v4_emotion.py --audio Eingang/Patient/demo.wav` exercises the CLI stack end-to-end. Install core deps with `pip install -r requirements.txt`, then extend prosody/emotion features via `pip install -r requirements_emotion.txt`. Run focused checks with `python3 -m pytest tests/test_full_integration.py -v` or `python3 test_prosody_pipeline.py` when iterating on Big-4 metrics.

## Coding Style & Naming Conventions
Code targets Python 3.12 with 4-space indentation, type hints on all public methods, and docstrings that explain therapeutic intent (not just mechanics). Module names stay `snake_case.py`, classes use `CamelCase`, and YAML marker IDs follow the `ATO_*`/`SEM_*` prefixes already present in `VP_ATO/`. Reuse helper utilities such as `audio_preprocessor.normalize_levels` instead of duplicating logic, and keep thresholds/config constants near the top of each module.

## Testing Guidelines
`pytest` is the canonical harness; prefer `python3 -m pytest tests -v` before pushing, plus targeted scripts for modules that embed fixtures (e.g., `test_transcriber_v4_prosody.py`). Add regression tests whenever you touch prosody thresholds, diarization, or YAML schemas, and mirror sample assets under `fixtures/` rather than `Eingang/`. Fail fast by asserting schema keys (see `test_yaml_structure.py`) and include at least one integration test (`tests/test_full_integration.py`) when a change spans multiple layers.

## Commit & Pull Request Guidelines
Follow the existing short, imperative commits (`feat: implement MVP features…`, `fix: stabilize diarization cache`). Branches mirror work type (`feat/<topic>`, `chore/<topic>`). Every PR should link the relevant spec or issue, summarize UX-impact, list config/env changes, and paste test commands + outcomes. Screenshots or transcript snippets are required whenever UI output, Markdown, or JSON payloads change.

## Security & Configuration Tips
Store Hugging Face and OpenAI tokens in `.env` (loaded via `os.getenv`) and keep the file out of Git. Do not upload patient media or generated transcripts; stash work copies under `Eingang/` or `Output/` locally and clean them before committing. When sharing logs, redact speaker identifiers and marker payloads. Sensitive YAML in `VP_ATO/` should be reviewed for accidental PII before pushing.
