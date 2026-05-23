import os

import requests


class OnlineRecognizerUnavailable(RuntimeError):
    pass


class HttpOnlineRecognizer:
    provider = "groq_whisper"

    def __init__(self, endpoint=None, enabled=None, timeout=None):
        if enabled is None:
            enabled = os.getenv("ALLOW_ONLINE_SPEECH_RECOGNITION", "False").lower() == "true"
        self.enabled = enabled
        self.endpoint = endpoint or "https://api.groq.com/openai/v1/audio/transcriptions"
        self.timeout = float(timeout or os.getenv("ONLINE_SPEECH_TIMEOUT_SECONDS", "25"))
        self.api_key = os.getenv("GROQ_API_KEY")

    def available(self):
        return bool(self.enabled and self.api_key)

    def transcribe_audio_file(self, path):
        if not self.available():
            raise OnlineRecognizerUnavailable("Online speech recognition is disabled or GROQ_API_KEY is missing.")

        try:
            with open(path, "rb") as audio:
                response = requests.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": (os.path.basename(path), audio, "audio/wav")},
                    data={"model": "whisper-large-v3"},
                    timeout=self.timeout,
                )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise OnlineRecognizerUnavailable(f"Groq Whisper failed: {exc}") from exc

        transcript = payload.get("text") or ""
        transcript = str(transcript).strip()
        if not transcript:
            raise OnlineRecognizerUnavailable("Groq Whisper returned an empty transcript.")
        return transcript
