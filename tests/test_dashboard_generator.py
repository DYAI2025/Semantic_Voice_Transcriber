# tests/test_dashboard_generator.py
import pytest
from pathlib import Path
import json
from dashboard_generator import DashboardGenerator

@pytest.fixture
def sample_analysis_result():
    """Sample psychoanalysis result with all components"""
    return {
        "input_meta": {
            "language": "de",
            "text_type": "therapeutic_session",
            "transcript_file": "test_session.md"
        },
        "utterance_states": [
            {
                "id": 1,
                "speaker": "A",
                "text": "Ich weiß nicht, was ich sagen soll...",
                "ued_emotions": {
                    "valence": -0.6,
                    "arousal": 0.7,
                    "dominance": 0.3,
                    "discrete_emotions": {"fear": 0.6, "sadness": 0.4},
                    "confidence": 0.85
                },
                "markers": ["ATO_RESISTANCE_SILENCE"],
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
                "text": "Ich fühle mich jetzt viel besser!",
                "ued_emotions": {
                    "valence": 0.5,
                    "arousal": 0.6,
                    "dominance": 0.7,
                    "discrete_emotions": {"joy": 0.7, "trust": 0.5},
                    "confidence": 0.90
                },
                "markers": [],
                "prosody": {
                    "tempo_wpm": 125,
                    "pitch_hz": 165.2,
                    "energy_db": -12.3,
                    "pause_before_ms": 2500
                }
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
        },
        "turnpoints": [
            {
                "utterance_id": 2,
                "type": "emotional_shift",
                "description": "Valenzsprung: -0.60 → 0.50",
                "significance": "high",
                "prosody_support": "Pause 2500ms"
            },
            {
                "utterance_id": 2,
                "type": "resistance_breakthrough",
                "description": "Widerstand aufgelöst, positive Valenz",
                "markers_involved": ["ATO_RESISTANCE_SILENCE"],
                "significance": "high"
            }
        ]
    }

def test_dashboard_generator_initialization():
    """Dashboard generator should initialize"""
    generator = DashboardGenerator()
    assert generator is not None

def test_generate_dashboard_creates_html(sample_analysis_result, tmp_path):
    """Should generate complete HTML dashboard file"""
    generator = DashboardGenerator()
    output_path = tmp_path / "dashboard.html"

    generator.generate_dashboard(sample_analysis_result, output_path)

    # Verify file was created
    assert output_path.exists()

    # Read and verify HTML structure
    html_content = output_path.read_text(encoding='utf-8')

    # Check for essential HTML structure
    assert "<!DOCTYPE html>" in html_content
    assert "<html" in html_content
    assert "</html>" in html_content

    # Check for required libraries
    assert "chart.js" in html_content.lower() or "chartjs" in html_content.lower()
    assert "cytoscape" in html_content.lower()

def test_dashboard_contains_utterances(sample_analysis_result, tmp_path):
    """Dashboard should display utterances with annotations"""
    generator = DashboardGenerator()
    output_path = tmp_path / "dashboard.html"

    generator.generate_dashboard(sample_analysis_result, output_path)

    html_content = output_path.read_text(encoding='utf-8')

    # Check for utterance text
    assert "Ich weiß nicht, was ich sagen soll" in html_content
    assert "Ich fühle mich jetzt viel besser" in html_content

    # Check for speaker labels
    assert "Speaker A" in html_content or "Sprecher A" in html_content

    # Check for markers
    assert "ATO_RESISTANCE_SILENCE" in html_content

def test_dashboard_contains_emotion_chart_data(sample_analysis_result, tmp_path):
    """Dashboard should include Chart.js emotion trajectory data"""
    generator = DashboardGenerator()
    output_path = tmp_path / "dashboard.html"

    generator.generate_dashboard(sample_analysis_result, output_path)

    html_content = output_path.read_text(encoding='utf-8')

    # Check for Chart.js canvas
    assert "canvas" in html_content.lower()

    # Check for emotion data (should be in JavaScript) - German labels
    assert "valenz" in html_content.lower()
    assert "arousal" in html_content.lower()
    assert "dominanz" in html_content.lower()

    # Check for actual data points
    assert "-0.6" in html_content or "-0.60" in html_content
    assert "0.5" in html_content or "0.50" in html_content

def test_dashboard_contains_turnpoint_timeline(sample_analysis_result, tmp_path):
    """Dashboard should display turnpoints in timeline"""
    generator = DashboardGenerator()
    output_path = tmp_path / "dashboard.html"

    generator.generate_dashboard(sample_analysis_result, output_path)

    html_content = output_path.read_text(encoding='utf-8')

    # Check for turnpoint data
    assert "emotional_shift" in html_content or "Emotional Shift" in html_content or "Valenzsprung" in html_content
    assert "resistance_breakthrough" in html_content or "Widerstand aufgelöst" in html_content

    # Check for significance markers
    assert "high" in html_content.lower()

def test_dashboard_contains_ued_metrics(sample_analysis_result, tmp_path):
    """Dashboard should display UED metrics summary"""
    generator = DashboardGenerator()
    output_path = tmp_path / "dashboard.html"

    generator.generate_dashboard(sample_analysis_result, output_path)

    html_content = output_path.read_text(encoding='utf-8')

    # Check for UED metric labels
    assert "home" in html_content.lower() or "heimatbasis" in html_content.lower()
    assert "variability" in html_content.lower() or "variabilität" in html_content.lower()
    assert "instability" in html_content.lower() or "instabilität" in html_content.lower()

def test_dashboard_contains_marker_network(sample_analysis_result, tmp_path):
    """Dashboard should include Cytoscape.js marker network visualization"""
    generator = DashboardGenerator()
    output_path = tmp_path / "dashboard.html"

    generator.generate_dashboard(sample_analysis_result, output_path)

    html_content = output_path.read_text(encoding='utf-8')

    # Check for Cytoscape container
    assert "cytoscape" in html_content.lower()

    # Check for marker data
    assert "ATO_RESISTANCE_SILENCE" in html_content

def test_dashboard_responsive_layout(sample_analysis_result, tmp_path):
    """Dashboard should have responsive two-panel layout"""
    generator = DashboardGenerator()
    output_path = tmp_path / "dashboard.html"

    generator.generate_dashboard(sample_analysis_result, output_path)

    html_content = output_path.read_text(encoding='utf-8')

    # Check for CSS grid or flexbox layout
    assert "grid" in html_content.lower() or "flex" in html_content.lower()

    # Check for viewport meta tag (responsive design)
    assert "viewport" in html_content.lower()
