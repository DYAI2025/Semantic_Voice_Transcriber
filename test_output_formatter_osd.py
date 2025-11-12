#!/usr/bin/env python3
from pathlib import Path
from output_formatter import OutputFormatter


def test_markdown_includes_overlap_marker():
    """Test Markdown output includes [OVERLAP] marker"""
    formatter = OutputFormatter()

    transcription_result = {
        'segments': [
            {
                'start': 5.0,
                'end': 7.0,
                'text': 'Test text',
                'has_overlap': True,
                'overlap_duration': 0.8
            }
        ],
        'prosody_features': [],
        'prosody_baseline': None,
        'confidence_scores': {'overall_confidence': 0.9, 'segments': []},
        'overlapped_speech': [
            {'start': 5.2, 'end': 6.0, 'duration': 0.8}
        ]
    }

    markdown = formatter._generate_markdown(
        'test.m4a',
        transcription_result['segments'],
        transcription_result['prosody_features'],
        transcription_result['prosody_baseline'],
        transcription_result['confidence_scores'],
        include_prosody_markers=True
    )

    assert '[OVERLAP]' in markdown or '[ÜBERLAPPUNG]' in markdown


def test_json_includes_overlap_data():
    """Test JSON output includes overlap fields"""
    formatter = OutputFormatter()

    transcription_result = {
        'segments': [
            {
                'start': 5.0,
                'end': 7.0,
                'text': 'Test',
                'has_overlap': True,
                'overlap_duration': 0.8
            }
        ],
        'prosody_features': [],
        'prosody_baseline': None,
        'confidence_scores': {'overall_confidence': 0.9, 'segments': []}
    }

    json_data = formatter._generate_json_sidecar(
        'test.m4a',
        transcription_result['segments'],
        transcription_result['prosody_features'],
        transcription_result['prosody_baseline'],
        transcription_result['confidence_scores']
    )

    # Check first segment has overlap fields
    assert 'has_overlap' in json_data['segments'][0]
    assert json_data['segments'][0]['has_overlap'] is True
    assert 'overlap_duration' in json_data['segments'][0]


def test_csv_includes_overlap_column():
    """Test CSV includes has_overlap column"""
    formatter = OutputFormatter()

    transcription_result = {
        'segments': [
            {
                'start': 5.0,
                'end': 7.0,
                'text': 'Test',
                'has_overlap': True,
                'overlap_duration': 0.8
            }
        ],
        'prosody_features': [],
        'confidence_scores': {'overall_confidence': 0.9, 'segments': []}
    }

    output_path = Path('/tmp/test_osd_output')
    csv_path = formatter.generate_csv(transcription_result, output_path)

    # Read CSV and check header
    import csv
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        assert 'has_overlap' in fieldnames
        assert 'overlap_duration_s' in fieldnames

        # Check first row
        row = next(reader)
        assert row['has_overlap'] == 'True'
