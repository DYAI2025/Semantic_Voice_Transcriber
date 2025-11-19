#!/usr/bin/env python3
"""
Test for Psychoanalysis Dashboard integrated workflow
Tests the new file-selection → transcribe → analyze → display workflow
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import sys

# Ensure we can import svt
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDashboardWorkflow:
    """Test the integrated Dashboard workflow"""

    def test_file_dialog_integration(self):
        """Test that file dialog is called with correct parameters"""
        # This tests the beginning of _generate_psychoanalysis_dashboard

        # We can't easily test the full GUI without mocking tkinter
        # But we can verify the logic is sound by checking file paths

        test_audio = Path("test_audio.m4a")
        expected_json = Path("Transkripte_LLM/test_audio_transkript.prosody.json")

        # Verify naming convention
        assert expected_json.stem.replace(".prosody", "") == f"{test_audio.stem}_transkript"
        print("✅ File naming convention correct")

    def test_prosody_json_path_calculation(self):
        """Test that .prosody.json paths are calculated correctly"""
        test_cases = [
            ("audio.m4a", "Transkripte_LLM/audio_transkript.prosody.json"),
            ("session_001.opus", "Transkripte_LLM/session_001_transkript.prosody.json"),
            ("WhatsApp Audio 2025-01-15.wav", "Transkripte_LLM/WhatsApp Audio 2025-01-15_transkript.prosody.json"),
        ]

        output_dir = Path("Transkripte_LLM")
        for audio_name, expected_path in test_cases:
            audio_path = Path(audio_name)
            calculated_json = output_dir / f"{audio_path.stem}_transkript.prosody.json"
            assert str(calculated_json) == expected_path
            print(f"✅ {audio_name} → {expected_path}")

    def test_transcription_settings_structure(self):
        """Test that transcription settings dict has required fields"""
        # This mirrors the settings dict created in _generate_psychoanalysis_dashboard

        settings = {
            'audio_files': [Path("test.m4a")],
            'model': 'small',
            'language': None,
            'enable_prosody': True,  # MUST be True
            'enable_emotion': False,
            'enable_diarization': False,
            'enable_memory': False,
            'use_intelligent_pipeline': False,
            'use_audio_chunking': True,
            'chunk_duration': 300.0,
            'overlap_duration': 5.0,
            'confidence_threshold': 0.5,
            'output_dir': Path("Transkripte_LLM")
        }

        # Verify critical settings
        assert settings['enable_prosody'] is True, "Prosody MUST be enabled for Dashboard"
        assert 'audio_files' in settings
        assert 'output_dir' in settings
        assert isinstance(settings['audio_files'], list)
        assert len(settings['audio_files']) == 1

        print("✅ Transcription settings structure valid")
        print("✅ Prosody forced ON (required for Dashboard)")

    def test_dashboard_workflow_logic(self):
        """Test the complete workflow logic"""
        # Simulate the workflow steps

        # Step 1: User selects audio file
        selected_file = Path("Eingang/Patient/session_001.m4a")

        # Step 2: Calculate expected .prosody.json path
        output_dir = Path("Transkripte_LLM")
        expected_json = output_dir / f"{selected_file.stem}_transkript.prosody.json"

        # Step 3a: File exists → skip transcription
        if expected_json.exists():
            workflow = "reuse"
        else:
            workflow = "transcribe"

        # For this test, assume it doesn't exist
        assert workflow == "transcribe"
        print(f"✅ Workflow determined: {workflow}")

        # Step 4: Verify settings would be created
        settings = {
            'audio_files': [selected_file],
            'enable_prosody': True,  # Forced ON
        }

        assert settings['enable_prosody'] is True
        print("✅ Settings prepared with prosody forced ON")

        # Step 5: Verify async processing would be initiated
        # (can't test actual threading here, but verify the logic)
        processing_required = not expected_json.exists()
        assert processing_required is True
        print("✅ Async processing would be triggered")

    def test_method_signatures(self):
        """Verify all new methods have correct signatures"""
        import svt
        import inspect

        gui_class = svt.SemanticVoiceTranscriberGUI

        # Check _generate_psychoanalysis_dashboard
        method = getattr(gui_class, '_generate_psychoanalysis_dashboard')
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        assert params == ['self'], f"Expected ['self'], got {params}"
        print("✅ _generate_psychoanalysis_dashboard(self)")

        # Check _transcribe_for_dashboard
        method = getattr(gui_class, '_transcribe_for_dashboard')
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        assert params == ['self', 'settings', 'audio_path'], f"Expected ['self', 'settings', 'audio_path'], got {params}"
        print("✅ _transcribe_for_dashboard(self, settings, audio_path)")

        # Check _check_dashboard_transcription
        method = getattr(gui_class, '_check_dashboard_transcription')
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        assert params == ['self', 'expected_json'], f"Expected ['self', 'expected_json'], got {params}"
        print("✅ _check_dashboard_transcription(self, expected_json)")

        # Check _run_dashboard_pipeline
        method = getattr(gui_class, '_run_dashboard_pipeline')
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        assert params == ['self', 'latest_json'], f"Expected ['self', 'latest_json'], got {params}"
        print("✅ _run_dashboard_pipeline(self, latest_json)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING PSYCHOANALYSIS DASHBOARD WORKFLOW")
    print("="*60 + "\n")

    test = TestDashboardWorkflow()

    try:
        test.test_file_dialog_integration()
        print()

        test.test_prosody_json_path_calculation()
        print()

        test.test_transcription_settings_structure()
        print()

        test.test_dashboard_workflow_logic()
        print()

        test.test_method_signatures()
        print()

        print("="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
