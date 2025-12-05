from pathlib import Path

from fastapi.testclient import TestClient

from services.transcription_service import api
from services.transcription_service.transcription_service import TranscriptionResponse


def test_api_transcribe_endpoint(monkeypatch, tmp_path: Path):
    dummy_file = tmp_path / "dummy.wav"
    dummy_file.write_bytes(b"RIFF....data")

    def fake_transcribe(_request):
        return TranscriptionResponse(
            text="hello api",
            segments=[{"text": "hello", "start": 0.0, "end": 0.5, "avg_logprob": -0.1, "no_speech_prob": 0.01}],
            confidence_scores={
                "segments": [
                    {"text": "hello", "start": 0.0, "end": 0.5, "confidence": 0.8},
                ],
                "low_confidence_threshold": 0.5,
                "overall_confidence": 0.8,
                "low_confidence_segments": [],
                "total_segments": 1,
            },
        )

    monkeypatch.setattr(api, "service", api.service)
    monkeypatch.setattr(api.service, "transcribe", fake_transcribe)

    client = TestClient(api.app)
    response = client.post(
        "/transcribe",
        data={"language": "de", "model_profile": "base"},
        files={"file": (dummy_file.name, dummy_file.read_bytes())},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["text"] == "hello api"
    assert payload["segments"]
    assert payload["confidence_scores"]["total_segments"] == 1
