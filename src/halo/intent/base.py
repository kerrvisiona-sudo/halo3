"""Base classes for intent classification chain.

Chain of Responsibility pattern: cada clasificador decide si maneja la request
o la pasa al siguiente en la cadena.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassificationResult:
    """Result from intent classification.

    Función pura: mismo input → mismo output (determinista)
    """

    tool_name: str
    parameters: dict
    confidence: float  # 0.0 - 1.0
    classifier_used: str  # Which classifier produced this result
    cached: bool = False  # Was this from cache?


class IntentClassifier(ABC):
    """Abstract base for intent classifiers.

    Cada implementación es una Strategy que puede manejar la request
    o pasar al siguiente en la cadena.
    """

    def __init__(self, name: str):
        self.name = name
        self._next_classifier: Optional["IntentClassifier"] = None

    def set_next(self, classifier: "IntentClassifier") -> "IntentClassifier":
        """Set the next classifier in the chain.

        Returns the next classifier for chaining convenience.
        """
        self._next_classifier = classifier
        return classifier

    def classify(self, user_input: str, context: dict = None) -> Optional[ClassificationResult]:
        """Classify user intent.

        Chain of Responsibility: intenta clasificar, si no puede pasa al siguiente.

        Args:
            user_input: User's natural language input
            context: Optional conversation context

        Returns:
            ClassificationResult if classified, None to pass to next
        """
        # Try to handle this request
        result = self._do_classify(user_input, context or {})

        if result is not None:
            # This classifier handled it
            return result

        # Pass to next in chain
        if self._next_classifier:
            return self._next_classifier.classify(user_input, context)

        # End of chain, no classifier handled it
        return None

    @abstractmethod
    def _do_classify(self, user_input: str, context: dict) -> Optional[ClassificationResult]:
        """Implement classification logic.

        Returns:
            ClassificationResult if this classifier can handle it
            None to pass to next classifier
        """
        pass

    @abstractmethod
    def confidence_threshold(self) -> float:
        """Minimum confidence to accept this classifier's result.

        Returns:
            Threshold between 0.0 and 1.0
        """
        pass
