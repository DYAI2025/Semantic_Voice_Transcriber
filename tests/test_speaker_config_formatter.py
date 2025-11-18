#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SpeakerConfig and new therapeutic format in OutputFormatter
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from output_formatter import SpeakerConfig, OutputFormatter
import tempfile


def test_speaker_config_modes():
    """Test all SpeakerConfig modes"""

    print("\n=== Testing SpeakerConfig Modes ===\n")

    # Test MODE_ANONYMOUS (default)
    config_anon = SpeakerConfig(mode=SpeakerConfig.MODE_ANONYMOUS)

    assert config_anon.get_speaker_label("SPEAKER_00") == "Therapeut"
    assert config_anon.get_speaker_label("SPEAKER_01") == "Patient"
    assert config_anon.get_speaker_label("Patient") == "Patient"
    assert config_anon.get_speaker_label(None) == "Unknown"
    print("✅ MODE_ANONYMOUS passed")

    # Test MODE_LETTERS
    config_letters = SpeakerConfig(mode=SpeakerConfig.MODE_LETTERS)

    assert config_letters.get_speaker_label("SPEAKER_00") == "Speaker A"
    assert config_letters.get_speaker_label("SPEAKER_01") == "Speaker B"
    assert config_letters.get_speaker_label("SPEAKER_02") == "Speaker C"
    print("✅ MODE_LETTERS passed")

    # Test MODE_NAMES
    config_names = SpeakerConfig(mode=SpeakerConfig.MODE_NAMES)

    assert config_names.get_speaker_label("Dr. Schmidt") == "Dr. Schmidt"
    assert config_names.get_speaker_label("Maria") == "Maria"
    print("✅ MODE_NAMES passed")

    # Test MODE_CUSTOM
    custom_mapping = {
        "SPEAKER_00": "Therapeutin Dr. Meyer",
        "SPEAKER_01": "Patient Hans"
    }
    config_custom = SpeakerConfig(
        mode=SpeakerConfig.MODE_CUSTOM,
        custom_mapping=custom_mapping
    )

    assert config_custom.get_speaker_label("SPEAKER_00") == "Therapeutin Dr. Meyer"
    assert config_custom.get_speaker_label("SPEAKER_01") == "Patient Hans"
    print("✅ MODE_CUSTOM passed")

    print("\n✅ All SpeakerConfig modes working correctly!\n")


def test_markdown_format():
    """Test new therapeutic markdown format"""

    print("\n=== Testing Markdown Format ===\n")

    # Create formatter with anonymous mode
    config = SpeakerConfig(mode=SpeakerConfig.MODE_ANONYMOUS)
    formatter = OutputFormatter(speaker_config=config)

    # Mock transcription result
    mock_result = {
        'segments': [
            {
                'id': 0,
                'start': 5.0,
                'end': 12.0,
                'text': 'Alles gut heute Morgen? Gut geschlafen?',
                'speaker': 'SPEAKER_00'
            },
            {
                'id': 1,
                'start': 12.5,
                'end': 18.0,
                'text': 'Ja, ich habe gut geschlafen. Träume gehabt.',
                'speaker': 'SPEAKER_01',
                'ato_markers': ['ATO_AFFIRMATION', 'ATO_THEME_SLEEP']
            }
        ],
        'prosody_features': [
            {
                'tempo_wpm': 115.0,
                'tempo_deviation_pct': -7.9,
                'pitch_mean_hz': 161.5,
                'pitch_deviation_pct': -6.8,
                'energy_rms': 0.0212,
                'energy_deviation_pct': 48.8,
                'pause_before_ms': 0
            },
            {
                'tempo_wpm': 125.0,
                'tempo_deviation_pct': 5.0,
                'pitch_mean_hz': 145.0,
                'pitch_deviation_pct': 3.0,
                'energy_rms': 0.015,
                'energy_deviation_pct': -10.0,
                'pause_before_ms': 500
            }
        ],
        'prosody_baseline': {
            'tempo_wpm_mean': 125.0,
            'pitch_mean_hz': 173.0,
            'energy_rms_mean': 0.0143
        },
        'confidence_scores': {
            'overall_confidence': 0.92,
            'segments': [
                {'confidence': 0.95},
                {'confidence': 0.89}
            ]
        }
    }

    # Generate markdown
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_transcript"
        files = formatter.format_transcript(
            mock_result,
            "test_audio.m4a",
            output_path,
            include_prosody_markers=True
        )

        # Read markdown
        with open(files['markdown'], 'r', encoding='utf-8') as f:
            markdown = f.read()

        print("Generated Markdown:\n")
        print("-" * 80)
        print(markdown)
        print("-" * 80)

        # Verify format
        assert "### **Therapeut** | 00:05 - 00:12" in markdown
        assert "### **Patient** | 00:12 - 00:18" in markdown
        assert "> **Metadaten:**" in markdown
        assert "📊 **Prosody**:" in markdown
        assert "🔍 **Marker**:" in markdown
        assert "ATO_AFFIRMATION" in markdown

        print("\n✅ Markdown format verified!\n")


def test_html_enhanced():
    """Test enhanced HTML generation"""

    print("\n=== Testing Enhanced HTML ===\n")

    # Create formatter
    config = SpeakerConfig(mode=SpeakerConfig.MODE_ANONYMOUS)
    formatter = OutputFormatter(speaker_config=config)

    # Mock data
    mock_result = {
        'segments': [
            {
                'id': 0,
                'start': 5.0,
                'end': 12.0,
                'text': 'Wie geht es Ihnen heute?',
                'speaker': 'SPEAKER_00'
            }
        ],
        'prosody_features': [
            {
                'tempo_wpm': 115.0,
                'tempo_deviation_pct': -7.9,
                'pitch_mean_hz': 161.5,
                'pitch_deviation_pct': -6.8,
                'energy_rms': 0.0212,
                'energy_deviation_pct': 28.0,
                'pause_before_ms': 0
            }
        ],
        'prosody_baseline': {
            'tempo_wpm_mean': 125.0,
            'pitch_mean_hz': 173.0,
            'energy_rms_mean': 0.0143
        },
        'confidence_scores': {
            'overall_confidence': 0.92,
            'segments': [
                {'confidence': 0.95}
            ]
        }
    }

    # Generate enhanced HTML
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_transcript"
        html_path = formatter.format_html_enhanced(
            mock_result,
            "test_audio.m4a",
            output_path
        )

        # Read HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Verify key elements
        assert '<!DOCTYPE html>' in html
        assert 'class="utterance therapeut"' in html
        assert 'class="speaker-label therapeut"' in html
        assert 'Wie geht es Ihnen heute?' in html
        assert '.badge-patient { background: #27ae60; }' in html
        assert '.badge-therapeut { background: #3498db; }' in html

        print(f"✅ Enhanced HTML generated: {html_path}")
        print(f"   File size: {html_path.stat().st_size} bytes")
        print("   Contains speaker color-coding and metadata boxes\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING NEW THERAPEUTIC TRANSCRIPT FORMAT")
    print("="*80)

    test_speaker_config_modes()
    test_markdown_format()
    test_html_enhanced()

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80 + "\n")
