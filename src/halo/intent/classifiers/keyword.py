"""Keyword-based classifier - Tier 3 (fast, 0 tokens)."""

from typing import Optional
from ..base import IntentClassifier, ClassificationResult
from ...tools.dispatcher import dispatch


class KeywordClassifier(IntentClassifier):
    """Tier 3: Keyword matching classifier.

    Uses regex and keyword patterns for common commands.
    Latency: <1ms
    Tokens: 0
    """

    def __init__(self):
        super().__init__("keyword")

    def _do_classify(self, user_input: str, context: dict) -> Optional[ClassificationResult]:
        """Try keyword-based dispatch.

        Args:
            user_input: User's input
            context: Conversation context (not used for keywords)

        Returns:
            ClassificationResult if keyword matched, None otherwise
        """
        result = dispatch(user_input)

        if result:
            tool_name, parameters = result
            return ClassificationResult(
                tool_name=tool_name,
                parameters=parameters,
                confidence=0.9,  # High confidence for keyword matches
                classifier_used=self.name,
                cached=False,
            )

        return None

    def confidence_threshold(self) -> float:
        """Keyword matching threshold."""
        return 0.9
