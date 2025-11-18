from pathlib import Path

from audit import audit_runner


def test_run_session_uses_dataset(tmp_path):
    dataset = tmp_path / "testdata"
    (dataset / "audio").mkdir(parents=True)
    (dataset / "transcripts").mkdir(parents=True)
    audio_file = dataset / "audio" / "sessionX.wav"
    audio_file.write_bytes(b"RIFF....")
    transcript_file = dataset / "transcripts" / "sessionX.json"
    transcript_file.write_text("{}", encoding="utf-8")

    report = audit_runner.run_session("sessionX", dataset)
    assert report["session"] == "sessionX"
    assert "features" in report
