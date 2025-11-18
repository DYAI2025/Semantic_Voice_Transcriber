import json
from pathlib import Path

from audit.cli import render_markdown


def test_render_markdown_basic():
    report = {
        "session": "s1",
        "features": {
            "emotions": {
                "name": "Emotion",
                "readiness": {"label": "pilot ready"},
                "availability": {"status": "ok"},
                "smoke": {"status": "pass"},
            }
        }
    }
    md = render_markdown(report)
    assert "Emotion" in md
    assert "pilot ready" in md
