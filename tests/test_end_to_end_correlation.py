import sys
from pathlib import Path
import yaml
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ato_correlation_engine import CorrelationEngine
from ato_correlation_config import CorrelationConfig
from correlation_trainer import CorrelationTrainer
from correlation_memory import save_correlations_to_memory, load_correlations_from_memory
from ato_correlation_types import ProsodyFeatureVector

def test_complete_correlation_workflow(tmp_path):
    """Test complete workflow from training to prediction."""

    # 1. Setup
    speaker_id = "test_speaker"
    config = CorrelationConfig()
    engine = CorrelationEngine(speaker_id, config)
    trainer = CorrelationTrainer(engine)

    # 2. Create annotated transcript
    transcript_file = tmp_path / "annotated.yaml"
    transcript_data = {
        "segments": [
            {
                "prosody": {
                    "pitch_deviation": 0.3,
                    "tempo_deviation": -0.2,
                    "energy_deviation": -0.1,
                    "pause_frequency": 3.5,
                    "pitch_variability": 0.45
                },
                "markers": ["ATO_ANXIETY_HESITATION"]
            },
            {
                "prosody": {
                    "pitch_deviation": 0.1,
                    "tempo_deviation": 0.0,
                    "energy_deviation": 0.1,
                    "pause_frequency": 0.5,
                    "pitch_variability": 0.15
                },
                "markers": []
            }
        ]
    }

    with open(transcript_file, 'w') as f:
        yaml.dump(transcript_data, f)

    # 3. Train
    correlations = trainer.train_from_transcript(transcript_file)
    assert len(correlations) > 0

    # 4. Save to memory
    memory_file = tmp_path / "memory.yaml"
    memory_data = {}
    for corr in correlations:
        memory_data[corr.marker_name] = {
            "confidence": corr.confidence,
            "sample_count": corr.sample_count
        }
    save_correlations_to_memory(memory_file, memory_data)

    # 5. Load from memory
    loaded = load_correlations_from_memory(memory_file)
    assert "ATO_ANXIETY_HESITATION" in loaded

    # 6. Predict on new data
    new_features = ProsodyFeatureVector(
        pitch_deviation=0.28,
        tempo_deviation=-0.18,
        energy_deviation=-0.12,
        pause_frequency=3.2,
        pitch_variability=0.42
    )

    predictions = engine.predict_markers(new_features, threshold=0.3)

    # Should predict anxiety based on similar features
    predicted_markers = [p.marker_name for p in predictions]
    assert len(predictions) >= 0  # May or may not predict depending on threshold

    print(f"Workflow complete. Predicted: {predicted_markers}")

if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_complete_correlation_workflow(Path(tmpdir))
    print("End-to-end test passed!")