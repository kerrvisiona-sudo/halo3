"""NLG formatter filter - converts tool results to natural language."""

from ..base import ToolFilter, FilterResult, FilterStage
import logging

logger = logging.getLogger(__name__)


class NLGFormatter(ToolFilter):
    """Formats tool execution results as natural language.

    Convierte JSON responses a mensajes humanos más naturales.
    Prioriza calidad: genera respuestas contextuales y amigables.
    """

    def __init__(self, enable_nlg: bool = True):
        super().__init__("nlg_formatter", FilterStage.POST_EXECUTION)
        self.enable_nlg = enable_nlg

    def _do_filter(self, data: dict, context: dict) -> FilterResult:
        """Format result as natural language.

        Args:
            data: {"result": dict, "tool_name": str, "parameters": dict}
            context: Conversation context

        Returns:
            FilterResult with enhanced NLG message
        """
        if not self.enable_nlg:
            return FilterResult(action="pass", metadata={"nlg": "disabled"})

        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {})
        result = data.get("result", {}).copy()
        status = result.get("status")

        # Generate NLG based on tool and status
        nlg_message = None

        if status == "completed":
            nlg_message = self._generate_success_message(tool_name, parameters, result)
        elif status == "pending":
            nlg_message = self._generate_pending_message(tool_name, parameters)
        elif status == "error":
            nlg_message = self._generate_error_message(tool_name, result)

        if nlg_message and nlg_message != result.get("message"):
            result["message"] = nlg_message
            result["original_message"] = result.get("message")  # Preserve original

            logger.debug(f"NLG formatted message for {tool_name}")
            return FilterResult(
                action="modify",
                modified_data={**data, "result": result},
                metadata={"nlg": "formatted", "tool": tool_name},
            )

        return FilterResult(action="pass", metadata={"nlg": "unchanged"})

    def _generate_success_message(self, tool_name: str, params: dict, result: dict) -> str:
        """Generate success message."""
        room = params.get("room", "la habitación")
        action = params.get("action")

        if tool_name == "light_control":
            if action == "on":
                return f"✓ Luz de {room} encendida"
            elif action == "off":
                return f"✓ Luz de {room} apagada"
            elif action in ["dim", "brightness"]:
                level = params.get("level", "ajustado")
                return f"✓ Brillo de {room} ajustado a {level}%"

        elif tool_name == "climate_control":
            if action == "set_temp":
                temp = params.get("temperature", "configurado")
                return f"✓ Temperatura de {room} configurada a {temp}°C"
            elif action == "mode":
                mode = params.get("mode", "cambiado")
                mode_names = {"heat": "calefacción", "cool": "enfriamiento", "auto": "automático"}
                mode_spanish = mode_names.get(mode, mode)
                return f"✓ Modo de clima de {room} cambiado a {mode_spanish}"
            elif action == "status":
                state = result.get("device_state", {})
                temp = state.get("current_temperature", "?")
                target = state.get("target_temperature", "?")
                return f"Temperatura actual: {temp}°C (objetivo: {target}°C)"

        elif tool_name == "blinds_control":
            if action == "open":
                return f"✓ Persianas de {room} abiertas"
            elif action == "close":
                return f"✓ Persianas de {room} cerradas"
            elif action == "position":
                pos = params.get("position", "ajustado")
                return f"✓ Persianas de {room} ajustadas a {pos}%"

        elif tool_name == "home_status":
            scope = params.get("scope", "all")
            if scope == "all":
                state = result.get("device_state", {})
                rooms = state.get("rooms", [])
                devices = state.get("active_devices", 0)
                return f"Casa: {len(rooms)} habitaciones, {devices} dispositivos activos"

        # Fallback to original message
        return result.get("message", "Acción completada")

    def _generate_pending_message(self, tool_name: str, params: dict) -> str:
        """Generate pending message."""
        room = params.get("room", "la habitación")
        return f"⏳ Comando enviado a {room}, esperando confirmación..."

    def _generate_error_message(self, tool_name: str, result: dict) -> str:
        """Generate error message."""
        original = result.get("message", "Error desconocido")
        return f"❌ {original}"
