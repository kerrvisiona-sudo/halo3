"""Exact match classifier - Tier 1 (fastest, 0ms)."""

from typing import Optional
from ..base import IntentClassifier, ClassificationResult
from ..cache import get_cache


class ExactMatchClassifier(IntentClassifier):
    """Tier 1: Exact string match classifier.

    Fastest path: O(1) dict lookup
    Latency: <1ms
    Tokens: 0
    """

    def __init__(self):
        super().__init__("exact_match")
        self.cache = get_cache()

    def _do_classify(self, user_input: str, context: dict) -> Optional[ClassificationResult]:
        """Try exact match from cache.

        Args:
            user_input: User's input
            context: Conversation context (not used for exact match)

        Returns:
            ClassificationResult if exact match found, None otherwise
        """
        # Normalize input (lowercase, strip)
        key = user_input.lower().strip()

        cached = self.cache.get_exact(key)
        if cached:
            return ClassificationResult(
                tool_name=cached["tool_name"],
                parameters=cached["parameters"],
                confidence=1.0,  # Exact match = 100% confidence
                classifier_used=self.name,
                cached=True,
            )

        return None

    def confidence_threshold(self) -> float:
        """Exact match always has 100% confidence."""
        return 1.0

    def learn(self, user_input: str, tool_name: str, parameters: dict):
        """Learn a new exact match.

        Args:
            user_input: User input to cache
            tool_name: Tool that was called
            parameters: Parameters used
        """
        key = user_input.lower().strip()
        self.cache.set_exact(key, tool_name, parameters)
