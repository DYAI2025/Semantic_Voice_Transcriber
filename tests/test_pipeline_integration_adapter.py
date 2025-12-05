from pathlib import Path

from services.transcription_service.pipeline_integration import (
    PipelineIntegrationResult,
    run_pipeline_with_service_sync,
)


class StubClient:
    async def transcribe(self, audio_path: Path, language: str, model_profile: str, initial_prompt):
        return {
            "text": f"ok:{audio_path.name}",
            "segments": [],
            "confidence_scores": {
                "segments": [],
                "low_confidence_threshold": 0.5,
                "overall_confidence": 0.0,
                "low_confidence_segments": [],
                "total_segments": 0,
            },
        }


def test_pipeline_adapter_enriches(monkeypatch, tmp_path: Path):
    dummy_audio = tmp_path / "demo.wav"
    dummy_audio.write_text("audio")

    def enrich(transcription):
        return {"prosody": "stub", "source": transcription["text"]}

    result: PipelineIntegrationResult = run_pipeline_with_service_sync(
        dummy_audio,
        client=StubClient(),
        prosody_enricher=lambda tx: enrich(tx),
    )

    assert result.transcription["text"].startswith("ok:")
    assert "prosody" in result.extras
