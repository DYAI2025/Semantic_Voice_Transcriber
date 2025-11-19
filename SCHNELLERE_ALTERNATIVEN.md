# Schnellere Alternativen zu OpenAI Whisper

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

## 🚀 Übersicht der Alternativen

### 1. **faster-whisper** (Empfohlen!)
- **Geschwindigkeit:** 4-5x schneller als OpenAI Whisper
- **Qualität:** Identisch zu OpenAI Whisper
- **Installation:** `pip install faster-whisper`
- **Vorteile:**
  - CTranslate2 backend für optimierte Inferenz
  - Geringerer Speicherverbrauch
  - Unterstützt alle Whisper-Modelle
  - CPU und GPU Support

### 2. **whisper.cpp**
- **Geschwindigkeit:** 3-4x schneller
- **Qualität:** Sehr nah an Original
- **Installation:** 
  ```bash
  git clone https://github.com/ggerganov/whisper.cpp
  cd whisper.cpp
  make
  ```
- **Vorteile:**
  - C++ Implementierung
  - Sehr geringer Speicherverbrauch
  - Läuft auf älteren Geräten

### 3. **WhisperX**
- **Geschwindigkeit:** 2-3x schneller + bessere Timestamps
- **Qualität:** Verbesserte Wort-Level Timestamps
- **Installation:** `pip install whisperx`
- **Vorteile:**
  - Wort-genaue Zeitstempel
  - Sprecherdiarisierung integriert
  - VAD (Voice Activity Detection)

### 4. **Insanely Fast Whisper**
- **Geschwindigkeit:** Bis zu 10x schneller (mit GPU)
- **Qualität:** Identisch zu OpenAI Whisper
- **Installation:** `pip install insanely-fast-whisper`
- **Vorteile:**
  - Optimiert für Batch-Processing
  - Nutzt Transformers library
  - Sehr schnell auf GPU

### 5. **SpeechRecognition mit Google/Azure**
- **Geschwindigkeit:** Echtzeit oder schneller
- **Qualität:** Sehr gut, aber Internet erforderlich
- **Installation:** `pip install SpeechRecognition`
- **Nachteile:**
  - Benötigt Internet
  - Datenschutz-Bedenken
  - Kosten bei großen Mengen

## 📊 Geschwindigkeitsvergleich

| Tool | Geschwindigkeit | Qualität | Offline | CPU/GPU |
|------|----------------|----------|---------|---------|
| OpenAI Whisper | 1x (Baseline) | 100% | ✅ | Beide |
| faster-whisper | 4-5x | 100% | ✅ | Beide |
| whisper.cpp | 3-4x | 98% | ✅ | CPU |
| WhisperX | 2-3x | 100%+ | ✅ | Beide |
| Insanely Fast | 10x | 100% | ✅ | GPU |

## 🛠️ Integration in WhisperSprecherMatcher

Das System verwendet bereits **faster-whisper** als Standard! 

### Installation von faster-whisper:
```bash
pip install faster-whisper
```

### Verwendung erzwingen:
```bash
python3 auto_transcriber_v2.py --local
```

### Standard Whisper verwenden (falls Probleme):
```bash
python3 auto_transcriber_v2.py --standard-whisper --local
```

## 💡 Empfehlungen

1. **Für normale Nutzung:** faster-whisper (bereits integriert)
2. **Für maximale Geschwindigkeit auf GPU:** Insanely Fast Whisper
3. **Für Wort-genaue Timestamps:** WhisperX
4. **Für alte/schwache Hardware:** whisper.cpp

## 🔧 Weitere Optimierungen

### Modell-Größe
- `tiny`: Sehr schnell, niedrigere Qualität
- `base`: Schnell, gute Qualität (Standard)
- `small`: Guter Kompromiss
- `medium`: Langsamer, bessere Qualität
- `large`: Sehr langsam, beste Qualität

### Batch-Processing
Mehrere Dateien gleichzeitig verarbeiten für bessere Effizienz.

### Hardware-Beschleunigung
- Apple Silicon: Metal Performance Shaders
- NVIDIA: CUDA
- AMD: ROCm  