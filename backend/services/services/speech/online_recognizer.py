import os

import requests


class OnlineRecognizerUnavailable(RuntimeError):
    pass


class HttpOnlineRecognizer:
    provider = "http_speech"

    def __init__(self, endpoint=None, enabled=None, timeout=None):
        if enabled is None:
            enabled = os.getenv("ALLOW_ONLINE_SPEECH_RECOGNITION", "False").lower() == "true"
        self.enabled = enabled
        self.endpoint = endpoint or os.getenv("ONLINE_SPEECH_ENDPOINT")
        self.timeout = float(timeout or os.getenv("ONLINE_SPEECH_TIMEOUT_SECONDS", "25"))

    def available(self):
        return bool(self.enabled and self.endpoint)

    def transcribe_audio_file(self, path):
        if not self.available():
            raise OnlineRecognizerUnavailable("Online speech recognition is disabled or not configured.")

        try:
            with open(path, "rb") as audio:
                response = requests.post(
                    self.endpoint,
                    files={"audio_file": audio},
                    timeout=self.timeout,
                )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise OnlineRecognizerUnavailable(f"Online speech recognition failed: {exc}") from exc

        transcript = payload.get("transcript") or payload.get("text") or payload.get("result") or ""
        transcript = str(transcript).strip()
        if not transcript:
            raise OnlineRecognizerUnavailable("Online speech recognition returned an empty transcript.")
        return transcript
