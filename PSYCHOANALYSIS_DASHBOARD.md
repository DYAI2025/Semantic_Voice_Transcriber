# Psychoanalysis Dashboard

## Überblick

Das **Psychoanalysis Dashboard** ist ein professionelles System zur psychoanalytischen Analyse therapeutischer Transkripte. Es kombiniert moderne KI-Technologie (GPT-4-Turbo) mit etablierten psychoanalytischen Konzepten und generiert interaktive HTML-Dashboards für die therapeutische Reflexion.

### Hauptmerkmale

- **🧠 KI-gestützte Emotionsanalyse**: GPT-4-Turbo mit Utterance Emotion Dynamics (UED)
- **🔄 Tri-modale Wendepunkt-Erkennung**: Emotion + Marker + Prosodie
- **📊 Interaktive Visualisierungen**: Chart.js (Emotionskurven) + Cytoscape.js (Marker-Netzwerke)
- **🎯 16 Psychoanalytische Marker**: Abwehr, Widerstand, Übertragung, unbewusste Themen
- **⚡ Intelligentes Caching**: SHA256-basiert zur Vermeidung redundanter API-Aufrufe
- **🎨 Zweispalten-Dashboard**: Annotiertes Transkript + Analyse-Visualisierungen

## Systemarchitektur

```
Transkript (MD/JSON) → [Cache-Check] → [OpenAI GPT-4-Turbo]
                                              ↓
                                    [UED Emotion Dynamics]
                                    [Psychoanalytic Markers]
                                              ↓
                                    [Prosody Data Merge]
                                              ↓
                                    [Tri-Modal Turnpoint Detection]
                                              ↓
                                    [HTML Dashboard Generator]
                                              ↓
                              Interactive Dashboard (Chart.js + Cytoscape.js)
```

## Installation & Setup

### 1. Python-Abhängigkeiten

```bash
# Ins virtuelle Environment wechseln
cd Super_semantic_whisper
source .venv/bin/activate

# OpenAI-Client installieren (bereits in requirements.txt)
pip install openai>=1.0.0
```

### 2. OpenAI API-Schlüssel

Erstellen Sie eine `.env` Datei im Hauptverzeichnis:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

Oder exportieren Sie die Variable:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Wichtig**: Ohne API-Schlüssel kann das System nur gecachte Analysen verwenden.

### 3. Konfiguration

Die Standardkonfiguration befindet sich in `config/psychoanalysis_config.yaml`:

```yaml
openai:
  model: gpt-4-turbo-preview
  max_tokens: 4096
  temperature: 0.3

cache:
  enabled: true
  directory: cache/psychoanalysis

turnpoints:
  valence_threshold: 0.5      # Emotionale Veränderung
  arousal_threshold: 0.3      # Aktivierungsänderung
  prosody_pause_threshold_ms: 2000  # Lange Pausen (2s)
```

## Verwendung

### Methode 1: SVT GUI (Empfohlen) - One-Click Workflow

1. **SVT starten**:
   ```bash
   python3 svt.py
   ```

2. **Dashboard erstellen** (Integrierter Workflow):
   - Button "🧠 Psychoanalysis Dashboard" klicken
   - **Dateiauswahl**: Audio-Datei im Dialog auswählen (m4a, opus, wav, mp3, etc.)
   - **Automatische Prüfung**:
     - Falls `.prosody.json` bereits existiert → wird wiederverwendet (keine Neutranskription)
     - Falls nicht vorhanden → automatische Transkription mit **Prosody forciert ON**
   - **Asynchrone Verarbeitung**: Transkription läuft im Hintergrund (Log zeigt Fortschritt)
   - **Dashboard-Generierung**: Nach Transkription automatisch
   - **Browser öffnet automatisch**: Dashboard wird angezeigt

**Vorteile**:
- ✅ Keine manuelle Transkription nötig
- ✅ Wiederverwendung existierender Transkripte (spart Zeit & API-Kosten)
- ✅ Ein Klick vom Audio bis zum Dashboard
- ✅ Prosody automatisch aktiviert (erforderlich für Dashboard)

### Methode 2: Programmatisch (Python)

```python
from pathlib import Path
import json
from psychoanalysis_pipeline import PsychoanalysisPipeline
from dashboard_generator import DashboardGenerator

# 1. Transkript laden
with open("Transkripte_LLM/session_001.prosody.json") as f:
    transcript_data = json.load(f)

# 2. Pipeline initialisieren
pipeline = PsychoanalysisPipeline(
    config_path="config/psychoanalysis_config.yaml"
)

# 3. Skill-Pfad
skill_path = Path("../emotion_dynaminc-skill/emotion-dynamics-deep-insight/SKILL.md")

# 4. Analyse durchführen
result = pipeline.analyze_transcript(transcript_data, skill_path)

# 5. Dashboard generieren
generator = DashboardGenerator()
generator.generate_dashboard(result, "dashboard.html")

print(f"Dashboard erstellt: dashboard.html")
print(f"Turnpoints: {len(result['turnpoints'])}")
print(f"Marker: {len(result['marker_summary']['frequencies'])}")
```

### Methode 3: Kommandozeile

```bash
# (Noch nicht implementiert - geplant für v2.0)
python3 generate_psychoanalysis_dashboard.py session_001.prosody.json
```

## Psychoanalytische Marker

Das System verwendet **16 Atomic Voice Markers (ATO)** aus vier Kategorien:

### 🛡️ Abwehrmechanismen (Defense)

- `ATO_DEFENSE_DENIAL`: Verleugnung ("das stimmt nicht")
- `ATO_DEFENSE_PROJECTION`: Projektion ("die anderen sind schuld")
- `ATO_DEFENSE_RATIONALIZATION`: Rationalisierung ("logisch betrachtet...")
- `ATO_DEFENSE_DISPLACEMENT`: Verschiebung (Fokus auf Nebensächliches)

### 🚧 Widerstand (Resistance)

- `ATO_RESISTANCE_SILENCE`: Schweigen/Pausen
- `ATO_RESISTANCE_TOPIC_CHANGE`: Abrupter Themenwechsel
- `ATO_RESISTANCE_HUMOR`: Ablenkung durch Humor
- `ATO_RESISTANCE_CANCEL`: Terminabsagen/Vergessen

### 💫 Übertragung (Transference)

- `ATO_TRANSFERENCE_POSITIVE`: Idealisierung
- `ATO_TRANSFERENCE_NEGATIVE`: Abwertung
- `ATO_TRANSFERENCE_EROTIC`: Erotisierte Beziehung
- `ATO_TRANSFERENCE_DEPENDENCY`: Übermäßige Abhängigkeit

### 🎭 Unbewusste Themen (Themes)

- `ATO_THEME_SEPARATION_ANXIETY`: Trennungsangst
- `ATO_THEME_CONTROL`: Kontrollbedürfnis
- `ATO_THEME_ABANDONMENT`: Verlassenwerden
- `ATO_THEME_SHAME_GUILT`: Scham- und Schuldgefühle

## Tri-modale Wendepunkt-Erkennung

Das System erkennt **4 Arten von Turnpoints** durch Kombination von:

1. **Emotionale Veränderungen** (VAD-Dimensionen)
2. **Psychoanalytische Marker** (ATO-Muster)
3. **Prosodische Signale** (Pausen, Tempo, Pitch)

### Turnpoint-Typen

#### 1️⃣ Emotional Shift (Emotionale Wendung)

**Erkennung**: Valenz-Sprung > 0.5
- **Beispiel**: Valenz von -0.6 → 0.5 (Stimmungswechsel)
- **Prosody Enhancement**: Lange Pause (>2s) erhöht Signifikanz auf "high"

#### 2️⃣ Resistance Breakthrough (Widerstandsdurchbruch)

**Erkennung**: Widerstandsmarker verschwindet + positive Valenz
- **Beispiel**: `ATO_RESISTANCE_SILENCE` → keine Marker + Valenz > 0
- **Therapeutische Bedeutung**: Patient öffnet sich

#### 3️⃣ Defensive Resolution (Abwehrauflösung)

**Erkennung**: Abwehrmarker reduziert + Dominanz steigt
- **Beispiel**: `ATO_DEFENSE_DENIAL` → Dominanz +0.2
- **Therapeutische Bedeutung**: Selbstermächtigung

#### 4️⃣ Narrative Shift (Themenwechsel)

**Erkennung**: Wechsel der unbewussten Themen
- **Beispiel**: `ATO_THEME_SHAME_GUILT` → `ATO_THEME_CONTROL`
- **Therapeutische Bedeutung**: Fokusverschiebung

## Dashboard-Komponenten

### Linkes Panel: Annotiertes Transkript

- **Sprecher-Labels** (farbcodiert)
- **VAD-Werte** (Valence, Arousal, Dominance)
- **Marker-Tags** (gelb hinterlegt)
- **Turnpoint-Badges** (rot hinterlegt)
- **Prosody-Daten** (Tempo, Pitch, Pausen)

### Rechtes Panel (Oben): Emotionsdynamik

- **Chart.js Liniendiagramm**: VAD-Kurven über Zeit
- **UED Metriken**:
  - Heimatbasis (emotionale Grundstimmung)
  - Variabilität (emotionale Schwankungsbreite)
  - Instabilität (schnelle Wechsel)
  - Rise/Recovery Rates (Dynamik)

### Rechtes Panel (Unten): Wendepunkte & Marker

- **Turnpoint-Timeline**: Chronologische Liste mit Beschreibungen
- **Marker-Häufigkeit**: Balkendiagramm (Chart.js)
- **Marker-Netzwerk**: Cytoscape.js Visualisierung (Ko-Okkurrenz)

## UED (Utterance Emotion Dynamics)

### VAD-Dimensionen

- **Valence** (-1 bis +1): Negativität ↔ Positivität
- **Arousal** (0 bis 1): Ruhe ↔ Aktivierung
- **Dominance** (0 bis 1): Submissivität ↔ Kontrolle

### UED-Metriken

1. **Home Base**: Emotionale Grundstimmung (Mittelwert)
2. **Variability**: Standardabweichung der Emotionen
3. **Instability**: Aufeinanderfolgende Sprünge
4. **Rise Rate**: Geschwindigkeit positiver Veränderungen
5. **Recovery Rate**: Rückkehr zur Baseline nach Negativität

## Caching-System

### Funktionsweise

1. **Hash-Berechnung**: SHA256 des Transkript-JSON (sortiert)
2. **Cache-Lookup**: `cache/psychoanalysis/<hash>.json`
3. **Cache-Hit**: Gespeicherte Analyse verwenden (keine API-Kosten)
4. **Cache-Miss**: OpenAI API aufrufen → Ergebnis cachen

### Cache-Invalidierung

Der Cache wird **automatisch invalidiert** bei:
- Änderung des Transkript-Texts
- Änderung der Sprecher-Labels
- Änderung der Prosody-Daten

**Wichtig**: Skill-Änderungen invalidieren Cache NICHT (manuell löschen nötig).

### Cache manuell löschen

```bash
rm -rf cache/psychoanalysis/
```

## Kosten & Performance

### OpenAI API-Kosten (GPT-4-Turbo)

- **Modell**: `gpt-4-turbo-preview`
- **Kosten**: ~$0.01-0.03 pro Transkript (je nach Länge)
- **Tokens**: ~1500-3000 Input + 2000-4000 Output

### Performance

- **Mit Cache**: ~1-2 Sekunden (Dashboard-Generierung)
- **Ohne Cache**: ~10-30 Sekunden (API + Dashboard)
- **Dashboard-Größe**: ~200-400 KB (HTML mit inline CSS/JS)

## Datenschutz & Ethik

### ⚠️ Wichtige Hinweise

1. **Keine klinische Diagnose**: System ist Reflexionswerkzeug, keine Diagnose
2. **Pseudonymisierung**: Dashboard verwendet nur Sprecher-Labels (A, B, C)
3. **Datenspeicherung**: Cache enthält Volltext → sensible Daten schützen
4. **OpenAI-Privacy**: Transkripte werden an OpenAI gesendet (siehe API-Richtlinien)

### Empfehlungen

- **Cache-Verschlüsselung**: Für hochsensible Daten empfohlen
- **Lokale LLMs**: Alternative zu OpenAI (z.B. Llama, Mistral) geplant
- **Einwilligung**: Klienteneinwilligung für KI-Analyse einholen

## Troubleshooting

### Problem: "OPENAI_API_KEY not set"

**Lösung**:
```bash
export OPENAI_API_KEY="sk-your-key"
# Oder in .env Datei
echo 'OPENAI_API_KEY=sk-your-key' > .env
```

### Problem: "No module named 'psychoanalysis_pipeline'"

**Lösung**:
```bash
# Sicherstellen, dass Sie im richtigen Verzeichnis sind
cd Super_semantic_whisper
source .venv/bin/activate
```

### Problem: Dashboard zeigt keine Turnpoints

**Mögliche Ursachen**:
1. Zu wenig emotionale Veränderungen (Schwellwerte in Config anpassen)
2. Keine Prosody-Daten im Transkript (Prosody-Extraktion aktivieren)
3. Zu kurzes Transkript (< 3 Utterances)

**Lösung**: Config anpassen:
```yaml
turnpoints:
  valence_threshold: 0.3  # Von 0.5 senken
  arousal_threshold: 0.2  # Von 0.3 senken
```

### Problem: API-Kosten zu hoch

**Lösungen**:
1. **Cache nutzen**: Wiederholte Analysen kosten nichts
2. **Kürzere Transkripte**: Max. 10-15 Utterances pro Analyse
3. **Temperature senken**: Weniger Tokens (in Config: `temperature: 0.1`)

## Testing

### Unit-Tests ausführen

```bash
# Alle Tests
python3 -m pytest tests/ -v

# Spezifische Test-Dateien
python3 -m pytest tests/test_psychoanalysis_pipeline.py -v
python3 -m pytest tests/test_dashboard_generator.py -v
python3 -m pytest tests/test_turnpoint_detector.py -v

# E2E-Tests
python3 -m pytest tests/test_e2e_psychoanalysis.py -v
```

### Test-Coverage

```bash
python3 -m pytest --cov=. --cov-report=html tests/
# Öffnen: htmlcov/index.html
```

## Erweiterungen & Roadmap

### Geplante Features (v2.0)

- [ ] **Lokale LLMs**: Llama 3, Mistral (keine OpenAI-Abhängigkeit)
- [ ] **Echtzeit-Analyse**: Während der Transkription
- [ ] **Marker-Editor**: GUI zum Hinzufügen eigener ATO-Marker
- [ ] **Export-Formate**: PDF, DOCX, LaTeX
- [ ] **Multi-Session-Analyse**: Verlaufsanalyse über mehrere Sitzungen
- [ ] **Supervisor-Modus**: Kommentarfunktion für Supervision

### Eigene Marker hinzufügen

1. **YAML-Datei erstellen** (`VP_ATO/psychoanalytic/ATO_YOUR_MARKER.yaml`):

```yaml
id: ATO_YOUR_MARKER
frame:
  signal:
    - pattern: '\b(keyword1|keyword2)\b'
      flags: IGNORECASE
  concept: "Beschreibung des Konzepts"
  pragmatics: "Verwendung in Therapie"
  narrative: "Narrative Bedeutung"
examples:
  - "Beispiel 1"
  - "Beispiel 2"
  - "Beispiel 3"
  - "Beispiel 4"
  - "Beispiel 5"
category: defense|resistance|transference|theme
severity: low|medium|high
```

2. **Marker testen**:
```bash
python3 -m pytest tests/test_psychoanalytic_markers.py -v
```

3. **Skill neu laden** (automatisch beim nächsten API-Call)

## Support & Kontakt

- **Issues**: Bitte GitHub Issues verwenden
- **Dokumentation**: `CLAUDE.md`, `PSYCHOANALYSIS_DASHBOARD.md`
- **Beispiele**: `tests/test_e2e_psychoanalysis.py`

## Lizenz & Credits

- **Projekt**: TransSemantic / Semantic Voice Transcriber
- **Emotion-Dynamics Skill**: Based on UED framework
- **Visualisierungen**: Chart.js (MIT), Cytoscape.js (MIT)
- **KI-Backend**: OpenAI GPT-4-Turbo

---

**Version**: 1.0.0 (Januar 2025)
**Status**: MVP Complete ✅
