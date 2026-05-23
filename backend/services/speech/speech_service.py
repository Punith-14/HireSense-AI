import os
import tempfile

from services.speech.offline_recognizer import OfflineRecognizerUnavailable, VoskOfflineRecognizer
from services.speech.online_recognizer import HttpOnlineRecognizer, OnlineRecognizerUnavailable
from services.speech.pause_detector import detect_pauses_wav
from services.speech.speech_metrics import calculate_speech_metrics


class SpeechServiceError(RuntimeError):
    pass


class SpeechService:

    def __init__(self, allow_online=True):
        self.offline = VoskOfflineRecognizer()
        self.allow_online = allow_online
        self.online = HttpOnlineRecognizer() if allow_online else None

    def transcribe_uploaded_file(self, uploaded_file):
        path = self._save_upload(uploaded_file)
        try:
            return self.transcribe_file(path)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def transcribe_file(self, path):
        pause_metrics = detect_pauses_wav(path)
        provider = None
        transcript = ""
        errors = []

        if self.offline.available():
            try:
                transcript = self.offline.transcribe_wav(path)
                provider = self.offline.provider
            except OfflineRecognizerUnavailable as exc:
                errors.append(str(exc))

        if not transcript and self.allow_online and self.online and self.online.available():
            try:
                transcript = self.online.transcribe_audio_file(path)
                provider = self.online.provider
            except OnlineRecognizerUnavailable as exc:
                errors.append(str(exc))

        if not transcript:
            metrics = calculate_speech_metrics("", pause_metrics.get("duration_seconds", 0), pause_metrics)
            return {
                "status": "transcription_unavailable",
                "provider": provider,
                "transcript": "",
                "metrics": metrics,
                "errors": errors
                or [
                    "No offline recognizer is available. Configure VOSK_MODEL_PATH or enable optional online recognition."
                ],
            }

        return {
            "status": "ok",
            "provider": provider,
            "transcript": transcript,
            "metrics": calculate_speech_metrics(
                transcript,
                pause_metrics.get("duration_seconds", 0),
                pause_metrics,
            ),
            "errors": errors,
        }

    def analyze_text(self, text, duration_seconds=0, pause_metrics=None):
        return calculate_speech_metrics(text, duration_seconds, pause_metrics)

    def _save_upload(self, uploaded_file):
        suffix = os.path.splitext(uploaded_file.name or "")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            return temp_file.name
