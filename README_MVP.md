# Semantic Voice Transcriber - MVP

**Transcription + Speaker Separation + Semantic Summary**

## Quick Start

```bash
# 1. Install dependencies
pip install openai-whisper librosa soundfile torch

# Optional: Speaker separation
pip install pyannote.audio

# 2. Run transcription
python transcribe_mvp.py interview.mp4

# 3. View results
cat ./transcripts/interview_*_summary.md
```

## Dependencies

| Package | Status | Purpose |
|--------|--------|---------|
| openai-whisper | Erforderlich | Transcription |
| librosa | Empfohlen | Audio analysis |
| torch | Optional | Speaker separation |
| pyannote.audio | Optional | Speaker diarization |

## Usage

```bash
# Basic transcription
python transcribe_mvp.py audio.mp3

# With speaker separation
python transcribe_mvp.py audio.mp4

# Smaller model (faster)
python transcribe_mvp.py audio.mp3 -m tiny

# Custom output directory
python transcribe_mvp.py audio.mp3 -o ./my_transcripts
```

## Output Files

- `*.json` - Full transcript with timestamps
- `*_summary.md` - Human-readable summary

## Features

✅ Whisper transcription (5 model sizes)  
✅ Speaker separation (pyannote.audio)  
✅ Semantic summary generation  
✅ Multiple output formats  
✅ CPU optimized  
