#!/usr/bin/env python3
"""
Semantic Voice Transcriber - Production MVP CLI

Transcription + Speaker Separation + Semantic Summary

Usage:
    python transcribe_mvp.py <audio_file> [--output_dir <path>]
    
Example:
    python transcribe_mvp.py interview.mp4 --output_dir ./results
    
Output:
    - transcript.json (full transcript with timestamps)
    - summary.md (semantic summary)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed."""
    errors = []
    warnings = []
    
    try:
        import whisper
    except ImportError:
        errors.append("❌ openai-whisper: pip install openai-whisper")
    
    try:
        import librosa
    except ImportError:
        warnings.append("⚠️ librosa (optional): pip install librosa")
    
    try:
        import torch
    except ImportError:
        warnings.append("⚠️ torch (optional für Speaker Diarization)")
    
    return errors, warnings

def transcribe(audio_path, model_size="base"):
    """Transcribe audio using Whisper."""
    import whisper
    
    print(f"🎤 Transcribing: {Path(audio_path).name}")
    print(f"   Using model: {model_size}")
    
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    
    return result

def separate_speakers(audio_path):
    """Separate speakers using pyannote.audio."""
    try:
        from svt_core.audio import SpeakerDiarizer
        
        print(f"👥 Separating speakers...")
        diarizer = SpeakerDiarizer()
        segments = diarizer.diarize(audio_path)
        
        return segments
    except Exception as e:
        print(f"⚠️ Speaker separation failed: {e}")
        return None

def create_summary(transcript_text, speaker_count=0):
    """Create semantic summary."""
    # Basic word count
    words = transcript_text.split()
    word_count = len(words)
    duration_info = f"{word_count} Wörter"
    
    summary = {
        "title": "Transkript Zusammenfassung",
        "generated": datetime.now().isoformat(),
        "statistics": {
            "word_count": word_count,
            "speaker_count": speaker_count,
            "duration_estimate": duration_info
        },
        "key_points": [
            "Transkription abgeschlossen",
            f"Anzahl Sprecher: {speaker_count}" if speaker_count else "Sprecher nicht erkannt",
            "Qualitätsprüfung: Manuell empfohlen"
        ],
        "action_items": [
            "Transkript auf Genauigkeit prüfen",
            "Sprecherlabels bei Bedarf korrigieren",
            "Für therapeutische Verwendung: Anonymisierung prüfen"
        ]
    }
    
    return summary

def format_transcript_markdown(result, speaker_segments=None):
    """Format as readable markdown."""
    segments = result.get("segments", [])
    
    lines = ["# Therapeutisches Transkript\n"]
    lines.append(f"*Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    lines.append("---\n\n")
    lines.append("## Transkript\n\n")
    
    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "").strip()
        if text:
            lines.append(f"[{start:.1f}s] {text}\n")
    
    return "".join(lines)

def save_outputs(audio_path, transcript_result, summary, markdown, output_dir):
    """Save all outputs."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    base = Path(audio_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_path = output_path / f"{base}_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "file": Path(audio_path).name,
            "generated": datetime.now().isoformat(),
            "result": transcript_result,
            "summary": summary
        }, f, indent=2, ensure_ascii=False)
    
    # Markdown
    md_path = output_path / f"{base}_{timestamp}_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    return str(json_path), str(md_path)

def main():
    parser = argparse.ArgumentParser(
        description="Semantic Voice Transcriber MVP"
    )
    parser.add_argument("audio", help="Audio/video file path")
    parser.add_argument("-o", "--output", default="./transcripts", help="Output directory")
    parser.add_argument("-m", "--model", default="base", 
                        choices=["tiny", "base", "small", "medium"],
                        help="Whisper model size")
    parser.add_argument("--no-speakers", action="store_true", 
                        help="Skip speaker separation")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"❌ Datei nicht gefunden: {args.audio}")
        sys.exit(1)
    
    # Check deps
    errors, warnings = check_dependencies()
    for w in warnings:
        print(w)
    if errors:
        for e in errors:
            print(e)
        print("\n❌ Bitte fehlende Dependencies installieren.")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🎙️  Semantic Voice Transcriber MVP")
    print("="*50 + "\n")
    
    try:
        # 1. Transcribe
        result = transcribe(args.audio, args.model)
        text = result.get("text", "")
        
        # 2. Speakers
        speakers = None
        if not args.no_speakers:
            speakers = separate_speakers(args.audio)
        
        speaker_count = len(set(s.get("speaker", "UNKNOWN") for s in (speakers or []) if s))
        
        # 3. Summary
        summary = create_summary(text, speaker_count)
        
        # 4. Format
        markdown = format_transcript_markdown(result, speakers)
        
        # 5. Save
        json_path, md_path = save_outputs(args.audio, result, summary, markdown, args.output)
        
        print("\n" + "="*50)
        print("✅ Fertig!")
        print("="*50)
        print(f"\n📁 Output: {args.output}")
        print(f"   📄 {Path(json_path).name}")
        print(f"   📝 {Path(md_path).name}")
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
