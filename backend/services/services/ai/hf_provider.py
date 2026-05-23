import os
import threading
from functools import lru_cache


class LocalHFProviderError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _load_local_model(model_id):
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise LocalHFProviderError("transformers/torch are not installed.") from exc

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device


class LocalHFProvider:
    provider = "hf_local"

    def __init__(self, model_id=None):
        self.model_id = model_id or os.getenv("HF_MODEL", "microsoft/Phi-3-mini-4k-instruct")
        self.enabled = os.getenv("HF_LOCAL_ENABLED", "False").lower() == "true"
        self.max_new_tokens = int(os.getenv("HF_MAX_NEW_TOKENS", "512"))
        self.temperature = float(os.getenv("HF_TEMPERATURE", "0.3"))
        self.lock = threading.Lock()

    def available(self):
        return self.enabled

    def generate(self, messages, max_tokens=700):
        if not self.available():
            raise LocalHFProviderError("Local Hugging Face inference is disabled.")

        max_new_tokens = max(1, min(int(max_tokens or self.max_new_tokens), self.max_new_tokens))
        tokenizer, model, device = _load_local_model(self.model_id)
        prompt_inputs = self._build_prompt(tokenizer, messages)
        input_ids = prompt_inputs.input_ids if hasattr(prompt_inputs, "input_ids") else prompt_inputs
        input_ids = input_ids.to(device)
        input_len = input_ids.shape[-1]

        with self.lock:
            try:
                import torch
            except ImportError as exc:
                raise LocalHFProviderError("torch is not installed.") from exc
            with torch.inference_mode():
                outputs = model.generate(
                    input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=self.temperature,
                    pad_token_id=tokenizer.eos_token_id,
                )

        generated_tokens = outputs[0][input_len:]
        return tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    def _build_prompt(self, tokenizer, messages):
        if hasattr(tokenizer, "apply_chat_template"):
            return tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt",
            )
        merged = "\n".join(f"{item['role']}: {item['content']}" for item in messages)
        return tokenizer(merged, return_tensors="pt").input_ids
