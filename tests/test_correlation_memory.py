import pytest
import sys
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from correlation_memory import (
    save_correlations_to_memory,
    load_correlations_from_memory
)

def test_save_correlations_to_memory(tmp_path):
    """Test saving correlations to speaker memory file."""
    memory_file = tmp_path / "test_speaker.yaml"

    correlations = {
        "ATO_ANXIETY_HESITATION": {
            "confidence": 0.85,
            "sample_count": 42,
            "features": {"pitch_variability": 0.7}
        }
    }

    save_correlations_to_memory(memory_file, correlations)

    assert memory_file.exists()
    with open(memory_file) as f:
        data = yaml.safe_load(f)

    assert "ato_correlations" in data
    assert "ATO_ANXIETY_HESITATION" in data["ato_correlations"]

def test_load_correlations_from_memory(tmp_path):
    """Test loading correlations from speaker memory."""
    memory_file = tmp_path / "test_speaker.yaml"

    # Create test memory file
    data = {
        "ato_correlations": {
            "ATO_TEMPO_FAST": {
                "confidence": 0.72,
                "sample_count": 15
            }
        }
    }

    with open(memory_file, 'w') as f:
        yaml.dump(data, f)

    correlations = load_correlations_from_memory(memory_file)

    assert "ATO_TEMPO_FAST" in correlations
    assert correlations["ATO_TEMPO_FAST"]["confidence"] == 0.72