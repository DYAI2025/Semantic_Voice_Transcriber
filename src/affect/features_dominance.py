"""Dominance features from turn-taking and loudness."""

def extract_dominance_features(speaker_segments, audio_segments):
    """Extract dominance indicators.

    Args:
        speaker_segments: List of {speaker, start, end, overlaps}
        audio_segments: Corresponding audio arrays

    Returns:
        dict: {interruption_index, loudness_delta, hedges_rate}
    """
    raise NotImplementedError
