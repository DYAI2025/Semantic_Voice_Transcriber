# Phase 2 Review – Dashboard Retries & Profiles

## Scope Recap
- Added configurable retry/backoff (FR-3) with jitter for OpenAI dashboard calls, surfaced retry counts for FR-2/FR-10 groundwork, and exposed API profiles via environment variables (FR-4).
- Ensured `_run_dashboard_pipeline` logs actual alias/profile/model pulled from `PsychoanalysisAPI` and carries retry counters forward.

## Code Changes
- `psychoanalysis_api.py`
  - Introduced profile-aware key/model resolution (`OPENAI_API_PROFILE`, `OPENAI_API_KEY_<PROFILE>`, `OPENAI_DASHBOARD_MODEL_<PROFILE>`), optional alias, and retry configuration derived from config/env vars.
  - Added `_call_with_retry` with exponential backoff + jitter, logging for RateLimit events, and tracking `last_retry_count` for telemetry.
  - `analyze_transcript` now routes through `_call_with_retry`; class accepts optional client injection for tests.
- `config/psychoanalysis_config.yaml`
  - Added a `retries` block with sane defaults.
- `.env.example`
  - Documented new profile + retry env variables.
- `svt.py`
  - Enhanced context builder to read alias/retry counts directly from the pipeline’s API object and persist the last retry total after successful runs.
- Tests
  - `tests/test_retry_helper.py`: validates retry success, max-attempt failure, and non-rate-limit behavior with patched timers and dummy errors.
  - Updated `tests/test_dashboard_error_handling.py` to align with alias-aware logging.

## Test Evidence
- `python3 -m pytest tests/test_dashboard_error_handling.py tests/test_retry_helper.py -q` ✅
- Full `pytest tests -q` remains blocked by missing `src.turning_point_pipeline` (see Phase 0 baseline).

## Risks / Follow-Ups
- GUI setting for profile selection still pending (FR-4 allows .env-only for now; consider UI toggle later).
- Need to integrate retry counter into telemetry summary (planned Phase 5).
- Ensure documentation (AGENTS/README) reflects new env knobs during FR-9 work.
