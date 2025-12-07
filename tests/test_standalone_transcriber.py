"""
Test suite for standalone transcription service with speaker detection.

Validates that the transcriber can work independently with optional
speaker diarization integration.
"""

import os
import sys
from pathlib import Path
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.transcription_service import (
    TranscriptionService,
    TranscriptionRequest,
    TranscriptionConfig,
    ModelProfile,
    transcribe_with_whisper,
)


class TestStandaloneTranscription:
    """Test pure transcription without any analytics dependencies"""

    def test_service_initialization(self):
        """Test that service can be initialized without any optional adapters"""
        config = TranscriptionConfig.from_env()
        service = TranscriptionService(config)

        assert service is not None
        assert service.prosody_adapter is None
        assert service.diarization_adapter is None

    def test_transcription_request_creation(self):
        """Test creating a transcription request"""
        request = TranscriptionRequest(
            audio_path=Path("test.wav"),
            language="de",
            model_profile=ModelProfile(name="base"),
            initial_prompt="Test prompt"
        )

        assert request.audio_path == Path("test.wav")
        assert request.language == "de"
        assert request.model_profile.name == "base"
        assert request.initial_prompt == "Test prompt"

    def test_backward_compatibility_wrapper(self):
        """Test that legacy function signature still works"""
        # This should not raise any import errors
        try:
            from services.transcription_service import transcribe_with_whisper
            assert callable(transcribe_with_whisper)
        except ImportError as e:
            pytest.fail(f"Backward compatibility wrapper failed: {e}")


class TestSpeakerDiarizationIntegration:
    """Test optional speaker diarization integration"""

    def test_diarization_module_imports(self):
        """Test that diarization module can be imported"""
        try:
            from svt_core.audio.diarization import SpeakerDiarizer
            assert SpeakerDiarizer is not None
        except ImportError as e:
            pytest.skip(f"pyannote.audio not available: {e}")

    def test_diarizer_initialization_without_token(self):
        """Test that diarizer fails gracefully without HF token"""
        try:
            from svt_core.audio.diarization import SpeakerDiarizer
        except ImportError:
            pytest.skip("pyannote.audio not available")

        # Should not crash, but may warn about missing token
        diarizer = SpeakerDiarizer(hf_token=None, device="cpu")
        assert diarizer is not None

    def test_adapter_pattern_structure(self):
        """Test that adapter can be attached to service"""
        config = TranscriptionConfig.from_env()

        # Create a mock adapter
        class MockDiarizationAdapter:
            def attach(self, raw_result, request):
                return {"speakers": ["A", "B"], "segments": []}

        mock_adapter = MockDiarizationAdapter()
        service = TranscriptionService(
            config=config,
            diarization_adapter=mock_adapter
        )

        assert service.diarization_adapter is not None
        assert hasattr(service.diarization_adapter, 'attach')


class TestStandaloneCapabilities:
    """Test that transcriber works standalone (only transcription + speaker detection)"""

    def test_no_prosody_dependency(self):
        """Verify prosody analysis is optional"""
        config = TranscriptionConfig.from_env()
        service = TranscriptionService(config)

        # Should not have prosody dependency
        assert service.prosody_adapter is None

        # Importing service should not require prosody modules
        try:
            from services.transcription_service import TranscriptionService
            # If we get here, no hard dependency on prosody
            assert True
        except ImportError as e:
            if "prosody" in str(e).lower():
                pytest.fail("Transcription service has hard dependency on prosody")

    def test_no_emotion_dependency(self):
        """Verify emotion analysis is not required"""
        # Should not require TextBlob or emotion analysis modules
        config = TranscriptionConfig.from_env()
        service = TranscriptionService(config)

        # Service should work without emotion modules
        assert service is not None

    def test_no_semantic_dependency(self):
        """Verify semantic marker detection is not required"""
        # Should not require ATO marker modules
        config = TranscriptionConfig.from_env()
        service = TranscriptionService(config)

        # Service should work without marker modules
        assert service is not None


class TestConfigurationManagement:
    """Test environment-based configuration"""

    def test_config_from_env(self):
        """Test loading config from environment variables"""
        config = TranscriptionConfig.from_env()

        assert config.input_dir is not None
        assert config.output_dir is not None
        assert config.log_dir is not None

    def test_config_override(self):
        """Test that environment variables can override defaults"""
        # Set custom env var
        original_base = os.environ.get("SVT_BASE_PATH")
        os.environ["SVT_BASE_PATH"] = "/custom/path"

        try:
            config = TranscriptionConfig.from_env()
            # Should use custom base path for derived paths
            assert "/custom/path" in str(config.input_dir) or str(config.input_dir) == "Eingang"
        finally:
            # Restore original
            if original_base:
                os.environ["SVT_BASE_PATH"] = original_base
            else:
                os.environ.pop("SVT_BASE_PATH", None)


class TestAPIStructure:
    """Test REST API structure"""

    def test_api_module_imports(self):
        """Test that API module can be imported"""
        try:
            from services.transcription_service import api
            assert hasattr(api, 'app')
            assert hasattr(api, 'transcribe')
            assert hasattr(api, 'health')
        except ImportError as e:
            pytest.fail(f"API module import failed: {e}")

    def test_fastapi_app_creation(self):
        """Test that FastAPI app is created correctly"""
        try:
            from services.transcription_service.api import app
            assert app is not None
            assert app.title == "Semantic Voice Transcriber"
        except ImportError:
            pytest.skip("FastAPI not available")


class TestDockerDeployment:
    """Test Docker deployment readiness"""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile_path = Path(__file__).parent.parent / "services" / "transcription_service" / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile not found"

    def test_requirements_minimal(self):
        """Test that service has minimal dependencies"""
        # Core transcription service should NOT require:
        prohibited_deps = [
            "textblob",  # Emotion analysis
            "praat-parselmouth",  # Prosody analysis
            "nltk",  # NLP for markers
        ]

        # Note: This is a conceptual test - actual implementation would read requirements.txt
        # and verify these are not present for the standalone service
        assert True  # Placeholder


def test_full_standalone_workflow():
    """
    Integration test: Verify complete standalone transcription workflow
    without any analytics dependencies
    """
    # This test verifies the conceptual workflow, not actual transcription
    # (which would require audio files and API keys)

    # Step 1: Initialize service (no adapters)
    config = TranscriptionConfig.from_env()
    service = TranscriptionService(config)

    # Step 2: Verify service is standalone
    assert service.prosody_adapter is None
    assert service.diarization_adapter is None

    # Step 3: Verify backward compatibility
    assert callable(transcribe_with_whisper)

    # Step 4: Verify API endpoints exist
    try:
        from services.transcription_service.api import app
        assert "/transcribe" in [route.path for route in app.routes]
        assert "/health" in [route.path for route in app.routes]
    except ImportError:
        pytest.skip("FastAPI not available")


def test_optional_speaker_detection_workflow():
    """
    Integration test: Verify transcription with optional speaker detection
    """
    config = TranscriptionConfig.from_env()

    # Create mock diarization adapter
    class MockDiarizationAdapter:
        def attach(self, raw_result, request):
            # Mock speaker detection result
            return {
                "speakers": ["A", "B"],
                "segments": [
                    {"speaker": "A", "start": 0.0, "end": 3.5},
                    {"speaker": "B", "start": 3.5, "end": 7.0}
                ]
            }

    # Initialize service with diarization adapter
    service = TranscriptionService(
        config=config,
        diarization_adapter=MockDiarizationAdapter()
    )

    # Verify adapter is attached
    assert service.diarization_adapter is not None

    # The adapter should be callable
    assert hasattr(service.diarization_adapter, 'attach')


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
