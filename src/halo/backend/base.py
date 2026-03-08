from abc import ABC, abstractmethod


class Backend(ABC):
    """Base class for inference backends."""

    @abstractmethod
    def initialize(self):
        """Load and initialize the model."""
        pass

    @abstractmethod
    def generate(self, prompt: str, max_new_tokens: int = 50, **kwargs) -> str:
        """Generate text from prompt."""
        pass
