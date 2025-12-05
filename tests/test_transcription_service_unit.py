import json
from pathlib import Path

import pytest

from services.transcription_service.model_manager import ModelProfile
from services.transcription_service.transcription_service import (
    TranscriptionRequest,
    TranscriptionService,
)


class StubModel:
    def __init__(self, result):
        self.result = result

    def transcribe(self, *_args, **_kwargs):
        return self.result


class StubManager:
    def __init__(self, result):
        self.result = result

    def load(self, _profile: ModelProfile):
        return StubModel(self.result)


@pytest.fixture()
def stub_result(tmp_path: Path):
    return {
        "text": "hello world",
        "segments": [
            {"text": "hello", "start": 0.0, "end": 0.5, "avg_logprob": -0.1, "no_speech_prob": 0.01},
            {"text": "world", "start": 0.5, "end": 1.0, "avg_logprob": -0.3, "no_speech_prob": 0.02},
        ],
    }


def test_transcription_service_calculates_confidence(stub_result):
    service = TranscriptionService(model_manager=StubManager(stub_result))
    request = TranscriptionRequest(audio_path=Path("dummy.wav"))

    response = service.transcribe(request)

    assert response.text == "hello world"
    assert response.confidence_scores["total_segments"] == 2
    assert response.confidence_scores["overall_confidence"] > 0


def test_transcription_service_serializable(stub_result):
    service = TranscriptionService(model_manager=StubManager(stub_result))
    request = TranscriptionRequest(audio_path=Path("dummy.wav"))

    response = service.transcribe(request)
    payload = {
        "text": response.text,
        "segments": response.segments,
        "confidence_scores": response.confidence_scores,
    }

    serialized = json.dumps(payload)
    assert "hello world" in serialized
