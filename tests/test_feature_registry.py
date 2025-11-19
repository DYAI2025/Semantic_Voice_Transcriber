from audit.feature_registry import FEATURE_REGISTRY, FeatureMetadata


def test_feature_registry_contains_all_features():
    expected_keys = {
        "emotions",
        "prosody",
        "memory_profile",
        "diarization",
        "turning_points",
        "dual_markers",
        "speaker_view",
    }
    assert expected_keys.issubset(set(FEATURE_REGISTRY)), "missing feature keys"
    for key in expected_keys:
        meta = FEATURE_REGISTRY[key]
        assert isinstance(meta, FeatureMetadata)
        assert meta.name
        assert meta.modules
