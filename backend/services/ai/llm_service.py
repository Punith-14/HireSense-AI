import json
import os
import re
import time
from functools import lru_cache

import requests


class LLMServiceError(RuntimeError):
    pass


class LLMService:
    def __init__(self):
        self.session = requests.Session()
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.hf_api_key = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        self.hf_model = os.getenv("HF_MODEL", "microsoft/Phi-3-mini-4k-instruct")

    def generate_json(self, prompt, fallback, max_tokens=700):
        groq_failed_with_hf_available = False
        if self.provider in ("auto", "groq") and self.groq_api_key:
            try:
                return self._call_groq(prompt, max_tokens=max_tokens)
            except LLMServiceError:
                groq_failed_with_hf_available = bool(self.hf_api_key)
                if self.provider == "groq" and not groq_failed_with_hf_available:
                    raise

        if (self.provider in ("auto", "huggingface", "hf") or groq_failed_with_hf_available) and self.hf_api_key:
            try:
                return self._call_huggingface(prompt)
            except LLMServiceError:
                if self.provider in ("huggingface", "hf"):
                    raise

        return fallback()

    def provider_status(self):
        return {
            "provider": self.provider,
            "groq_configured": bool(self.groq_api_key),
            "groq_model": self.groq_model,
            "huggingface_configured": bool(self.hf_api_key),
            "huggingface_model": self.hf_model,
            "fallback_enabled": True,
        }

    def _call_groq(self, prompt, max_tokens):
        payload = {
            "model": self.groq_model,
            "messages": [
                {"role": "system", "content": "Return valid compact JSON only. No markdown."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.35,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        data = self._post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {self.groq_api_key}"},
        )
        content = data["choices"][0]["message"]["content"]
        return self._parse_json(content)

    def _call_huggingface(self, prompt):
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 650, "temperature": 0.35, "return_full_text": False},
            "options": {"wait_for_model": True},
        }
        data = self._post_json(
            f"https://api-inference.huggingface.co/models/{self.hf_model}",
            payload,
            headers={"Authorization": f"Bearer {self.hf_api_key}"},
        )
        if isinstance(data, list) and data:
            text = data[0].get("generated_text", "")
        elif isinstance(data, dict):
            text = data.get("generated_text", "")
        else:
            text = ""
        return self._parse_json(text)

    def _post_json(self, url, payload, headers):
        last_error = None
        for attempt in range(3):
            try:
                response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
                if response.status_code in (429, 500, 502, 503, 504):
                    time.sleep(0.8 * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                time.sleep(0.5 * (attempt + 1))
        raise LLMServiceError(str(last_error or "LLM request failed"))

    def _parse_json(self, text):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text or "", flags=re.DOTALL)
            if not match:
                raise LLMServiceError("LLM did not return JSON")
            return json.loads(match.group(0))


@lru_cache(maxsize=1)
def get_llm_service():
    return LLMService()
