# Transcription Debugging Guide

**Last Updated:** 2025-11-21

This guide explains how to use the built-in debugging and performance monitoring system to diagnose transcription crashes and lags.

---

## 🔍 Overview

SVT now includes a comprehensive debugging system that:

- ✅ **Tracks every step** of the transcription pipeline with timestamps
- ✅ **Measures performance** for each operation (model loading, transcription, prosody, etc.)
- ✅ **Logs detailed errors** with full stack traces
- ✅ **Monitors memory usage** during processing
- ✅ **Saves detailed logs** to files for later analysis

---

## 📊 Understanding the 1-Minute Lag

The ~1 minute lag you experience when starting transcription is **normal** and caused by:

### 1. **Whisper Model Loading** (30-90 seconds on first run)
   - **First time:** Model downloaded from Hugging Face (~1GB for "small" model)
   - **Subsequent runs:** Model loaded from disk cache (~/.cache/whisper/)
   - **CPU vs GPU:** Slower on CPU-only machines

### 2. **Audio Duration Detection** (1-5 seconds)
   - Librosa analyzes entire audio file to get duration
   - Required before chunking decision

### 3. **Speaker Diarization Model Loading** (if enabled, 10-30 seconds)
   - Pyannote.audio models downloaded on first run
   - Cached after first download

---

## 🛠️ Using the Debug Logger

### Automatic Logging

**The debug logger is now automatically active** for all transcriptions. No configuration needed!

### Where to Find Logs

Logs are automatically saved to:
```
logs/transcription_debug_YYYYMMDD_HHMMSS.log
```

Example:
```
logs/transcription_debug_20251121_143052.log
```

### Log Format

Each log entry includes:
- **Timestamp:** When the event occurred
- **Level:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Function:** Which function generated the log
- **Message:** What happened

Example log entry:
```
2025-11-21 14:30:52 | INFO     | transcribe_with_whisper        | ⏰ Start Time: 2025-11-21 14:30:52
2025-11-21 14:30:52 | DEBUG    | transcribe_with_whisper        | 📊 System Info:
2025-11-21 14:30:52 | DEBUG    | transcribe_with_whisper        |    Memory: 2456.3 MB
2025-11-21 14:30:52 | DEBUG    | transcribe_with_whisper        |    CPU: 12.5%
2025-11-21 14:30:55 | INFO     | transcribe_with_whisper        | ✅ Loading Audio Duration: 3.24s
2025-11-21 14:30:55 | WARNING  | transcribe_with_whisper        | ⚠️  This step may take 30-90 seconds on first run (downloading model)
2025-11-21 14:31:47 | INFO     | transcribe_with_whisper        | ✅ Loading Whisper Model: 51.89s
2025-11-21 14:32:35 | INFO     | transcribe_with_whisper        | ✅ Transcribing Audio: 48.12s
```

---

## 📝 Reading Debug Logs

### Step-by-Step Breakdown

A typical transcription log shows these steps:

```
📍 STEP: Initialization
   File: test_audio.m4a
   Memory: 1234.5 MB
✅ Initialization: 0.03s

📍 STEP: Loading Audio Duration
   Using librosa
   Memory: 1245.2 MB
   Audio duration: 180.50s (3.0 min)
✅ Loading Audio Duration: 2.45s

📍 STEP: Loading Whisper Model
   Model: small
   ⚠️  This step may take 30-90 seconds on first run (downloading model)
   Memory: 1256.8 MB
✅ Loading Whisper Model: 52.31s

📍 STEP: Transcribing Audio
   Language: de
   Memory: 3456.9 MB
   Transcription complete: 45 segments
✅ Transcribing Audio: 48.67s

📍 STEP: Extracting Confidence Scores
   Memory: 3487.2 MB
✅ Extracting Confidence Scores: 0.12s

📍 STEP: Prosody Extraction
   Big 4 features: Tempo, Pitch, Energy, Pauses
   Memory: 3501.5 MB
✅ Prosody Extraction: 15.34s

📍 STEP: Speaker Diarization
   Detecting speakers
   Memory: 4123.7 MB
✅ Speaker Diarization: 23.45s

========================================================
✅ PIPELINE COMPLETE
========================================================
⏱️  Total Duration: 142.37s (2.4 min)

📊 Step Summary:
   Initialization: 0.03s (0.0%)
   Loading Audio Duration: 2.45s (1.7%)
   Loading Whisper Model: 52.31s (36.7%)
   Transcribing Audio: 48.67s (34.2%)
   Extracting Confidence Scores: 0.12s (0.1%)
   Prosody Extraction: 15.34s (10.8%)
   Speaker Diarization: 23.45s (16.5%)
```

### Performance Breakdown

From the above example:
- **Model Loading:** 36.7% of time (normal on first run)
- **Transcription:** 34.2% of time (actual Whisper processing)
- **Prosody:** 10.8% of time
- **Diarization:** 16.5% of time

---

## 🐛 Diagnosing Crashes

### If SVT Crashes During Transcription

1. **Check the latest log file**:
   ```bash
   ls -lht logs/transcription_debug_*.log | head -1
   ```

2. **Look for ERROR entries**:
   ```bash
   grep "ERROR" logs/transcription_debug_20251121_143052.log
   ```

3. **Find the crash point**:
   Look for the last completed step before the error.

### Common Crash Patterns

#### Memory Overflow
```
❌ ERROR in Transcribing Audio
Exception Type: MemoryError
Exception Message: Unable to allocate array
```
**Solution:** Enable audio chunking, use smaller model (tiny/base instead of small/medium)

#### Model Download Failure
```
❌ ERROR in Loading Whisper Model
Exception Type: ConnectionError
Exception Message: HTTPSConnectionPool
```
**Solution:** Check internet connection, clear cache (~/.cache/whisper/), try again

#### Missing Dependencies
```
❌ ERROR in Prosody Extraction
Exception Type: ImportError
Exception Message: No module named 'parselmouth'
```
**Solution:** Install missing dependencies
```bash
pip install praat-parselmouth librosa soundfile
```

#### Audio File Corruption
```
❌ ERROR in Loading Audio Duration
Exception Type: LibrosaError
Exception Message: Soundfile failed to open
```
**Solution:** Verify audio file integrity, try converting to different format

---

## ⚡ Optimizing Performance

### Reducing Lag

#### 1. Use Smaller Models
In SVT GUI → Model dropdown:
- **tiny:** Fastest (39M params), lower accuracy
- **base:** Fast (74M params), good balance
- **small:** Default (244M params), high accuracy
- **medium/large:** Slowest, best accuracy

**Recommendation:** Start with "base" for testing

#### 2. Disable Heavy Features
- **Prosody Analysis:** Adds ~10-15% processing time
- **Speaker Diarization:** Adds ~15-25% processing time
- **Emotion Detection:** Minimal impact (~1-2%)

#### 3. Enable Audio Chunking
For large files (>5 minutes):
- ✅ Check "Audio Chunking verwenden"
- Set chunk duration to 300s (5 minutes)
- Reduces memory usage significantly

#### 4. Use Intelligent Pipeline
- Analyzes audio quality first
- Selects optimal model automatically
- Applies preprocessing only when needed

---

## 📈 Monitoring Real-Time Progress

### Console Output

During transcription, SVT logs progress to console:
```
🚀 Starte Transkription von 1 Datei(en)
🎤 test_audio.m4a (12.3 MB)
    🔍 Analysiere Audio-Qualität...
    📊 Qualität: 0.75 | SNR: 18.5dB | Clipping: 0.12%
    🎯 Small Modell (memory-optimized)
    🎤 Transkribiere mit small Modell...
    ✅ Transkription abgeschlossen
```

### GUI Progress Bar

The main GUI shows:
- **Status:** Current step being processed
- **Progress bar:** Overall progress percentage
- **Log output:** Detailed messages in text area

---

## 🔧 Advanced Debugging

### Enabling More Verbose Logging

Edit `svt_core/tools/transcription_debugger.py`:

```python
# Change logger level
logger.setLevel(logging.DEBUG)  # Most verbose
logger.setLevel(logging.INFO)   # Default
```

### Custom Debug Points

Add custom logging in your code:

```python
from svt_core.tools.transcription_debugger import log_info, log_debug, log_error

log_info("Starting custom processing")
log_debug(f"Variable value: {my_variable}")
log_error("Something went wrong", exc_info=True)
```

### Profiling Specific Functions

Wrap functions with the profiler:

```python
from svt_core.tools.transcription_debugger import profile_function, TranscriptionDebugger

debugger = TranscriptionDebugger()

@profile_function(debugger)
def my_slow_function():
    # Your code here
    pass
```

---

## 📞 Getting Help

If you still experience crashes or unexplained lags:

1. **Collect the debug log**:
   ```bash
   cat logs/transcription_debug_LATEST.log
   ```

2. **Note system info**:
   - OS version
   - Python version (`python3 --version`)
   - RAM available
   - GPU available (if any)

3. **Provide steps to reproduce**:
   - Audio file size and format
   - SVT settings used
   - Exact error message

4. **Check existing issues**:
   - GitHub issues: https://github.com/DYAI2025/Semantic_Voice_Transcriber/issues

---

## 🎓 FAQ

### Q: Why does the first transcription take so long?

**A:** Whisper models are downloaded on first run (~1GB per model). Subsequent runs load from cache and are much faster.

### Q: Can I disable debug logging?

**A:** Yes, set `DEBUGGER_AVAILABLE = False` in `auto_transcriber_v4_emotion.py` line 57.

### Q: Where are Whisper models stored?

**A:** `~/.cache/whisper/` (Linux/Mac) or `C:\Users\YourName\.cache\whisper\` (Windows)

### Q: How much RAM do I need?

**A:**
- **tiny/base model:** 2-4 GB
- **small model:** 4-8 GB
- **medium model:** 8-16 GB
- **large model:** 16-32 GB

### Q: Can I use GPU acceleration?

**A:** Yes, if PyTorch with CUDA is installed. Whisper will automatically use GPU if available.

---

**Happy Debugging!** 🐛🔧

If you find this guide helpful, consider contributing improvements via Pull Request.
