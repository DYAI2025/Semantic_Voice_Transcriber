#!/usr/bin/env python3
"""
SOFORT-TEST - Minimaler Test aller Kernfunktionen

Testet:
✅ Sprechertrennung
✅ Spracherkennung
✅ HTML-Output
✅ Prosody-Marker
"""
import sys
from pathlib import Path

TEST_AUDIO = "Eingang/Patient/KAH EGOSTATE (2).m4a"

print("=" * 80)
print("SVT SOFORT-TEST")
print("=" * 80)
print()

# Check audio
if not Path(TEST_AUDIO).exists():
    print(f"❌ Audio nicht gefunden: {TEST_AUDIO}")
    sys.exit(1)
print(f"✓ Audio gefunden: {TEST_AUDIO}")
print()

# Run transcription
print("Transkribiere Audio (dauert 1-2 Minuten)...")
try:
    from auto_transcriber_v4_emotion import transcribe_with_whisper

    result = transcribe_with_whisper(
        TEST_AUDIO,
        model_size="small",  # Korrekt: model_size statt model_name
        language="de",
        enable_diarization=True,  # Korrekt: enable_diarization
        extract_prosody=True
    )

    segments = result.get('segments', [])
    print(f"✓ Transkription fertig: {len(segments)} Segmente")

    # Check speakers
    speakers = set(seg.get('speaker') for seg in segments if seg.get('speaker'))
    if speakers:
        print(f"✓ Sprechertrennung: {len(speakers)} Sprecher ({', '.join(sorted(speakers))})")
    else:
        print("⚠️  Keine Sprecher erkannt (bitte .env mit HF_TOKEN prüfen)")

    # Check prosody
    prosody = result.get('prosody_features', [])
    if prosody:
        print(f"✓ Prosody: {len(prosody)} Segmente analysiert")
    else:
        print("⚠️  Keine Prosody-Features")

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Generate outputs
print("Generiere Outputs...")
try:
    from output_formatter import OutputFormatter
    formatter = OutputFormatter()

    output_path = Path("Transkripte_LLM/SOFORT_TEST")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    outputs = formatter.format_all(
        result,
        TEST_AUDIO,
        output_path,
        generate_html=True
    )

    print("✓ Outputs generiert:")
    for fmt, path in outputs.items():
        if path and path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"  - {fmt.upper()}: {path.name} ({size_kb:.1f} KB)")

except Exception as e:
    print(f"❌ Output-Fehler: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("FERTIG!")
print(f"HTML öffnen: Transkripte_LLM/SOFORT_TEST.html")
print("=" * 80)
