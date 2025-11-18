"""Simple CPU-only diarization fallback using energy-based segmentation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import librosa
import numpy as np


@dataclass
class CPUFallbackSettings:
    top_db: float = 35.0
    max_speakers: int = 2


class CPUDiarizer:
    """Lightweight diarizer that alternates speakers on speech segments."""

    def __init__(self, settings: Optional[CPUFallbackSettings] = None):
        self.settings = settings or CPUFallbackSettings()

    def diarize(self, audio_path: Path, num_speakers: Optional[int] = None) -> List[Dict[str, Any]]:
        y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        if y.size == 0:
            return []

        intervals = librosa.effects.split(y, top_db=self.settings.top_db)
        if len(intervals) == 0:
            total = len(y) / sr
            return [self._segment(0.0, total, 0)]

        speaker_count = num_speakers or self.settings.max_speakers
        segments: List[Dict[str, Any]] = []
        speaker_idx = 0
        for start, end in intervals:
            seg = self._segment(start / sr, end / sr, speaker_idx)
            segments.append(seg)
            if speaker_count > 1:
                speaker_idx = (speaker_idx + 1) % speaker_count
        return segments

    def align_with_transcription(self, diarization_segments, transcription_segments):
        aligned = []
        for seg in transcription_segments:
            trans_start = seg['start']
            trans_end = seg['end']
            trans_mid = (trans_start + trans_end) / 2
            best_speaker = diarization_segments[0]['speaker'] if diarization_segments else 'Speaker A'
            max_overlap = 0.0
            for dia in diarization_segments:
                overlap_start = max(trans_start, dia['start'])
                overlap_end = min(trans_end, dia['end'])
                overlap = max(0.0, overlap_end - overlap_start)
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = dia['speaker']
                if dia['start'] <= trans_mid <= dia['end']:
                    best_speaker = dia['speaker']
                    break
            enriched = seg.copy()
            enriched['speaker'] = best_speaker
            aligned.append(enriched)
        return aligned

    @staticmethod
    def get_speaker_statistics(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        stats: Dict[str, Dict[str, Any]] = {}
        total_duration = 0.0
        for seg in segments:
            spk = seg['speaker']
            duration = seg['end'] - seg['start']
            total_duration += duration
            bucket = stats.setdefault(spk, {"total_duration": 0.0, "num_segments": 0})
            bucket["total_duration"] += duration
            bucket["num_segments"] += 1
        for bucket in stats.values():
            bucket["percentage"] = (bucket["total_duration"] / total_duration * 100.0) if total_duration else 0.0
        return stats

    def _segment(self, start: float, end: float, idx: int) -> Dict[str, Any]:
        speaker_label = chr(ord('A') + idx)
        return {
            'start': float(start),
            'end': float(end),
            'speaker': f"Speaker {speaker_label}",
            'speaker_id': f"CPU_{idx:02d}",
        }
