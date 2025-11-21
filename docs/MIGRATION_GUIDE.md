# Migration Guide - Legacy to Modular Architecture

**Last Updated:** 2025-11-21 | **Status:** Phase 1 Complete

This guide helps developers and users transition from the legacy codebase structure to the new modular architecture.

---

## For End Users

### No Breaking Changes! ✅

All functionality remains accessible via the main GUI:

```bash
python3 svt.py
```

### Deprecated Entry Points

The following entry points are deprecated but still functional:

- ❌ `python3 super_semantic_gui.py` → Use `python3 svt.py` instead
- ❌ `python3 start_super_semantic.py` → Use `python3 svt.py` instead

**Reason:** Unified GUI interface provides all features in one place.

---

## For Developers

### Phase 1 Changes (Complete)

#### 1. Dead Code Removed

The following files have been deleted (1,227 LOC):

- `auto_transcriber_v3.py` (371 LOC) - replaced by v4
- `whisper_transcriber_v3.py` (443 LOC) - replaced by v4
- `whisper_transcriber.py` (0 LOC) - empty stub
- `whisper_auto_runner.py` (0 LOC) - empty stub
- `mvp_integrator.py` (413 LOC) - depends on deleted v3

**Action Required:** None - no active imports detected

#### 2. Test Files Reorganized

All test files have been moved to `tests/` directory (17 files):

**OLD:**
```bash
python3 test_prosody_analyzer.py
```

**NEW:**
```bash
pytest tests/test_prosody_analyzer.py
# Or run all tests:
pytest tests/
```

**Benefits:**
- Centralized test location
- Better pytest integration
- Easier CI/CD configuration

**Configuration:** `pytest.ini` created with markers and settings

#### 3. Entry Points Consolidated

**Semantic GUI moved to modular location:**

**OLD:**
```python
import super_semantic_gui
```

**NEW:**
```python
from svt_core.ui.semantic_gui import main
```

**Backward Compatibility:** `super_semantic_gui.py` shim created - old imports still work with deprecation warning.

**Deprecated Launchers:**
- `start_super_semantic.py` - shows deprecation warning
- `super_semantic_gui.py` - redirects to `svt_core.ui.semantic_gui`

---

## Phase 2 Changes (In Progress)

### Audio Module Migration

Audio processing modules are being moved to `svt_core/audio/`:

#### Import Changes

**OLD (Legacy - Will be deprecated):**
```python
from audio_quality_analyzer import AudioQualityAnalyzer
from audio_preprocessor import AudioPreprocessor
from prosody_extractor import ProsodyExtractor
from speaker_diarizer import SpeakerDiarizer
```

**NEW (Modular):**
```python
from svt_core.audio import (
    AudioQualityAnalyzer,
    AudioPreprocessor,
    ProsodyExtractor,
    SpeakerDiarizer,
)
```

**Status:** Migration in progress - both imports currently work

---

## Upcoming Changes (Phase 3-6)

### Phase 3: Output System
- `output_formatter.py` → `svt_core/output/` (multiple modules)
- `html_formatter.py` → `svt_core/output/html.py`

### Phase 4: Semantic & Memory
- `super_semantic_processor.py` → `svt_core/semantic/processor.py`
- `speaker_database.py` → `svt_core/memory/database.py`

### Phase 5: Core Transcription
- `auto_transcriber_v4_emotion.py` → `svt_core/transcription/engine.py` (split into multiple modules)

### Phase 6: LLM Migration
- `psychoanalysis_api.py` → Use `svt_core.llm_provider/` (already exists)

---

## Testing Strategy

### Before Migration (Legacy)

```bash
# Individual test files in root
python3 test_prosody_analyzer.py
python3 test_transcription.py
```

### After Migration (Modular)

```bash
# All tests in tests/ directory
pytest tests/                                    # Run all
pytest tests/test_prosody_analyzer.py            # Run specific
pytest tests/ -m prosody                         # Run by marker
pytest tests/ -m "not slow"                      # Exclude slow tests
```

### Test Markers

Use markers in test files:

```python
import pytest

@pytest.mark.prosody
@pytest.mark.slow
def test_prosody_extraction():
    # ...
```

Available markers (see `pytest.ini`):
- `slow` - Long-running tests
- `integration` - Integration tests
- `ci` - Fast CI/CD tests
- `audio` - Requires audio files
- `llm` - Requires LLM API
- `prosody`, `diarization`, `transcription`, `output`, `memory`, `semantic`

---

## Backward Compatibility

### Compatibility Shims

For legacy code, compatibility shims are provided:

**Example: `super_semantic_gui.py`**
```python
# This file now redirects to svt_core.ui.semantic_gui
# Old code continues to work:
import super_semantic_gui  # ⚠️ DeprecationWarning

# New code should use:
from svt_core.ui.semantic_gui import main
```

**Deprecation Timeline:**
- **Phase 1-6:** Shims active with warnings
- **Version 2.0:** Shims will be removed

### Migration Checklist for External Tools

If you have scripts or tools that import SVT modules:

- [ ] Update test imports to use `pytest tests/`
- [ ] Update GUI imports from `super_semantic_gui` → `svt_core.ui.semantic_gui`
- [ ] Prepare for audio module imports (`svt_core.audio`)
- [ ] Watch for deprecation warnings in logs

---

## Troubleshooting

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'auto_transcriber_v3'
```

**Solution:** v3 modules deleted - use v4 (`auto_transcriber_v4_emotion.py`)

---

**Error:**
```
ModuleNotFoundError: No module named 'super_semantic_gui'
```

**Solution:**
```python
# OLD:
import super_semantic_gui

# NEW:
from svt_core.ui.semantic_gui import main
```

---

### Test Discovery Issues

**Error:**
```
ERROR: file or directory not found: test_prosody_analyzer.py
```

**Solution:** Tests moved to `tests/` directory
```bash
# OLD:
python3 test_prosody_analyzer.py

# NEW:
pytest tests/test_prosody_analyzer.py
```

---

### Deprecation Warnings

**Warning:**
```
DeprecationWarning: super_semantic_gui.py is deprecated.
```

**Solution:** Update imports to use modular paths (see above)

**Suppress warnings (not recommended):**
```bash
python3 -W ignore::DeprecationWarning your_script.py
```

---

## FAQ

### Q: Do I need to change my existing scripts?

**A:** Not immediately. Backward compatibility shims ensure old code continues to work. However, you should update imports when possible to avoid breaking changes in version 2.0.

### Q: When will backward compatibility be removed?

**A:** Planned for version 2.0 (after all phases 1-6 complete). Estimated: Q1 2026.

### Q: Where can I find examples of new imports?

**A:** See `tests/` directory for examples using modular imports.

### Q: What if I find a bug in the migration?

**A:** Report issues on GitHub or check logs for detailed error messages.

### Q: Can I still use the old v3 transcriber?

**A:** No, v3 has been removed. Use v4 instead (`auto_transcriber_v4_emotion.py` or soon `svt_core.transcription.TranscriptionEngine`).

---

## Reference

### Old vs New Structure

| Old (Legacy) | New (Modular) | Status |
|-------------|---------------|--------|
| `test_*.py` (root) | `tests/test_*.py` | ✅ Complete |
| `super_semantic_gui.py` (root) | `svt_core/ui/semantic_gui.py` | ✅ Complete |
| `audio_quality_analyzer.py` | `svt_core/audio/quality.py` | 🔄 In Progress |
| `prosody_extractor.py` | `svt_core/audio/prosody.py` | 🔄 In Progress |
| `speaker_diarizer.py` | `svt_core/audio/diarization.py` | 🔄 In Progress |
| `output_formatter.py` | `svt_core/output/formatter.py` | ⏳ Planned |
| `auto_transcriber_v4_emotion.py` | `svt_core/transcription/engine.py` | ⏳ Planned |

---

## Getting Help

- **Documentation:** `docs/plans/LEGACY_REFACTORING_PLAN.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Project Guide:** `CLAUDE.md`

---

**Migration Status:** Phase 1 Complete ✅ | Phase 2 In Progress 🔄
