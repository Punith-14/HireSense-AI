import os


class OnlineRecognizerUnavailable(RuntimeError):
    pass


class SpeechRecognitionOnlineRecognizer:
    provider = "speech_recognition_google"

    def __init__(self, enabled=None):
        if enabled is None:
            enabled = os.getenv("ALLOW_ONLINE_SPEECH_RECOGNITION", "False").lower() == "true"
        self.enabled = enabled

    def available(self):
        if not self.enabled:
            return False
        try:
            import speech_recognition  # noqa: F401
        except ImportError:
            return False
        return True

    def transcribe_audio_file(self, path):
        if not self.available():
            raise OnlineRecognizerUnavailable("Online speech recognition is disabled or unavailable.")

        import speech_recognition as sr

        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(path) as source:
                audio = recognizer.record(source)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError as exc:
            raise OnlineRecognizerUnavailable("Could not understand uploaded audio.") from exc
        except sr.RequestError as exc:
            raise OnlineRecognizerUnavailable(f"Online speech recognition failed: {exc}") from exc
        except ValueError as exc:
            raise OnlineRecognizerUnavailable("Unsupported audio format for online recognition.") from exc
