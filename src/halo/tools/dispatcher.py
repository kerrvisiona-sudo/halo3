"""Hybrid tool dispatcher: keyword matching + LLM fallback.

For edge models (0.8B), keyword matching saves tokens and improves accuracy.
Only falls back to LLM when no keyword match is found.
"""

import re
from .registry import TOOLS, get_tool


class DispatchRule:
    """Keyword-based dispatch rule."""

    def __init__(self, tool_name: str, keywords: list[str], param_extractors: dict = None):
        self.tool_name = tool_name
        self.keywords = keywords
        self.param_extractors = param_extractors or {}

    def matches(self, text: str) -> bool:
        """Check if any keyword matches the text."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)

    def extract_params(self, text: str) -> dict:
        """Extract parameters from text using simple patterns."""
        params = {}
        text_lower = text.lower()

        for param_name, extractor in self.param_extractors.items():
            if callable(extractor):
                value = extractor(text_lower)
                if value is not None:
                    params[param_name] = value

        return params


# Dispatch rules for common patterns (0 tokens!)
DISPATCH_RULES = [
    # Light control
    DispatchRule(
        "light_control",
        keywords=["luz", "luces", "encender", "apagar", "enciende", "apaga", "iluminación"],
        param_extractors={
            "action": lambda t: (
                "on"
                if any(w in t for w in ["encender", "enciende", "prende", "prende"])
                else "off" if any(w in t for w in ["apagar", "apaga"]) else "on"
            ),
            "room": lambda t: (
                extract_room(t)
            ),
        },
    ),
    # Climate control
    DispatchRule(
        "climate_control",
        keywords=["temperatura", "aire", "calefacción", "climatización", "grados", "frío", "calor"],
        param_extractors={
            "action": lambda t: "set_temp" if any(w in t for w in ["pon", "ajusta", "grados"]) else "status",
            "room": lambda t: extract_room(t),
            "temperature": lambda t: extract_temperature(t),
        },
    ),
    # Blinds control
    DispatchRule(
        "blinds_control",
        keywords=["persiana", "persianas", "cortina", "cortinas", "ventana"],
        param_extractors={
            "action": lambda t: (
                "open"
                if any(w in t for w in ["abrir", "abre", "sube"])
                else "close" if any(w in t for w in ["cerrar", "cierra", "baja"]) else "open"
            ),
            "room": lambda t: extract_room(t),
        },
    ),
    # Status queries
    DispatchRule(
        "home_status",
        keywords=["estado", "cómo está", "mostrar", "ver", "consulta", "info", "información"],
        param_extractors={
            "scope": lambda t: "all",  # Default to all
        },
    ),
]


def extract_room(text: str) -> str | None:
    """Extract room name from text."""
    rooms = ["sala", "salón", "cocina", "dormitorio", "baño", "comedor", "habitación"]
    for room in rooms:
        if room in text:
            return room
    return "sala"  # Default fallback


def extract_temperature(text: str) -> float | None:
    """Extract temperature from text (e.g., '22 grados')."""
    match = re.search(r"(\d+)\s*grados?", text)
    if match:
        return float(match.group(1))
    return None


def dispatch(user_input: str) -> tuple[str, dict] | None:
    """Dispatch user input to appropriate tool.

    Uses keyword matching first (fast, 0 tokens).
    Falls back to LLM classification only if no match.

    Args:
        user_input: User's natural language input

    Returns:
        Tuple of (tool_name, parameters) or None if no dispatch
    """
    # Try keyword-based dispatch first
    for rule in DISPATCH_RULES:
        if rule.matches(user_input):
            params = rule.extract_params(user_input)
            # Validate we have required params
            tool = get_tool(rule.tool_name)
            if tool:
                return rule.tool_name, params

    # No keyword match - return None (LLM will handle)
    return None
