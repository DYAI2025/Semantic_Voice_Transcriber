# tests/test_psychoanalysis_cache.py
import pytest
from pathlib import Path
import json
import hashlib
from psychoanalysis_cache import CacheManager

@pytest.fixture
def temp_cache_dir(tmp_path):
    """Temporary cache directory"""
    return tmp_path / "cache"

@pytest.fixture
def sample_transcript():
    """Sample transcript data"""
    return {
        "transcript_meta": {
            "file": "test.md",
            "speaker_labels": ["A", "B"],
            "duration_seconds": 300
        },
        "utterances": [
            {"id": 1, "speaker": "A", "text": "test utterance"}
        ]
    }

@pytest.fixture
def sample_analysis():
    """Sample analysis result"""
    return {
        "utterance_states": [
            {"id": 1, "valence": -0.5, "arousal": 0.6, "markers": ["ATO_RESISTANCE_SILENCE"]}
        ],
        "ued_metrics": {
            "home_base": {"valence": -0.3, "arousal": 0.5}
        },
        "marker_summary": {
            "frequencies": {"ATO_RESISTANCE_SILENCE": 1}
        }
    }

def test_cache_manager_initialization(temp_cache_dir):
    """Cache manager should create directory if not exists"""
    cache = CacheManager(cache_dir=temp_cache_dir)
    assert cache.cache_dir.exists()
    assert cache.cache_dir.is_dir()

def test_compute_transcript_hash(temp_cache_dir, sample_transcript):
    """Should compute SHA256 hash of transcript JSON"""
    cache = CacheManager(cache_dir=temp_cache_dir)

    hash1 = cache.compute_transcript_hash(sample_transcript)

    # Hash should be consistent
    hash2 = cache.compute_transcript_hash(sample_transcript)
    assert hash1 == hash2

    # Hash should be SHA256 hex string (64 chars)
    assert len(hash1) == 64
    assert all(c in '0123456789abcdef' for c in hash1)

def test_cache_miss_on_first_access(temp_cache_dir, sample_transcript):
    """Should return None if no cache exists"""
    cache = CacheManager(cache_dir=temp_cache_dir)

    result = cache.get_cached_analysis(sample_transcript)
    assert result is None

def test_cache_hit_after_save(temp_cache_dir, sample_transcript, sample_analysis):
    """Should retrieve cached analysis if hash matches"""
    cache = CacheManager(cache_dir=temp_cache_dir)

    # Save to cache
    cache.save_analysis(sample_transcript, sample_analysis)

    # Retrieve from cache
    cached = cache.get_cached_analysis(sample_transcript)
    assert cached is not None
    assert cached["utterance_states"] == sample_analysis["utterance_states"]
    assert cached["ued_metrics"] == sample_analysis["ued_metrics"]

def test_cache_invalidation_on_transcript_change(temp_cache_dir, sample_transcript, sample_analysis):
    """Should invalidate cache if transcript content changes"""
    cache = CacheManager(cache_dir=temp_cache_dir)

    # Save original
    cache.save_analysis(sample_transcript, sample_analysis)

    # Modify transcript
    modified_transcript = sample_transcript.copy()
    modified_transcript["utterances"][0]["text"] = "CHANGED TEXT"

    # Should not find cache for modified transcript
    cached = cache.get_cached_analysis(modified_transcript)
    assert cached is None
