import json
import os
import wave
from functools import lru_cache


class OfflineRecognizerUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _load_vosk_model(model_path):
    try:
        from vosk import Model
    except ImportError as exc:
        raise OfflineRecognizerUnavailable("Vosk package is not installed.") from exc

    if not model_path or not os.path.isdir(model_path):
        raise OfflineRecognizerUnavailable("VOSK_MODEL_PATH is not configured or does not exist.")
    return Model(model_path)


class VoskOfflineRecognizer:
    provider = "vosk"

    def __init__(self, model_path=None):
        self.model_path = model_path or os.getenv("VOSK_MODEL_PATH")

    def available(self):
        try:
            _load_vosk_model(self.model_path)
            return True
        except OfflineRecognizerUnavailable:
            return False

    def transcribe_wav(self, path):
        try:
            from vosk import KaldiRecognizer
        except ImportError as exc:
            raise OfflineRecognizerUnavailable("Vosk package is not installed.") from exc

        model = _load_vosk_model(self.model_path)
        try:
            with wave.open(path, "rb") as wav_file:
                if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2:
                    raise OfflineRecognizerUnavailable("Vosk requires mono 16-bit PCM WAV audio.")
                recognizer = KaldiRecognizer(model, wav_file.getframerate())
                parts = []
                while True:
                    data = wav_file.readframes(4000)
                    if not data:
                        break
                    if recognizer.AcceptWaveform(data):
                        parts.append(json.loads(recognizer.Result()).get("text", ""))
                parts.append(json.loads(recognizer.FinalResult()).get("text", ""))
        except wave.Error as exc:
            raise OfflineRecognizerUnavailable("Unsupported WAV audio for offline recognition.") from exc

        return " ".join(part for part in parts if part).strip()
