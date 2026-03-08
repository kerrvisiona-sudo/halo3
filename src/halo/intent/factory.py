"""Factory for building classifier chains.

Configuración centralizada de la cadena de clasificadores.
"""

from .chain import ClassifierChain
from .classifiers import (
    ExactMatchClassifier,
    EmbeddingClassifier,
    KeywordClassifier,
    LLMClassifier,
)
from ..backend import Backend


# System prompt for LLM classifier
LLM_SYSTEM_PROMPT = """Asistente de hogar. Responde SOLO JSON.

Tools:
- light_control: {"action": "on|off|dim|brightness", "room": "sala|cocina|...", "level": 0-100}
- climate_control: {"action": "set_temp|mode|status", "room": "sala|...", "temperature": 22, "mode": "heat|cool|auto|off"}
- blinds_control: {"action": "open|close|position", "room": "sala|...", "position": 0-100}
- home_status: {"scope": "all|room|device", "room": "sala|..."}

Ejemplos:
"enciende la luz del salon" -> {"tool": "light_control", "parameters": {"action": "on", "room": "salon"}}
"como esta la casa?" -> {"tool": "home_status", "parameters": {"scope": "all"}}
"muestra el estado de todos los dispositivos" -> {"tool": "home_status", "parameters": {"scope": "all"}}
"pon el aire a 22 grados" -> {"tool": "climate_control", "parameters": {"action": "set_temp", "temperature": 22}}
"cierra las persianas de la cocina" -> {"tool": "blinds_control", "parameters": {"action": "close", "room": "cocina"}}
"gracias" -> {"response": "De nada! ¿Algo más?"}

Formato:
{"tool": "nombre_tool", "parameters": {...}}"""


def create_default_chain(backend: Backend, enable_embeddings: bool = True) -> ClassifierChain:
    """Create the default classifier chain for intent classification.

    Chain order (priority):
    1. ExactMatchClassifier (0ms, cached exact matches)
    2. EmbeddingClassifier (5-10ms, semantic similarity) [optional]
    3. KeywordClassifier (<1ms, regex/keyword patterns)
    4. LLMClassifier (7s, LLM fallback)

    Args:
        backend: Backend instance for LLM classifier
        enable_embeddings: Whether to enable embedding classifier (requires sentence-transformers)

    Returns:
        Configured ClassifierChain
    """
    classifiers = [
        ExactMatchClassifier(),
    ]

    if enable_embeddings:
        try:
            classifiers.append(EmbeddingClassifier(similarity_threshold=0.85))
        except ImportError:
            # sentence-transformers not installed, skip
            pass

    classifiers.extend(
        [
            KeywordClassifier(),
            LLMClassifier(backend, LLM_SYSTEM_PROMPT),
        ]
    )

    return ClassifierChain(classifiers)
