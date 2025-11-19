"""VAD rule-based scoring engine."""

def compute_vad_raw(prosody_features, text_features, dominance_features, config):
    """Combine features into raw V/A/D scores.

    Args:
        prosody_features: dict from features_prosody
        text_features: dict from features_text
        dominance_features: dict from features_dominance
        config: dict with weights {alpha, beta, gamma}

    Returns:
        dict: {valence_raw, arousal_raw, dominance_raw}
    """
    raise NotImplementedError
