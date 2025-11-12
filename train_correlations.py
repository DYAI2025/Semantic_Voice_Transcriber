#!/usr/bin/env python3
"""
Train ATO-prosody correlations from annotated transcripts.

Usage:
    python train_correlations.py --speaker NAME --input DIR [--output FILE]
"""

import argparse
import sys
from pathlib import Path
import yaml

from ato_correlation_engine import CorrelationEngine
from ato_correlation_config import CorrelationConfig
from correlation_trainer import CorrelationTrainer
from correlation_memory import save_correlations_to_memory

def main():
    parser = argparse.ArgumentParser(
        description="Train ATO-prosody correlations from annotated transcripts"
    )
    parser.add_argument(
        "--speaker",
        required=True,
        help="Speaker ID for training"
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Directory containing annotated transcripts"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output memory file (default: Memory/{speaker}.yaml)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default="correlation_config.yaml",
        help="Configuration file"
    )

    args = parser.parse_args()

    # Validate input directory
    if not args.input.exists():
        print(f"Error: Input directory {args.input} does not exist")
        sys.exit(1)

    # Load configuration
    config = CorrelationConfig.from_yaml(args.config) if args.config.exists() else CorrelationConfig()

    # Initialize engine and trainer
    print(f"Initializing correlation engine for speaker: {args.speaker}")
    engine = CorrelationEngine(speaker_id=args.speaker, config=config)
    trainer = CorrelationTrainer(engine)

    # Train from directory
    print(f"Training from transcripts in: {args.input}")
    correlations = trainer.train_from_directory(args.input)

    if not correlations:
        print("No correlations found in training data")
        sys.exit(1)

    # Format for memory storage
    memory_correlations = {}
    for marker_name, corr_list in correlations.items():
        # Use most recent/confident correlation
        best = max(corr_list, key=lambda c: c.confidence)
        memory_correlations[marker_name] = {
            "confidence": best.confidence,
            "sample_count": sum(c.sample_count for c in corr_list),
            "contributing_features": best.contributing_features
        }

    # Save to memory
    output_file = args.output or Path(f"Memory/{args.speaker}.yaml")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving correlations to: {output_file}")
    save_correlations_to_memory(output_file, memory_correlations)

    # Print summary
    print("\nTraining Summary:")
    print(f"  Total markers learned: {len(memory_correlations)}")
    for marker, data in memory_correlations.items():
        print(f"  - {marker}: {data['confidence']:.0%} confidence ({data['sample_count']} samples)")

    print("\nTraining complete!")

if __name__ == "__main__":
    main()