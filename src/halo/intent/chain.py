"""Classifier chain orchestrator.

Intercepting Filter Pattern: cada request pasa por una cadena de filtros
hasta que uno la maneje.
"""

from typing import List, Optional
from .base import IntentClassifier, ClassificationResult
import logging

logger = logging.getLogger(__name__)


class ClassifierChain:
    """Orchestrates a chain of intent classifiers.

    Design pattern: Chain of Responsibility
    Permite agregar/quitar/reordenar clasificadores sin tocar código existente.
    """

    def __init__(self, classifiers: List[IntentClassifier] = None):
        """Initialize chain with optional list of classifiers.

        Args:
            classifiers: List of classifiers in priority order
        """
        self.classifiers = classifiers or []
        self._build_chain()

    def add_classifier(self, classifier: IntentClassifier, position: int = -1):
        """Add a classifier to the chain.

        Args:
            classifier: Classifier to add
            position: Position in chain (-1 = end)
        """
        if position == -1:
            self.classifiers.append(classifier)
        else:
            self.classifiers.insert(position, classifier)
        self._build_chain()

    def remove_classifier(self, name: str):
        """Remove a classifier by name.

        Args:
            name: Name of classifier to remove
        """
        self.classifiers = [c for c in self.classifiers if c.name != name]
        self._build_chain()

    def _build_chain(self):
        """Build the chain by linking classifiers."""
        for i in range(len(self.classifiers) - 1):
            self.classifiers[i].set_next(self.classifiers[i + 1])

    def classify(self, user_input: str, context: dict = None) -> Optional[ClassificationResult]:
        """Classify user intent using the chain.

        Args:
            user_input: User's natural language input
            context: Optional conversation context

        Returns:
            ClassificationResult or None if no classifier handled it
        """
        if not self.classifiers:
            logger.warning("No classifiers in chain")
            return None

        # Start the chain
        result = self.classifiers[0].classify(user_input, context)

        if result:
            logger.info(
                f"Intent classified by {result.classifier_used} "
                f"(confidence={result.confidence:.2f}, cached={result.cached})"
            )
        else:
            logger.warning(f"No classifier handled: {user_input}")

        return result

    def get_chain_info(self) -> List[dict]:
        """Get information about classifiers in the chain.

        Returns:
            List of classifier info dicts
        """
        return [
            {
                "name": c.name,
                "type": c.__class__.__name__,
                "threshold": c.confidence_threshold(),
            }
            for c in self.classifiers
        ]
