#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick transcription test
"""
import auto_transcriber_v4_emotion as v4
from audio_quality_analyzer import AudioQualityAnalyzer
from audio_preprocessor import AudioPreprocessor
from pathlib import Path
import time

# Audio file
audio_file = "Eingang/KAH EGOSTATE (2).m4a"

if not Path(audio_file).exists():
    print(f"❌ Datei nicht gefunden: {audio_file}")
    exit(1)

print(f"📂 Audio-Datei: {audio_file}")
print(f"📊 Größe: {Path(audio_file).stat().st_size / 1024 / 1024:.1f} MB\n")

# Option 1: MIT Intelligent Pipeline
print("🤖 Option 1: Mit Intelligent Pipeline")
print("=" * 50)

analyzer = AudioQualityAnalyzer()
preprocessor = AudioPreprocessor()

print("🔍 Analysiere Qualität...")
start_time = time.time()
metrics = analyzer.analyze_audio_file(audio_file)
analysis_time = time.time() - start_time

print(f"✅ Qualitäts-Score: {metrics['quality_score']:.2f}")
print(f"   SNR: {metrics['snr_db']:.1f} dB")
print(f"   Clipping: {metrics['clipping_ratio']:.2%}")
print(f"   Silence: {metrics['silence_ratio']:.2%}")
print(f"   Dauer: {metrics['duration']:.1f}s")
print(f"⏱️  Analyse-Zeit: {analysis_time:.2f}s\n")

# Model selection
if metrics['quality_score'] < 0.4:
    model = "large"
    print("🎯 Niedrige Qualität → large Modell")
elif metrics['quality_score'] < 0.6:
    model = "medium"
    print("🎯 Mittlere Qualität → medium Modell")
elif metrics['quality_score'] < 0.8:
    model = "medium"
    print("🎯 Gute Qualität → medium Modell")
else:
    model = "small"
    print("🎯 Sehr gute Qualität → small Modell")

print(f"\n🎤 Transkribiere mit {model} Modell...")
print("⏳ Das kann einige Minuten dauern...\n")

start_time = time.time()
result = v4.transcribe_with_whisper(
    audio_file,
    model_size=model,
    language="de",
    use_intelligent_pipeline=True,
    quality_score=metrics['quality_score'],
    quality_analyzer=analyzer,
    audio_preprocessor=preprocessor
)
transcription_time = time.time() - start_time

print(f"✅ Transkription fertig!")
print(f"⏱️  Zeit: {transcription_time:.1f}s ({transcription_time/60:.1f} min)")
print(f"📝 Text-Länge: {len(result['text'])} Zeichen")
print(f"📊 Segmente: {len(result.get('segments', []))}")

# Show first 500 characters
print(f"\n📄 Erste 500 Zeichen:\n")
print("-" * 50)
print(result['text'][:500])
print("-" * 50)

# Save to file
output_file = "Transkripte_LLM/test_transcription.txt"
Path("Transkripte_LLM").mkdir(exist_ok=True)
Path(output_file).write_text(result['text'], encoding='utf-8')
print(f"\n💾 Gespeichert in: {output_file}")

print(f"\n⏱️  Gesamt-Zeit: {(time.time() - start_time + analysis_time):.1f}s")
print(f"📊 Real-Time Factor: {(transcription_time + analysis_time) / metrics['duration']:.2f}x")
