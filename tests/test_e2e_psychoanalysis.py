# tests/test_e2e_psychoanalysis.py
"""End-to-end integration test for complete psychoanalysis pipeline"""
import pytest
from pathlib import Path
import json
import os
from psychoanalysis_pipeline import PsychoanalysisPipeline
from dashboard_generator import DashboardGenerator


@pytest.fixture
def sample_transcript_full():
    """Full sample transcript with prosody for E2E test"""
    return {
        "transcript_meta": {
            "file": "therapeutic_session_001.md",
            "speaker_labels": ["Therapeut", "Patient"],
            "duration_seconds": 180,
            "timestamp": "2024-01-15T14:30:00"
        },
        "utterances": [
            {
                "id": 1,
                "speaker": "Patient",
                "timestamp": "00:00:05",
                "text": "Ich weiß nicht, wo ich anfangen soll...",
                "prosody": {
                    "tempo_wpm": 75,
                    "pitch_hz": 142.3,
                    "energy_db": -20.1,
                    "pause_before_ms": 3000
                }
            },
            {
                "id": 2,
                "speaker": "Therapeut",
                "timestamp": "00:00:12",
                "text": "Nehmen Sie sich Zeit. Was bewegt Sie heute?",
                "prosody": {
                    "tempo_wpm": 110,
                    "pitch_hz": 165.8,
                    "energy_db": -14.2,
                    "pause_before_ms": 800
                }
            },
            {
                "id": 3,
                "speaker": "Patient",
                "timestamp": "00:00:22",
                "text": "Ich fühle mich so schuldig wegen allem.",
                "prosody": {
                    "tempo_wpm": 80,
                    "pitch_hz": 138.5,
                    "energy_db": -22.5,
                    "pause_before_ms": 2200
                }
            },
            {
                "id": 4,
                "speaker": "Patient",
                "timestamp": "00:00:35",
                "text": "Aber eigentlich... nein, das stimmt nicht. Ich bin nicht schuld.",
                "prosody": {
                    "tempo_wpm": 95,
                    "pitch_hz": 155.2,
                    "energy_db": -16.3,
                    "pause_before_ms": 1500
                }
            },
            {
                "id": 5,
                "speaker": "Therapeut",
                "timestamp": "00:00:48",
                "text": "Sie haben gerade etwas Wichtiges erkannt.",
                "prosody": {
                    "tempo_wpm": 105,
                    "pitch_hz": 168.4,
                    "energy_db": -13.8,
                    "pause_before_ms": 700
                }
            },
            {
                "id": 6,
                "speaker": "Patient",
                "timestamp": "00:00:58",
                "text": "Ja, ich fühle mich jetzt viel leichter!",
                "prosody": {
                    "tempo_wpm": 130,
                    "pitch_hz": 172.6,
                    "energy_db": -11.5,
                    "pause_before_ms": 600
                }
            }
        ]
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for E2E test"""
    return {
        "input_meta": {
            "language": "de",
            "text_type": "therapeutic_session",
            "notes": "Therapeutisches Erstgespräch mit Schuld-Thematik"
        },
        "utterance_states": [
            {
                "id": 1,
                "speaker": "Patient",
                "text": "Ich weiß nicht, wo ich anfangen soll...",
                "valence": -0.5,
                "arousal": 0.6,
                "dominance": 0.2,
                "discrete_emotions": {"fear": 0.5, "sadness": 0.4},
                "confidence": 0.80,
                "markers": ["ATO_RESISTANCE_SILENCE"]
            },
            {
                "id": 2,
                "speaker": "Therapeut",
                "text": "Nehmen Sie sich Zeit. Was bewegt Sie heute?",
                "valence": 0.3,
                "arousal": 0.4,
                "dominance": 0.6,
                "discrete_emotions": {"trust": 0.6, "anticipation": 0.4},
                "confidence": 0.90,
                "markers": []
            },
            {
                "id": 3,
                "speaker": "Patient",
                "text": "Ich fühle mich so schuldig wegen allem.",
                "valence": -0.7,
                "arousal": 0.7,
                "dominance": 0.1,
                "discrete_emotions": {"sadness": 0.7, "fear": 0.5},
                "confidence": 0.85,
                "markers": ["ATO_THEME_SHAME_GUILT"]
            },
            {
                "id": 4,
                "speaker": "Patient",
                "text": "Aber eigentlich... nein, das stimmt nicht. Ich bin nicht schuld.",
                "valence": 0.2,
                "arousal": 0.5,
                "dominance": 0.6,
                "discrete_emotions": {"anticipation": 0.5, "trust": 0.4},
                "confidence": 0.88,
                "markers": ["ATO_DEFENSE_DENIAL"]
            },
            {
                "id": 5,
                "speaker": "Therapeut",
                "text": "Sie haben gerade etwas Wichtiges erkannt.",
                "valence": 0.4,
                "arousal": 0.3,
                "dominance": 0.5,
                "discrete_emotions": {"trust": 0.7, "joy": 0.3},
                "confidence": 0.92,
                "markers": []
            },
            {
                "id": 6,
                "speaker": "Patient",
                "text": "Ja, ich fühle mich jetzt viel leichter!",
                "valence": 0.7,
                "arousal": 0.5,
                "dominance": 0.7,
                "discrete_emotions": {"joy": 0.8, "trust": 0.6},
                "confidence": 0.95,
                "markers": []
            }
        ],
        "ued_metrics": {
            "home_base": {"valence": 0.0, "arousal": 0.5, "dominance": 0.45},
            "variability": {"valence": 0.60, "arousal": 0.15, "dominance": 0.25},
            "instability": {"valence": 0.82, "arousal": 0.20, "dominance": 0.35},
            "rise_rate": {"valence": 1.2, "arousal": -0.1, "dominance": 0.5},
            "recovery_rate": {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
        },
        "marker_summary": {
            "frequencies": {
                "ATO_RESISTANCE_SILENCE": 1,
                "ATO_THEME_SHAME_GUILT": 1,
                "ATO_DEFENSE_DENIAL": 1
            },
            "dominance_ranking": [
                "ATO_THEME_SHAME_GUILT",
                "ATO_RESISTANCE_SILENCE",
                "ATO_DEFENSE_DENIAL"
            ]
        },
        "psychological_lenses": {
            "primary_conflict": "Schuld-Verleugnung-Dynamik",
            "defense_pattern": "Verleugnungstendenz bei Schuldthemen",
            "therapeutic_progress": "Durchbruch am Ende erkennbar"
        },
        "disclaimers": {
            "no_diagnosis": "Keine klinische Diagnose",
            "reflection_tool": "Therapeutisches Reflexionswerkzeug"
        }
    }


def test_e2e_pipeline_with_mock_api(sample_transcript_full, mock_openai_response, tmp_path, monkeypatch):
    """E2E test: Full pipeline from transcript to dashboard with mocked API"""

    # Setup
    cache_dir = tmp_path / "cache"
    pipeline = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=cache_dir
    )

    # Mock OpenAI API
    def mock_analyze_transcript(self, transcript_data, skill_path):
        return mock_openai_response

    if pipeline.api:
        monkeypatch.setattr(pipeline.api, "analyze_transcript", lambda td, sp: mock_openai_response)

    # Pre-populate cache to avoid API call
    pipeline.cache.save_analysis(sample_transcript_full, mock_openai_response)

    # Get skill path
    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    # Step 1: Run pipeline
    result = pipeline.analyze_transcript(sample_transcript_full, skill_path)

    # Verify pipeline output
    assert "utterance_states" in result
    assert "ued_metrics" in result
    assert "turnpoints" in result
    assert len(result["utterance_states"]) == 6

    # Step 2: Verify turnpoints were detected
    turnpoints = result["turnpoints"]
    assert len(turnpoints) > 0

    # Should detect emotional shift from negative to positive
    emotional_shifts = [tp for tp in turnpoints if tp["type"] == "emotional_shift"]
    assert len(emotional_shifts) > 0

    # Should detect resistance breakthrough (utterance 1 → 4)
    resistance_breakthroughs = [tp for tp in turnpoints if tp["type"] == "resistance_breakthrough"]
    assert len(resistance_breakthroughs) > 0

    # Step 3: Generate dashboard
    generator = DashboardGenerator()
    dashboard_path = tmp_path / "e2e_dashboard.html"

    generator.generate_dashboard(result, dashboard_path)

    # Verify dashboard was created
    assert dashboard_path.exists()
    assert dashboard_path.stat().st_size > 0

    # Step 4: Verify dashboard content
    html_content = dashboard_path.read_text(encoding='utf-8')

    # Check for all key components
    assert "<!DOCTYPE html>" in html_content
    assert "Chart.js" in html_content or "chart.js" in html_content
    assert "Cytoscape" in html_content or "cytoscape" in html_content

    # Check for utterance text
    assert "Ich weiß nicht, wo ich anfangen soll" in html_content
    assert "fühle mich jetzt viel leichter" in html_content

    # Check for markers
    assert "ATO_RESISTANCE_SILENCE" in html_content
    assert "ATO_THEME_SHAME_GUILT" in html_content
    assert "ATO_DEFENSE_DENIAL" in html_content

    # Check for UED metrics
    assert "heimatbasis" in html_content.lower() or "home" in html_content.lower()

    # Check for turnpoints
    assert "wendepunkte" in html_content.lower() or "turnpoint" in html_content.lower()


def test_e2e_cache_reuse(sample_transcript_full, mock_openai_response, tmp_path):
    """E2E test: Verify cache is reused on second run"""

    cache_dir = tmp_path / "cache"

    # First run
    pipeline1 = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=cache_dir
    )

    # Pre-populate cache
    pipeline1.cache.save_analysis(sample_transcript_full, mock_openai_response)

    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    result1 = pipeline1.analyze_transcript(sample_transcript_full, skill_path)

    # Second run (should use cache)
    pipeline2 = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=cache_dir
    )

    result2 = pipeline2.analyze_transcript(sample_transcript_full, skill_path)

    # Results should be identical (from cache)
    assert result1["ued_metrics"] == result2["ued_metrics"]
    assert len(result1["utterance_states"]) == len(result2["utterance_states"])
    assert len(result1["turnpoints"]) == len(result2["turnpoints"])


def test_e2e_prosody_integration(sample_transcript_full, mock_openai_response, tmp_path):
    """E2E test: Verify prosody data flows through entire pipeline"""

    cache_dir = tmp_path / "cache"
    pipeline = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=cache_dir
    )

    # Pre-populate cache
    pipeline.cache.save_analysis(sample_transcript_full, mock_openai_response)

    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    result = pipeline.analyze_transcript(sample_transcript_full, skill_path)

    # Verify prosody data is present in utterances
    for utt_state in result["utterance_states"]:
        assert "prosody" in utt_state
        assert "tempo_wpm" in utt_state["prosody"]
        assert "pitch_hz" in utt_state["prosody"]
        assert "pause_before_ms" in utt_state["prosody"]

    # Verify prosody enhanced turnpoints (long pauses should trigger high significance)
    emotional_shifts = [tp for tp in result["turnpoints"] if tp["type"] == "emotional_shift"]

    # Find shifts with prosody support
    prosody_enhanced = [tp for tp in emotional_shifts if "prosody_support" in tp]

    # At least one turnpoint should have prosody enhancement (pause > 2000ms)
    assert len(prosody_enhanced) > 0


def test_e2e_marker_network_in_dashboard(sample_transcript_full, mock_openai_response, tmp_path):
    """E2E test: Verify marker network visualization is included in dashboard"""

    cache_dir = tmp_path / "cache"
    pipeline = PsychoanalysisPipeline(
        config_path="config/psychoanalysis_config.yaml",
        cache_dir=cache_dir
    )

    pipeline.cache.save_analysis(sample_transcript_full, mock_openai_response)

    skill_path = Path(__file__).parent.parent.parent / "emotion_dynaminc-skill" / "emotion-dynamics-deep-insight" / "SKILL.md"

    result = pipeline.analyze_transcript(sample_transcript_full, skill_path)

    # Generate dashboard
    generator = DashboardGenerator()
    dashboard_path = tmp_path / "network_dashboard.html"
    generator.generate_dashboard(result, dashboard_path)

    html_content = dashboard_path.read_text(encoding='utf-8')

    # Verify Cytoscape.js network is present
    assert "cytoscape" in html_content.lower()
    assert "cytoscape-container" in html_content

    # Verify network contains marker nodes
    assert "ATO_RESISTANCE_SILENCE" in html_content or "resistance_silence" in html_content.lower()
