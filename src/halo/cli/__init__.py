import requests
import json
from typing import List, Dict, Any


class HaloClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self._last_request = None
        self._last_response = None

    def generate(
        self, prompt: str, max_new_tokens: int = 50, backend: str = "qwen"
    ) -> str:
        """Generate text using the custom API."""
        self._last_request = {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "backend": backend,
        }
        response = requests.post(
            f"{self.base_url}/generate",
            json=self._last_request,
        )
        response.raise_for_status()
        self._last_response = response.json()
        return self._last_response["response"]

    def get_debug_info(self) -> dict:
        """Return debug info from last request."""
        return {"request": self._last_request, "response": self._last_response}


class HomeAssistantClient:
    """Client for smart home assistant with context management."""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.context = {}
        self._last_request = None
        self._last_raw_response = None
        self._last_parsed = None

    def command(self, prompt: str, max_tokens: int = 50) -> tuple[str, dict]:
        """Execute a command and get response + updated context."""
        self._last_request = {
            "prompt": prompt,
            "context": self.context,
            "max_tokens": max_tokens,
        }
        response = requests.post(
            f"{self.base_url}/command",
            json=self._last_request,
        )
        response.raise_for_status()
        result = response.json()
        self._last_raw_response = response.text
        self._last_parsed = result
        self.context = result.get("context", {})
        return result["response"], self.context

    def reset_context(self):
        """Reset conversation context."""
        self.context = {}

    def get_debug_info(self) -> dict:
        """Return debug info from last request."""
        return {
            "request": self._last_request,
            "raw_response": self._last_raw_response,
            "parsed": self._last_parsed,
        }


class OpenAIClient:
    def __init__(self, base_url="http://localhost:8000/v1"):
        self.base_url = base_url

    def chat_completions(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 50,
        temperature: float = 1.0,
    ) -> Dict[str, Any]:
        """OpenAI-compatible chat completions."""
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()
        return response.json()

    def list_models(self) -> Dict[str, Any]:
        """List available models."""
        response = requests.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()
