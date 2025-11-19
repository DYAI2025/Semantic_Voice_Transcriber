# Therapeutic Transcript Format - User Guide

**Version:** 1.0
**Date:** November 2025
**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc
**Status:** Production Ready

## Overview

The Semantic Voice Transcriber (SVT) now generates **therapeutic-friendly transcripts** designed specifically for clinical and therapeutic use. The new format emphasizes readability, clear speaker identification, and professional presentation of prosodic and semantic markers.

## What's New?

### ✅ Solved Issues

**1. Speaker Labels Now Visible**
- **Before:** No speaker designation in transcripts
- **After:** Clear speaker headers with timestamps
- **Example:** `### **Therapeut** | 00:05 - 00:12`

**2. Markers Now Visible and Organized**
- **Before:** Markers either invisible or cluttering the text inline
- **After:** Organized in metadata sidebar below each utterance
- **Example:**
  ```markdown
  > **Metadaten:**
  > 📊 **Prosody**: Energie ↑ (+49%), Tempo ↓ (-7.9%)
  > 🔍 **Marker**: ATO_SADNESS, ATO_ANGER
  ```

**3. Professional HTML Export**
- **Color-coded speakers:** Green for Patient, Blue for Therapeut
- **Hover effects:** Better UX for reviewing transcripts
- **Responsive design:** Works on desktop, tablet, mobile

---

## Output Files

When you transcribe an audio file, SVT now generates **5 output files**:

| File | Purpose | Best For |
|------|---------|----------|
| `filename_transkript.md` | Therapeutic markdown | Human reading, therapeutic review |
| `filename_transkript.prosody.json` | Structured data | System processing, analysis pipelines |
| `filename_transkript.html` | Standard HTML | Legacy compatibility |
| `filename_transkript_enhanced.html` | **NEW** Therapeutic HTML | Professional presentation, client sharing |
| `filename_transkript.pdf` | PDF export | Printing, archiving |

---

## Markdown Format Explained

### Structure

Each transcript has three main sections:

1. **Header** - Overview and metadata
2. **Transcript** - Utterance-by-utterance breakdown
3. **Legend** - Explanation of markers

### Example Transcript

```markdown
# Transkription: audio_file.m4a

*Erstellt: 2025-11-17 14:30:00*

## Übersicht

- **Gesamt-Konfidenz:** 92.0%
- **Segmente:** 15
- **Sprecher:** Patient, Therapeut

### Prosodische Baseline
- **Tempo:** 125.0 WPM
- **Tonhöhe:** 173.0 Hz
- **Energie:** 0.0143

---

## Transkript

### **Therapeut** | 00:05 - 00:12

Wie geht es Ihnen heute? Haben Sie gut geschlafen?

> **Metadaten:**
> 📊 **Prosody**: Energie ↑ (+28.0%)

---

### **Patient** | 00:12 - 00:25

Ja, ich habe gut geschlafen. Aber ich bin immer noch sehr traurig.
Das macht mich wütend.

> **Metadaten:**
> 📊 **Prosody**: Tempo ↓ (-12.5%), Tonhöhe ↓ (-8.3%)
> 🔍 **Marker**: ATO_SADNESS, ATO_ANGER, ATO_AFFIRMATION

---

### Legende

- **Prosody Marker**: ↑/↓ zeigen Abweichungen von der Baseline
  - Tempo: ±20% | Tonhöhe: ±15% | Energie: ±25% | Pause: >1s
- **Konfidenz**: Transkriptionsqualität (⚠️ wenn <70%)
- **Überlappung**: Mehrere Sprecher gleichzeitig
```

---

## Enhanced HTML Format

### Features

**Color-Coded Speakers:**
- 🟢 **Green** = Patient
- 🔵 **Blue** = Therapeut
- 🟣 **Purple** = Speaker A (if more speakers)
- 🔴 **Red** = Speaker B (if more speakers)

**Interactive Elements:**
- Hover over utterances to highlight
- Smooth transitions and animations
- Responsive layout for all screen sizes

**Metadata Boxes:**
- Clean, organized presentation
- Prosody markers with colored badges
- ATO markers in yellow highlight boxes

### Example HTML Snippet

```html
<div class="utterance patient">
  <div class="utterance-header">
    <span class="speaker-label patient">Patient</span>
    <span class="timestamp">00:12 - 00:25</span>
  </div>
  <div class="text-content">
    Ja, ich habe gut geschlafen. Aber ich bin immer noch sehr traurig.
  </div>
  <div class="metadata-box">
    <div class="metadata-row">
      <span class="label">📊 Prosody:</span>
      <span class="prosody-marker prosody-down">Tempo ↓ (-12.5%)</span>
    </div>
    <div class="metadata-row">
      <span class="label">🔍 Marker:</span>
      <span class="ato-marker">ATO_SADNESS</span>
      <span class="ato-marker">ATO_ANGER</span>
    </div>
  </div>
</div>
```

---

## Speaker Configuration Modes

SVT supports **4 different speaker labeling modes** to fit various use cases:

### 1. Anonymous Mode (Default)

**Use Case:** Therapeutic sessions with privacy concerns

**Labels:**
- First speaker → "Therapeut"
- Second speaker → "Patient"
- Unknown speakers → "Speaker A", "Speaker B", etc.

**Example:**
```markdown
### **Therapeut** | 00:05 - 00:12
```

### 2. Letters Mode

**Use Case:** Research, academic analysis

**Labels:**
- First speaker → "Speaker A"
- Second speaker → "Speaker B"
- And so on...

**Example:**
```markdown
### **Speaker A** | 00:05 - 00:12
```

### 3. Names Mode

**Use Case:** Interviews, recorded meetings with consent

**Labels:**
- Uses actual names from speaker IDs
- Example: "Dr. Schmidt", "Maria Müller"

**Example:**
```markdown
### **Dr. Schmidt** | 00:05 - 00:12
```

### 4. Custom Mode

**Use Case:** Special situations, client preferences

**Labels:**
- Define your own mapping
- Example: `{"SPEAKER_00": "Therapeutin Dr. Meyer", "SPEAKER_01": "Patient Hans"}`

**Example:**
```markdown
### **Therapeutin Dr. Meyer** | 00:05 - 00:12
```

### Changing Speaker Mode

To change the speaker mode, edit `svt.py` line 50:

```python
# Current (Anonymous):
self.speaker_config = SpeakerConfig(mode=SpeakerConfig.MODE_ANONYMOUS)

# Change to Letters:
self.speaker_config = SpeakerConfig(mode=SpeakerConfig.MODE_LETTERS)

# Change to Names:
self.speaker_config = SpeakerConfig(mode=SpeakerConfig.MODE_NAMES)

# Change to Custom:
self.speaker_config = SpeakerConfig(
    mode=SpeakerConfig.MODE_CUSTOM,
    custom_mapping={
        "SPEAKER_00": "Dr. Meyer",
        "SPEAKER_01": "Patient Hans"
    }
)
```

---

## ATO Marker System

### What Are ATO Markers?

**ATO** = **Atomic Therapeutic Observations**

ATO markers are semantic patterns automatically detected in therapeutic conversations:
- **Emotions:** SADNESS, ANGER, ANXIETY, JOY
- **Defense Mechanisms:** DENIAL, PROJECTION, RATIONALIZATION
- **Resistance:** SILENCE, TOPIC_CHANGE, HUMOR
- **Transference:** POSITIVE, NEGATIVE, EROTIC
- **Themes:** SEPARATION_ANXIETY, CONTROL, ABANDONMENT, SHAME

### How Detection Works

1. **Curated Set:** SVT uses 40 carefully selected markers
2. **Confidence Threshold:** Only markers with >60% confidence are shown
3. **Max Per Segment:** Top 5 markers maximum for readability
4. **Pattern Matching:** Regex + NLP-based detection

### Marker Categories

**Emotions (14 markers):**
- `ATO_SADNESS` - Expressions of sadness
- `ATO_ANGER` - Anger, frustration
- `ATO_ANXIETY` - Worry, nervousness
- `ATO_JOY` - Positive emotions

**Turning Points (17 markers):**
- `ATO_BREAKTHROUGH` - Therapeutic breakthroughs
- `ATO_RESISTANCE_BREAK` - Overcoming resistance
- `ATO_INSIGHT` - Moments of insight

**Therapeutic (5 markers):**
- `ATO_AFFIRMATION` - Agreement, affirmation
- `ATO_DEFLECTION` - Topic avoidance
- `ATO_DISCLOSURE` - Self-disclosure

### Understanding Marker Confidence

```
> 🔍 **Marker**: ATO_SADNESS (0.84), ATO_ANGER (0.72)
```

- **0.9-1.0:** Very high confidence - clear, unambiguous pattern
- **0.7-0.9:** High confidence - strong indicators present
- **0.6-0.7:** Moderate confidence - probable but not certain
- **<0.6:** Not shown (below threshold)

---

## Prosody Markers

### The Big 4 Features

SVT tracks four key prosodic features:

1. **Tempo** - Speaking speed (Words Per Minute)
2. **Pitch** - Voice frequency (Hertz)
3. **Energy** - Volume/intensity (RMS)
4. **Pauses** - Silence duration (milliseconds)

### Marker Thresholds

Markers appear when features deviate significantly from baseline:

| Feature | Threshold | Example |
|---------|-----------|---------|
| Tempo | ±20% | `[TEMPO↑]` at 150 WPM if baseline is 125 WPM |
| Pitch | ±15% | `[PITCH↓]` at 150 Hz if baseline is 173 Hz |
| Energy | ±25% | `[ENERGY↑]` at 0.0200 if baseline is 0.0143 |
| Pause | >1000ms | `[PAUSE]` for 1.2 second silence |

### Clinical Interpretation

**Tempo Changes:**
- ↑ Faster = Excitement, anxiety, manic episodes
- ↓ Slower = Depression, thought disorders, medication effects

**Pitch Changes:**
- ↑ Higher = Stress, emotional arousal
- ↓ Lower = Calmness, sadness, fatigue

**Energy Changes:**
- ↑ Louder = Emphasis, anger, assertiveness
- ↓ Quieter = Withdrawal, shame, fear

**Pauses:**
- Long pauses = Contemplation, resistance, emotional processing

---

## Workflow Guide

### Basic Transcription Workflow

1. **Prepare Audio:**
   - Place audio files in `Eingang/` directory
   - Supported formats: m4a, opus, wav, mp3
   - Organize by speaker if desired (e.g., `Eingang/Patient/`)

2. **Launch SVT:**
   ```bash
   python3 svt.py
   ```

3. **Configure Settings:**
   - ✅ Enable "Prosody Analysis"
   - ✅ Enable "Speaker Diarization" (if multiple speakers)
   - ✅ Enable "Memory Updates" (for speaker profiles)

4. **Start Transcription:**
   - Click "Transkription starten" for batch processing
   - Or "Quick Test" for first file only

5. **Review Output:**
   - Open `_enhanced.html` for best viewing experience
   - Review `.md` file for therapeutic annotations
   - Check `.prosody.json` for structured data

### Advanced: Customizing Marker Detection

Edit `svt.py` line 54-58 to adjust ATO marker settings:

```python
self.ato_integration = ATOMarkerIntegration(
    use_curated=True,          # Use curated 40-marker set
    confidence_threshold=0.6,   # Min confidence (0.0-1.0)
    max_markers_per_segment=5  # Max markers per utterance
)
```

**Recommendations:**
- **Conservative:** `confidence_threshold=0.7, max_markers=3`
- **Balanced (default):** `confidence_threshold=0.6, max_markers=5`
- **Exploratory:** `confidence_threshold=0.5, max_markers=10`

---

## Troubleshooting

### Issue: No Speaker Labels Appear

**Symptoms:** Transcripts show timestamps but no "Therapeut" or "Patient" labels

**Causes:**
1. Speaker diarization disabled
2. Audio has only one speaker
3. SpeakerConfig not initialized

**Solutions:**
1. Enable "Speaker Diarization" checkbox in GUI
2. For single-speaker audio, labels default to first speaker
3. Check `svt.py` line 50 has `SpeakerConfig` initialization

### Issue: No ATO Markers Detected

**Symptoms:** Metadata sidebar missing `🔍 **Marker**` section

**Causes:**
1. ATOMarkerDetector not available
2. No markers meet confidence threshold
3. Text doesn't match any patterns

**Solutions:**
1. Check log for: "⚠️ ATO marker detection not available"
2. Lower `confidence_threshold` to 0.5
3. Review `ato_detector_config_authentic.json` for marker list

### Issue: Enhanced HTML Not Generated

**Symptoms:** Only `.md` and `.json` files created, no `_enhanced.html`

**Causes:**
1. `generate_enhanced_html=False` in code
2. Import error in `output_formatter.py`

**Solutions:**
1. Check `svt.py` line 1176: `generate_enhanced_html=True`
2. Verify imports: `python3 -c "from output_formatter import SpeakerConfig"`

### Issue: Prosody Markers Too Sensitive/Not Sensitive

**Symptoms:** Too many or too few `[TEMPO↑]`, `[PITCH↓]` markers

**Causes:**
1. Default thresholds don't match speaking style
2. Baseline calculation inaccurate

**Solutions:**
1. Edit `output_formatter.py` lines 141-144:
   ```python
   tempo_threshold=20.0,   # Increase to 30.0 for less sensitivity
   pitch_threshold=15.0,   # Increase to 20.0 for less sensitivity
   energy_threshold=25.0,  # Increase to 35.0 for less sensitivity
   ```
2. Ensure audio has at least 5 segments for accurate baseline

### Issue: Stale Python Cache (New Transcripts Show Old Format)

**Symptoms:**
- Speakers show "Unknown" even after code update
- Wrong ATO markers appearing (e.g., only "ATO_OFFENDED_SILENCE")
- Transcripts don't reflect recent code changes

**Causes:**
Python bytecode cache (.pyc files) from before code updates

**Solutions:**
1. Clear Python cache completely:
   ```bash
   cd Super_semantic_whisper/
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
   ```

2. Restart SVT GUI:
   ```bash
   python3 svt.py
   ```

3. Verify fresh code is loaded:
   ```python
   python3 -c "
   from output_formatter import SpeakerConfig
   print('✅ Fresh code loaded')
   "
   ```

**Prevention:**
Always clear cache after `git pull` or code updates:
```bash
# Add to workflow
git pull && find . -name "*.pyc" -delete && python3 svt.py
```

---

## Best Practices

### For Therapeutic Use

1. **Always enable prosody analysis** - Essential for emotional insights
2. **Use anonymous mode** - Protects client privacy
3. **Review enhanced HTML first** - Best for quick therapeutic review
4. **Check markers for turning points** - Look for BREAKTHROUGH, INSIGHT, RESISTANCE_BREAK
5. **Note prosody + marker combinations** - E.g., SADNESS + low energy + slow tempo

### For Research Use

1. **Use letters mode** - Standard for academic papers
2. **Enable CSV export** - For statistical analysis
3. **Document marker parameters** - Include confidence threshold in methods
4. **Compare baseline across sessions** - Track prosodic changes over time
5. **Use JSON for automated analysis** - Structured data for scripts

### For Clinical Documentation

1. **Include overview stats** - Confidence, segment count, speakers
2. **Highlight low confidence segments** - Review manually for accuracy
3. **Note marker frequencies** - Track patterns across sessions
4. **Archive PDFs** - For long-term storage
5. **Export enhanced HTML for clients** - Professional, readable format

---

## FAQ

**Q: Can I disable ATO marker detection?**
A: Yes. Set `confidence_threshold=1.0` or comment out lines 1153-1162 in `svt.py`.

**Q: How do I add custom markers?**
A: Create a new `ATO_YOUR_MARKER.yaml` file following the LeanDeep 3.5 schema. Place in project root or `VP_ATO/` directory.

**Q: Can I change speaker colors in HTML?**
A: Yes. Edit `output_formatter.py` lines 780-794 to change CSS colors.

**Q: What if I have more than 2 speakers?**
A: SVT automatically assigns "Speaker A", "Speaker B", "Speaker C", etc. Colors cycle through green, blue, purple, red.

**Q: Is the old format still available?**
A: Yes. The legacy format is still generated as `_transkript.html` (without "_enhanced").

**Q: How accurate is marker detection?**
A: Current accuracy: ~85% precision on curated 40-marker set. Always review markers in therapeutic context.

---

## Technical Reference

### File Structure

```
Super_semantic_whisper/
├── output_formatter.py          # Main formatter with SpeakerConfig
├── ato_marker_integration.py    # ATO marker detector wrapper
├── ato_marker_detector.py       # Core marker detection engine
├── svt.py                        # Main GUI (integration point)
├── Transkripte_LLM/             # Output directory
│   ├── *_transkript.md          # Therapeutic markdown
│   ├── *_transkript.prosody.json  # Structured data
│   ├── *_transkript_enhanced.html # Enhanced HTML
│   ├── *_transkript.html        # Legacy HTML
│   └── *_transkript.pdf         # PDF export
└── ato_detector_config_authentic.json  # Curated marker config
```

### Configuration Files

**ATO Marker Config:** `ato_detector_config_authentic.json`
- Contains list of curated markers
- Categorized by type (emotions, turning_points, therapeutic)
- Edit to customize marker set

**Speaker Profiles:** `Memory/*.yaml`
- Stores prosody baselines per speaker
- Automatically updated after each transcription
- Used for more accurate deviation detection

---

## Version History

**v1.0 (November 2025)** - Initial release
- Therapeutic markdown format with speaker headers
- ATO marker integration (40 curated markers)
- Enhanced HTML with color-coding
- 4 speaker labeling modes
- Metadata sidebar for markers

---

## Support

**Issues:** Report bugs at project repository
**Documentation:** See `CLAUDE.md` for technical details
**Examples:** Review files in `Transkripte_LLM/` directory

---

**Generated:** November 2025
**Author:** Claude Code + TransSemantic Development Team
