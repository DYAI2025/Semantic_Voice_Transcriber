# PROJEKT.md - Detaillierte Feature-Analyse

**Analysedatum:** 2025-11-20
**Commit:** a3568d4
**Analysemethode:** Iterative manuelle Feature-Checks + Code-Inspektion

---

## 📊 Executive Summary

### Gesamtstatus: ⚠️ **Teilweise funktionsfähig**

- **4/7 Features** vollständig verfügbar (57%)
- **2/7 Features** haben fehlende Dependencies (29%)
- **1/7 Features** teilweise verfügbar (14%)

### Kritische Findings

1. ❌ **BLOCKER**: Prosody Extraction nicht verfügbar (`librosa` fehlt)
2. ❌ **BLOCKER**: Speaker Diarization nicht verfügbar (`torch` fehlt)
3. ⚠️ **WARNING**: Memory System hat keine SQLite DB
4. ⚠️ **WARNING**: VP_ATO Marker in Unterverzeichnis (nicht im Root)
5. ⚠️ **INFO**: PDF-Export deaktiviert (`weasyprint` fehlt)

---

## 🔍 Detaillierte Feature-Analyse

### 1. Prosody Extraction (❌ NICHT VERFÜGBAR)

**Status:** ❌ Missing Dependencies
**Priorität:** 🔴 **KRITISCH** - Kern-Feature

#### Aktueller Zustand
```
ERROR: No module named 'librosa'
```

#### Erwartete Module
- `prosody_extractor.py` ✅ Vorhanden
- `prosody_analyzer.py` ✅ Vorhanden
- `librosa` ❌ Fehlt
- `parselmouth` ❌ Fehlt
- `soundfile` ❌ Fehlt

#### Abhängigkeiten
```python
# requirements.txt
librosa>=0.9.0
soundfile>=0.10.0
praat-parselmouth>=0.4.0
scipy>=1.9.0
```

#### Features betroffen
- ❌ "Big 4" Prosody-Features (Tempo, Pitch, Energy, Pauses)
- ❌ Baseline-Berechnung
- ❌ Deviation Detection
- ❌ Prosody-Marker in Transkripten
- ❌ Psychoanalysis Dashboard (benötigt `.prosody.json`)

#### Impact
- **Functional**: Keine Prosody-Analyse möglich
- **Documentation**: CLAUDE.md behauptet "✅ Complete" → **FALSCH**
- **Tests**: 6+ Prosody-Tests können nicht laufen
- **Users**: One-Click Workflow funktioniert nicht vollständig

#### Lösungsansatz
```bash
pip install librosa soundfile praat-parselmouth scipy
```

**Geschätzte Zeit:** 5-10 Minuten (Installation + Smoke Test)

---

### 2. Speaker Diarization (❌ NICHT VERFÜGBAR)

**Status:** ❌ Missing Dependencies
**Priorität:** 🟠 **HOCH** - Wichtiges Feature

#### Aktueller Zustand
```
ERROR: No module named 'torch'
```

#### Erwartete Module
- `speaker_diarizer.py` ✅ Vorhanden
- `svt_core/audio/diarization_cpu.py` ✅ Vorhanden (CPU Fallback)
- `torch` ❌ Fehlt
- `pyannote.audio` ❌ Wahrscheinlich fehlt

#### Abhängigkeiten
```python
# requirements.txt
torch>=2.0.0
pyannote.audio>=2.1.0
```

#### Features betroffen
- ❌ Automatische Sprechertrennung
- ❌ Speaker A, B, C Labels
- ❌ Overlapped Speech Detection (OSD)
- ❌ Multi-Speaker Transkripte

#### Impact
- **Functional**: Nur Single-Speaker möglich
- **Documentation**: CLAUDE.md behauptet "✅ Complete" → **FALSCH**
- **Tests**: Diarization-Tests können nicht laufen
- **Users**: Therapeutische Gespräche (2+ Sprecher) nicht analysierbar

#### Zusätzliche Anforderungen
- Hugging Face Token für `pyannote.audio` Models
- `.env` Datei mit `HF_TOKEN=...`

#### Lösungsansatz
```bash
pip install torch pyannote.audio
# + HF Token Setup
```

**Geschätzte Zeit:** 10-15 Minuten (Installation + HF Setup + Smoke Test)

---

### 3. Output Formatter (✅ VERFÜGBAR)

**Status:** ✅ Fully Available
**Priorität:** 🟢 **OK**

#### Aktueller Zustand
```
✅ Multi-format export ready
✅ SpeakerConfig OK
⚠️ PDF support: False (weasyprint fehlt)
```

#### Verfügbare Formate
1. ✅ **Markdown** (.md) - Therapeutisches Format mit Metadaten-Sidebar
2. ✅ **JSON** (.prosody.json) - Strukturierte Prosody-Daten
3. ✅ **HTML** (.html) - Color-coded Sprecher
4. ✅ **Enhanced HTML** (_enhanced.html) - Therapeutisches Layout
5. ❌ **PDF** (.pdf) - Deaktiviert (weasyprint fehlt)
6. ✅ **CSV** (.csv) - Tabellarische Daten

#### Speaker Modes
- ✅ `MODE_ANONYMOUS`: "Therapeut", "Patient"
- ✅ `MODE_LETTERS`: "Speaker A", "Speaker B"
- ✅ `MODE_NAMES`: Echte Namen
- ✅ `MODE_CUSTOM`: Custom Mapping

#### Fehlende Optimierung
- PDF-Export optional, aber gut zu haben
- `weasyprint` Installation empfohlen

#### Lösungsansatz
```bash
pip install weasyprint
```

**Geschätzte Zeit:** 2-3 Minuten

---

### 4. Memory System (✅ VERFÜGBAR, ⚠️ INKOMPLETT)

**Status:** ✅ Partially Available
**Priorität:** 🟡 **MEDIUM**

#### Aktueller Zustand
```
✅ 5 YAML profiles vorhanden
❌ speaker_profiles.db NICHT vorhanden
```

#### Vorhandene Profile
1. `Memory/Unknown.yaml`
2. 4 weitere Speaker-Profile

#### Strukturanalyse
```yaml
# Typisches Profil
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8 Hz
  tempo_profile:
    mean_bpm: 118.5
  energy_profile:
    mean_energy: 0.045

statistics:
  avg_sentence_length: 15.3
  sentiment: {positive: 42, negative: 8}

topics: {technology: 15, business: 8}
characteristics: [technisch_orientiert, bedächtig]
interactions: [...]  # Last 50
```

#### Fehlende Komponenten
- ❌ `speaker_profiles.db` (SQLite) - Dokumentiert, aber nicht vorhanden
- ⚠️ Unklar ob YAML-only Modus oder DB wird bei Nutzung erstellt

#### Funktionalität
- ✅ YAML Loading funktioniert
- ✅ Profile Updates funktionieren (vermutlich)
- ❌ SQLite-Backup unklar

#### Lösungsansatz
1. Prüfen ob DB bei erster Transkription erstellt wird
2. Oder: `initialize_person.py` manuell ausführen
3. Dokumentation aktualisieren

**Geschätzte Zeit:** 5 Minuten (Testing)

---

### 5. LLM Provider System (✅ VERFÜGBAR)

**Status:** ✅ Fully Available
**Priorität:** 🟢 **OK**

#### Aktueller Zustand
```
✅ Provider abstraction layer OK
✅ Base classes: LLMProvider, LLMResponse
✅ Factory pattern: build_default_manager()
✅ LocalOllamaProvider importable
```

#### Verfügbare Provider
1. ✅ **Ollama** (`LocalOllamaProvider`) - FREE local LLM
2. ✅ **OpenAI** (via factory) - GPT-4 Turbo
3. ✅ **Dummy** (Testing) - Placeholder

#### Architektur
```
svt_core/llm_provider/
├── base.py           ✅ LLMProvider interface
├── factory.py        ✅ build_default_manager()
├── manager.py        ✅ Session management
├── local_ollama.py   ✅ FREE local provider
├── providers/        ✅ Cloud providers (OpenAI, etc.)
├── config/
│   └── settings.py   ✅ ProviderProfile persistence
└── ui/
    └── provider_dialog.py  ✅ GUI configuration
```

#### Integration
- ✅ GUI: "Einstellungen → Provider-Einstellungen"
- ✅ Config: `config/psychoanalysis_config.yaml`
- ✅ Health Check: `svt_core/health_check.py`

#### Status
**Vollständig funktionsfähig** - Keine Probleme identifiziert

---

### 6. ATO Marker Integration (✅ VERFÜGBAR)

**Status:** ✅ Fully Available
**Priorität:** 🟢 **OK**

#### Aktueller Zustand
```
✅ ATOMarkerIntegration importable
✅ 18 ATO markers (root)
✅ 3 SEM markers (root)
✅ 16 VP_ATO markers (VP_ATO/psychoanalytic/)
```

#### Marker-Verteilung

**Root-Level ATO (18 Dateien):**
```
ATO_ADHD_DISORGANIZED_THOUGHTS.yaml
ATO_ANXIETY_HESITATION.yaml
ATO_BLAME_SHIFT.yaml
ATO_CLARIFICATION_REQUEST.yaml
ATO_COLLABORATIVE_FRAMING.yaml
ATO_CONCEPT_ELABORATION.yaml
ATO_DISCLOSURE_STATEMENT.yaml
ATO_DISGUST.yaml
ATO_EMO_HIGH_VALENCE_MARKER.yaml
ATO_EMO_LOW_VALENCE_MARKER.yaml
ATO_EPISTEMIC_HEDGE.yaml
ATO_EXPRESSIVE_APHASIA.yaml
ATO_FEAR.yaml
ATO_META_EPISTEMIC_STANCE.yaml
ATO_THEORETICAL_FRAMING.yaml
... (3 weitere)
```

**Root-Level SEM (3 Dateien):**
```
SEM_COLLABORATIVE_ALLIANCE.yaml
SEM_DIDACTIC_ELABORATION.yaml
SEM_EPISTEMICALLY_GROUNDED_DISCOURSE.yaml
```

**VP_ATO/psychoanalytic/ (16 Dateien):**
```
Psychoanalytisch orientierte Marker
(in Unterverzeichnis, nicht direkt geladen?)
```

#### LeanDeep 3.5 Schema-Konformität
```yaml
id: ATO_MARKER_NAME
frame:
  signal: "regex pattern"
  concept: "What it represents"
  pragmatics: "How it's used"
  narrative: "Why it matters"
examples: [5+ required]
pattern: "detection logic"
```

#### Integration Points
- ✅ `ato_marker_integration.py` - Hauptintegration
- ✅ `super_semantic_processor.py` - Semantic Engine
- ⚠️ `output_formatter.py` - Marker in Transkripte (unklar ob aktiv)

#### Offene Fragen
1. Werden VP_ATO/psychoanalytic/ Marker geladen?
2. Wie funktioniert ATO→SEM→CLU→MEMA Hierarchie?
3. Prosody-Trigger-Integration (Phase 2d)?

**Geschätzte Zeit für Klärung:** 10 Minuten

---

### 7. Health Check System (✅ VERFÜGBAR)

**Status:** ✅ Fully Available
**Priorität:** 🟢 **OK**

#### Aktueller Zustand
```
✅ svt_core/health_check.py importable
✅ System monitoring OK
```

#### Funktionen
- ✅ Real-time status monitoring
- ✅ Provider health verification
- ✅ Status levels: ok (green), warn (yellow), error (red)
- ✅ GUI integration (top-right indicator)
- ✅ Automatic checks on startup

#### Implementierung
```python
from svt_core import health_check

# Health check verfügbar für:
- Ollama connectivity
- OpenAI API key validation
- System resources
- Provider availability
```

**Vollständig funktionsfähig** - Keine Probleme identifiziert

---

## 📈 Zusätzliche Metriken

### Codebase-Statistiken (Verifiziert)

| Kategorie | Count | Status |
|-----------|-------|--------|
| Python files (root) | 64 | ✅ |
| Test files (total) | 58 | ✅ |
| Test files (tests/) | 42 | ✅ |
| Test files (root) | 16 | ✅ |
| Markdown docs | 57 | ✅ |
| ATO markers (root) | 18 | ✅ |
| SEM markers (root) | 3 | ✅ |
| VP_ATO markers | 16 | ✅ |
| **Total markers** | **37** | ✅ |

### Dependency-Status

| Package | Required | Installed | Status |
|---------|----------|-----------|--------|
| numpy | ✅ | ✅ | ✅ |
| jsonschema | ✅ | ❓ | ⚠️ |
| librosa | ✅ | ❌ | ❌ |
| soundfile | ✅ | ❌ | ❌ |
| parselmouth | ✅ | ❌ | ❌ |
| torch | ✅ | ❌ | ❌ |
| pyannote.audio | ✅ | ❌ | ❌ |
| weasyprint | Optional | ❌ | ⚠️ |
| openai | ✅ | ❓ | ⚠️ |

---

## 🎯 Gaps & Issues Summary

### Kritische Gaps (BLOCKER)

1. **Prosody Dependencies Missing**
   - Impact: Kern-Feature nicht nutzbar
   - Betroffene Features: Big 4, Baselines, Psychoanalysis Dashboard
   - Fix: `pip install librosa soundfile praat-parselmouth scipy`
   - Zeit: 10 Minuten

2. **Diarization Dependencies Missing**
   - Impact: Multi-Speaker nicht nutzbar
   - Betroffene Features: Speaker A/B/C, OSD, Therapeutische Gespräche
   - Fix: `pip install torch pyannote.audio` + HF Token Setup
   - Zeit: 15 Minuten

### Wichtige Gaps (HIGH)

3. **SQLite Memory DB fehlt**
   - Impact: Backup-Mechanismus unklar
   - Betroffene Features: Memory Persistence
   - Fix: Testen ob auto-created oder manuell initialisieren
   - Zeit: 5 Minuten

4. **VP_ATO Marker nicht im Root**
   - Impact: Möglicherweise nicht geladen
   - Betroffene Features: Psychoanalytische Marker
   - Fix: Prüfen ob Unterverzeichnis automatisch geladen wird
   - Zeit: 5 Minuten

### Optionale Verbesserungen (MEDIUM)

5. **PDF Export deaktiviert**
   - Impact: Ein Ausgabeformat fehlt
   - Betroffene Features: Professional Export
   - Fix: `pip install weasyprint`
   - Zeit: 3 Minuten

6. **Dokumentation nicht synchron**
   - Impact: User-Verwirrung
   - Betroffene Docs: CLAUDE.md, README.md, VERSION_STATUS.md
   - Fix: "✅ Complete" → "⚠️ Dependencies required"
   - Zeit: 20 Minuten

---

## ⚡ Quick Wins (Top 5)

### 1. Install Core Dependencies (HÖCHSTE PRIORITÄT)
```bash
pip install librosa soundfile praat-parselmouth scipy torch pyannote.audio
```
**Impact:** ✅ Prosody + ✅ Diarization
**Zeit:** 15 Minuten
**Value:** 🔴🔴🔴🔴🔴 (5/5)

### 2. Install Optional Dependencies
```bash
pip install weasyprint jsonschema
```
**Impact:** ✅ PDF Export + ✅ Audit CLI
**Zeit:** 5 Minuten
**Value:** 🟠🟠🟠 (3/5)

### 3. Test Memory DB Creation
```bash
python3 initialize_person.py --name "TestSpeaker"
# Check if speaker_profiles.db is created
```
**Impact:** ✅ Memory System vollständig
**Zeit:** 5 Minuten
**Value:** 🟡🟡 (2/5)

### 4. Verify VP_ATO Loading
```python
from ato_marker_integration import ATOMarkerIntegration
ato = ATOMarkerIntegration()
# Check if VP_ATO/psychoanalytic/ markers are loaded
```
**Impact:** ✅ Alle 37 Marker verfügbar
**Zeit:** 5 Minuten
**Value:** 🟡🟡 (2/5)

### 5. Update Dokumentation
- CLAUDE.md: Dependencies-Sektion hinzufügen
- README.md: Installation Prerequisites
- VERSION_STATUS.md: Realistische Status-Angaben
**Impact:** ✅ User-Experience
**Zeit:** 30 Minuten
**Value:** 🟡🟡🟡 (3/5)

---

## 🚀 Empfohlenes Nächstes Inkrement

### Inkrement 1: "Dependency Resolution & Core Features" (30 Minuten)

**Ziel:** Prosody + Diarization vollständig verfügbar machen

#### Schritte:
1. ✅ Dependencies installieren (15 min)
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_emotion.txt
   ```

2. ✅ HF Token Setup (5 min)
   ```bash
   # Create .env file
   echo "HF_TOKEN=hf_YOUR_TOKEN" > .env
   ```

3. ✅ Smoke Tests ausführen (5 min)
   ```bash
   python3 test_prosody_analyzer.py
   python3 test_prosody_pipeline.py
   python3 -c "from speaker_diarizer import SpeakerDiarizer; print('OK')"
   ```

4. ✅ Feature Audit CLI ausführen (5 min)
   ```bash
   python3 -m audit.cli
   ```

#### Erfolgskriterien:
- [ ] Prosody Extraction: ✅ Available
- [ ] Speaker Diarization: ✅ Available
- [ ] Audit CLI: ✅ Läuft ohne Fehler
- [ ] Mindestens 6/7 Features "available"

#### Deliverables:
- Alle Core Dependencies installiert
- Smoke Tests bestanden
- Audit Report generiert
- PROJEKT.md aktualisiert mit Audit-Ergebnissen

---

## 📋 Follow-Up Inkremente

### Inkrement 2: "Documentation Sync" (30 Minuten)
- CLAUDE.md: Dependencies Warning hinzufügen
- README.md: Installation Prerequisites
- VERSION_STATUS.md: Realistische Status
- Verification Banners aktualisieren

### Inkrement 3: "Memory & Marker Verification" (20 Minuten)
- SQLite DB testen
- VP_ATO Loading verifizieren
- ATO→SEM Hierarchie dokumentieren

### Inkrement 4: "Integration Tests" (30 Minuten)
- End-to-End Test: Audio → Transkript mit Prosody + Diarization
- Psychoanalysis Dashboard Test mit Ollama
- Full Audit Report generieren

---

## 📝 Notizen

### Positive Findings
- ✅ LLM Provider System gut architektiert und voll funktionsfähig
- ✅ Output Formatter robust (5/6 Formate ohne Dependencies)
- ✅ Health Check System gut integriert
- ✅ 37 Marker-Dateien vorhanden und strukturiert
- ✅ 58 Test-Dateien vorhanden (gute Coverage-Basis)

### Bedenken
- ❌ Dokumentation behauptet "Phase 2c Complete", aber 2 Kern-Features fehlen Dependencies
- ⚠️ Unklar ob VP_ATO/psychoanalytic/ Marker automatisch geladen werden
- ⚠️ SQLite DB nicht vorhanden (dokumentiert aber nicht implementiert?)
- ⚠️ Tests können nicht laufen ohne Dependencies

### Empfehlungen
1. **Sofort**: Dependencies installieren (Quick Win #1)
2. **Dann**: Dokumentation realistisch anpassen
3. **Danach**: End-to-End Tests zur Verifikation
4. **Langfristig**: CI/CD Pipeline für Dependency-Checks

---

**Erstellt von:** Claude Code Assistant
**Nächster Review:** Nach Inkrement 1
**Status:** 🔄 In Progress
