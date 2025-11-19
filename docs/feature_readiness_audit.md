# Feature Readiness Audit

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

## CLI Usage
```
python -m audit.cli --session session1 --json reports/audit.json --markdown reports/audit.md
```
- `--dataset`: overrides testdata path
- Output: JSON + Markdown summary

## Readiness Levels
See `docs/feature_readiness_scale.md`.

## Interpreting Reports
- Table lists each feature with readiness label + availability/smoke status.
- Issues array highlights missing dependencies or failures.

## CI Integration
- `feature_audit.yml` runs the CLI on PRs, uploads reports, and enforces readiness >= 2 for critical features.
- Gate logic: `scripts/check_readiness_gate.py` fails CI when emotions, prosody, or diarization readiness level < 2 or missing.
