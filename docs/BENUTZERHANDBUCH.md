# SVT Benutzerhandbuch

## Semantic Voice Transcriber für Therapeuten

**Version:** 1.0 | **Stand:** Februar 2026

---

## Inhaltsverzeichnis

1. [Was ist SVT?](#was-ist-svt)
2. [Schnellstart](#schnellstart)
3. [Installation](#installation)
4. [Audio-Upload](#audio-upload)
5. [Die Analyseergebnisse verstehen](#die-analyseergebnisse-verstehen)
6. [Das Dashboard nutzen](#das-dashboard-nutzen)
7. [ATO-Marker: Therapeutische Marker](#ato-marker-therapeutische-marker)
8. [Wendepunkte erkennen](#wendepunkte-erkennen)
9. [Best Practices für die Therapie](#best-practices-für-die-therapie)
10. [Datenschutz & Sicherheit](#datenschutz--sicherheit)
11. [Fehlerbehebung](#fehlerbehebung)
12. [Technischer Support](#technischer-support)

---

## Was ist SVT?

SVT (Semantic Voice Transcriber) ist eine Software, die Sprachaufnahmen aus therapeutischen Sitzungen automatisch analysiert und aufbereitet. Anders als einfache Transkriptions-Tools bietet SVT:

| Funktion | Beschreibung |
|----------|-------------|
| **Transkription** | Sprachaufnahmen werden in Text umgewandelt |
| **Sprechererkennung** | Automatische Unterscheidung zwischen Therapeut und Patient |
| **Prosodie-Analyse** | Tempo, Tonhöhe, Energie und Pausen werden analysiert |
| **Emotionserkennung** | Emotionale Veränderungen in der Stimme werden erkannt |
| **ATO-Marker** | Therapeutisch relevante Marker werden identifiziert |
| **Wendepunkt-Erkennung** | Bedeutsame Momente in der Sitzung werden hervorgehoben |
| **Memory-System** | Wiederkehrende Patienten werden über Sitzungen hinweg erkannt |

### Für wen ist SVT geeignet?

SVT richtet sich an:
- Psychotherapeuten (tiefenpsychologisch, verhaltenstherapeutisch)
- Psychoanalytiker
- klinische Psychisch, systemologen
- Forschende in der Therapieforschung

---

## Schnellstart

### Voraussetzungen

- Computer mit Windows 10/11, macOS oder Linux
- Mindestens 8 GB RAM (16 GB empfohlen)
- Python 3.8 oder höher
- Ca. 5 GB freier Speicherplatz

### Die ersten Schritte

1. **Software starten:**
   ```bash
   cd Semantic_Voice_Transcriber
   python svt_local_gui.py
   ```

2. **Audio-Datei auswählen:** Klicken Sie auf "Durchsuchen" und wählen Sie eine Audiodatei (MP3, WAV, M4A, OGG)

3. **Analyse-Optionen wählen:**
   - Prosodie-Analyse (empfohlen)
   - Sprechererkennung
   - Emotionsanalyse
   - ATO-Marker

4. **Transkription starten:** Klicken Sie auf "Transkription starten"

5. **Ergebnisse ansehen:** Die Analyse erscheint im Fenster und wird im Ordner `Transkripte_LLM/` gespeichert

---

## Installation

### Windows

1. **Python installieren:**
   - Laden Sie Python 3.11 von python.org herunter
   - Wichtig: ✅ "Add Python to PATH" aktivieren

2. **SVT installieren:**
   - Entpacken Sie das SVT-Paket
   - Führen Sie `install_svt.bat` als Administrator aus
   - Oder manuell: `pip install -r requirements.txt`

3. **Starten:**
   - Doppelklick auf `svt_local_gui.py`
   - Oder: `python svt_local_gui.py` im Terminal

### macOS

1. **Python installieren:**
   ```bash
   brew install python@3.11
   ```

2. **FFmpeg installieren:**
   ```bash
   brew install ffmpeg
   ```

3. **SVT installieren:**
   ```bash
   cd Semantic_Voice_Transcriber
   pip3 install -r requirements.txt
   ```

4. **Starten:**
   ```bash
   python3 svt_local_gui.py
   ```

### Linux (Ubuntu/Debian)

1. **Python und Abhängigkeiten installieren:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip ffmpeg
   ```

2. **SVT installieren:**
   ```bash
   cd Semantic_Voice_Transcriber
   pip3 install -r requirements.txt
   ```

3. **Starten:**
   ```bash
   python3 svt_local_gui.py
   ```

---

## Audio-Upload

### Unterstützte Formate

| Format | Dateiendung | Empfehlung |
|--------|-------------|-------------|
| MP3 | .mp3 | ✅ Am besten geeignet |
| WAV | .wav | ✅ Unkomprimiert, beste Qualität |
| M4A | .m4a | ✅ Apple-Format |
| OGG | .ogg | ✅ Open Source |
| FLAC | .flac | ✅ Verlustfrei |

### Dateigröße

- **Empfohlen:** Bis zu 500 MB pro Datei
- **Maximale Sitzungslänge:** 4 Stunden (bei ausreichend RAM)

### Tipps für gute Aufnahmen

1. **Umgebung:**
   - Ruhiger Raum ohne Hintergrundgeräusche
   - Keine Musik oder Nebengespräche
   - Tür und Fenster geschlossen

2. **Mikrofon:**
   - Nahmikrofon bevorzugt
   - Konstante Lautstärke
   - Kein zu großer Abstand zum Sprecher

3. **Aufnahmequalität:**
   - Mindestens 16 kHz Sample rate
   - Mono reicht für Transkription
   - Stereo besser für Sprechertrennung

### Ordnerstruktur

Die Software erwartet folgende Struktur:

```
Semantic_Voice_Transcriber/
├── Eingang/
│   ├── Patient_01/
│   │   ├── sitzung_2026-01-15.opus
│   │   └── sitzung_2026-01-22.opus
│   └── Patient_02/
│       └── sitzung_2026-01-20.m4a
├── Transkripte_LLM/       # Hier landen die Ergebnisse
│   └── Patient_01/
└── Memory/                # Patientenprofile
    └── patient_01.yaml
```

---

## Die Analyseergebnisse verstehen

### Die Transkription

Das Transkript enthält:

```markdown
# Therapeutisches Transkript

**Patient:** Max Mustermann
**Sitzung:** 2026-01-15
**Dauer:** 45:32

## Sprecher-Statistik

| Sprecher | Anteil |
|----------|--------|
| Therapeut | 35% |
| Patient | 65% |

## Transkription

[T00:00:15] Therapeut: Guten Tag, wie geht es Ihnen heute?
[T00:00:18] Patient: Mir geht es... na ja, es ist kompliziert.
[T00:00:25] Therapeut: Kompliziert?
[T00:00:27] Patient: Ja, ich habe die ganze Woche über wieder
         diese Gedanken gehabt...
```

### Prosodie-Analyse

Die Prosodie-Analyse zeigt **wie** etwas gesagt wurde:

| Merkmal | Beschreibung | Klinische Bedeutung |
|---------|--------------|---------------------|
| **Tempo** | Sprechgeschwindigkeit (Wörter/Min) | Schnell = Aufregung, Angst; Langsam = Depression, Überlegung |
| **Tonhöhe (Pitch)** | Mittlere Frequenz in Hz | Hohe Stimmlage = emotionale Erregung; Tiefe = Ruhe, Trauer |
| **Energie** | Lautstärke/Lautstärkevariation | Laut = Erregung, Wut; Leise = Scham, Unsicherheit |
| **Pausen** | Schweigephasen und ihre Länge | Lange Pausen = Nachdenken, Widerstand; Kurze = Redefluss, Angst |

**Beispiel-Interpretation:**

```
Segment: "Ich habe Angst vor der Zukunft"
- Tempo: 120 Wörter/Min (normal: 110)
- Pitch: 180 Hz (Basis: 165 Hz) → ↑ Erregung
- Energie: 0.045 (Basis: 0.038) → ↑ Lautstärke
- Pausen: 2.3 Sekunden vorher → ↑ Unsicherheit
```

### Emotionsanalyse

SVT erkennt folgende Basisemotionen:

| Emotion | Erkennungsmerkmale |
|---------|-------------------|
| 😢 Trauer | Tiefe Tonlage, langsames Tempo, leise |
| 😠 Wut | Hohe Energie, schnelles Tempo, laut |
| 😨 Angst | Variable Tonhöhe, Pausen, unsicheres Sprechen |
| 😊 Freude | Höhere Tonlage, schneller, energiegeladen |
| 😔 Neutral | Normale Werte bei allen Merkmalen |

### Confidence-Score

Jedes Segment hat einen Confidence-Score (0-1):

| Score | Bedeutung | Handlung |
|-------|-----------|----------|
| ≥ 0.8 | Sehr zuverlässig | Keine Überprüfung nötig |
| 0.6 - 0.8 | Zuverlässig | Meist korrekt |
| 0.4 - 0.6 | Unsicher | Bitte manuell prüfen |
| < 0.4 | Unzuverlässig | Korrektur erforderlich |

Unsichere Segmente werden im Transkript markiert:
```
[UNSICHER:0.35] ...konnte nicht genau verstanden werden...
```

---

## Das Dashboard nutzen

Das Dashboard ist eine webbasierte Oberfläche zur visuellen Analyse.

### Dashboard starten

```bash
cd Semantic_Voice_Transcriber/dashboard
python3 -m http.server 8080
```

Dann im Browser: `http://localhost:8080`

### Dashboard-Funktionen

1. **Audio-Upload**
   - Drag & Drop
   - Unterstützte Formate: MP3, WAV, M4A, OGG, FLAC

2. **Transkript-Ansicht**
   - Farbcodierte Sprecher
   - Suchfunktion
   - Filter nach Sprecher

3. **ATO-Marker-Highlighting**
   - Marker werden farblich hervorgehoben
   - Klick auf Marker zeigt Details

4. **Wendepunkte-Timeline**
   - Visuelle Darstellung des Sitzungsverlaufs
   - Filterung nach Wendepunkt-Typ

5. **Export**
   - PDF (für Akten)
   - DOCX (für Word-Bearbeitung)
   - JSON (für Datenanalyse)

---

## ATO-Marker: Therapeutische Marker

ATO-Marker (Advanced Therapeutic Output) sind semantische Marker, die therapeutisch relevante Inhalte und Verhaltensweisen kennzeichnen.

### Marker-Kategorien

#### 🛡️ Abwehrmechanismen

| Marker | Abkürzung | Beschreibung |
|--------|-----------|--------------|
| Denial | DEN | Verleugnung von Gedanken/Gefühlen |
| Projection | PROJ | Projektion eigener Gefühle auf andere |
| Rationalization | RAT | Rationalisierung/Logisierung |
| Displacement | DISP | Gefühlsverschiebung auf anderes Ziel |
| Defensive Shift | DEF | Abwehr-Verhaltenswechsel |

#### 🚧 Widerstand

| Marker | Abkürzung | Beschreibung |
|--------|-----------|--------------|
| Silence | SIL | Schweigen/lange Pausen |
| Topic Change | TC | Themenwechsel |
| Hedge | HED | Unsicherheitsmarkierer ("äh", "ich weiß nicht") |
| Avoidance | AVO | Ausweichen |
| Humor | HUM | Ablenkung durch Humor |

#### 💫 Emotionale Marker

| Marker | Abkürzung | Beschreibung |
|--------|-----------|--------------|
| Fear | FEA | Angst/Beunruhigung |
| Disgust | DIS | Ekel/Aversion |
| Sadness | SAD | Traurigkeit |
| Joy | JOY | Freude/Zufriedenheit |
| Anger | ANG | Wut/Frustration |
| Surprise | SUR | Überraschung |

#### 🔄 Kognitive Marker

| Marker | Abkürzung | Beschreibung |
|--------|-----------|--------------|
| Cognitive Bias | CB | Kognitive Verzerrung |
| Metacognition | META | Selbstreflexion |
| Insight | INS | Erkenntnisgewinn |
| Clarification Request | CRR | Klärungswunsch |

#### 🎭 Übertragung

| Marker | Abkürzung | Beschreibung |
|--------|-----------|--------------|
| Positive Transference | TRP+ | Idealisierung |
| Negative Transference | TRN- | Abwertung |
| Dependency | DEP | Abhängigkeitssignale |

### Marker lesen

Im Transkript erscheinen Marker so:

```
Patient: "Meine Mutter hat immer gesagt, dass ich... 
         [PROJ: Projektion der Mutterbeziehung]
         ...nie gut genug bin."
         [INS: ErkenntnisMoment]
```

### Marker interpretieren

**Beispiel: Widerstand erkennen**

```
Therapeut: "Erzählen Sie mir mehr über Ihre Kindheit."
Patient: "Äh... [HED] 
         Also... [SIL] 
         Da gibt es nicht viel zu erzählen. [AVO]
         Wollen wir nicht über etwas anderes sprechen?" [TC]
```

→ Diese Sequenz zeigt deutlichen Widerstand.

**Beispiel: Wendepunkt**

```
Patient: "Es war immer alles... [SIL]
         Ich war immer der Außenseiter. [SAD]
         [META] Aber jetzt verstehe ich vielleicht, warum...
         [INS] ...ich mich immer wieder in dieser Situation wiederfinde."
```

→ Hier zeigt sich ein möglicher therapeutischer Wendepunkt.

---

## Wendepunkte erkennen

Wendepunkte (Turning Points) sind Momente in der Sitzung, in denen etwas Bedeutsames passiert – emotional, kognitiv oder interaktionell.

### Arten von Wendepunkten

| Typ | Beschreibung | Indikatoren |
|-----|--------------|-------------|
| **Emotional Shift** | Emotionale Veränderung | Stimmwechsel, Pausen, Tränen |
| **Resistance Breakthrough** | Widerstand wird durchbrochen | Patient beginnt zu öffnen |
| **Defensive Resolution** | Abwehr löst sich | Weniger Hedge, mehr Offenheit |
| **Narrative Shift** | Themenwechsel | Neue Themen, Perspektivwechsel |
| **Insight Moment** | Erkenntnismoment | "Aha"-Momente, Metakognition |

### Im Dashboard erkennen

Das Dashboard zeigt Wendepunkte in einer **Timeline-Ansicht**:

```
|----|----|----|----|----|----|----|----|----|----|
0:00 5:00 10:00 15:00 20:00 25:00 30:00 35:00 40:00 45:00
  |     |         |    |         |    |
  |     |         |    |    [INS]|    |
  |     |    [RES]|    |         |    |
  | [EMO]         |    |         |    |
  |     |         |    |         |    |
```

Jeder Marker ist klickbar und zeigt:
- Den genauen Zeitstempel
- Das zugehörige Textzitat
- Den Kontext (vorher/nachher)

---

## Best Practices für die Therapie

### 1. Regelmäßige Transkription

- Transkribieren Sie Sitzungen möglichst bald nach dem Termin
- Nutzen Sie die Zeitersparnis für klinische Dokumentation
- Bauen Sie ein Memory-Profil für jeden Patienten auf

### 2. Ergebnisse kritisch nutzen

- **Empfehlung:** Nutzen Sie SVT als **Unterstützung**, nicht als Ersatz für Ihr klinisches Urteil
- Die Marker sind **Hinweise**, keine Diagnosen
- Besprechen Sie auffällige Befunde im Team oder mit Supervisoren

### 3. Dokumentation

- Exportieren Sie wichtige Sitzungen als PDF für die Patientenakte
- Nutzen Sie die JSON-Exporte für Forschungszwecke
- Achten Sie auf Datenschutz bei der Speicherung

### 4. Qualitätskontrolle

- Prüfen Sie immer die Confidence-Scores
- Korrigieren Sie fehlerhafte Transkripte manuell
- Nutzen Sie das Memory-System für wiederkehrende Patienten

### 5. Datensparsamkeit

- Speichern Sie nur, was Sie wirklich brauchen
- Löschen Sie Rohaufnahmen nach Transkription (optional)
- Nutzen Sie lokale Speicherung, nicht Cloud

---

## Datenschutz & Sicherheit

### Lokale Verarbeitung

✅ **Alle Daten bleiben auf Ihrem Computer**
- Keine Cloud-Verarbeitung
- Keine Serverübertragung
- Keine Drittanbieter-Zugriffe

### DSGVO-Konformität

| Aspekt | Umsetzung |
|--------|-----------|
| **Datenspeicherung** | Lokal auf Ihrem Gerät |
| **Zugriffskontrolle** | Nur Sie haben Zugriff |
| **Löschung** | Vollständige Kontrolle |
| **Auftragsverarbeitung** | Nicht erforderlich |

### Empfehlungen

1. **Backup:** Erstellen Sie regelmäßige Backups Ihrer Transkripte
2. **Verschlüsselung:** Nutzen Sie Festplattenverschlüsselung (BitLocker, FileVault)
3. **Zugang:** Schützen Sie Ihren Computer mit Passwort
4. **Weitergabe:** Geben Sie Transkripte nur mit Einwilligung weiter

---

## Fehlerbehebung

### Häufige Probleme

#### "Whisper-Modell wird nicht gefunden"

**Lösung:**
```bash
pip install --upgrade openai-whisper
```

#### "FFmpeg nicht gefunden"

**Lösung:**
- Windows: FFmpeg herunterladen und zum PATH hinzufügen
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

#### "Niedrige Transkriptionsqualität"

**Mögliche Ursachen:**
1. Schlechte Audioqualität → Aufnahme verbessern
2. Zu leise → Mikrofon verstärken
3. Hintergrundgeräusche → Ruhigere Umgebung

**Lösung:**
- Nutzen Sie das Dashboard für Audio-Qualitätsanalyse
- Probieren Sie verschiedene Whisper-Modelle (medium/large)

#### "Sprecher werden nicht erkannt"

**Ursache:** Zu viele überlappende Sprecher oder schlechte Audioqualität

**Lösung:**
- Bessere Aufnahmebedingungen schaffen
- Stereo-Aufnahme nutzen
- Manuelle Sprecherzuordnung im Nachgang

#### "Programm startet nicht"

**Ursache:** Fehlende Python-Abhängigkeiten

**Lösung:**
```bash
pip install -r requirements.txt
```

### Support-Kontakt

Bei weiteren Fragen wenden Sie sich an:
- Dokumentation: Siehe `/docs` Ordner
- GitHub Issues: https://github.com/DYAI2025/Semantic_Voice_Transcriber/issues

---

## Technischer Support

### Systemanforderungen

| Komponente | Minimum | Empfohlen |
|------------|---------|-----------|
| **Betriebssystem** | Windows 10, macOS 11, Ubuntu 20.04 | Neueste Version |
| **RAM** | 8 GB | 16 GB |
| **Speicher** | 10 GB | 20 GB |
| **Prozessor** | Intel/AMD x64 | M1/M2/Apple Silicon |
| **Python** | 3.8+ | 3.11 |

### Glossar

| Begriff | Bedeutung |
|---------|-----------|
| **Whisper** | OpenAI Spracherkennungsmodell |
| **Prosodie** | Sprechweise (Tempo, Tonhöhe, Energie) |
| **Diarization** | Sprechertrennung |
| **ATO** | Advanced Therapeutic Output |
| **Confidence** | Zuverlässigkeitswert (0-1) |
| **Memory-System** | System zur Speicherung von Patientenprofilen |

---

**Lizenz:** Creative Commons BY-NC-SA 4.0

**Entwickelt für die therapeutische Praxis**
