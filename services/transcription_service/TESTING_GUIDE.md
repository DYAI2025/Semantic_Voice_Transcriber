# Testing Guide - Standalone Transcription GUI

**Version:** 1.0.0 | **Last Updated:** 2025-12-07

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies (required)
pip install numpy openai-whisper librosa soundfile fastapi pydantic

# System dependencies
sudo apt install python3-tk ffmpeg  # Ubuntu/Debian

# Optional: Speaker detection
pip install pyannote.audio torch
```

### 2. Configure HF Token (for Speaker Detection)

```bash
# Create .env file in repository root
echo "HF_TOKEN=hf_YourTokenHere" >> .env

# Get token from: https://huggingface.co/settings/tokens
# Accept model agreements:
#  - https://huggingface.co/pyannote/segmentation-3.0
#  - https://huggingface.co/pyannote/speaker-diarization-3.1
```

### 3. Launch GUI

```bash
# From repository root
./services/transcription_service/launch_gui.sh

# Or directly
python3 services/transcription_service/gui.py
```

---

## Testing Speaker Separation

### Test 1: Single Speaker Audio

**Objective:** Verify transcription works without speaker detection

**Steps:**
1. Launch GUI
2. Select audio file with single speaker
3. Uncheck "Enable Speaker Detection"
4. Click "🎙️ Transcribe Audio"

**Expected Results:**
- ✅ Transcription completes successfully
- ✅ Full transcript appears in "Full Transcript" tab
- ✅ Segments show "Unknown" in speaker column
- ✅ Confidence score displayed (should be > 70% for clear audio)
- ✅ Quality report shows metrics

**Pass Criteria:**
- Overall confidence > 70%
- No crashes or errors
- All segments have text content

---

### Test 2: Multi-Speaker Audio (with Detection)

**Objective:** Verify speaker separation works correctly

**Prerequisites:**
- HF_TOKEN configured
- pyannote.audio installed
- Audio file with 2+ speakers

**Steps:**
1. Launch GUI
2. Select multi-speaker audio file
3. Check "Enable Speaker Detection"
4. Set "Number of Speakers" to "auto" or specific number
5. Click "🎙️ Transcribe Audio"

**Expected Results:**
- ✅ Diarization runs successfully
- ✅ Speakers labeled as A, B, C, etc.
- ✅ "Segments (with Speakers)" tab shows speaker labels
- ✅ Speakers indicator shows detected speakers (e.g., "A, B")
- ✅ Quality report includes speaker detection section

**Pass Criteria:**
- Speakers are correctly identified (manual verification needed)
- Speaker changes align with actual speaker changes
- No "Unknown" speakers if detection succeeded
- DER (Diarization Error Rate) < 15% (estimated visually)

---

### Test 3: Speaker Detection Accuracy

**Objective:** Verify speaker labels are accurate

**Test Audio Setup:**
Create or use audio with known speaker patterns:
- Speaker A: 0-10s
- Speaker B: 10-20s
- Speaker A: 20-30s

**Steps:**
1. Enable speaker detection
2. Set number of speakers = 2
3. Transcribe audio
4. Compare detected speakers with ground truth

**Validation:**
```python
# Expected pattern
expected = ["A", "A", "A", "B", "B", "B", "A", "A", "A"]

# Actual pattern (from GUI segments)
actual = [seg["speaker"] for seg in response.segments]

# Calculate accuracy
correct = sum(e == a for e, a in zip(expected, actual))
accuracy = correct / len(expected)

# Pass if accuracy > 80%
assert accuracy > 0.8
```

---

## Testing Transcript Quality

### Test 4: High-Quality Audio

**Objective:** Verify transcription accuracy on clear audio

**Audio Characteristics:**
- Clear speech
- Minimal background noise
- Standard recording (16kHz, mono)
- Professional or studio recording

**Steps:**
1. Select high-quality audio
2. Choose model: "medium" or "large"
3. Set correct language
4. Transcribe

**Expected Results:**
- ✅ Confidence > 85%
- ✅ Few or no low-confidence segments
- ✅ Text is accurate (manually verify)
- ✅ Word Error Rate (WER) < 5%

**Manual Verification:**
1. Read transcript while listening to audio
2. Count errors (insertions, deletions, substitutions)
3. Calculate WER: `errors / total_words`

**Pass Criteria:**
- Overall confidence > 85%
- WER < 5%
- Low confidence segments < 10%

---

### Test 5: Low-Quality Audio

**Objective:** Verify graceful degradation on poor audio

**Audio Characteristics:**
- Background noise
- Compression artifacts
- Low volume or distortion
- Non-standard format

**Steps:**
1. Select low-quality audio
2. Choose model: "large" (best accuracy)
3. Enable audio preprocessing if available
4. Transcribe

**Expected Results:**
- ✅ Transcription completes (no crash)
- ✅ Confidence score reflects quality (may be low)
- ✅ Low-confidence segments are marked
- ✅ Quality report shows warnings

**Pass Criteria:**
- Service doesn't crash
- Low-confidence segments are flagged
- Confidence score < 70% is acceptable
- WER < 20%

---

### Test 6: Confidence Scoring Accuracy

**Objective:** Verify confidence scores correlate with accuracy

**Steps:**
1. Transcribe multiple audio files
2. For each segment, note:
   - Confidence score
   - Actual transcription quality (manual check)

**Validation:**
```
High Confidence (>80%):
  - Should have accurate text
  - Few or no errors

Medium Confidence (50-80%):
  - May have minor errors
  - Generally understandable

Low Confidence (<50%):
  - Likely has errors
  - Should be marked with [UNSICHER] tag
```

**Pass Criteria:**
- High confidence correlates with accuracy
- Low confidence segments actually have errors
- [UNSICHER] markers appear on poor segments

---

## Testing GUI Functionality

### Test 7: File Selection

**Steps:**
1. Click "Browse..." button
2. Select various audio formats:
   - .opus
   - .m4a
   - .wav
   - .mp3
   - .ogg

**Expected Results:**
- ✅ File dialog opens
- ✅ All formats are selectable
- ✅ Selected file path appears in entry
- ✅ Status bar shows "Selected: filename"

---

### Test 8: Model Selection

**Steps:**
1. Test each model size:
   - tiny (fastest, least accurate)
   - base
   - small
   - medium (recommended)
   - large (slowest, most accurate)

**Expected Results:**
- ✅ Each model loads and processes
- ✅ Larger models take longer
- ✅ Larger models have better accuracy
- ✅ Quality report shows model used

**Performance Benchmarks:**
| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| tiny | 0.05x RT | ~12% WER | Quick tests |
| base | 0.10x RT | ~8% WER | Fast processing |
| small | 0.15x RT | ~6% WER | Balanced |
| medium | 0.25x RT | ~4% WER | Recommended |
| large | 0.40x RT | ~3% WER | Best quality |

---

### Test 9: Language Detection

**Steps:**
1. Test with different languages:
   - German (de)
   - English (en)
   - Auto-detect (auto)

**Expected Results:**
- ✅ Correct language is detected (in auto mode)
- ✅ Forced language works correctly
- ✅ Multi-language audio handled (if applicable)

---

### Test 10: Save Functionality

**Steps:**
1. Complete a transcription
2. File → Save Transcript...
3. Test saving as:
   - .txt (plain text)
   - .json (structured data)
   - .md (markdown)

**Expected Results:**
- ✅ File save dialog opens
- ✅ File is saved successfully
- ✅ Saved file contains correct content
- ✅ JSON file has valid structure

**JSON Structure Validation:**
```json
{
  "text": "Full transcript...",
  "segments": [...],
  "confidence_scores": {...},
  "extras": {...}
}
```

---

### Test 11: HF Token Configuration

**Steps:**
1. Settings → Configure HF Token
2. Enter token
3. Click Save

**Expected Results:**
- ✅ Dialog opens
- ✅ Token is saved to .env file
- ✅ HF_TOKEN environment variable is set
- ✅ Speaker detection becomes available

---

### Test 12: Error Handling

**Test Scenarios:**

**A. Missing File**
1. Clear file path
2. Click Transcribe
- Expected: Warning dialog "Please select an audio file first"

**B. Invalid File**
1. Select non-audio file (e.g., .txt)
2. Click Transcribe
- Expected: Error message with clear explanation

**C. Missing HF Token (with speaker detection enabled)**
1. Enable speaker detection without token
2. Click Transcribe
- Expected: Prompt to configure token

**D. Service Crash**
1. Simulate error condition
- Expected: Error dialog, service remains functional

---

## Performance Testing

### Test 13: Long Audio Files

**Objective:** Verify handling of long audio

**Test Cases:**
- 5 minutes (baseline)
- 15 minutes (standard)
- 30 minutes (long)
- 60+ minutes (very long)

**Expected Results:**
- ✅ All durations process successfully
- ✅ No memory errors
- ✅ Progress indication works
- ✅ Processing time scales linearly

**Performance Targets:**
- 30-min audio should process in < 10 minutes (medium model)
- Memory usage < 4GB (medium model)
- No crashes or timeouts

---

### Test 14: Concurrent Processing Prevention

**Steps:**
1. Start transcription
2. Try to start another while first is processing

**Expected Results:**
- ✅ Process button is disabled during processing
- ✅ Warning: "Already processing. Please wait."
- ✅ Second request is blocked

---

## Integration Testing

### Test 15: Full Workflow Test

**Complete Workflow:**

1. **Setup**
   - Launch GUI
   - Configure HF token
   - Verify service status (green)

2. **Single Speaker**
   - Select audio file
   - Model: medium
   - Language: auto
   - Speaker detection: OFF
   - Transcribe
   - Verify results
   - Save as .txt

3. **Multi-Speaker**
   - Select 2-speaker audio
   - Model: medium
   - Language: de
   - Speaker detection: ON
   - Num speakers: 2
   - Transcribe
   - Verify speaker labels
   - Save as .json

4. **Quality Review**
   - Switch to "Quality Report" tab
   - Verify all metrics present
   - Check for warnings
   - Review low-confidence segments

5. **Export**
   - Save transcript (.md)
   - Save quality report (manual copy)

**Pass Criteria:**
- All steps complete without errors
- Results are accurate
- Files are saved correctly
- GUI remains responsive

---

## Automated Testing

### Run Unit Tests

```bash
# From repository root
python3 tests/test_speaker_separation_quality.py
```

**Expected Output:**
```
========================================
SPEAKER SEPARATION TESTS
========================================
✅ Service initializes without diarization adapter
✅ pyannote.audio module is available
✅ Diarization adapter initialized successfully

========================================
TRANSCRIPT QUALITY TESTS
========================================
✅ Overall confidence calculated
✅ Low confidence segments detected
✅ Confidence markers added

========================================
ALL TESTS PASSED
========================================
```

---

## Troubleshooting

### Issue: GUI won't start

**Check:**
```bash
# Python version
python3 --version  # Should be 3.10+

# Tkinter
python3 -c "import tkinter"

# Dependencies
pip list | grep -E "numpy|whisper|librosa"
```

---

### Issue: Speaker detection not working

**Check:**
1. HF_TOKEN set: `echo $HF_TOKEN` or check `.env`
2. pyannote.audio installed: `pip list | grep pyannote`
3. Model agreements accepted on Hugging Face
4. Internet connection (for model download)

---

### Issue: Low accuracy

**Solutions:**
1. Use larger model (medium or large)
2. Check audio quality (SNR, noise level)
3. Verify correct language selected
4. Try audio preprocessing

---

## Test Results Template

```
==================================================
TEST RESULTS - Standalone Transcription GUI
==================================================

Date: YYYY-MM-DD
Tester: [Name]
Version: 1.0.0

ENVIRONMENT:
- OS: Linux/Windows/macOS
- Python: 3.x.x
- Dependencies: All/Partial

TESTS COMPLETED:
[✓] Test 1: Single Speaker Audio
[✓] Test 2: Multi-Speaker Audio
[✓] Test 3: Speaker Detection Accuracy
[✓] Test 4: High-Quality Audio
[✓] Test 5: Low-Quality Audio
[✓] Test 6: Confidence Scoring
[✓] Test 7: File Selection
[✓] Test 8: Model Selection
[✓] Test 9: Language Detection
[✓] Test 10: Save Functionality
[✓] Test 11: HF Token Configuration
[✓] Test 12: Error Handling
[✓] Test 13: Long Audio Files
[✓] Test 14: Concurrent Processing
[✓] Test 15: Full Workflow

ISSUES FOUND:
[List any bugs or problems]

PERFORMANCE METRICS:
- Average confidence: XX%
- Average WER: XX%
- Speaker detection accuracy: XX%
- Processing speed: X.XXx RT

NOTES:
[Any additional observations]

==================================================
```

---

## Next Steps

After testing:
1. Document any issues in GitHub Issues
2. Share test results with team
3. Update documentation with findings
4. Plan improvements based on feedback

---

**Maintained By:** SVT Development Team
**Last Updated:** 2025-12-07
