import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from correlation_trainer import CorrelationTrainer
from ato_correlation_engine import CorrelationEngine

def test_trainer_initialization():
    """Test trainer initialization with engine."""
    engine = CorrelationEngine(speaker_id="test")
    trainer = CorrelationTrainer(engine)
    assert trainer.engine == engine

def test_load_annotated_transcript():
    """Test loading annotated transcript data."""
    engine = CorrelationEngine(speaker_id="test")
    trainer = CorrelationTrainer(engine)

    # Create test fixture if needed
    fixture_path = Path("fixtures/annotated_transcripts/sample_annotated.yaml")
    fixture_path.parent.mkdir(parents=True, exist_ok=True)

    data = trainer.load_annotated_transcript(fixture_path)
    assert "segments" in data
    assert isinstance(data["segments"], list)

def test_train_from_transcript():
    """Test training correlations from annotated transcript."""
    engine = CorrelationEngine(speaker_id="test")
    trainer = CorrelationTrainer(engine)

    fixture_path = Path("fixtures/annotated_transcripts/sample_annotated.yaml")
    correlations = trainer.train_from_transcript(fixture_path)

    assert len(correlations) > 0
    assert all(c.marker_name for c in correlations)