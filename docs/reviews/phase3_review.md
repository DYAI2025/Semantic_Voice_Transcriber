# Phase 3 Review – Thread-Safe Diarization Timeout

## Scope Recap
- Ensured speaker diarization can run from background threads without triggering the `signal` constraint; fallback worker executes in a separate process with join-based timeout (FR-5).
- Added structured logging for fallback usage, including start method, duration, and timeout failures (FR-6 foundation) plus counters for future telemetry.

## Code Changes
- `speaker_diarizer.py`
  - Added multiprocessing/threading hooks, serialization helpers, and worker entrypoints (`_forked_diarization_worker`, `_spawned_diarization_worker`).
  - `_run_diarization_with_timeout` now routes non-main-thread calls through `_run_fallback_diarization`, which spawns a process (fork when possible, spawn otherwise) and enforces timeouts via `process.join`. Success logs duration; timeouts raise `DiarizationTimeoutError` after terminating the worker.
  - Added annotation serialization/deserialization to keep inter-process payloads lightweight and guaranteed picklable. Introduced fallback counters for telemetry.
- Tests
  - `tests/test_diarization_timeout_fallback.py` validates fallback selection, success path reconstruction, and timeout handling using stubbed multiprocessing contexts.

## Test Evidence
- `python3 -m pytest tests/test_dashboard_error_handling.py tests/test_retry_helper.py tests/test_diarization_timeout_fallback.py -q` ✅
- Full `pytest tests -q` still blocked by missing `src.turning_point_pipeline` (see Phase 0 notes).

## Risks / Follow-Ups
- Spawn workers re-load pyannote models on platforms without `fork`, which may be slow; consider pooling workers or forcing fork where possible in future iterations.
- Telemetry counters (`fallback_invocations`, `fallback_timeouts`) are collected but not yet surfaced in logs—scheduled for Phase 5 (FR-10).
- Need to monitor memory/ GPU usage when fallback processes terminate frequently; add health-check coverage later (FR-11/12).
