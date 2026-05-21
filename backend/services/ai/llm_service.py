import json
import os
import re
from concurrent.futures import TimeoutError as FuturesTimeoutError
from functools import lru_cache

import requests

from services.ai.grok_provider import GrokProvider, GrokProviderError
from services.ai.hf_provider import LocalHFProvider, LocalHFProviderError
from services.runtime.task_executor import get_inference_executor


class LLMServiceError(RuntimeError):
    pass


class LLMService:
    def __init__(self):
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
        self.provider = os.getenv("LLM_PROVIDER", "auto").lower()
        self.fallback_enabled = os.getenv("LLM_FALLBACK_ENABLED", "True").lower() == "true"
        self.session = requests.Session()
        self.grok = GrokProvider(session=self.session, timeout=self.timeout)
        self.hf_local = LocalHFProvider()

    def set_provider(self, provider):
        self.provider = (provider or "auto").lower()

    def generate_json(self, prompt, fallback, max_tokens=700):
        messages = [
            {"role": "system", "content": "Return valid compact JSON only. No markdown."},
            {"role": "user", "content": prompt},
        ]
        last_error = None
        attempted = False

        for provider in self._provider_chain():
            try:
                if provider == "grok" and self.grok.available():
                    attempted = True
                    content = self.grok.generate(messages, max_tokens=max_tokens)
                    return self._parse_json(content)
                if provider == "hf_local" and self.hf_local.available():
                    attempted = True
                    content = self._call_local(messages, max_tokens)
                    return self._parse_json(content)
            except (GrokProviderError, LocalHFProviderError, LLMServiceError) as exc:
                last_error = exc
                continue

        if not self.fallback_enabled:
            if last_error:
                raise LLMServiceError(str(last_error))
            if not attempted:
                raise LLMServiceError("No LLM provider is available.")
        return fallback()

    def provider_status(self):
        return {
            "provider": self.provider,
            "grok_configured": self.grok.available(),
            "grok_model": self.grok.model,
            "hf_local_enabled": self.hf_local.available(),
            "hf_local_model": self.hf_local.model_id,
            "fallback_enabled": self.fallback_enabled,
            "provider_chain": self._provider_chain(),
        }

    def _provider_chain(self):
        if self.provider in ("grok", "xai"):
            return ["grok", "hf_local"] if self.fallback_enabled else ["grok"]
        if self.provider in ("hf", "huggingface", "local", "hf_local"):
            return ["hf_local"]
        if self.provider in ("auto", "", "default"):
            return ["grok", "hf_local"]
        return ["grok", "hf_local"]

    def _call_local(self, messages, max_tokens):
        executor = get_inference_executor()
        future = executor.submit(self.hf_local.generate, messages, max_tokens)
        try:
            return future.result(timeout=self.timeout)
        except FuturesTimeoutError as exc:
            future.cancel()
            raise LLMServiceError("Local HF inference timed out.") from exc

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
