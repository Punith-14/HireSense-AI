import os

import pytest


def test_speech_text_metrics():
    from speech.services import SpeechAnalyzer

    metrics = SpeechAnalyzer().analyze_text(
        "Um I would basically design the API with tests and indexes because reliability matters.",
        duration_seconds=10,
    )

    assert metrics["filler_count"] == 2
    assert metrics["word_count"] > 8
    assert metrics["words_per_minute"] > 0


def test_sounddevice_dependency_installed():
    import sounddevice as sd

    assert sd.__version__ == "0.5.5"


def test_vosk_dependency_installed():
    import vosk

    assert hasattr(vosk, "Model")


def test_offline_first_returns_graceful_unavailable_without_model(tmp_path, monkeypatch):
    import wave
    from services.speech.speech_service import SpeechService

    monkeypatch.delenv("VOSK_MODEL_PATH", raising=False)
    monkeypatch.setenv("ALLOW_ONLINE_SPEECH_RECOGNITION", "False")
    wav_path = tmp_path / "empty.wav"
    with wave.open(str(wav_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"\x00\x00" * 16000)

    result = SpeechService().transcribe_file(str(wav_path))

    assert result["status"] == "transcription_unavailable"
    assert result["metrics"]["duration_seconds"] == 1.0


@pytest.mark.hardware
def test_microphone_device_probe():
    if os.getenv("RUN_LIVE_HARDWARE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_HARDWARE_TESTS=1 to run real microphone validation.")

    import sounddevice as sd

    devices = [device for device in sd.query_devices() if device.get("max_input_channels", 0) > 0]
    assert devices, "No microphone input devices detected"
