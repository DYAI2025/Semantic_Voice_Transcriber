import queue
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import speaker_diarizer
from speaker_diarizer import SpeakerDiarizer, DiarizationTimeoutError


class ImmediateProcess:
    def __init__(self, target, args):
        self._target = target
        self._args = args

    def start(self):
        self._target(*self._args)

    def join(self, timeout=None):
        pass

    def is_alive(self):
        return False

    def terminate(self):
        pass


class HangingProcess:
    def __init__(self, target, args):
        self._running = False

    def start(self):
        self._running = True

    def join(self, timeout=None):
        pass

    def is_alive(self):
        return self._running

    def terminate(self):
        self._running = False


class DummyContext:
    def __init__(self, process_cls):
        self._process_cls = process_cls

    def Queue(self):
        return queue.Queue()

    def Process(self, target, args):
        return self._process_cls(target, args)


@pytest.fixture(autouse=True)
def stub_pipeline(monkeypatch):
    # Avoid heavy pyannote loads in tests
    monkeypatch.setattr(speaker_diarizer, "PYANNOTE_AVAILABLE", True)
    monkeypatch.setattr(speaker_diarizer, "Pipeline", MagicMock())
    yield


def test_threaded_diarization_invokes_fallback(monkeypatch, tmp_path):
    diarizer = SpeakerDiarizer(use_auth_token=None)
    diarizer.pipeline = MagicMock()
    diarizer._run_fallback_diarization = MagicMock(return_value="fallback")
    monkeypatch.setattr(speaker_diarizer.threading, "current_thread", lambda: object())

    result = diarizer._run_diarization_with_timeout(tmp_path / "sample.wav", {})

    diarizer._run_fallback_diarization.assert_called_once()
    assert result == "fallback"


def test_fallback_worker_success(monkeypatch, tmp_path):
    diarizer = SpeakerDiarizer(use_auth_token=None)
    diarizer.pipeline = MagicMock()
    diarizer._mp_start_method = "spawn"
    diarizer.timeout_seconds = 1

    def fake_worker(config, audio_path, kwargs, result_queue):
        result_queue.put(("ok", [{"start": 0.0, "end": 1.0, "speaker": "Speaker A"}]))

    monkeypatch.setattr(speaker_diarizer, "_spawned_diarization_worker", fake_worker)
    monkeypatch.setattr(speaker_diarizer.mp, "get_context", lambda method: DummyContext(ImmediateProcess))

    annotation = diarizer._run_fallback_diarization(tmp_path / "sample.wav", {"min_speakers": 1, "max_speakers": 2})
    assert isinstance(annotation, speaker_diarizer.Annotation)
    assert len(list(annotation.itertracks())) == 1


def test_fallback_worker_timeout(monkeypatch, tmp_path):
    diarizer = SpeakerDiarizer(use_auth_token=None)
    diarizer.pipeline = MagicMock()
    diarizer._mp_start_method = "spawn"
    diarizer.timeout_seconds = 0.1

    monkeypatch.setattr(speaker_diarizer.mp, "get_context", lambda method: DummyContext(HangingProcess))

    with pytest.raises(DiarizationTimeoutError):
        diarizer._run_fallback_diarization(tmp_path / "sample.wav", {"min_speakers": 1})
