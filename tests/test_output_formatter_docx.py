import importlib

import pytest

from output_formatter import DOCX_AVAILABLE, OutputFormatter


@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
def test_generate_docx_creates_word_file(tmp_path):
    formatter = OutputFormatter()
    transcription_result = {
        'text': 'Hallo Welt',
        'segments': [
            {
                'id': 0,
                'start': 0.0,
                'end': 1.5,
                'speaker': 'SPEAKER_00',
                'text': 'Hallo Welt',
                'ato_markers': ['TEST_MARKER'],
            }
        ],
        'prosody_features': [
            {
                'tempo_deviation': 5.0,
                'pitch_deviation': -2.0,
                'energy_deviation': 1.0,
                'pause_duration': 120.0,
            }
        ],
        'confidence_scores': {
            'overall_confidence': 0.92,
            'segments': [{'confidence': 0.92}],
            'low_confidence_segments': [],
        },
    }

    base_output = tmp_path / "session"
    docx_path = formatter.generate_docx(
        transcription_result,
        "session.wav",
        base_output,
        include_prosody_markers=True,
    )

    assert docx_path.suffix == ".docx"
    assert docx_path.exists()

    document_module = importlib.import_module('docx')
    Document = getattr(document_module, 'Document')
    document = Document(docx_path)
    combined_text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "session.wav" in combined_text
    assert "Hallo Welt" in combined_text
    assert "TEST_MARKER" in combined_text
