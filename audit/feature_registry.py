"""Central registry for advanced SVT features."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from audit.checks.emotion_checks import emotion_availability, emotion_smoke
from audit.checks.prosody_checks import prosody_availability, prosody_smoke
from audit.checks.memory_checks import memory_availability, memory_smoke
from audit.checks.diarization_checks import diarization_availability, diarization_smoke
from audit.checks.turning_points_checks import turning_points_availability, turning_points_smoke
from audit.checks.dual_marker_checks import dual_marker_availability, dual_marker_smoke
from audit.checks.speaker_view_checks import speaker_view_availability, speaker_view_smoke


AvailabilityResult = Dict[str, str]
SmokeResult = Dict[str, str]


def _placeholder_availability(_: "FeatureMetadata") -> AvailabilityResult:
    return {"status": "unknown", "details": "Check not implemented"}


def _placeholder_smoke(_: "FeatureMetadata") -> SmokeResult:
    return {"status": "not_run", "details": "Smoke test not implemented"}


@dataclass(frozen=True)
class FeatureMetadata:
    key: str
    name: str
    modules: List[str]
    description: str
    availability_check: Callable[["FeatureMetadata"], AvailabilityResult] = _placeholder_availability
    smoke_test: Callable[["FeatureMetadata"], SmokeResult] = _placeholder_smoke


FEATURE_REGISTRY: Dict[str, FeatureMetadata] = {
    "emotions": FeatureMetadata(
        key="emotions",
        name="Emotionale Analyse",
        modules=["auto_transcriber_v4_emotion.EmotionalAnalyzer"],
        description="Sentiment- und Marker-basierte Emotionserkennung.",
        availability_check=emotion_availability,
        smoke_test=emotion_smoke,
    ),
    "prosody": FeatureMetadata(
        key="prosody",
        name="Prosody Extraktion",
        modules=["prosody_extractor", "prosody_analyzer"],
        description="Pitch/Tempo/Energy Analyse pro Segment.",
        availability_check=prosody_availability,
        smoke_test=prosody_smoke,
    ),
    "memory_profile": FeatureMetadata(
        key="memory_profile",
        name="Therapeutische Memory Profile",
        modules=["Memory", "psychoanalysis_cache"],
        description="Speicherung von YAML/SQLite Profilen.",
        availability_check=memory_availability,
        smoke_test=memory_smoke,
    ),
    "diarization": FeatureMetadata(
        key="diarization",
        name="Sprechertrennung",
        modules=["speaker_diarizer", "svt_core.audio.diarization_cpu"],
        description="pyannote + CPU-Fallback Diarisierung.",
        availability_check=diarization_availability,
        smoke_test=diarization_smoke,
    ),
    "turning_points": FeatureMetadata(
        key="turning_points",
        name="Wendepunkte-Erkennung",
        modules=["Turning_Points_in_Transcription"],
        description="TurningPointsLayer + Detector Pipeline.",
        availability_check=turning_points_availability,
        smoke_test=turning_points_smoke,
    ),
    "dual_markers": FeatureMetadata(
        key="dual_markers",
        name="Duale Marker",
        modules=["Turning_Points_in_Transcription.integration.dual_marker_system"],
        description="Kombination therapeutischer Marker-Ebenen.",
        availability_check=dual_marker_availability,
        smoke_test=dual_marker_smoke,
    ),
    "speaker_view": FeatureMetadata(
        key="speaker_view",
        name="Erweiterte Sprecherdarstellung",
        modules=["speaker_visualizer_v2"],
        description="Visualisierung von Sprecher-Timelines.",
        availability_check=speaker_view_availability,
        smoke_test=speaker_view_smoke,
    ),
}


def iter_features() -> List[FeatureMetadata]:
    return list(FEATURE_REGISTRY.values())
