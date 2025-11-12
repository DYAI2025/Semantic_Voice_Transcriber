# Nächste Schritte & Entwicklungsempfehlungen
# Semantic Voice Transcriber (SVT)

**Stand**: 2025-11-01
**Aktueller Status**: Phase 2b Complete ✅
**Nächste Phase**: Phase 2c - ATO-Marker-Integration

---

## 🎯 Executive Summary

Das SVT-System ist **produktionsreif** für:
- ✅ Basis-Transkription mit Whisper (5 Formate)
- ✅ Prosody-Analyse (Big 4 Features)
- ✅ Emotions-Analyse (7 Kategorien)
- ✅ Speaker Diarization (Mehrsprechererkennung)
- ✅ Multi-Format Export (MD, JSON, HTML, PDF, CSV)
- ✅ Memory-basiertes Speaker Learning

**Empfohlene nächste Schritte**: Phase 2c - ATO-Marker-Integration für therapeutische Wendepunkt-Erkennung.

---

## 🔥 Priorität 1: Phase 2c - ATO-Marker-Integration

### Warum jetzt?

- **Therapeutischer Nutzen**: Direkter Mehrwert für Therapeuten
- **Auf bestehendem System aufbauend**: Prosody-System ist fertig
- **Klarer Use-Case**: Wendepunkt-Erkennung in Therapiegesprächen
- **Marker-System existiert**: VP_ATO/*.yaml Dateien sind vorhanden

### Was ist zu tun?

#### 1. VP_ATO Marker Loading (1 Woche)

**Ziel**: YAML-Dateien aus `VP_ATO/` einlesen und in System integrieren

**Tasks**:
```python
# Neues Modul: ato_marker_loader.py

class ATOMarkerLoader:
    def __init__(self, marker_dir='VP_ATO/'):
        self.marker_dir = marker_dir
        self.markers = {}

    def load_all_markers(self):
        """Lädt alle ATO-Marker aus VP_ATO/*.yaml"""
        # Implementierung

    def get_markers_for_prosody(self, prosody_marker):
        """Gibt passende ATO-Marker für Prosody-Marker zurück"""
        # TEMPO↑ → ['ATO_ACCELERATION', 'ATO_URGENCY']
        # PITCH↑ → ['ATO_EXCITEMENT', 'ATO_TENSION']
        # ENERGY↓ → ['ATO_EXHAUSTION', 'ATO_RESIGNATION']
        # PAUSE → ['ATO_REFLECTION', 'ATO_HESITATION']
```

**Integration Points**:
- `prosody_extractor.py`: Nach Marker-Detection ATO-Marker hinzufügen
- `output_formatter.py`: ATO-Marker in Markdown/JSON rendern
- `html_formatter.py`: ATO-Marker farblich hervorheben

**Erfolgskriterium**: ATO-Marker erscheinen neben Prosody-Markern in allen Outputs

#### 2. Prosody → ATO Mapping-Tabelle (3 Tage)

**Ziel**: Regelwerk erstellen, welche Prosody-Marker welche ATO-Marker triggern

**Mapping-Beispiele**:

```python
# ato_mapping.py

PROSODY_TO_ATO_MAPPING = {
    'TEMPO↑': {
        'primary': ['ATO_ACCELERATION', 'ATO_URGENCY'],
        'context_dependent': {
            'high_pitch': ['ATO_EXCITEMENT'],  # Tempo↑ + Pitch↑
            'low_energy': ['ATO_ANXIETY'],     # Tempo↑ + Energy↓
        }
    },
    'PITCH↑': {
        'primary': ['ATO_EXCITEMENT', 'ATO_TENSION'],
        'context_dependent': {
            'high_tempo': ['ATO_ENTHUSIASM'],  # Pitch↑ + Tempo↑
            'pause_after': ['ATO_SURPRISE'],   # Pitch↑ + Pause
        }
    },
    'ENERGY↓': {
        'primary': ['ATO_EXHAUSTION', 'ATO_RESIGNATION'],
        'context_dependent': {
            'slow_tempo': ['ATO_DEPRESSION'],  # Energy↓ + Tempo↓
            'low_pitch': ['ATO_SADNESS'],      # Energy↓ + Pitch↓
        }
    },
    'PAUSE': {
        'primary': ['ATO_REFLECTION', 'ATO_HESITATION'],
        'context_dependent': {
            'long_pause': ['ATO_CONFUSION'],         # >3000ms
            'after_question': ['ATO_UNCERTAINTY'],   # Context: Fragesatz
        }
    }
}
```

**Features**:
- Context-Aware Selection (kombinierte Prosody-Marker)
- Confidence Scores für ATO-Marker
- Threshold-based Triggering

**Erfolgskriterium**: Sinnvolle ATO-Marker werden basierend auf Prosody automatisch gesetzt

#### 3. 4-Tier Hierarchie (1 Woche)

**Ziel**: ATO → SEM → CLU → MEMA Hierarchie implementieren

**Struktur**:

```python
# hierarchical_marker_system.py

@dataclass
class ATOMarker:
    """Tier 1: Atomic Voice Markers"""
    type: str                    # z.B. 'ATO_ACCELERATION'
    timestamp: float
    confidence: float
    prosody_source: str          # z.B. 'TEMPO↑'

@dataclass
class SEMMarker:
    """Tier 2: Semantic Markers"""
    type: str                    # z.B. 'SEM_PRESSURE'
    ato_markers: List[ATOMarker] # Aggregiert aus ATOs
    timestamp_range: Tuple[float, float]
    confidence: float

@dataclass
class CLUMarker:
    """Tier 3: Clustered Markers"""
    type: str                    # z.B. 'CLU_CRISIS'
    sem_markers: List[SEMMarker] # Aggregiert aus SEMs
    theme: str                   # z.B. 'Beziehungskrise'
    timestamp_range: Tuple[float, float]

@dataclass
class MEMAMarker:
    """Tier 4: Meta-Narrative Markers"""
    type: str                    # z.B. 'MEMA_TURNING_POINT'
    clu_markers: List[CLUMarker] # Aggregiert aus CLUs
    narrative: str               # Textuelle Beschreibung
    therapeutic_significance: str
```

**Aggregation-Regeln**:

```python
# ATO → SEM Beispiel
if (has_marker('ATO_ACCELERATION') and
    has_marker('ATO_URGENCY') and
    has_marker('ATO_ANXIETY')):
    create_marker('SEM_PRESSURE')

# SEM → CLU Beispiel
if (count_markers('SEM_PRESSURE') >= 3 and
    count_markers('SEM_TENSION') >= 2 and
    within_time_window(120)):  # 2 Minuten
    create_marker('CLU_CRISIS')

# CLU → MEMA Beispiel
if (has_marker('CLU_CRISIS') and
    has_marker('CLU_BREAKTHROUGH') and
    sequential_order()):
    create_marker('MEMA_TURNING_POINT')
```

**Integration**:
- Neues Modul: `hierarchical_marker_processor.py`
- Integration in Pipeline nach Prosody-Extraktion
- Output in JSON mit vollständiger Hierarchie

**Erfolgskriterium**: 4-Tier Hierarchie wird in JSON-Sidecar exportiert

#### 4. Wendepunkt-Erkennung (5 Tage)

**Ziel**: Automatische Erkennung therapeutisch relevanter Wendepunkte

**Wendepunkt-Typen**:

```python
# turning_point_detector.py

class TurningPointType(Enum):
    BREAKTHROUGH = "breakthrough"       # Durchbruch
    BREAKDOWN = "breakdown"             # Zusammenbruch
    INSIGHT = "insight"                 # Einsicht
    RESISTANCE = "resistance"           # Widerstand
    ACCEPTANCE = "acceptance"           # Akzeptanz
    ESCALATION = "escalation"           # Eskalation
    DEESCALATION = "deescalation"       # Deeskalation

class TurningPointDetector:
    def detect_turning_points(self,
                             prosody_features,
                             ato_markers,
                             sem_markers,
                             clu_markers):
        """
        Erkennt Wendepunkte basierend auf:
        1. Multiple Prosody-Marker in kurzer Zeit
        2. High-Confidence ATO-Marker
        3. SEM/CLU-Marker-Kombinationen
        """
        turning_points = []

        # BREAKTHROUGH-Pattern
        # - ENERGY↑ + PITCH↑ + TEMPO↑ + ATO_EXCITEMENT + ATO_CLARITY

        # BREAKDOWN-Pattern
        # - ENERGY↓ + PITCH↓ + PAUSE + ATO_EXHAUSTION + ATO_RESIGNATION

        # INSIGHT-Pattern
        # - PAUSE + PITCH↑ + TEMPO↓ + ATO_REFLECTION + ATO_REALIZATION

        return turning_points
```

**Features**:
- Pattern-based Detection
- Confidence Scoring
- Timeline Visualization (JSON)
- Markdown-Highlighting mit 🔴/🟢 Emojis

**Output-Beispiel**:

```markdown
## Wendepunkte

### [12:34] 🟢 BREAKTHROUGH - "Durchbruch"
**Confidence**: 0.87
**Marker**: ATO_EXCITEMENT, ATO_CLARITY, SEM_REALIZATION
**Beschreibung**: Patient zeigt plötzliches Verständnis, erhöhte Energie und Klarheit in der Sprache.

### [18:45] 🔴 BREAKDOWN - "Zusammenbruch"
**Confidence**: 0.92
**Marker**: ATO_EXHAUSTION, ATO_RESIGNATION, SEM_DESPAIR
**Beschreibung**: Starker Energie- und Pitch-Abfall, lange Pausen, Anzeichen von Erschöpfung.
```

**Erfolgskriterium**: Therapeuten können Wendepunkte sofort in Transkripten identifizieren

---

## 🔧 Priorität 2: GUI-Verbesserungen (Schnelle Wins)

### Warum?

- **User Experience**: GUI ist funktional, aber verbesserungswürdig
- **Geringer Aufwand**: 1-2 Tage pro Feature
- **Hoher Impact**: Deutlich bessere Usability

### Schnelle Verbesserungen (1-2 Wochen)

#### 1. Speaker Diarization GUI-Controls (2 Tage)

**Was fehlt**:
- Checkbox in GUI für Diarization (aktuell: nur via Code)
- Min/Max Speaker Input-Felder
- HF Token Input (mit "Save" Button)

**Implementierung** (`svt.py`):

```python
# Neue GUI-Elemente
self.diarization_var = tk.BooleanVar(value=False)
self.diarization_check = tk.Checkbutton(
    self.features_frame,
    text="Speaker Diarization (erfordert HF Token)",
    variable=self.diarization_var
)

self.min_speakers_label = tk.Label(self.features_frame, text="Min Speakers:")
self.min_speakers_entry = tk.Entry(self.features_frame, width=5)
self.min_speakers_entry.insert(0, "1")

self.max_speakers_label = tk.Label(self.features_frame, text="Max Speakers:")
self.max_speakers_entry = tk.Entry(self.features_frame, width=5)
self.max_speakers_entry.insert(0, "5")

# HF Token Eingabe
self.hf_token_label = tk.Label(self.config_frame, text="HF Token:")
self.hf_token_entry = tk.Entry(self.config_frame, width=40, show="*")
self.hf_token_save_btn = tk.Button(
    self.config_frame,
    text="Save Token",
    command=self.save_hf_token
)
```

#### 2. Asynchrones Threading (2 Tage)

**Problem**: GUI freezt während langer Transkriptionen

**Lösung**: Threading mit Queue-based Progress Updates

```python
# svt.py - Async Processing

import threading
import queue

class SemanticVoiceTranscriberGUI:
    def __init__(self, root):
        # ...
        self.progress_queue = queue.Queue()
        self.check_progress()

    def start_transcription_async(self):
        """Startet Transkription in separatem Thread"""
        thread = threading.Thread(target=self._transcribe_batch)
        thread.daemon = True
        thread.start()

    def _transcribe_batch(self):
        """Läuft in separatem Thread"""
        try:
            # Transkription durchführen
            for i, file in enumerate(files):
                result = self.transcribe_file(file)

                # Progress-Update an GUI senden
                self.progress_queue.put({
                    'type': 'progress',
                    'current': i+1,
                    'total': len(files),
                    'file': file
                })
        except Exception as e:
            self.progress_queue.put({
                'type': 'error',
                'message': str(e)
            })
        finally:
            self.progress_queue.put({'type': 'complete'})

    def check_progress(self):
        """Prüft Queue und aktualisiert GUI (läuft in Main-Thread)"""
        try:
            while True:
                msg = self.progress_queue.get_nowait()
                if msg['type'] == 'progress':
                    self.update_progress(msg['current'], msg['total'])
                    self.log_message(f"Processing: {msg['file']}")
                elif msg['type'] == 'error':
                    self.log_message(f"ERROR: {msg['message']}")
                elif msg['type'] == 'complete':
                    self.log_message("✅ Batch complete!")
        except queue.Empty:
            pass

        # Re-schedule check
        self.root.after(100, self.check_progress)
```

#### 3. Advanced Settings Panel (1 Tag)

**Was fehlt**: Konfiguration von Schwellwerten und Parametern

**Implementierung**:

```python
# Neues Fenster: Advanced Settings

def open_advanced_settings(self):
    settings_window = tk.Toplevel(self.root)
    settings_window.title("Advanced Settings")

    # Prosody-Schwellwerte
    tk.Label(settings_window, text="Prosody Thresholds").pack()

    self.tempo_threshold = tk.Scale(
        settings_window,
        from_=0.05, to=0.50, resolution=0.05,
        orient=tk.HORIZONTAL,
        label="Tempo Threshold (±%)"
    )
    self.tempo_threshold.set(0.20)  # Default: ±20%

    # Audio-Preprocessing
    tk.Label(settings_window, text="Audio Preprocessing").pack()

    self.noise_reduction_strength = tk.Scale(
        settings_window,
        from_=0.0, to=1.0, resolution=0.1,
        orient=tk.HORIZONTAL,
        label="Noise Reduction Strength"
    )
    self.noise_reduction_strength.set(0.5)

    # Export-Format-Auswahl
    tk.Label(settings_window, text="Export Formats").pack()

    self.export_md = tk.BooleanVar(value=True)
    self.export_json = tk.BooleanVar(value=True)
    self.export_html = tk.BooleanVar(value=False)
    self.export_pdf = tk.BooleanVar(value=False)
    self.export_csv = tk.BooleanVar(value=False)
```

---

## 🐛 Priorität 3: Bug-Fixes & Stabilität (1 Woche)

### 1. Memory-Profile File-Locking (2 Tage)

**Problem**: Gleichzeitige Schreibzugriffe können YAML korruptieren

**Lösung**: File-Locking mit `fcntl` (Linux) oder `msvcrt` (Windows)

```python
# memory_manager.py

import fcntl  # Linux
import os

class MemoryManager:
    def save_profile_safe(self, speaker, profile_data):
        """Thread-safe YAML saving"""
        filepath = f"Memory/{speaker}.yaml"

        # Open with exclusive lock
        with open(filepath, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                yaml.dump(profile_data, f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### 2. Bessere Error-Messages (1 Tag)

**Problem**: Cryptische Fehlermeldungen bei HF Token, FFmpeg, etc.

**Lösung**: User-friendly Error-Handler

```python
# error_handler.py

class UserFriendlyException(Exception):
    """Exception mit hilfreichen Lösungsvorschlägen"""
    def __init__(self, error, solution):
        self.error = error
        self.solution = solution
        super().__init__(f"{error}\n\n✅ Lösung: {solution}")

# Beispiel-Verwendung
try:
    diarizer = SpeakerDiarizer()
except Exception as e:
    if "gated" in str(e).lower():
        raise UserFriendlyException(
            "Speaker Diarization erfordert Hugging Face Token.",
            "1. Erstelle Token: https://huggingface.co/settings/tokens\n"
            "2. Model Access: https://huggingface.co/pyannote/speaker-diarization-3.1\n"
            "3. Setze ENV: export HF_TOKEN='hf_xxxxx'\n"
            "4. Oder in GUI: HF Token Feld ausfüllen"
        )
```

### 3. Robusteres YAML-Parsing (1 Tag)

**Problem**: Korrupte YAML-Dateien führen zu Crash

**Lösung**: Validation + Backup + Recovery

```python
# yaml_handler.py

class SafeYAMLHandler:
    def load_profile(self, filepath):
        """Lädt YAML mit Validation und Fallback"""
        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)

            # Validate structure
            self.validate_profile(data)
            return data

        except yaml.YAMLError as e:
            # Backup korrupte Datei
            shutil.copy(filepath, f"{filepath}.corrupted")

            # Versuche Backup zu laden
            backup = f"{filepath}.backup"
            if os.path.exists(backup):
                with open(backup) as f:
                    return yaml.safe_load(f)

            # Letzte Option: Empty Profile
            return self.create_empty_profile()

    def save_profile(self, filepath, data):
        """Speichert YAML mit Backup"""
        # Backup erstellen
        if os.path.exists(filepath):
            shutil.copy(filepath, f"{filepath}.backup")

        # Speichern
        with open(filepath, 'w') as f:
            yaml.dump(data, f)
```

---

## 📅 Zeitplan-Vorschlag (3 Monate)

### Monat 1: Phase 2c - ATO-Integration

| Woche | Task | Aufwand |
|-------|------|---------|
| 1 | VP_ATO Marker Loading | 1 Woche |
| 2 | Prosody → ATO Mapping | 3 Tage |
| 2-3 | 4-Tier Hierarchie | 1 Woche |
| 3-4 | Wendepunkt-Erkennung | 5 Tage |
| 4 | Testing & Debugging | 2 Tage |

**Deliverables**:
- ✅ ATO-Marker erscheinen in allen Outputs
- ✅ 4-Tier Hierarchie vollständig implementiert
- ✅ Wendepunkt-Erkennung funktionsfähig
- ✅ Dokumentation aktualisiert

### Monat 2: GUI & Stabilität

| Woche | Task | Aufwand |
|-------|------|---------|
| 1 | Speaker Diarization GUI | 2 Tage |
| 1 | Asynchrones Threading | 2 Tage |
| 1 | Advanced Settings Panel | 1 Tag |
| 2 | Memory File-Locking | 2 Tage |
| 2 | Bessere Error-Messages | 1 Tag |
| 2 | YAML-Parsing Robustheit | 1 Tag |
| 3-4 | Testing & Bug-Fixing | 1 Woche |

**Deliverables**:
- ✅ GUI deutlich verbessert
- ✅ Keine bekannten kritischen Bugs
- ✅ Stabile Produktion-Version

### Monat 3: Polish & Vorbereitung Phase 3

| Woche | Task | Aufwand |
|-------|------|---------|
| 1-2 | User Testing & Feedback | 1 Woche |
| 2 | Performance-Optimierung | 3 Tage |
| 3 | Dokumentation finalisieren | 2 Tage |
| 3-4 | Phase 3 Planung & Research | 1 Woche |

**Deliverables**:
- ✅ Version 2.1 Release (Phase 2c Complete)
- ✅ Vollständige Dokumentation
- ✅ Phase 3 Implementierungsplan

---

## 📈 Erfolgsmetriken

### Phase 2c (ATO-Integration)

**Quantitative Metriken**:
- [ ] 100% VP_ATO Marker geladen
- [ ] 4-Tier Hierarchie in 100% der Outputs
- [ ] Wendepunkt-Detection mit >80% Confidence
- [ ] 0 kritische Bugs

**Qualitative Metriken**:
- [ ] Therapeuten finden Wendepunkte intuitiv
- [ ] ATO-Marker semantisch sinnvoll
- [ ] Dokumentation verständlich

### GUI-Verbesserungen

**User Experience**:
- [ ] GUI friert nicht mehr ein (0% freeze-time)
- [ ] Speaker Diarization in <3 Klicks aktivierbar
- [ ] Settings in <2 Klicks erreichbar

**Fehlerrate**:
- [ ] <5% User-Error-Rate bei HF Token Setup
- [ ] 0 Crashes bei Standard-Workflows

---

## 🎓 Learning & Research

### Parallele Forschungsaktivitäten

Während Phase 2c Entwicklung sollten folgende Themen researched werden:

1. **Real-Time Whisper Alternativen**
   - faster-whisper
   - WhisperLive
   - Distil-Whisper
   - **Ziel**: Vorbereitung für Phase 3

2. **Cross-Cultural Prosody**
   - Literatur-Review: Prosody in verschiedenen Sprachen
   - Baseline-Daten sammeln (DE, EN, FR, ES)
   - **Ziel**: Vorbereitung für Phase 4

3. **LLM-Integration Best Practices**
   - Claude API vs. Local Models
   - Prompt Engineering für Semantic Analysis
   - Cost-Benefit Analyse
   - **Ziel**: Vorbereitung für Phase 5

---

## 💡 Quick Wins (Optional, wenn Zeit übrig)

### Kleine Features mit hohem Impact (jeweils <1 Tag)

1. **Keyboard Shortcuts** in GUI
   - `Ctrl+T`: Transkription starten
   - `Ctrl+Q`: Quick Test
   - `Ctrl+P`: Prosody Test
   - `Ctrl+S`: Settings öffnen

2. **Drag & Drop** für Audio-Dateien
   - Dateien direkt in GUI ziehen
   - Automatisch zu Input-Ordner hinzufügen

3. **Recent Files** Liste
   - Letzte 5 verarbeitete Dateien anzeigen
   - Quick-Access zum Re-Processing

4. **Export-Vorschau**
   - Markdown/HTML-Preview direkt in GUI
   - Vor finalem Export prüfbar

5. **Batch-Report**
   - Summary nach Batch-Processing
   - Statistiken: Gesamt-Zeit, Avg. Quality, Fehler, etc.

---

## 📞 Support & Fragen

Bei Fragen zu diesem Entwicklungsplan:

1. Prüfe `VERSION_STATUS.md` für aktuellen Status
2. Prüfe `README.md` für technische Details
3. Konsultiere `CLAUDE.md` für Architektur-Entscheidungen

**Maintainer**: DYAI 2025
**Last Updated**: 2025-11-12

---

**TL;DR**:
- **Jetzt**: Phase 2c (ATO-Integration) - 1 Monat
- **Dann**: GUI & Bugs - 1 Monat
- **Danach**: Polish & Phase 3 Vorbereitung - 1 Monat
- **Ziel**: Version 2.1 mit vollständiger therapeutischer Wendepunkt-Erkennung
