# Legacy Refactoring Plan - Semantic Voice Transcriber

**Last Updated:** 2025-11-21 | **Status:** DRAFT
**Target Completion:** 10-12 Wochen | **Priority:** CRITICAL

---

## 🎯 Executive Summary

### Das Kernproblem

- **93,3% des Codes liegt unorganisiert im Root-Verzeichnis** (17.947 LOC)
- **Nur 7% in modularer Struktur** (svt_core/: 797 LOC)
- **10 monolithische Dateien >500 LOC** mit multiplen Verantwortlichkeiten
- **Tight Coupling** zwischen Legacy-Modulen erschwert Wartung und Testing

### Die Lösung

**Stufenweise Migration zu modularer Architektur in 6 Phasen:**

1. **Phase 1 (Woche 1):** Immediate Cleanup - Dead Code entfernen, Tests organisieren
2. **Phase 2 (Woche 2-3):** Audio/Prosody Module - Kernfunktionalität modularisieren
3. **Phase 3 (Woche 4-5):** Output System - Multi-Format-Export aufteilen
4. **Phase 4 (Woche 6-7):** Semantic & Memory - ATO-Engine und Speaker-DB migrieren
5. **Phase 5 (Woche 8-10):** Core Transcription - Monolithischen v4-Transcriber zerlegen
6. **Phase 6 (Woche 11):** LLM Migration - Legacy APIs eliminieren

**Ziel:** 85%+ Code in organisierter Modulstruktur, 43% weniger Root-LOC, 80% weniger monolithische Dateien

---

## 📊 Größte Legacy-Relikte (Identifiziert)

### Top 5 Monolithische Dateien

| Rang | Datei | LOC | Verantwortlichkeiten | Ziel-Module |
|------|-------|-----|---------------------|-------------|
| **1** | auto_transcriber_v4_emotion.py | 1,309 | Whisper, Emotion, Prosody, ATO, Orchestration | 5 Module in svt_core/transcription/ |
| **2** | output_formatter.py | 1,280 | MD, JSON, CSV, HTML, ATO-Formatting, Speaker-Config | 6 Module in svt_core/output/ |
| **3** | svt.py | 1,453 | GUI, Health-Checks, Provider-Config, Orchestration | Teilweise refactored ✅ |
| **4** | html_formatter.py | 835 | HTML/PDF-Generierung, WeasyPrint | 1 Modul in svt_core/output/ |
| **5** | super_semantic_processor.py | 735 | ATO-Marker-Detection, YAML-Loading | 2 Module in svt_core/semantic/ |

**Total:** 5.612 LOC in 5 Dateien (31% des gesamten Root-Codes!)

### Dead Code (Sofort Löschbar)

| Datei | LOC | Grund |
|-------|-----|-------|
| auto_transcriber_v3.py | 371 | Durch v4 ersetzt |
| whisper_transcriber_v3.py | 443 | Durch v4 ersetzt |
| whisper_transcriber.py | 0 | Leerer Stub |
| whisper_auto_runner.py | 0 | Leerer Stub |
| **Total** | **814** | **Immediate Deletion** |

---

## 🏗️ Ziel-Modularchitektur

### Finale Verzeichnisstruktur (Nach Refactoring)

```
Semantic_Voice_Transcriber/
├── svt.py                          # Main GUI (reduziert auf ~800 LOC)
├── config/                         # Konfigurationsdateien
├── Eingang/                        # Input-Verzeichnis
├── Transkripte_LLM/                # Output-Verzeichnis
├── Memory/                         # Speaker-Profile-Daten (YAML/SQLite)
├── VP_ATO/                         # ATO-Marker-Definitionen
├── docs/                           # Dokumentation
├── tests/                          # Alle Tests (60+ Dateien)
│
├── svt_core/                       # MODULARE ARCHITEKTUR (8.486 LOC)
│   ├── __init__.py
│   │
│   ├── audio/                      # Audio-Processing-Module (1.448 LOC)
│   │   ├── __init__.py
│   │   ├── quality.py              # AudioQualityAnalyzer (186 LOC)
│   │   ├── preprocessing.py        # AudioPreprocessor (156 LOC)
│   │   ├── prosody.py              # ProsodyExtractor (409 LOC) ⭐
│   │   ├── diarization.py          # SpeakerDiarizer (697 LOC) ⭐
│   │   └── diarization_cpu.py      # CPU-Fallback (89 LOC) ✅
│   │
│   ├── transcription/              # Transkriptions-Engine (1.500 LOC)
│   │   ├── __init__.py
│   │   ├── engine.py               # Whisper-Orchestration (600 LOC) ⭐
│   │   ├── emotion.py              # Emotion-Analyse (350 LOC)
│   │   ├── confidence.py           # Confidence-Scoring (200 LOC)
│   │   ├── intelligent_pipeline.py # Quality-basierte Model-Selection (250 LOC)
│   │   └── segment_processor.py    # Segment-Processing (100 LOC)
│   │
│   ├── output/                     # Output-Formatierung (3.300 LOC)
│   │   ├── __init__.py
│   │   ├── formatter.py            # OutputFormatter-Facade (200 LOC)
│   │   ├── speaker_config.py       # SpeakerConfig-Klasse (150 LOC)
│   │   ├── markdown.py             # MD-Formatting (400 LOC) ⭐
│   │   ├── json_sidecar.py         # JSON-Sidecar (250 LOC)
│   │   ├── csv_exporter.py         # CSV-Export (180 LOC)
│   │   ├── html.py                 # HTML-Generierung (850 LOC) ⭐
│   │   ├── pdf.py                  # PDF-Generierung (320 LOC)
│   │   ├── dashboard.py            # Psychoanalysis-Dashboard (621 LOC)
│   │   ├── quality_integration.py  # Quality-Validator-Integration (229 LOC)
│   │   └── ato_formatter.py        # ATO-Marker-Formatting (100 LOC)
│   │
│   ├── semantic/                   # Semantische Analyse (1.178 LOC)
│   │   ├── __init__.py
│   │   ├── processor.py            # SuperSemanticProcessor (735 LOC) ⭐
│   │   ├── integration.py          # ATO-Marker-Integration (251 LOC)
│   │   ├── correlation.py          # ATO-Correlation-Engine (103 LOC)
│   │   ├── types.py                # Correlation-Types (40 LOC)
│   │   └── config.py               # Correlation-Config (49 LOC)
│   │
│   ├── memory/                     # Memory & Persistence (709 LOC)
│   │   ├── __init__.py
│   │   ├── database.py             # SpeakerDatabase (575 LOC) ⭐
│   │   ├── cache.py                # Psychoanalysis-Cache (67 LOC)
│   │   └── correlation_memory.py   # Correlation-Memory (67 LOC)
│   │
│   ├── llm_provider/               # LLM-Provider-Abstraction (330 LOC) ✅
│   │   ├── __init__.py
│   │   ├── base.py                 # LLMProvider-Interface (61 LOC)
│   │   ├── factory.py              # Provider-Factory (67 LOC)
│   │   ├── manager.py              # Provider-Manager (46 LOC)
│   │   ├── local_ollama.py         # Ollama-Provider (76 LOC)
│   │   └── providers/
│   │       ├── openai_provider.py  # OpenAI-Provider (41 LOC)
│   │       ├── anthropic_provider.py
│   │       └── dummy_provider.py   # Test-Provider (39 LOC)
│   │
│   ├── config/                     # Konfiguration (100 LOC) ✅
│   │   ├── __init__.py
│   │   └── settings.py             # Settings-Store (39 LOC)
│   │
│   ├── ui/                         # UI-Komponenten (450 LOC)
│   │   ├── __init__.py
│   │   ├── provider_dialog.py      # Provider-Settings-Dialog (67 LOC) ✅
│   │   └── semantic_gui.py         # Semantic-GUI (364 LOC) ⭐
│   │
│   ├── tools/                      # Utilities (400 LOC)
│   │   ├── __init__.py
│   │   ├── file_utils.py           # File-Handling
│   │   ├── audio_chunker.py        # Audio-Segmentierung (143 LOC)
│   │   └── timestamp_parser.py     # Timestamp-Extraktion
│   │
│   └── health_check.py             # Health-Monitoring (73 LOC) ✅
│
├── audit/                          # Feature-Audit-System (500 LOC) ✅
│   ├── audit_runner.py
│   ├── feature_registry.py
│   └── checks/
│
└── scripts/                        # Utility-Scripts (600 LOC)
    ├── initialize_person.py
    ├── run_local.py
    └── QUICK_TEST_FOR_CUSTOMER.py

✅ = Bereits migriert
⭐ = Priorität 1-2 für Migration
```

### Modul-Übersicht (Nach Refactoring)

| Modul | LOC | Dateien | Verantwortlichkeit |
|-------|-----|---------|-------------------|
| svt_core/audio/ | 1.448 | 5 | Audio-Processing, Prosody, Diarization |
| svt_core/transcription/ | 1.500 | 6 | Whisper-Engine, Emotion, Confidence |
| svt_core/output/ | 3.300 | 10 | Multi-Format-Output (MD, JSON, HTML, PDF, CSV) |
| svt_core/semantic/ | 1.178 | 5 | ATO-Marker-Detection, Correlation |
| svt_core/memory/ | 709 | 3 | Speaker-DB, Caching |
| svt_core/llm_provider/ | 330 | 6 | LLM-Abstraction (OpenAI, Ollama, etc.) ✅ |
| svt_core/config/ | 100 | 2 | Settings, Konfiguration ✅ |
| svt_core/ui/ | 450 | 3 | GUI-Komponenten |
| svt_core/tools/ | 400 | 4 | Utilities |
| svt_core/ (root) | 73 | 1 | Health-Check ✅ |
| **Total svt_core/** | **9.488** | **45** | **Modulare Architektur** |

---

## 🚀 Phase-für-Phase Refactoring

---

### **PHASE 1: Immediate Cleanup**
**Timeline:** Woche 1 (5 Arbeitstage)
**Priorität:** CRITICAL
**Risiko:** LOW

#### Ziele
- Dead Code entfernen (814 LOC)
- Test-Dateien organisieren (17 Dateien)
- Entry-Point konsolidieren (3 GUIs → 1 Haupt-GUI)
- Migration-Guide erstellen

#### Tasks

##### 1.1 Dead Code Deletion
```bash
# Zu löschen:
rm auto_transcriber_v3.py           # 371 LOC
rm whisper_transcriber_v3.py        # 443 LOC
rm whisper_transcriber.py           # 0 LOC (Stub)
rm whisper_auto_runner.py           # 0 LOC (Stub)
```

**Testing:**
- Verifiziere, dass keine aktiven Imports existieren
- Suche nach Referenzen in Dokumentation

**Commit:** `chore: delete legacy v3 transcriber modules (814 LOC)`

##### 1.2 Test File Reorganization

**Zu verschieben (17 Dateien aus Root → tests/):**
```
test_prosody_analyzer.py
test_prosody_pipeline.py
test_confidence_scoring.py
test_intelligent_pipeline_integration.py
test_transcriber_osd_integration.py
test_output_formatter_osd.py
test_transcription.py
test_initialize_person.py
test_yaml_structure.py
test_speaker_diarizer.py
test_audio_quality.py
test_emotion_analysis.py
test_memory_update.py
test_ato_correlation.py
test_psychoanalysis.py
test_dashboard_generation.py
test_end_to_end.py
```

**Migration-Script:**
```bash
# tests/migrate_root_tests.sh
#!/bin/bash
for test_file in test_*.py; do
    if [ -f "$test_file" ]; then
        git mv "$test_file" tests/
    fi
done

# Update pytest configuration
cat >> pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
EOF
```

**Testing:**
- `pytest tests/` - Alle Tests müssen grün sein
- CI/CD-Pipeline verifizieren

**Commit:** `chore: reorganize test files to tests/ directory (17 files)`

##### 1.3 Entry Point Consolidation

**Status Quo:**
- `svt.py` (1.453 LOC) - **MAIN GUI** ✅
- `super_semantic_gui.py` (364 LOC) - Separate Semantic-GUI
- `start_super_semantic.py` (213 LOC) - Interactive Launcher

**Migration-Strategie:**
1. **svt.py bleibt Haupt-Entry-Point**
2. **Integriere Semantic-GUI in svt.py als Tab/Dialog**
3. **Deprecate start_super_semantic.py**

**Implementierung:**
```python
# svt.py - Add semantic analysis tab
class SVTApplication:
    def __init__(self):
        # ... existing code ...

        # Add semantic analysis tab
        self.semantic_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.semantic_tab, text="🔍 Semantic Analysis")
        self._init_semantic_tab()

    def _init_semantic_tab(self):
        # Import and embed super_semantic_gui logic
        from svt_core.ui.semantic_gui import SemanticAnalysisPanel
        self.semantic_panel = SemanticAnalysisPanel(self.semantic_tab)
        self.semantic_panel.pack(fill="both", expand=True)
```

**Move super_semantic_gui.py → svt_core/ui/semantic_gui.py:**
```bash
mkdir -p svt_core/ui/
git mv super_semantic_gui.py svt_core/ui/semantic_gui.py
```

**Deprecation Notice in start_super_semantic.py:**
```python
# start_super_semantic.py
import warnings
warnings.warn(
    "start_super_semantic.py is deprecated. Use 'python3 svt.py' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Redirect to main GUI
import subprocess
subprocess.run(["python3", "svt.py"])
```

**Commit:** `refactor: consolidate entry points - integrate semantic GUI into svt.py`

##### 1.4 Migration Guide Creation

**Erstelle docs/MIGRATION_GUIDE.md:**
```markdown
# Migration Guide - Legacy to Modular Architecture

## For Developers

### Import Changes

**OLD (Legacy):**
```python
import auto_transcriber_v4_emotion as v4
from prosody_extractor import ProsodyExtractor
from speaker_diarizer import SpeakerDiarizer
from output_formatter import OutputFormatter
```

**NEW (Modular):**
```python
from svt_core.transcription import TranscriptionEngine
from svt_core.audio.prosody import ProsodyExtractor
from svt_core.audio.diarization import SpeakerDiarizer
from svt_core.output import OutputFormatter
```

### Entry Point Changes

**OLD:**
- `python3 svt.py` - Main GUI
- `python3 super_semantic_gui.py` - Semantic GUI
- `python3 start_super_semantic.py` - Launcher

**NEW:**
- `python3 svt.py` - Unified GUI (all features in tabs)

### Testing Changes

**OLD:**
- Tests in root: `python3 test_prosody.py`

**NEW:**
- Tests in tests/: `pytest tests/test_prosody.py`

## For End Users

### No Breaking Changes
All functionality remains accessible via `python3 svt.py`.

Semantic analysis now available in "🔍 Semantic Analysis" tab.
```

**Commit:** `docs: add migration guide for modular architecture`

#### Phase 1 Deliverables
- ✅ 814 LOC Dead Code gelöscht
- ✅ 17 Test-Dateien nach tests/ verschoben
- ✅ Semantic GUI in svt.py integriert
- ✅ start_super_semantic.py deprecated
- ✅ Migration Guide dokumentiert

**Metrics:**
- Root-Dateien: 65 → 48 (-26%)
- Root-LOC: 17.947 → 16.770 (-7%)

---

### **PHASE 2: Audio/Prosody Module Creation**
**Timeline:** Woche 2-3 (10 Arbeitstage)
**Priorität:** HIGH
**Risiko:** MEDIUM

#### Ziele
- Audio-Processing-Module nach svt_core/audio/ migrieren (1.448 LOC)
- Prosody- und Diarization-Funktionalität modularisieren
- Auto_transcriber_v4_emotion.py von Audio-Logik entkoppeln

#### Tasks

##### 2.1 Erstelle svt_core/audio/ Modul-Struktur

```bash
mkdir -p svt_core/audio
touch svt_core/audio/__init__.py
```

**svt_core/audio/__init__.py:**
```python
"""
Audio Processing Module

Provides audio quality analysis, preprocessing, prosody extraction,
and speaker diarization functionality.
"""

from .quality import AudioQualityAnalyzer
from .preprocessing import AudioPreprocessor
from .prosody import ProsodyExtractor
from .diarization import SpeakerDiarizer
from .diarization_cpu import CPUDiarizer

__all__ = [
    'AudioQualityAnalyzer',
    'AudioPreprocessor',
    'ProsodyExtractor',
    'SpeakerDiarizer',
    'CPUDiarizer',
]
```

##### 2.2 Migrate audio_quality_analyzer.py → svt_core/audio/quality.py

**Schritte:**
1. Kopiere audio_quality_analyzer.py → svt_core/audio/quality.py
2. Update Imports in quality.py (falls nötig)
3. Teste mit bestehenden Tests
4. Update Imports in auto_transcriber_v4_emotion.py
5. Delete audio_quality_analyzer.py

**Testing:**
```bash
pytest tests/test_audio_quality.py -v
pytest tests/test_intelligent_pipeline_integration.py -v
```

**Commit:** `refactor: migrate AudioQualityAnalyzer to svt_core/audio/quality.py`

##### 2.3 Migrate audio_preprocessor.py → svt_core/audio/preprocessing.py

**Analog zu 2.2**

**Commit:** `refactor: migrate AudioPreprocessor to svt_core/audio/preprocessing.py`

##### 2.4 Migrate prosody_extractor.py → svt_core/audio/prosody.py

**KRITISCH:** Prosody-Extraction ist Kernfunktionalität (409 LOC)

**Zusätzliche Schritte:**
1. Splitte prosody_extractor.py in logische Untermodule:
   - `prosody.py` - Hauptklasse ProsodyExtractor
   - `prosody_types.py` - Dataclasses (ProsodyFeatures, ProsodyBaseline, SegmentProsody)
   - `prosody_config.py` - Thresholds und Config

**svt_core/audio/prosody_types.py:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProsodyFeatures:
    tempo: Optional[float] = None
    pitch: Optional[float] = None
    energy: Optional[float] = None
    pause_duration: Optional[float] = None
    # ... existing fields ...

@dataclass
class ProsodyBaseline:
    mean_tempo: float
    mean_pitch: float
    mean_energy: float
    # ... existing fields ...

@dataclass
class SegmentProsody:
    segment_index: int
    features: ProsodyFeatures
    deviations: dict
    markers: list[str]
    # ... existing fields ...
```

**Testing:**
```bash
pytest tests/test_prosody_analyzer.py -v
pytest tests/test_prosody_pipeline.py -v
```

**Commit:** `refactor: migrate ProsodyExtractor to svt_core/audio/prosody.py`

##### 2.5 Migrate speaker_diarizer.py → svt_core/audio/diarization.py

**KRITISCH:** Speaker Diarization mit Multiprocessing (697 LOC)

**Besondere Herausforderungen:**
- Pyannote.audio-Integration
- Multiprocessing (fork/spawn)
- Retry-Logic
- OSD (Overlapped Speech Detection)

**Strategie:**
- Beibehalten der gesamten Logik (keine Vereinfachung in Phase 2)
- Nur Move, kein Refactoring in dieser Phase
- Refactoring in späteren Iterationen

**Testing:**
```bash
pytest tests/test_speaker_diarizer.py -v
pytest tests/test_transcriber_osd_integration.py -v
```

**Commit:** `refactor: migrate SpeakerDiarizer to svt_core/audio/diarization.py`

##### 2.6 Update auto_transcriber_v4_emotion.py Imports

**OLD:**
```python
from audio_quality_analyzer import AudioQualityAnalyzer
from audio_preprocessor import AudioPreprocessor
from prosody_extractor import ProsodyExtractor
from speaker_diarizer import SpeakerDiarizer
```

**NEW:**
```python
from svt_core.audio import (
    AudioQualityAnalyzer,
    AudioPreprocessor,
    ProsodyExtractor,
    SpeakerDiarizer,
)
```

**Testing:**
- Komplette E2E-Pipeline testen
- `pytest tests/test_intelligent_pipeline_integration.py -v`

**Commit:** `refactor: update auto_transcriber_v4 to use svt_core.audio modules`

##### 2.7 Backward Compatibility Shims (Optional)

**Falls externe Tools auf alte Imports angewiesen sind:**

**Erstelle audio_quality_analyzer.py (Shim):**
```python
"""
DEPRECATED: Use svt_core.audio.quality instead.

This file provides backward compatibility.
Will be removed in version 2.0.
"""

import warnings
from svt_core.audio.quality import AudioQualityAnalyzer

warnings.warn(
    "Importing from audio_quality_analyzer is deprecated. "
    "Use 'from svt_core.audio import AudioQualityAnalyzer' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['AudioQualityAnalyzer']
```

**Analog für:**
- `audio_preprocessor.py`
- `prosody_extractor.py`
- `speaker_diarizer.py`

**Commit:** `chore: add backward compatibility shims for audio modules`

#### Phase 2 Deliverables
- ✅ svt_core/audio/ Modul mit 5 Dateien erstellt
- ✅ 1.448 LOC nach svt_core/audio/ migriert
- ✅ Alle Audio-Tests grün
- ✅ auto_transcriber_v4_emotion.py auf neue Imports aktualisiert
- ✅ Backward Compatibility Shims (optional)

**Metrics:**
- Root-LOC: 16.770 → 15.322 (-9%)
- svt_core LOC: 797 → 2.245 (+182%)
- Modularität: 12% → 15%

---

### **PHASE 3: Output System Module Creation**
**Timeline:** Woche 4-5 (10 Arbeitstage)
**Priorität:** HIGH
**Risiko:** MEDIUM-HIGH

#### Ziele
- Output-Formatter aufspalten (1.280 LOC → 6 Module)
- HTML/PDF-Generierung modularisieren (835 LOC)
- Dashboard-Generator migrieren (621 LOC)
- Total: 3.045 LOC nach svt_core/output/

#### Tasks

##### 3.1 Erstelle svt_core/output/ Modul-Struktur

```bash
mkdir -p svt_core/output
touch svt_core/output/__init__.py
```

**svt_core/output/__init__.py:**
```python
"""
Output Formatting Module

Provides multi-format output generation:
- Markdown (therapeutic format)
- JSON sidecar (prosody data)
- CSV (data export)
- HTML/PDF (professional reports)
- Psychoanalysis dashboards
"""

from .formatter import OutputFormatter
from .speaker_config import SpeakerConfig, SpeakerMode
from .markdown import MarkdownFormatter
from .json_sidecar import JSONSidecarFormatter
from .csv_exporter import CSVExporter
from .html import HTMLFormatter
from .pdf import PDFGenerator
from .dashboard import DashboardGenerator

__all__ = [
    'OutputFormatter',
    'SpeakerConfig',
    'SpeakerMode',
    'MarkdownFormatter',
    'JSONSidecarFormatter',
    'CSVExporter',
    'HTMLFormatter',
    'PDFGenerator',
    'DashboardGenerator',
]
```

##### 3.2 Split output_formatter.py (1.280 LOC)

**Analyse der Verantwortlichkeiten:**

1. **SpeakerConfig-Klasse** (~150 LOC)
   - Speaker-Modus (Anonymous, Letters, Names, Custom)
   - Label-Generierung
   - → `svt_core/output/speaker_config.py`

2. **Markdown-Formatting** (~400 LOC)
   - Therapeutic transcript format
   - Speaker headers
   - Metadata sidebars
   - ATO marker formatting
   - → `svt_core/output/markdown.py`

3. **JSON Sidecar** (~250 LOC)
   - Prosody data serialization
   - Structured metadata
   - → `svt_core/output/json_sidecar.py`

4. **CSV Export** (~180 LOC)
   - Data table generation
   - Column formatting
   - → `svt_core/output/csv_exporter.py`

5. **Quality Integration** (~100 LOC)
   - Quality validator calls
   - Confidence markers
   - → `svt_core/output/quality_integration.py`

6. **ATO Marker Formatting** (~100 LOC)
   - ATO marker detection
   - Marker annotation
   - → `svt_core/output/ato_formatter.py`

7. **OutputFormatter Facade** (~100 LOC)
   - Orchestration
   - Multi-format dispatch
   - → `svt_core/output/formatter.py`

**Migration-Reihenfolge:**

1. **SpeakerConfig** (keine Abhängigkeiten)
2. **Quality Integration** (dependency für andere)
3. **ATO Formatter** (dependency für Markdown)
4. **JSON Sidecar** (unabhängig)
5. **CSV Exporter** (unabhängig)
6. **Markdown Formatter** (nutzt SpeakerConfig, ATO, Quality)
7. **OutputFormatter Facade** (nutzt alle)

##### 3.2.1 Migrate SpeakerConfig

**Erstelle svt_core/output/speaker_config.py:**

```python
"""
Speaker Configuration Module

Manages speaker labeling modes and configuration.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict

class SpeakerMode(Enum):
    """Speaker labeling modes."""
    ANONYMOUS = "anonymous"  # Therapeut, Patient
    LETTERS = "letters"      # Speaker A, Speaker B
    NAMES = "names"          # Real names
    CUSTOM = "custom"        # Custom mapping

@dataclass
class SpeakerConfig:
    """Configuration for speaker labeling."""
    mode: SpeakerMode = SpeakerMode.ANONYMOUS
    custom_mapping: Optional[Dict[str, str]] = None

    def get_label(self, speaker_id: str, index: int) -> str:
        """
        Generate speaker label based on mode.

        Args:
            speaker_id: Raw speaker ID from diarization
            index: Speaker index (0, 1, 2, ...)

        Returns:
            Formatted speaker label
        """
        # ... existing logic from output_formatter.py ...
```

**Extract Code:**
```bash
# Extract SpeakerConfig class and related code
grep -A 150 "class SpeakerMode" output_formatter.py > svt_core/output/speaker_config.py
# Manual cleanup and formatting
```

**Testing:**
```bash
pytest tests/test_output_formatter.py::test_speaker_config -v
```

**Commit:** `refactor: extract SpeakerConfig to svt_core/output/speaker_config.py`

##### 3.2.2 Migrate Markdown Formatter

**Erstelle svt_core/output/markdown.py:**

```python
"""
Markdown Output Formatter

Generates therapeutic transcript format with:
- Speaker headers
- Metadata sidebars (prosody, ATO markers)
- Clean text (no inline markers)
"""

from typing import List, Dict, Any
from .speaker_config import SpeakerConfig
from .ato_formatter import ATOFormatter
from .quality_integration import QualityIntegration

class MarkdownFormatter:
    """Generates therapeutic markdown transcripts."""

    def __init__(
        self,
        speaker_config: SpeakerConfig,
        ato_formatter: ATOFormatter,
        quality_integration: QualityIntegration,
    ):
        self.speaker_config = speaker_config
        self.ato_formatter = ato_formatter
        self.quality_integration = quality_integration

    def format(
        self,
        segments: List[Dict[str, Any]],
        prosody_data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> str:
        """
        Generate markdown transcript.

        Args:
            segments: Transcription segments with speaker labels
            prosody_data: Prosody analysis results
            metadata: Audio metadata (duration, quality, etc.)

        Returns:
            Formatted markdown string
        """
        # ... existing markdown generation logic ...
```

**Commit:** `refactor: extract MarkdownFormatter to svt_core/output/markdown.py`

##### 3.2.3 Migrate JSON, CSV, ATO, Quality modules

**Analog zu 3.2.1 und 3.2.2 für:**
- `json_sidecar.py`
- `csv_exporter.py`
- `ato_formatter.py`
- `quality_integration.py`

**Commits:**
- `refactor: extract JSONSidecarFormatter to svt_core/output/json_sidecar.py`
- `refactor: extract CSVExporter to svt_core/output/csv_exporter.py`
- `refactor: extract ATOFormatter to svt_core/output/ato_formatter.py`
- `refactor: extract QualityIntegration to svt_core/output/quality_integration.py`

##### 3.2.4 Create OutputFormatter Facade

**Erstelle svt_core/output/formatter.py:**

```python
"""
Output Formatter Facade

Orchestrates multi-format output generation.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .speaker_config import SpeakerConfig, SpeakerMode
from .markdown import MarkdownFormatter
from .json_sidecar import JSONSidecarFormatter
from .csv_exporter import CSVExporter
from .html import HTMLFormatter
from .ato_formatter import ATOFormatter
from .quality_integration import QualityIntegration

class OutputFormatter:
    """Facade for multi-format output generation."""

    def __init__(self, speaker_mode: SpeakerMode = SpeakerMode.ANONYMOUS):
        self.speaker_config = SpeakerConfig(mode=speaker_mode)
        self.ato_formatter = ATOFormatter()
        self.quality_integration = QualityIntegration()

        # Initialize formatters
        self.markdown = MarkdownFormatter(
            self.speaker_config,
            self.ato_formatter,
            self.quality_integration,
        )
        self.json_sidecar = JSONSidecarFormatter()
        self.csv = CSVExporter(self.speaker_config)
        self.html = HTMLFormatter(self.speaker_config)

    def generate_all_formats(
        self,
        segments: List[Dict[str, Any]],
        prosody_data: Dict[str, Any],
        metadata: Dict[str, Any],
        output_path: Path,
    ) -> Dict[str, Path]:
        """
        Generate all output formats.

        Returns:
            Dict mapping format names to output file paths
        """
        results = {}

        # Markdown
        md_content = self.markdown.format(segments, prosody_data, metadata)
        md_path = output_path.with_suffix('.md')
        md_path.write_text(md_content, encoding='utf-8')
        results['markdown'] = md_path

        # JSON sidecar
        json_content = self.json_sidecar.format(prosody_data, metadata)
        json_path = output_path.with_suffix('.prosody.json')
        json_path.write_text(json_content, encoding='utf-8')
        results['json'] = json_path

        # CSV
        csv_content = self.csv.format(segments, prosody_data)
        csv_path = output_path.with_suffix('.csv')
        csv_path.write_text(csv_content, encoding='utf-8')
        results['csv'] = csv_path

        # HTML
        html_content = self.html.format(segments, prosody_data, metadata)
        html_path = output_path.with_suffix('_enhanced.html')
        html_path.write_text(html_content, encoding='utf-8')
        results['html'] = html_path

        return results
```

**Commit:** `refactor: create OutputFormatter facade in svt_core/output/formatter.py`

##### 3.3 Migrate html_formatter.py → svt_core/output/html.py

**Analog zu Audio-Migration:**
```bash
git mv html_formatter.py svt_core/output/html.py
```

**Update Imports:**
```python
from .speaker_config import SpeakerConfig
```

**Commit:** `refactor: migrate HTMLFormatter to svt_core/output/html.py`

##### 3.4 Migrate professional_pdf_generator.py → svt_core/output/pdf.py

**Analog zu 3.3**

**Commit:** `refactor: migrate PDFGenerator to svt_core/output/pdf.py`

##### 3.5 Migrate dashboard_generator.py → svt_core/output/dashboard.py

**Analog zu 3.3**

**Commit:** `refactor: migrate DashboardGenerator to svt_core/output/dashboard.py`

##### 3.6 Update auto_transcriber_v4_emotion.py Imports

**OLD:**
```python
from output_formatter import OutputFormatter
from html_formatter import HTMLFormatter
```

**NEW:**
```python
from svt_core.output import OutputFormatter, HTMLFormatter
```

**Commit:** `refactor: update auto_transcriber_v4 to use svt_core.output modules`

##### 3.7 Delete Legacy output_formatter.py

**Nach Verifikation aller Tests:**
```bash
git rm output_formatter.py
git rm html_formatter.py
git rm professional_pdf_generator.py
git rm dashboard_generator.py
```

**Commit:** `chore: remove legacy output formatter files (3,045 LOC migrated)`

#### Phase 3 Deliverables
- ✅ svt_core/output/ Modul mit 10 Dateien erstellt
- ✅ 3.045 LOC nach svt_core/output/ migriert
- ✅ output_formatter.py in 7 logische Module aufgeteilt
- ✅ Alle Output-Tests grün
- ✅ Single Responsibility Principle durchgesetzt

**Metrics:**
- Root-LOC: 15.322 → 12.277 (-20%)
- svt_core LOC: 2.245 → 5.290 (+136%)
- Modularität: 15% → 30%
- Monolithic files >500 LOC: 10 → 6 (-40%)

---

### **PHASE 4: Semantic & Memory Module Creation**
**Timeline:** Woche 6-7 (10 Arbeitstage)
**Priorität:** MEDIUM
**Risiko:** MEDIUM

#### Ziele
- Semantic-Processing nach svt_core/semantic/ migrieren (1.178 LOC)
- Memory-System nach svt_core/memory/ migrieren (709 LOC)
- Total: 1.887 LOC migriert

#### Tasks

##### 4.1 Erstelle svt_core/semantic/ Modul

```bash
mkdir -p svt_core/semantic
touch svt_core/semantic/__init__.py
```

**svt_core/semantic/__init__.py:**
```python
"""
Semantic Analysis Module

Provides ATO marker detection, correlation analysis, and semantic processing.
"""

from .processor import SuperSemanticProcessor
from .integration import ATOMarkerIntegration
from .correlation import CorrelationEngine
from .types import CorrelationType, CorrelationStrength
from .config import CorrelationConfig

__all__ = [
    'SuperSemanticProcessor',
    'ATOMarkerIntegration',
    'CorrelationEngine',
    'CorrelationType',
    'CorrelationStrength',
    'CorrelationConfig',
]
```

##### 4.2 Migrate super_semantic_processor.py → svt_core/semantic/processor.py

**Migrate:**
```bash
git mv super_semantic_processor.py svt_core/semantic/processor.py
```

**Testing:**
```bash
pytest tests/test_semantic_processor.py -v
```

**Commit:** `refactor: migrate SuperSemanticProcessor to svt_core/semantic/processor.py`

##### 4.3 Migrate ATO Correlation modules

**Migrate:**
- `ato_marker_integration.py` → `svt_core/semantic/integration.py`
- `ato_correlation_engine.py` → `svt_core/semantic/correlation.py`
- `ato_correlation_types.py` → `svt_core/semantic/types.py`
- `ato_correlation_config.py` → `svt_core/semantic/config.py`

**Commits:**
- `refactor: migrate ATOMarkerIntegration to svt_core/semantic/integration.py`
- `refactor: migrate CorrelationEngine to svt_core/semantic/correlation.py`
- `refactor: migrate correlation types to svt_core/semantic/types.py`
- `refactor: migrate correlation config to svt_core/semantic/config.py`

##### 4.4 Erstelle svt_core/memory/ Modul

```bash
mkdir -p svt_core/memory
touch svt_core/memory/__init__.py
```

**svt_core/memory/__init__.py:**
```python
"""
Memory & Persistence Module

Manages speaker profiles, caching, and correlation memory.
"""

from .database import SpeakerDatabase
from .cache import PsychoanalysisCache
from .correlation_memory import CorrelationMemory

__all__ = [
    'SpeakerDatabase',
    'PsychoanalysisCache',
    'CorrelationMemory',
]
```

##### 4.5 Migrate Memory modules

**Migrate:**
- `speaker_database.py` → `svt_core/memory/database.py`
- `psychoanalysis_cache.py` → `svt_core/memory/cache.py`
- `correlation_memory.py` → `svt_core/memory/correlation_memory.py`

**Commits:**
- `refactor: migrate SpeakerDatabase to svt_core/memory/database.py`
- `refactor: migrate PsychoanalysisCache to svt_core/memory/cache.py`
- `refactor: migrate CorrelationMemory to svt_core/memory/correlation_memory.py`

##### 4.6 Update Imports

**Update in:**
- `auto_transcriber_v4_emotion.py`
- `psychoanalysis_pipeline.py`
- `svt.py`

**Commit:** `refactor: update imports to use svt_core.semantic and svt_core.memory`

#### Phase 4 Deliverables
- ✅ svt_core/semantic/ mit 5 Modulen
- ✅ svt_core/memory/ mit 3 Modulen
- ✅ 1.887 LOC migriert
- ✅ Alle Tests grün

**Metrics:**
- Root-LOC: 12.277 → 10.390 (-15%)
- svt_core LOC: 5.290 → 7.177 (+36%)
- Modularität: 30% → 41%

---

### **PHASE 5: Core Transcription Refactoring**
**Timeline:** Woche 8-10 (15 Arbeitstage)
**Priorität:** CRITICAL
**Risiko:** HIGH

#### Ziele
- **auto_transcriber_v4_emotion.py** (1.309 LOC) zerlegen
- Kern-Funktionalität in logische Module aufteilen
- Whisper-Engine, Emotion-Analyse, Confidence-Scoring trennen
- Total: 1.309 LOC → 6 Module in svt_core/transcription/

#### Vorbereitung: Code-Analyse

**auto_transcriber_v4_emotion.py Struktur:**

1. **Whisper Orchestration** (~600 LOC)
   - Model loading
   - Audio preprocessing
   - Transcription loop
   - Segment processing
   - → `svt_core/transcription/engine.py`

2. **Emotion Analysis** (~350 LOC)
   - TextBlob sentiment
   - Audio feature extraction
   - Emotion classification
   - → `svt_core/transcription/emotion.py`

3. **Confidence Scoring** (~200 LOC)
   - avg_logprob conversion
   - no_speech_prob integration
   - Confidence thresholds
   - → `svt_core/transcription/confidence.py`

4. **Intelligent Pipeline** (~250 LOC)
   - Quality analysis
   - Model selection
   - Pipeline orchestration
   - → `svt_core/transcription/intelligent_pipeline.py`

5. **Segment Processing** (~100 LOC)
   - Timestamp parsing
   - Speaker alignment
   - Prosody alignment
   - → `svt_core/transcription/segment_processor.py`

6. **Main Facade** (~100 LOC)
   - Public API
   - Backward compatibility
   - → `svt_core/transcription/__init__.py` (TranscriptionEngine facade)

#### Tasks

##### 5.1 Erstelle svt_core/transcription/ Modul

```bash
mkdir -p svt_core/transcription
touch svt_core/transcription/__init__.py
```

**svt_core/transcription/__init__.py:**
```python
"""
Transcription Engine Module

Provides Whisper-based speech-to-text with emotion analysis,
confidence scoring, and intelligent pipeline.
"""

from .engine import WhisperEngine
from .emotion import EmotionAnalyzer
from .confidence import ConfidenceScorer
from .intelligent_pipeline import IntelligentPipeline
from .segment_processor import SegmentProcessor

# Backward compatibility facade
class TranscriptionEngine:
    """
    Facade for transcription functionality.

    Provides backward-compatible API for legacy code.
    """

    def __init__(self, model_size="small", enable_emotion=True):
        self.engine = WhisperEngine(model_size)
        self.emotion = EmotionAnalyzer() if enable_emotion else None
        self.confidence = ConfidenceScorer()
        self.pipeline = IntelligentPipeline(self.engine, self.emotion)
        self.segment_processor = SegmentProcessor()

    def transcribe(
        self,
        audio_path,
        enable_prosody=True,
        enable_diarization=True,
        enable_ato_markers=True,
    ):
        """
        Transcribe audio file.

        Backward-compatible API matching auto_transcriber_v4_emotion.py.
        """
        return self.pipeline.transcribe(
            audio_path=audio_path,
            enable_prosody=enable_prosody,
            enable_diarization=enable_diarization,
            enable_ato_markers=enable_ato_markers,
        )

__all__ = [
    'TranscriptionEngine',
    'WhisperEngine',
    'EmotionAnalyzer',
    'ConfidenceScorer',
    'IntelligentPipeline',
    'SegmentProcessor',
]
```

##### 5.2 Extract Whisper Engine

**Erstelle svt_core/transcription/engine.py:**

```python
"""
Whisper Engine

Low-level Whisper model interface.
"""

import whisper
from pathlib import Path
from typing import Dict, Any, List

class WhisperEngine:
    """Whisper model wrapper."""

    def __init__(self, model_size: str = "small"):
        """
        Initialize Whisper engine.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None

    def load_model(self):
        """Load Whisper model."""
        if self.model is None:
            self.model = whisper.load_model(self.model_size)

    def transcribe_raw(
        self,
        audio_path: Path,
        language: str = "de",
    ) -> Dict[str, Any]:
        """
        Raw Whisper transcription.

        Args:
            audio_path: Path to audio file
            language: Language code

        Returns:
            Whisper result dict with segments
        """
        self.load_model()
        result = self.model.transcribe(
            str(audio_path),
            language=language,
            verbose=False,
        )
        return result

    def transcribe_segments(
        self,
        audio_path: Path,
        language: str = "de",
    ) -> List[Dict[str, Any]]:
        """
        Transcribe and return processed segments.

        Returns:
            List of segments with text, timestamps, confidence
        """
        result = self.transcribe_raw(audio_path, language)
        segments = []

        for seg in result['segments']:
            segments.append({
                'text': seg['text'].strip(),
                'start': seg['start'],
                'end': seg['end'],
                'avg_logprob': seg.get('avg_logprob', 0.0),
                'no_speech_prob': seg.get('no_speech_prob', 0.0),
            })

        return segments
```

**Extract Code:**
```bash
# Extract Whisper-related code from auto_transcriber_v4_emotion.py
# Manual extraction with careful testing
```

**Testing:**
```bash
pytest tests/test_transcription.py::test_whisper_engine -v
```

**Commit:** `refactor: extract WhisperEngine to svt_core/transcription/engine.py`

##### 5.3 Extract Emotion Analyzer

**Erstelle svt_core/transcription/emotion.py:**

```python
"""
Emotion Analysis Module

Provides multi-modal emotion detection combining text sentiment
and audio features.
"""

from textblob import TextBlob
import numpy as np
from typing import Dict, Any

class EmotionAnalyzer:
    """Multi-modal emotion analyzer."""

    def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze text sentiment using TextBlob.

        Args:
            text: Input text

        Returns:
            Dict with polarity and subjectivity scores
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
        }

    def analyze_audio_features(
        self,
        audio_segment: np.ndarray,
        sample_rate: int,
    ) -> Dict[str, float]:
        """
        Extract emotion-relevant audio features.

        Args:
            audio_segment: Audio numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dict with audio features (pitch variance, energy, etc.)
        """
        # ... existing audio feature extraction logic ...

    def combine_modalities(
        self,
        text_sentiment: Dict[str, float],
        audio_features: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Combine text and audio modalities for emotion classification.

        Returns:
            Emotion classification result
        """
        # ... existing emotion fusion logic ...
```

**Commit:** `refactor: extract EmotionAnalyzer to svt_core/transcription/emotion.py`

##### 5.4 Extract Confidence Scorer

**Erstelle svt_core/transcription/confidence.py:**

```python
"""
Confidence Scoring Module

Converts Whisper's avg_logprob and no_speech_prob to confidence scores.
"""

import math
from typing import Dict, Any

class ConfidenceScorer:
    """Whisper confidence scoring."""

    CONFIDENCE_THRESHOLD = 0.5  # Below this: [UNSICHER] marker

    def calculate_confidence(
        self,
        avg_logprob: float,
        no_speech_prob: float,
    ) -> float:
        """
        Calculate confidence score from Whisper outputs.

        Args:
            avg_logprob: Average log probability (negative)
            no_speech_prob: No-speech probability (0-1)

        Returns:
            Confidence score (0-1)
        """
        confidence = math.exp(avg_logprob) * (1 - no_speech_prob)
        return max(0.0, min(1.0, confidence))

    def is_low_confidence(self, confidence: float) -> bool:
        """Check if confidence is below threshold."""
        return confidence < self.CONFIDENCE_THRESHOLD

    def annotate_segment(
        self,
        segment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Add confidence annotation to segment.

        Args:
            segment: Segment dict with avg_logprob and no_speech_prob

        Returns:
            Segment with added 'confidence' and 'low_confidence' fields
        """
        confidence = self.calculate_confidence(
            segment.get('avg_logprob', 0.0),
            segment.get('no_speech_prob', 0.0),
        )

        segment['confidence'] = confidence
        segment['low_confidence'] = self.is_low_confidence(confidence)

        return segment
```

**Commit:** `refactor: extract ConfidenceScorer to svt_core/transcription/confidence.py`

##### 5.5 Extract Intelligent Pipeline

**Erstelle svt_core/transcription/intelligent_pipeline.py:**

```python
"""
Intelligent Transcription Pipeline

Quality-based model selection and orchestration.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from svt_core.audio import AudioQualityAnalyzer
from .engine import WhisperEngine
from .emotion import EmotionAnalyzer
from .confidence import ConfidenceScorer

class IntelligentPipeline:
    """Intelligent transcription pipeline with quality-based model selection."""

    MODEL_SELECTION_RULES = {
        'high_quality': 'small',
        'medium_quality': 'base',
        'low_quality': 'medium',
    }

    def __init__(
        self,
        whisper_engine: WhisperEngine,
        emotion_analyzer: Optional[EmotionAnalyzer] = None,
    ):
        self.whisper = whisper_engine
        self.emotion = emotion_analyzer
        self.confidence_scorer = ConfidenceScorer()
        self.quality_analyzer = AudioQualityAnalyzer()

    def select_model(self, audio_path: Path) -> str:
        """
        Select Whisper model based on audio quality.

        Args:
            audio_path: Path to audio file

        Returns:
            Model size string
        """
        quality_metrics = self.quality_analyzer.analyze(audio_path)

        if quality_metrics['snr'] > 20:
            return 'small'
        elif quality_metrics['snr'] > 10:
            return 'base'
        else:
            return 'medium'

    def transcribe(
        self,
        audio_path: Path,
        enable_prosody: bool = True,
        enable_diarization: bool = True,
        enable_ato_markers: bool = True,
    ) -> Dict[str, Any]:
        """
        Full transcription pipeline.

        Returns:
            Complete transcription result with all features
        """
        # Quality analysis and model selection
        model_size = self.select_model(audio_path)
        self.whisper.model_size = model_size

        # Whisper transcription
        segments = self.whisper.transcribe_segments(audio_path)

        # Confidence scoring
        for seg in segments:
            self.confidence_scorer.annotate_segment(seg)

        # Emotion analysis (if enabled)
        if self.emotion:
            for seg in segments:
                sentiment = self.emotion.analyze_text_sentiment(seg['text'])
                seg['emotion'] = sentiment

        # Prosody, diarization, ATO markers integrated here
        # (calls to svt_core.audio.prosody, svt_core.audio.diarization, etc.)

        return {
            'segments': segments,
            'model_used': model_size,
            'metadata': {
                'audio_path': str(audio_path),
                # ... other metadata ...
            },
        }
```

**Commit:** `refactor: extract IntelligentPipeline to svt_core/transcription/intelligent_pipeline.py`

##### 5.6 Extract Segment Processor

**Erstelle svt_core/transcription/segment_processor.py:**

```python
"""
Segment Processing Utilities

Timestamp parsing, speaker alignment, prosody alignment.
"""

from typing import List, Dict, Any

class SegmentProcessor:
    """Utilities for segment processing."""

    def align_speakers(
        self,
        transcription_segments: List[Dict[str, Any]],
        diarization_segments: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Align speaker labels with transcription segments.

        Args:
            transcription_segments: Whisper segments
            diarization_segments: Speaker diarization segments

        Returns:
            Segments with speaker labels added
        """
        # ... existing speaker alignment logic ...

    def align_prosody(
        self,
        segments: List[Dict[str, Any]],
        prosody_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Align prosody features with segments.

        Returns:
            Segments with prosody data added
        """
        # ... existing prosody alignment logic ...
```

**Commit:** `refactor: extract SegmentProcessor to svt_core/transcription/segment_processor.py`

##### 5.7 Update svt.py to Use New TranscriptionEngine

**OLD:**
```python
import auto_transcriber_v4_emotion as v4

def run_transcription(self):
    # ... setup ...
    v4.transcribe_file(audio_path, options)
```

**NEW:**
```python
from svt_core.transcription import TranscriptionEngine

def run_transcription(self):
    engine = TranscriptionEngine(
        model_size="small",
        enable_emotion=self.emotion_var.get(),
    )

    result = engine.transcribe(
        audio_path,
        enable_prosody=self.prosody_var.get(),
        enable_diarization=self.diarization_var.get(),
        enable_ato_markers=self.ato_var.get(),
    )
```

**Commit:** `refactor: update svt.py to use svt_core.transcription.TranscriptionEngine`

##### 5.8 Delete auto_transcriber_v4_emotion.py

**Nach vollständiger Migration und Test-Verifikation:**

```bash
git rm auto_transcriber_v4_emotion.py
```

**Commit:** `chore: remove legacy auto_transcriber_v4_emotion.py (1,309 LOC migrated)`

#### Phase 5 Deliverables
- ✅ svt_core/transcription/ mit 6 Modulen
- ✅ 1.309 LOC in logische Komponenten aufgeteilt
- ✅ Whisper-Engine, Emotion, Confidence, Pipeline getrennt
- ✅ Backward-compatible TranscriptionEngine facade
- ✅ Alle Tests grün

**Metrics:**
- Root-LOC: 10.390 → 9.081 (-13%)
- svt_core LOC: 7.177 → 8.486 (+18%)
- Modularität: 41% → 48%
- **auto_transcriber_v4_emotion.py eliminiert** 🎉

---

### **PHASE 6: LLM Migration**
**Timeline:** Woche 11 (5 Arbeitstage)
**Priorität:** LOW
**Risiko:** LOW

#### Ziele
- Legacy LLM APIs durch svt_core/llm_provider/ ersetzen
- psychoanalysis_api.py und psychoanalysis_api_ollama.py entfernen (419 LOC)
- psychoanalysis_pipeline.py aktualisieren

#### Tasks

##### 6.1 Update psychoanalysis_pipeline.py

**OLD:**
```python
from psychoanalysis_api import PsychoanalysisAPI
from psychoanalysis_api_ollama import OllamaPsychoanalysisAPI

if provider == "openai":
    api = PsychoanalysisAPI()
elif provider == "ollama":
    api = OllamaPsychoanalysisAPI()

result = api.analyze(transcript)
```

**NEW:**
```python
from svt_core.llm_provider import build_default_manager

manager = build_default_manager()
provider = manager.get_provider()

result = provider.generate(
    prompt=f"Analyze this transcript:\n\n{transcript}",
    system_prompt="You are a psychoanalysis assistant.",
)
```

**Commit:** `refactor: migrate psychoanalysis_pipeline to use svt_core.llm_provider`

##### 6.2 Update dashboard_generator.py

**Similar migration to use svt_core.llm_provider**

**Commit:** `refactor: migrate dashboard_generator to use svt_core.llm_provider`

##### 6.3 Delete Legacy LLM APIs

```bash
git rm psychoanalysis_api.py
git rm psychoanalysis_api_ollama.py
```

**Commit:** `chore: remove legacy LLM APIs (419 LOC migrated to svt_core)`

##### 6.4 Update Documentation

**Update CLAUDE.md:**
- Remove references to legacy APIs
- Document svt_core/llm_provider/ usage
- Update architecture diagrams

**Commit:** `docs: update CLAUDE.md for LLM provider migration`

#### Phase 6 Deliverables
- ✅ psychoanalysis_pipeline uses svt_core/llm_provider
- ✅ 419 LOC legacy APIs deleted
- ✅ Unified LLM abstraction across codebase
- ✅ Documentation updated

**Metrics:**
- Root-LOC: 9.081 → 8.662 (-5%)
- svt_core LOC: 8.486 → 8.486 (0%, already migrated)
- Modularität: 48% → 50%
- **Code-Duplikation eliminiert** 🎉

---

## 📈 Final Metrics (Nach Phase 6)

### Code-Verteilung

| Location | Before | After | Change |
|----------|--------|-------|--------|
| Root LOC | 17.947 | 8.662 | -52% 🎉 |
| svt_core LOC | 797 | 8.486 | +965% 🎉 |
| tests/ LOC | 2.800 | 2.800 | 0% (moved from root) |
| audit/ LOC | 500 | 500 | 0% |
| **Total LOC** | **22.044** | **20.448** | **-7%** (dead code deleted) |

### File-Verteilung

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Root Python files | 65 | 25 | -62% 🎉 |
| svt_core files | 18 | 45 | +150% 🎉 |
| tests files | 60 | 60 | 0% |
| **Total files** | **143** | **130** | **-9%** |

### Code-Organisation

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Modularität (LOC in svt_core/) | 7% | 50% | +43pp 🎉 |
| Monolithic files >500 LOC | 10 | 2 | -80% 🎉 |
| Duplicate code (LLM APIs) | 419 LOC | 0 | -100% 🎉 |
| Dead code | 814 LOC | 0 | -100% 🎉 |
| Root clutter (files) | 65 | 25 | -62% 🎉 |

### Modularität nach Komponenten

| Komponente | LOC | Dateien | Status |
|------------|-----|---------|--------|
| svt_core/audio/ | 1.448 | 5 | ✅ Migriert |
| svt_core/transcription/ | 1.500 | 6 | ✅ Migriert |
| svt_core/output/ | 3.300 | 10 | ✅ Migriert |
| svt_core/semantic/ | 1.178 | 5 | ✅ Migriert |
| svt_core/memory/ | 709 | 3 | ✅ Migriert |
| svt_core/llm_provider/ | 330 | 6 | ✅ Bereits vorhanden |
| svt_core/config/ | 100 | 2 | ✅ Bereits vorhanden |
| svt_core/ui/ | 450 | 3 | ✅ Migriert |
| svt_core/tools/ | 400 | 4 | ✅ Neu erstellt |
| svt_core/ (root) | 73 | 1 | ✅ Bereits vorhanden |

---

## 🎯 Erfolgskriterien

### Technische Kriterien

- ✅ **85%+ Code in modularer Struktur** (Target: 50%, erreicht)
- ✅ **<30 Python-Dateien im Root** (Target: 25, erreicht)
- ✅ **Monolithische Dateien reduziert** (10 → 2, -80%)
- ✅ **Dead Code eliminiert** (814 LOC → 0)
- ✅ **Code-Duplikation eliminiert** (419 LOC LLM APIs)
- ✅ **Alle Tests grün** (60 Test-Dateien)
- ✅ **Backward Compatibility** (via Facades und Shims)

### Wartbarkeits-Kriterien

- ✅ **Single Responsibility Principle** (jedes Modul eine Aufgabe)
- ✅ **Dependency Injection** (Komponenten entkoppelt)
- ✅ **Testbarkeit** (Komponenten isoliert testbar)
- ✅ **Dokumentation** (Module dokumentiert, Migration Guide)

### Nutzer-Kriterien

- ✅ **Keine Breaking Changes** (svt.py funktioniert weiterhin)
- ✅ **Performance unverändert** (keine Regressionen)
- ✅ **Funktionalität unverändert** (alle Features intakt)

---

## 🔄 Rollback-Strategie

Falls kritische Probleme auftreten:

### Phase 1-4: Git Revert
```bash
git revert <commit-hash>
```

### Phase 5 (Transcription): Feature Flag
```python
# svt.py
USE_LEGACY_V4 = os.getenv("SVT_USE_LEGACY_V4", "false").lower() == "true"

if USE_LEGACY_V4:
    import auto_transcriber_v4_emotion as v4
else:
    from svt_core.transcription import TranscriptionEngine
```

### Kompletter Rollback
```bash
git checkout <commit-before-refactoring>
```

---

## 📚 Referenz-Dokumentation

### Zu erstellende Dokumente

1. **MIGRATION_GUIDE.md** (Phase 1)
   - Import-Änderungen
   - Entry-Point-Änderungen
   - Testing-Änderungen

2. **ARCHITECTURE_REFACTORED.md** (Phase 6)
   - Neue Modulstruktur
   - Komponenten-Diagramme
   - Dependency-Graphen

3. **DEVELOPER_GUIDE.md** (Phase 6)
   - Wo neue Features hinzufügen
   - Testing-Best-Practices
   - Modul-Konventionen

### Zu aktualisierende Dokumente

1. **CLAUDE.md**
   - Import-Pfade aktualisieren
   - Architektur-Sektion updaten
   - Neue Modul-Beschreibungen

2. **README.md**
   - Entry-Point-Änderungen
   - Installations-Anleitung (falls nötig)

3. **VERSION_STATUS.md**
   - Refactoring-Status tracken
   - Modul-Übersicht

---

## 🛠️ Tools und Scripts

### Migration Helper Scripts

**scripts/check_imports.py:**
```python
"""Check for legacy imports in codebase."""
import subprocess
import sys

LEGACY_IMPORTS = [
    "import auto_transcriber_v4_emotion",
    "from audio_quality_analyzer import",
    "from prosody_extractor import",
    "from speaker_diarizer import",
    "from output_formatter import",
    "from psychoanalysis_api import",
]

def check_imports():
    errors = []
    for pattern in LEGACY_IMPORTS:
        result = subprocess.run(
            ["grep", "-r", pattern, ".", "--include=*.py"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            errors.append(f"Found legacy import: {pattern}\n{result.stdout}")

    if errors:
        print("❌ Legacy imports detected:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("✅ No legacy imports found")

if __name__ == "__main__":
    check_imports()
```

**scripts/validate_modules.py:**
```python
"""Validate module structure."""
from pathlib import Path

REQUIRED_MODULES = [
    "svt_core/audio/__init__.py",
    "svt_core/transcription/__init__.py",
    "svt_core/output/__init__.py",
    "svt_core/semantic/__init__.py",
    "svt_core/memory/__init__.py",
    "svt_core/llm_provider/__init__.py",
]

def validate():
    missing = []
    for module in REQUIRED_MODULES:
        if not Path(module).exists():
            missing.append(module)

    if missing:
        print("❌ Missing modules:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    else:
        print("✅ All modules present")

if __name__ == "__main__":
    validate()
```

### CI/CD Integration

**.github/workflows/refactoring-checks.yml:**
```yaml
name: Refactoring Checks

on: [push, pull_request]

jobs:
  validate-structure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate module structure
        run: python3 scripts/validate_modules.py

      - name: Check for legacy imports
        run: python3 scripts/check_imports.py

      - name: Run all tests
        run: pytest tests/ -v
```

---

## ⚠️ Risiken und Mitigationen

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| **Breaking Changes** | MEDIUM | HIGH | Backward compatibility facades, comprehensive testing |
| **Test-Regressionen** | MEDIUM | HIGH | Run full test suite after each phase |
| **Performance-Regressionen** | LOW | MEDIUM | Benchmark before/after, profiling |
| **Import-Konflikte** | MEDIUM | LOW | check_imports.py script, CI/CD checks |
| **Dokumentation veraltet** | HIGH | LOW | Update docs with each phase commit |
| **Migration zu komplex** | LOW | HIGH | Phased approach, rollback strategy |

---

## 🎓 Lessons Learned (Post-Refactoring)

### Was gut funktioniert hat
- _Wird nach Abschluss ausgefüllt_

### Was herausfordernd war
- _Wird nach Abschluss ausgefüllt_

### Was verbessert werden kann
- _Wird nach Abschluss ausgefüllt_

---

## ✅ Checklisten

### Phase 1 Checklist
- [ ] Dead code deleted (814 LOC)
- [ ] Test files moved to tests/ (17 files)
- [ ] Semantic GUI integrated into svt.py
- [ ] start_super_semantic.py deprecated
- [ ] MIGRATION_GUIDE.md created
- [ ] All tests green
- [ ] Commit messages descriptive

### Phase 2 Checklist
- [ ] svt_core/audio/ created
- [ ] AudioQualityAnalyzer migrated
- [ ] AudioPreprocessor migrated
- [ ] ProsodyExtractor migrated
- [ ] SpeakerDiarizer migrated
- [ ] auto_transcriber_v4 imports updated
- [ ] Backward compatibility shims created
- [ ] All audio tests green

### Phase 3 Checklist
- [ ] svt_core/output/ created
- [ ] SpeakerConfig extracted
- [ ] MarkdownFormatter extracted
- [ ] JSONSidecarFormatter extracted
- [ ] CSVExporter extracted
- [ ] HTMLFormatter migrated
- [ ] PDFGenerator migrated
- [ ] DashboardGenerator migrated
- [ ] OutputFormatter facade created
- [ ] Legacy output_formatter.py deleted
- [ ] All output tests green

### Phase 4 Checklist
- [ ] svt_core/semantic/ created
- [ ] SuperSemanticProcessor migrated
- [ ] ATOMarkerIntegration migrated
- [ ] CorrelationEngine migrated
- [ ] svt_core/memory/ created
- [ ] SpeakerDatabase migrated
- [ ] PsychoanalysisCache migrated
- [ ] All imports updated
- [ ] All tests green

### Phase 5 Checklist
- [ ] svt_core/transcription/ created
- [ ] WhisperEngine extracted
- [ ] EmotionAnalyzer extracted
- [ ] ConfidenceScorer extracted
- [ ] IntelligentPipeline extracted
- [ ] SegmentProcessor extracted
- [ ] TranscriptionEngine facade created
- [ ] svt.py updated to use new engine
- [ ] auto_transcriber_v4_emotion.py deleted
- [ ] All transcription tests green
- [ ] E2E tests green

### Phase 6 Checklist
- [ ] psychoanalysis_pipeline updated
- [ ] dashboard_generator updated
- [ ] Legacy LLM APIs deleted (419 LOC)
- [ ] Documentation updated
- [ ] All tests green

### Final Checklist
- [ ] ARCHITECTURE_REFACTORED.md created
- [ ] DEVELOPER_GUIDE.md created
- [ ] CLAUDE.md updated
- [ ] VERSION_STATUS.md updated
- [ ] README.md updated
- [ ] All 60 test files green
- [ ] CI/CD pipeline green
- [ ] Performance benchmarks passed
- [ ] User acceptance testing passed

---

## 📞 Kontakt und Support

Bei Fragen oder Problemen während des Refactorings:

1. **Check Documentation:** MIGRATION_GUIDE.md, this file
2. **Run Validation:** `python3 scripts/validate_modules.py`
3. **Check Tests:** `pytest tests/ -v`
4. **Review Commits:** `git log --oneline`

---

**End of Refactoring Plan**

**Status:** DRAFT - Ready for implementation
**Next Step:** Begin Phase 1 (Immediate Cleanup)
