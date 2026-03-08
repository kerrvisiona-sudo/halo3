"""Parameter normalizer filter - normalizes parameter values."""

from ..base import ToolFilter, FilterResult, FilterStage
import logging

logger = logging.getLogger(__name__)


class ParameterNormalizer(ToolFilter):
    """Normalizes parameter values to canonical forms.

    Examples:
    - "salon" → "sala"
    - "living" → "sala"
    - "cocina" → "cocina" (ya es canónico)
    - temperature: "22" (string) → 22 (int)
    """

    def __init__(self):
        super().__init__("parameter_normalizer", FilterStage.PRE_EXECUTION)

        # Room name normalization mappings
        self.room_mappings = {
            "salon": "sala",
            "living": "sala",
            "salón": "sala",
            "cuarto": "dormitorio",
            "habitacion": "dormitorio",
            "habitación": "dormitorio",
            "pieza": "dormitorio",
            "baño": "bano",
            "bano": "bano",
        }

        # Action normalization (if needed)
        self.action_mappings = {
            "encender": "on",
            "enciende": "on",
            "prender": "on",
            "prende": "on",
            "apagar": "off",
            "apaga": "off",
            "abrir": "open",
            "abre": "open",
            "cerrar": "close",
            "cierra": "close",
        }

    def _do_filter(self, data: dict, context: dict) -> FilterResult:
        """Normalize parameters to canonical forms.

        Args:
            data: {"tool_name": str, "parameters": dict}
            context: Conversation context

        Returns:
            FilterResult (modify if normalized, pass otherwise)
        """
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {}).copy()
        normalized = False

        # Normalize room names
        if "room" in parameters:
            original_room = parameters["room"]
            normalized_room = self.room_mappings.get(original_room.lower(), original_room)
            if normalized_room != original_room:
                parameters["room"] = normalized_room
                normalized = True
                logger.debug(f"Normalized room: {original_room} → {normalized_room}")

        # Normalize action (if tool uses Spanish actions)
        if "action" in parameters:
            original_action = parameters["action"]
            if isinstance(original_action, str):
                normalized_action = self.action_mappings.get(
                    original_action.lower(), original_action
                )
                if normalized_action != original_action:
                    parameters["action"] = normalized_action
                    normalized = True
                    logger.debug(f"Normalized action: {original_action} → {normalized_action}")

        # Normalize numeric parameters (string → number)
        for param in ["temperature", "level", "position"]:
            if param in parameters:
                value = parameters[param]
                if isinstance(value, str) and value.replace(".", "").isdigit():
                    try:
                        # Try int first, then float
                        if "." in value:
                            parameters[param] = float(value)
                        else:
                            parameters[param] = int(value)
                        normalized = True
                        logger.debug(f"Normalized {param}: {value} → {parameters[param]}")
                    except ValueError:
                        pass

        if normalized:
            logger.info(f"Normalized parameters for {tool_name}")
            return FilterResult(
                action="modify",
                modified_data={"tool_name": tool_name, "parameters": parameters},
                metadata={"normalizer": "parameters", "normalized": True},
            )

        return FilterResult(
            action="pass", metadata={"normalizer": "parameters", "normalized": False}
        )
