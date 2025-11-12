import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from output_formatter import format_ato_markers
from html_formatter import create_correlation_badge

def test_format_ato_markers_with_confidence():
    """Test formatting ATO markers with confidence scores."""
    markers = ["ATO_ANXIETY_HESITATION", "ATO_TEMPO_SLOW"]
    confidence = {
        "ATO_ANXIETY_HESITATION": 0.85,
        "ATO_TEMPO_SLOW": 0.62
    }

    formatted = format_ato_markers(markers, confidence)

    assert "ATO_ANXIETY_HESITATION" in formatted
    assert "85%" in formatted or "0.85" in formatted
    assert "62%" in formatted or "0.62" in formatted

def test_create_correlation_badge_html():
    """Test creating HTML badge for correlation confidence."""
    html = create_correlation_badge("ATO_FEAR", 0.92)

    assert "ATO_FEAR" in html
    assert "92" in html
    assert "background-color" in html  # Should have styling