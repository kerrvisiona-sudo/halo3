import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from ..base import Backend


class QwenBackend(Backend):
    """Qwen 3.5-0.8B backend for text generation."""

    def __init__(self, model_name="Qwen/Qwen3.5-0.8B"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def initialize(self):
        """Load and initialize the Qwen model."""
        # Load token
        if os.path.exists(".keys"):
            load_dotenv(".keys")
            hf_token = os.getenv("HF_TOKEN")
            if hf_token:
                from huggingface_hub import login

                login(token=hf_token, add_to_git_credential=False)

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map="cpu",
                low_cpu_mem_usage=True,
            )
            print("✓ Qwen model loaded successfully!")
        except Exception as e:
            raise RuntimeError(f"Failed to load Qwen model: {e}")

    def generate(self, prompt: str, max_new_tokens: int = 50, **kwargs) -> str:
        """Generate text from prompt."""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        inputs = self.tokenizer(prompt, return_tensors="pt")

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
            **kwargs,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
