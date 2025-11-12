# ATO-Prosody Correlation System Guide

## Overview

The ATO-Prosody Correlation System learns statistical relationships between prosodic features and ATO markers, enabling automatic marker prediction based on voice patterns.

## Quick Start

### 1. Prepare Annotated Data

Create YAML files with prosody features and markers:

```yaml
segments:
  - prosody:
      pitch_deviation: 0.25
      tempo_deviation: -0.15
      energy_deviation: -0.10
      pause_frequency: 3.0
      pitch_variability: 0.40
    markers:
      - ATO_ANXIETY_HESITATION
```

### 2. Train Correlations

```bash
python train_correlations.py \
  --speaker zoe \
  --input annotated_transcripts/ \
  --output Memory/zoe.yaml
```

### 3. Use in Transcription

Correlations are automatically applied during transcription:

```bash
python auto_transcriber_v4_emotion.py --local
```

## Configuration

Edit `correlation_config.yaml`:

```yaml
correlation_settings:
  min_confidence_threshold: 0.5  # Minimum confidence for predictions
  feature_window_size: 5.0        # Analysis window in seconds

feature_weights:
  pitch_deviation: 1.0      # Weight for pitch changes
  tempo_deviation: 1.2      # Weight for tempo changes
  pause_frequency: 1.5      # Weight for pause patterns
```

## Interpreting Results

### Confidence Scores

- **80-100%**: High confidence - strong correlation
- **60-79%**: Medium confidence - likely correlation
- **50-59%**: Low confidence - possible correlation
- **<50%**: Not applied (below threshold)

### Contributing Features

Each prediction shows which prosodic features contributed:

```
ATO_ANXIETY_HESITATION (85%)
  Primary indicators: pitch_variability: 0.70, pause_frequency: 0.65
```

## Adding New Markers

1. Annotate transcripts with new marker
2. Retrain correlations
3. System learns patterns automatically

## Troubleshooting

### No Correlations Found

- Check annotation format
- Ensure sufficient training samples (>3 per marker)
- Verify prosody features are present

### Low Confidence Predictions

- Add more training data
- Adjust feature weights in config
- Check for consistent annotation

## Architecture

```
Transcription → Prosody Extraction → Correlation Engine → Marker Prediction
                                            ↑
                                     Training Data
```

## Files

- `ato_correlation_engine.py` - Core prediction engine
- `correlation_trainer.py` - Training from annotations
- `correlation_config.yaml` - System configuration
- `correlation_memory.py` - Speaker profile integration