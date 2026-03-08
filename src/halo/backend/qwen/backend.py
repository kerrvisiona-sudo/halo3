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

        # Decode only the generated tokens (exclude the input prompt)
        input_length = inputs.input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        return response

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the tokenizer.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not initialized. Call initialize() first.")
        return len(self.tokenizer.encode(text))

    def format_messages(
        self, messages: list[dict], system: str | None = None
    ) -> str:
        """Format messages using Qwen's chat template (ChatML).

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            system: Optional system prompt to prepend

        Returns:
            Formatted prompt string ready for generation
        """
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not initialized. Call initialize() first.")

        # Prepend system message if provided
        if system:
            messages = [{"role": "system", "content": system}] + list(messages)

        # Use tokenizer's chat template (Qwen uses ChatML format)
        return self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
