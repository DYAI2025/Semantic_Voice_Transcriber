"""Per-speaker baseline normalization."""

def normalize_speaker_baseline(vad_samples, speaker_id):
    """Z-score normalize per speaker, then map to [-1, +1].

    Args:
        vad_samples: List of {timestamp, speaker_id, valence_raw, arousal_raw, dominance_raw}
        speaker_id: Speaker identifier

    Returns:
        List of {timestamp, speaker_id, valence, arousal, dominance}
    """
    raise NotImplementedError
