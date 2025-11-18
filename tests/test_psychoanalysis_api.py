# tests/test_psychoanalysis_api.py
import pytest
from pathlib import Path
from psychoanalysis_api import PsychoanalysisAPI
import json
import os

@pytest.fixture
def mock_transcript():
    """Sample transcript data"""
    return {
        "transcript_meta": {
            "file": "test_session.md",
            "speaker_labels": ["A", "B"],
            "duration_seconds": 300,
            "timestamp": "2024-01-15T14:30:00"
        },
        "utterances": [
            {
                "id": 1,
                "speaker": "A",
                "timestamp": "00:00:15",
                "text": "Ich weiß nicht, was ich sagen soll...",
                "prosody": {"tempo_wpm": 85, "pitch_hz": 147.8}
            }
        ]
    }

@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_api_client_initialization():
    """API client should initialize with config"""
    api = PsychoanalysisAPI(config_path="config/psychoanalysis_config.yaml")
    assert api.model == "gpt-4-turbo-preview"
    assert api.max_tokens == 4096

def test_build_system_prompt(mock_transcript):
    """System prompt should include SKILL.md content"""
    # Skip if no API key (but can still test prompt building)
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping API client init")

    api = PsychoanalysisAPI(config_path="config/psychoanalysis_config.yaml")
    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    system_prompt = api.build_system_prompt(skill_path)

    assert "emotion-dynamics-deep-insight" in system_prompt
    assert "Utterance Emotion Dynamics" in system_prompt or "UED" in system_prompt
    assert "Workflow" in system_prompt or "Anweisungen" in system_prompt

def test_build_user_prompt(mock_transcript):
    """User prompt should format transcript as JSON"""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    api = PsychoanalysisAPI(config_path="config/psychoanalysis_config.yaml")

    user_prompt = api.build_user_prompt(mock_transcript)

    assert "test_session.md" in user_prompt
    assert "Ich weiß nicht" in user_prompt

def test_build_function_schema():
    """Function schema should enforce unified JSON structure"""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    api = PsychoanalysisAPI(config_path="config/psychoanalysis_config.yaml")

    schema = api.build_function_schema()

    assert schema["name"] == "analyze_transcript_ued_markers"
    assert "parameters" in schema
    assert "properties" in schema["parameters"]
    assert "utterance_states" in schema["parameters"]["properties"]
    assert "ued_metrics" in schema["parameters"]["properties"]
    assert "marker_summary" in schema["parameters"]["properties"]
