"""Embedding model wrapper for semantic similarity.

Uses sentence-transformers for edge-friendly embeddings.
Model: all-MiniLM-L6-v2 (80MB, CPU-optimized)
"""

import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for sentence-transformer embeddings.

    Lazy loading: modelo solo se carga cuando se usa por primera vez.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info("✓ Embedding model loaded")
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed. "
                    "Embedding classifier will be disabled. "
                    "Install with: pip install sentence-transformers"
                )
                raise

    def encode(self, text: str) -> np.ndarray:
        """Encode text to embedding vector.

        Args:
            text: Input text

        Returns:
            Embedding vector (384 dimensions for MiniLM)
        """
        self._load_model()
        return self._model.encode(text, convert_to_numpy=True)

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts.

        Args:
            texts: List of input texts

        Returns:
            Matrix of embeddings
        """
        self._load_model()
        return self._model.encode(texts, convert_to_numpy=True)

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings.

        Args:
            emb1: First embedding
            emb2: Second embedding

        Returns:
            Similarity score (0.0 to 1.0)
        """
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


# Global embedding model instance
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    """Get global embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model
