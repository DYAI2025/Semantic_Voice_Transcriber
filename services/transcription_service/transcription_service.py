from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .config import TranscriptionConfig
from .model_manager import ModelManager, ModelProfile

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionRequest:
    audio_path: Path
    language: str = "de"
    model_profile: ModelProfile = field(default_factory=ModelProfile)
    initial_prompt: Optional[str] = None


@dataclass
class TranscriptionResponse:
    text: str
    segments: List[Dict[str, Any]]
    confidence_scores: Dict[str, Any]
    extras: Dict[str, Any] = field(default_factory=dict)


class TranscriptionService:
    """Isolated Whisper runner with optional adapters for extra features."""

    def __init__(
        self,
        config: Optional[TranscriptionConfig] = None,
        model_manager: Optional[ModelManager] = None,
        prosody_adapter: Optional[Any] = None,
        diarization_adapter: Optional[Any] = None,
    ) -> None:
        self.config = config or TranscriptionConfig.from_env()
        self.model_manager = model_manager or ModelManager(self.config)
        self.prosody_adapter = prosody_adapter
        self.diarization_adapter = diarization_adapter

    def transcribe(self, request: TranscriptionRequest) -> TranscriptionResponse:
        logger.info("Starting transcription for %s", request.audio_path)
        model = self.model_manager.load(request.model_profile)

        # Run Whisper
        raw_result = model.transcribe(
            str(request.audio_path),
            language=request.language,
            verbose=False,
            word_timestamps=True,
            initial_prompt=request.initial_prompt,
        )

        confidence_scores = _extract_confidence_scores(raw_result)
        extras: Dict[str, Any] = {}

        if self.prosody_adapter:
            extras["prosody"] = self.prosody_adapter.attach(raw_result, request)

        if self.diarization_adapter:
            extras["diarization"] = self.diarization_adapter.attach(raw_result, request)

        response = TranscriptionResponse(
            text=raw_result.get("text", ""),
            segments=raw_result.get("segments", []),
            confidence_scores=confidence_scores,
            extras=extras,
        )
        logger.info("Finished transcription for %s", request.audio_path)
        return response


def _extract_confidence_scores(
    whisper_result: Dict[str, Any],
    low_confidence_threshold: float = 0.5,
) -> Dict[str, Any]:
    segments = whisper_result.get("segments", [])
    segment_confidences = []
    low_confidence_segments = []
    total_confidence = 0.0

    for seg in segments:
        avg_logprob = seg.get("avg_logprob", -1.0)
        no_speech_prob = seg.get("no_speech_prob", 0.0)
        confidence = min(1.0, max(0.0, np.exp(avg_logprob) * (1 - no_speech_prob)))

        segment_info = {
            "text": seg.get("text", "").strip(),
            "start": seg.get("start", 0.0),
            "end": seg.get("end", 0.0),
            "confidence": float(confidence),
            "avg_logprob": float(avg_logprob),
            "no_speech_prob": float(no_speech_prob),
        }

        segment_confidences.append(segment_info)
        total_confidence += confidence

        if confidence < low_confidence_threshold:
            low_confidence_segments.append(segment_info)

    overall_confidence = total_confidence / len(segments) if segments else 0.0

    return {
        "overall_confidence": float(overall_confidence),
        "segments": segment_confidences,
        "low_confidence_segments": low_confidence_segments,
        "low_confidence_threshold": low_confidence_threshold,
        "total_segments": len(segments),
    }


def mark_low_confidence_segments(transcription_result: Dict[str, Any]) -> str:
    text = transcription_result.get("text", "")
    confidence_scores = transcription_result.get("confidence_scores", {})
    segments = confidence_scores.get("segments", [])
    if not segments:
        return text

    marked_text = text
    sorted_segments = sorted(segments, key=lambda s: s["start"], reverse=True)

    for seg in sorted_segments:
        if seg["confidence"] < confidence_scores.get("low_confidence_threshold", 0.5):
            seg_text = seg.get("text", "").strip()
            if seg_text and seg_text in marked_text:
                marker = f" [UNSICHER:{seg['confidence']:.2f}]"
                marked_text = marked_text.replace(seg_text, seg_text + marker, 1)

    return marked_text


_default_service: Optional[TranscriptionService] = None


def _get_default_service() -> TranscriptionService:
    global _default_service
    if _default_service is None:
        _default_service = TranscriptionService()
    return _default_service


def transcribe_with_whisper(
    audio_path: str,
    model_size: str = "base",
    language: str = "de",
    initial_prompt: Optional[str] = None,
    **_: Any,
) -> Dict[str, Any]:
    """Compatibility wrapper delegating to the isolated service."""

    request = TranscriptionRequest(
        audio_path=Path(audio_path),
        language=language,
        model_profile=ModelProfile(name=model_size),
        initial_prompt=initial_prompt,
    )
    response = _get_default_service().transcribe(request)
    return {
        "text": response.text,
        "segments": response.segments,
        "confidence_scores": response.confidence_scores,
        **({"prosody_features": response.extras.get("prosody")} if response.extras else {}),
    }
