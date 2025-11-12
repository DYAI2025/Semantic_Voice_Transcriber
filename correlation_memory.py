import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

def save_correlations_to_memory(memory_file: Path, correlations: Dict[str, Any]) -> None:
    """Save correlation data to speaker memory YAML file."""
    # Load existing memory if it exists
    if memory_file.exists():
        with open(memory_file, 'r') as f:
            memory_data = yaml.safe_load(f) or {}
    else:
        memory_data = {}

    # Update correlations section
    if "ato_correlations" not in memory_data:
        memory_data["ato_correlations"] = {}

    memory_data["ato_correlations"].update(correlations)
    memory_data["ato_correlations_updated"] = datetime.now().isoformat()

    # Save back to file
    try:
        with open(memory_file, 'w') as f:
            yaml.dump(memory_data, f, default_flow_style=False, sort_keys=False)
    except (IOError, OSError) as e:
        print(f"Error: Could not write to memory file '{memory_file}'. {e}")

def load_correlations_from_memory(memory_file: Path) -> Dict[str, Any]:
    """Load correlation data from speaker memory YAML file."""
    if not memory_file.exists():
        return {}

    with open(memory_file, 'r') as f:
        memory_data = yaml.safe_load(f) or {}

    return memory_data.get("ato_correlations", {})

def update_correlation_statistics(
    memory_file: Path,
    marker_name: str,
    new_confidence: float,
    new_samples: int
) -> None:
    """Update correlation statistics with running average."""
    correlations = load_correlations_from_memory(memory_file)

    if marker_name in correlations:
        # Running average update
        old_conf = correlations[marker_name]["confidence"]
        old_count = correlations[marker_name]["sample_count"]

        total_samples = old_count + new_samples
        new_avg_confidence = (
            (old_conf * old_count + new_confidence * new_samples) / total_samples
        )

        correlations[marker_name] = {
            "confidence": new_avg_confidence,
            "sample_count": total_samples
        }
    else:
        correlations[marker_name] = {
            "confidence": new_confidence,
            "sample_count": new_samples
        }

    save_correlations_to_memory(memory_file, correlations)