# tests/test_psychoanalysis_pipeline.py
import pytest
from pathlib import Path
import json
import os
from psychoanalysis_pipeline import PsychoanalysisPipeline

@pytest.fixture
def sample_transcript():
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
                "prosody": {
                    "tempo_wpm": 85,
                    "pitch_hz": 147.8,
                    "energy_db": -18.5,
                    "pause_before_ms": 2500
                }
            },
            {
                "id": 2,
                "speaker": "A",
                "timestamp": "00:00:22",
                "text": "Ich fühle mich jetzt viel besser!",
                "prosody": {
                    "tempo_wpm": 125,
                    "pitch_hz": 165.2,
                    "energy_db": -12.3,
                    "pause_before_ms": 2500
                }
            }
        ]
    }

@pytest.fixture
def mock_api_response():
    """Mock OpenAI API response"""
    return {
        "input_meta": {
            "language": "de",
            "text_type": "therapeutic_session"
        },
        "utterance_states": [
            {
                "id": 1,
                "speaker": "A",
                "text": "Ich weiß nicht, was ich sagen soll...",
                "valence": -0.6,
                "arousal": 0.7,
                "dominance": 0.3,
                "discrete_emotions": {"fear": 0.6, "sadness": 0.4},
                "confidence": 0.85,
                "markers": ["ATO_RESISTANCE_SILENCE"]
            },
            {
                "id": 2,
                "speaker": "A",
                "text": "Ich fühle mich jetzt viel besser!",
                "valence": 0.5,
                "arousal": 0.6,
                "dominance": 0.7,
                "discrete_emotions": {"joy": 0.7, "trust": 0.5},
                "confidence": 0.90,
                "markers": []
            }
        ],
        "ued_metrics": {
            "home_base": {"valence": -0.05, "arousal": 0.65, "dominance": 0.50},
            "variability": {"valence": 0.55, "arousal": 0.05, "dominance": 0.20},
            "instability": {"valence": 0.78, "arousal": 0.12, "dominance": 0.28},
            "rise_rate": {"valence": 1.1, "arousal": -0.1, "dominance": 0.4},
            "recovery_rate": {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
        },
        "marker_summary": {
            "frequencies": {"ATO_RESISTANCE_SILENCE": 1},
            "dominance_ranking": ["ATO_RESISTANCE_SILENCE"]
        }
    }

def test_pipeline_initialization():
    """Pipeline should load config and initialize components"""
    pipeline = PsychoanalysisPipeline(config_path="config/psychoanalysis_config.yaml")

    assert pipeline.config is not None
    assert pipeline.cache is not None
    assert pipeline.turnpoint_detector is not None

@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_pipeline_with_api_call(sample_transcript, tmp_path):
    """Pipeline should call API and detect turnpoints (integration test)"""
    # Use temp cache to avoid polluting real cache
    pipeline = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=tmp_path / "cache"
    )

    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    result = pipeline.analyze_transcript(sample_transcript, skill_path)

    # Verify structure
    assert "utterance_states" in result
    assert "ued_metrics" in result
    assert "marker_summary" in result
    assert "turnpoints" in result

    # Verify turnpoints were detected (emotional shift from -0.6 to 0.5 valence)
    assert len(result["turnpoints"]) > 0

def test_pipeline_uses_cache(sample_transcript, mock_api_response, tmp_path, monkeypatch):
    """Pipeline should use cached results when available"""
    cache_dir = tmp_path / "cache"

    # Create pipeline
    pipeline = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=cache_dir
    )

    # Pre-populate cache
    pipeline.cache.save_analysis(sample_transcript, mock_api_response)

    # Mock API to ensure it's not called
    api_called = False

    def mock_analyze(*args, **kwargs):
        nonlocal api_called
        api_called = True
        return mock_api_response

    if pipeline.api is not None:
        monkeypatch.setattr(pipeline.api, "analyze_transcript", mock_analyze)

    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    result = pipeline.analyze_transcript(sample_transcript, skill_path)

    # Verify result came from cache (API should not be called)
    # If API key not set, api won't exist, so we skip this check
    if pipeline.api is not None:
        assert not api_called, "API should not be called when cache exists"

    # Verify structure
    assert "utterance_states" in result
    assert "turnpoints" in result

def test_pipeline_merges_prosody_data(sample_transcript, mock_api_response, tmp_path):
    """Pipeline should merge prosody data from transcript into utterance states"""
    pipeline = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=tmp_path / "cache"
    )

    # Pre-populate cache to avoid API call
    pipeline.cache.save_analysis(sample_transcript, mock_api_response)

    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    result = pipeline.analyze_transcript(sample_transcript, skill_path)

    # Verify prosody data was merged into utterances
    assert "ued_emotions" in result["utterance_states"][0]
    assert "prosody" in result["utterance_states"][0]
    assert result["utterance_states"][0]["prosody"]["tempo_wpm"] == 85
    assert result["utterance_states"][0]["prosody"]["pause_before_ms"] == 2500

def test_pipeline_detects_turnpoints(sample_transcript, mock_api_response, tmp_path):
    """Pipeline should detect turnpoints using tri-modal algorithm"""
    pipeline = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=tmp_path / "cache"
    )

    # Pre-populate cache
    pipeline.cache.save_analysis(sample_transcript, mock_api_response)

    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    result = pipeline.analyze_transcript(sample_transcript, skill_path)

    # Verify turnpoints were detected
    assert "turnpoints" in result
    assert len(result["turnpoints"]) > 0

    # Find emotional_shift turnpoint (valence jump -0.6 → 0.5 = 1.1)
    emotional_shifts = [tp for tp in result["turnpoints"] if tp["type"] == "emotional_shift"]
    assert len(emotional_shifts) > 0

    # Verify prosody enhancement (long pause should increase significance)
    assert emotional_shifts[0]["significance"] == "high"
    assert "prosody_support" in emotional_shifts[0]
