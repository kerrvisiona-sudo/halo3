"""Shared cache storage for intent classification."""

from typing import Dict, Optional
import json
import os


class IntentCache:
    """In-memory cache for intent classification results.

    Función pura: mismo input → mismo output (determinista)
    """

    def __init__(self, cache_file: str = None):
        """Initialize cache.

        Args:
            cache_file: Optional file to persist cache
        """
        self.cache_file = cache_file
        self._exact_cache: Dict[str, dict] = {}
        self._load_cache()

    def get_exact(self, key: str) -> Optional[dict]:
        """Get exact match from cache.

        Args:
            key: Exact user input

        Returns:
            Cached result or None
        """
        return self._exact_cache.get(key)

    def set_exact(self, key: str, tool_name: str, parameters: dict):
        """Store exact match in cache.

        Args:
            key: User input
            tool_name: Tool name
            parameters: Tool parameters
        """
        self._exact_cache[key] = {"tool_name": tool_name, "parameters": parameters}
        self._save_cache()

    def clear(self):
        """Clear all cache."""
        self._exact_cache.clear()
        self._save_cache()

    def _load_cache(self):
        """Load cache from file if it exists."""
        if self.cache_file and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    self._exact_cache = data.get("exact_cache", {})
            except Exception:
                pass

    def _save_cache(self):
        """Save cache to file."""
        if self.cache_file:
            try:
                with open(self.cache_file, "w") as f:
                    json.dump({"exact_cache": self._exact_cache}, f, indent=2)
            except Exception:
                pass


# Global cache instance
_cache_instance: Optional[IntentCache] = None


def get_cache() -> IntentCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        cache_file = os.getenv("HALO_INTENT_CACHE", ".halo_intent_cache.json")
        _cache_instance = IntentCache(cache_file)
    return _cache_instance
