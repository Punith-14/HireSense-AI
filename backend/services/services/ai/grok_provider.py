import os
import time

import requests


class GrokProviderError(RuntimeError):
    pass


class GrokProvider:
    provider = "grok"

    def __init__(self, session=None, api_key=None, model=None, base_url=None, timeout=None, retries=None):
        self.session = session or requests.Session()
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.model = model or os.getenv("XAI_MODEL", "grok-2-latest")
        self.base_url = (base_url or os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")).rstrip("/")
        self.timeout = float(timeout or os.getenv("LLM_TIMEOUT_SECONDS", "20"))
        self.retries = int(retries or os.getenv("LLM_RETRY_COUNT", "3"))

    def available(self):
        return bool(self.api_key)

    def generate(self, messages, max_tokens=700, temperature=0.35):
        if not self.available():
            raise GrokProviderError("XAI_API_KEY is not configured.")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        last_error = None

        for attempt in range(self.retries):
            try:
                response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
                if response.status_code in (429, 500, 502, 503, 504):
                    time.sleep(0.8 * (attempt + 1))
                    continue
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
                last_error = exc
                time.sleep(0.5 * (attempt + 1))

        raise GrokProviderError(str(last_error or "Grok request failed"))
