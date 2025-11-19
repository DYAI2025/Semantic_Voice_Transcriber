#!/usr/bin/env python3
from pathlib import Path
import math
import wave
import struct

OUT = Path(__file__).parent / "audio" / "session1.wav"
OUT.parent.mkdir(parents=True, exist_ok=True)

def main():
    duration = 2.0
    sample_rate = 16000
    num_samples = int(duration * sample_rate)
    with wave.open(str(OUT), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            amplitude = 0.2 if i < num_samples // 2 else 0.5
            value = int(amplitude * math.sin(2 * math.pi * 440 * i / sample_rate) * 32767)
            wf.writeframes(struct.pack('<h', value))
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
