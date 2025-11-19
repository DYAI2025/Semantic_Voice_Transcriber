import numpy as np
import soundfile as sf
from pathlib import Path

from svt_core.audio.diarization_cpu import CPUDiarizer


def _write_wav(path: Path, freq: float, duration: float, sr: int = 16000):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * freq * t)
    sf.write(str(path), signal, sr)


def test_cpu_diarizer_segments(tmp_path):
    audio_path = tmp_path / "tone.wav"
    _write_wav(audio_path, 440, 1.0)
    diarizer = CPUDiarizer()
    segments = diarizer.diarize(audio_path)
    assert segments
    stats = diarizer.get_speaker_statistics(segments)
    assert stats


def test_cpu_diarizer_alignment(tmp_path):
    audio_path = tmp_path / "tone.wav"
    _write_wav(audio_path, 440, 1.0)
    diarizer = CPUDiarizer()
    segments = diarizer.diarize(audio_path)
    transcripts = [
        {'id': 0, 'start': 0.0, 'end': 0.5, 'text': 'hi'},
        {'id': 1, 'start': 0.5, 'end': 1.0, 'text': 'again'},
    ]
    aligned = diarizer.align_with_transcription(segments, transcripts)
    assert len(aligned) == len(transcripts)
    assert all('speaker' in seg for seg in aligned)
