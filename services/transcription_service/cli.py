from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import TranscriptionConfig
from .model_manager import ModelProfile
from .transcription_service import TranscriptionRequest, TranscriptionService


def main():
    parser = argparse.ArgumentParser(description="CLI wrapper for the transcription service")
    parser.add_argument("audio", type=Path, help="Path to the audio file")
    parser.add_argument("--language", default="de", help="Language hint for Whisper")
    parser.add_argument("--model", default="base", help="Model profile name")
    parser.add_argument("--initial-prompt", dest="initial_prompt", help="Optional initial prompt")
    args = parser.parse_args()

    service = TranscriptionService(TranscriptionConfig.from_env())
    request = TranscriptionRequest(
        audio_path=args.audio,
        language=args.language,
        model_profile=ModelProfile(name=args.model),
        initial_prompt=args.initial_prompt,
    )
    response = service.transcribe(request)
    print(json.dumps(
        {
            "text": response.text,
            "segments": response.segments,
            "confidence_scores": response.confidence_scores,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
