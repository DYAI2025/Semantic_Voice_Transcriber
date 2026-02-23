# SVT Therapeuten Dashboard

**Modernes, intuitives Web-Dashboard für die semantische Sprachanalyse in der Therapie.**

## Features

### 🎤 Audio-Upload
- Drag & Drop Unterstützung
- Unterstützte Formate: MP3, WAV, M4A, OGG, FLAC
- Max. Dateigröße: 500 MB
- Echtzeit-Fortschrittsanzeige

### 📝 Transkription
- Automatische Sprecherkennung (Therapeut/Patient)
- Farbcodierte Sprecherzuordnung
- Suche im Transkript
- Filter nach Sprecher
- ATO-Marker-Highlighting

### 🧠 Analyse & Interpretation
- Automatische ATO-Marker-Erkennung
- Themenextraktion
- Therapeutische Vorschläge
- Sprecher-Verhältnis-Statistiken
- Sentiment-Verlauf

### 📈 Wendepunkte
- Tri-modale Wendepunkterkennung
- Timeline-Visualisierung
- Filter nach Typ (Emotional, Widerstand, Abwehr, Narrativ)
- Kontext-Zitate

### 📤 Export
- PDF-Export
- DOCX-Export
- JSON-Export
- Vorschau-Funktion

## Installation

### Lokal (Empfohlen)

```bash
# Dashboard-Verzeichnis
cd Semantic_Voice_Transcriber/dashboard

# Mit Python HTTP Server starten
python3 -m http.server 8080

# Oder mit Node.js
npx serve .
```

### Im Browser öffnen

```
http://localhost:8080
```

## Integration mit SVT

### API-Integration

```javascript
const api = new SVTAPI('http://localhost:8000');

// Transkription starten
const result = await api.transcribeWithProsody(audioFile, (stage, percent) => {
    console.log(`${stage}: ${percent}%`);
});

// Analyse durchführen
const analysis = await api.analyzeTranscript(transcriptData);
```

### Verfügbare API-Endpunkte

| Endpunkt | Methode | Beschreibung |
|----------|---------|-------------|
| `/api/transcribe` | POST | Audio-Datei transkribieren |
| `/api/transcribe/status/:id` | GET | Transkriptions-Status |
| `/api/analyze` | POST | Transkription analysieren |
| `/api/turnpoints` | POST | Wendepunkte erkennen |
| `/api/export/pdf` | POST | PDF-Export |
| `/api/export/docx` | POST | DOCX-Export |
| `/api/export/json` | POST | JSON-Export |

## ATO-Marker

Das Dashboard erkennt folgende Marker-Kategorien:

### 🛡️ Abwehrmechanismen
- **Denial** (Verleugnung)
- **Projection** (Projektion)
- **Rationalization** (Rationalisierung)
- **Displacement** (Verschiebung)

### 🚧 Widerstand
- **Silence** (Schweigen)
- **Topic Change** (Themenwechsel)
- **Humor** (Ablenkung)

### 💫 Übertragung
- **Positive** (Idealisierung)
- **Negative** (Abwertung)
- **Dependency** (Abhängigkeit)

### 🎭 Themen
- **Separation Anxiety** (Trennungsangst)
- **Control** (Kontrollbedürfnis)
- **Abandonment** (Verlassenwerden)
- **Shame/Guilt** (Scham/Schuld)

## Wendepunkt-Typen

1. **Emotional Shift** - Emotionale Valenz-Änderung
2. **Resistance Breakthrough** - Widerstand löst sich
3. **Defensive Resolution** - Abwehr wird durchbrochen
4. **Narrative Shift** - Themenwechsel

## Technische Details

### Technologie-Stack
- **Frontend**: Vanilla HTML5, CSS3, JavaScript ES6+
- **Design System**: Custom CSS Variables
- **Icons**: SVG (inline)
- **Browser-Kompatibilität**: Modern Browser (Chrome, Firefox, Safari, Edge)

### Dateistruktur

```
dashboard/
├── index.html          # Hauptseite
├── css/
│   └── styles.css       # Stylesheet
├── js/
│   ├── api.js          # API-Client
│   └── app.js          # Hauptanwendung
└── assets/             # Statische Assets
```

## Lizenz

SVT - Semantic Voice Transcriber
Lizenz: Creative Commons BY-NC-SA 4.0

## Support

Bei Problemen:
1. Browser-Konsole prüfen (F12)
2. API-Server Status prüfen
3. Console-Logs überprüfen
