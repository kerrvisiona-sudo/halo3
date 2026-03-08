"""Context updater filter - updates conversation context with result."""

from ..base import ToolFilter, FilterResult, FilterStage
import logging

logger = logging.getLogger(__name__)


class ContextUpdater(ToolFilter):
    """Updates conversation context based on tool execution result.

    Tracks:
    - last_room: última habitación mencionada
    - last_device: último dispositivo controlado
    - device_states: estados actuales de dispositivos
    - last_temperature: última temperatura configurada
    - last_brightness: último nivel de brillo
    """

    def __init__(self):
        super().__init__("context_updater", FilterStage.POST_EXECUTION)

    def _do_filter(self, data: dict, context: dict) -> FilterResult:
        """Update context with execution result.

        Args:
            data: {"result": dict, "tool_name": str, "parameters": dict}
            context: Current conversation context (will be updated in-place)

        Returns:
            FilterResult with updated context in metadata
        """
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {})
        result = data.get("result", {})
        device_state = result.get("device_state", {})

        context_updates = {}

        # Update last_room if specified
        if "room" in parameters:
            context_updates["last_room"] = parameters["room"]

        # Tool-specific context updates
        if tool_name == "light_control":
            context_updates.update(self._update_light_context(parameters, device_state))
        elif tool_name == "climate_control":
            context_updates.update(self._update_climate_context(parameters, device_state))
        elif tool_name == "blinds_control":
            context_updates.update(self._update_blinds_context(parameters, device_state))

        # Update device states registry
        if device_state:
            device_states = context.get("device_states", {})
            room = parameters.get("room", "unknown")
            device_type = self._get_device_type(tool_name)

            device_key = f"{room}_{device_type}"
            device_states[device_key] = device_state
            context_updates["device_states"] = device_states

        if context_updates:
            logger.info(f"Context updated with: {list(context_updates.keys())}")
            return FilterResult(
                action="modify",
                modified_data=data,  # Pass through result unchanged
                metadata={
                    "context_updater": "context",
                    "context_updates": context_updates,
                },
            )

        return FilterResult(
            action="pass",
            metadata={"context_updater": "context", "updates": None},
        )

    def _update_light_context(self, params: dict, state: dict) -> dict:
        """Update context for light control."""
        updates = {}

        if "brightness" in state:
            updates["last_brightness"] = state["brightness"]

        if "light" in state:
            updates["last_light_state"] = state["light"]

        return updates

    def _update_climate_context(self, params: dict, state: dict) -> dict:
        """Update context for climate control."""
        updates = {}

        if "target_temperature" in state:
            updates["last_temperature"] = state["target_temperature"]

        if "mode" in state:
            updates["last_climate_mode"] = state["mode"]

        return updates

    def _update_blinds_context(self, params: dict, state: dict) -> dict:
        """Update context for blinds control."""
        updates = {}

        if "position" in state:
            updates["last_blinds_position"] = state["position"]

        return updates

    def _get_device_type(self, tool_name: str) -> str:
        """Get device type from tool name."""
        mapping = {
            "light_control": "light",
            "climate_control": "climate",
            "blinds_control": "blinds",
        }
        return mapping.get(tool_name, "unknown")
