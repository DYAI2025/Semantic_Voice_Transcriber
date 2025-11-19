# Repository Guidelines

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

## Project Structure & Module Organization
`svt.py` orchestrates the GUI and routes sessions through `auto_transcriber_v4_emotion.py`, `prosody_extractor.py`, `speaker_diarizer.py`, and `super_semantic_processor.py`. Raw WAVs land in `Eingang/`, curated samples mirror in `fixtures/`, and generated transcripts are archived in `Transkripte_LLM/`. Therapeutic memories (YAML plus SQLite) sit in `Memory/`, while symbolic grammars and narrative templates remain in `VP_ATO/` and `Marker_LD3.5_SSoTh/`. Keep research briefs and design notes inside `docs/` or `FusionEngine_ProjectSpec.md` for quick reference.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` installs the baseline runtime; append `-r requirements_emotion.txt` when exploring prosody or affect modeling.
- `python3 svt.py` launches the production therapist console, while `python3 start_super_semantic.py` exposes the controller UI plus debugging toggles.
- `python3 auto_transcriber_v4_emotion.py --audio Eingang/Patient/demo.wav` exercises the ingest → diarization → semantic pipeline on a fixture clip.
- `python3 -m pytest tests -v` runs the regression pack; scope down with `python3 test_prosody_pipeline.py` or `python3 -m pytest tests/test_full_integration.py -v` before shipping multi-layer work.

## Coding Style & Naming Conventions
Target Python 3.12, 4-space indentation, and type hints on every public function. Docstrings should describe therapeutic intent, not just mechanics. Modules stay `snake_case.py`, classes use `CamelCase`, YAML marker IDs start with `ATO_` or `SEM_`, and shared thresholds belong near the top of each module. Prefer extracting helpers into `audio_preprocessor.py` or `utilities/` instead of duplicating logic.

## Testing Guidelines
Pytest is mandatory. Place any new audio artifacts in `fixtures/` and replicate the schema expectations shown in `tests/test_yaml_structure.py`. Add or update integration checks (`tests/test_full_integration.py`, `test_intelligent_pipeline_integration.py`) whenever changes touch transcription, diarization, or semantic orchestration simultaneously.

## Commit & Pull Request Guidelines
Use imperative subjects with prefixes like `feat:`, `fix:`, or `chore:` and branch by workstream (e.g., `feat/prosody-calibration`). Pull requests must reference the driving spec or issue, summarize clinician impact, list configuration or env changes, and paste the exact test commands plus outcomes. Attach screenshots or transcript excerpts whenever UI, Markdown exports, or JSON payloads shift so reviewers can validate behavior quickly.

## Security & Configuration Tips
Load OpenAI or Hugging Face secrets from `.env` via `os.getenv`, keep the file untracked, and scrub PHI before sharing artifacts. Store raw patient media under `Eingang/` or `Output/`, redact speaker names inside logs, and audit YAML in `VP_ATO/` for inadvertent identifiers prior to release.
