"""Context enricher filter - enriches parameters with context."""

from ..base import ToolFilter, FilterResult, FilterStage
import logging

logger = logging.getLogger(__name__)


class ContextEnricher(ToolFilter):
    """Enriches tool parameters with information from context.

    Examples:
    - "enciende la luz" (sin room) → usa last_room del contexto
    - "sube más" (sin level) → usa current_level + 10
    - "apágala" → usa last_device del contexto
    """

    def __init__(self):
        super().__init__("context_enricher", FilterStage.PRE_EXECUTION)

    def _do_filter(self, data: dict, context: dict) -> FilterResult:
        """Enrich parameters with context.

        Args:
            data: {"tool_name": str, "parameters": dict}
            context: Conversation context

        Returns:
            FilterResult (modify if enriched, pass otherwise)
        """
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {}).copy()
        enriched = False

        # Enrich based on tool type
        if tool_name == "light_control":
            enriched |= self._enrich_light_params(parameters, context)
        elif tool_name == "climate_control":
            enriched |= self._enrich_climate_params(parameters, context)
        elif tool_name == "blinds_control":
            enriched |= self._enrich_blinds_params(parameters, context)

        if enriched:
            logger.info(f"Context enriched parameters for {tool_name}: {parameters}")
            return FilterResult(
                action="modify",
                modified_data={"tool_name": tool_name, "parameters": parameters},
                metadata={"enricher": "context", "enriched": True},
            )

        return FilterResult(
            action="pass", metadata={"enricher": "context", "enriched": False}
        )

    def _enrich_light_params(self, params: dict, context: dict) -> bool:
        """Enrich light control parameters.

        Returns:
            True if enriched
        """
        enriched = False

        # If no room specified, use last room or current room
        if "room" not in params or not params["room"]:
            last_room = context.get("last_room") or context.get("room")
            if last_room:
                params["room"] = last_room
                enriched = True
                logger.debug(f"Enriched room with: {last_room}")

        # If brightness action but no level, use default or last level
        if params.get("action") in ["brightness", "dim"] and "level" not in params:
            if params["action"] == "dim":
                params["level"] = 30  # Default dim level
            else:
                params["level"] = context.get("last_brightness", 100)
            enriched = True

        return enriched

    def _enrich_climate_params(self, params: dict, context: dict) -> bool:
        """Enrich climate control parameters."""
        enriched = False

        # If setting temp but no room, use last room
        if "room" not in params or not params["room"]:
            last_room = context.get("last_room") or context.get("room")
            if last_room:
                params["room"] = last_room
                enriched = True

        # If no temperature specified for set_temp, use default
        if params.get("action") == "set_temp" and "temperature" not in params:
            params["temperature"] = context.get("last_temperature", 22)
            enriched = True

        return enriched

    def _enrich_blinds_params(self, params: dict, context: dict) -> bool:
        """Enrich blinds control parameters."""
        enriched = False

        # If no room specified, use last room
        if "room" not in params or not params["room"]:
            last_room = context.get("last_room") or context.get("room")
            if last_room:
                params["room"] = last_room
                enriched = True

        # If position action but no position value, use default
        if params.get("action") == "position" and "position" not in params:
            params["position"] = 50  # Default middle position
            enriched = True

        return enriched
