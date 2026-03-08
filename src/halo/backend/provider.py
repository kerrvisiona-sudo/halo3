"""Singleton provider for backend instances."""

from .base import Backend
from .qwen.backend import QwenBackend

_backend: Backend | None = None


def get_backend() -> Backend:
    """Get or create the singleton backend instance.

    This ensures only one model is loaded in memory across all routes.
    Thread-safe for FastAPI's dependency injection system.
    """
    global _backend
    if _backend is None:
        _backend = QwenBackend()
        _backend.initialize()
    return _backend


def reset_backend():
    """Reset the backend (for testing purposes)."""
    global _backend
    _backend = None
