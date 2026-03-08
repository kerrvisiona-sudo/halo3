"""Schema validator filter - validates parameters against JSON Schema."""

from ..base import ToolFilter, FilterResult, FilterStage
from ...registry import get_tool
import logging

logger = logging.getLogger(__name__)


class SchemaValidator(ToolFilter):
    """Validates tool parameters against JSON Schema.

    Prioriza calidad: rechaza ejecución si parámetros no son válidos.
    """

    def __init__(self):
        super().__init__("schema_validator", FilterStage.PRE_EXECUTION)

    def _do_filter(self, data: dict, context: dict) -> FilterResult:
        """Validate parameters against tool schema.

        Args:
            data: {"tool_name": str, "parameters": dict}
            context: Conversation context

        Returns:
            FilterResult (pass or reject)
        """
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {})

        tool = get_tool(tool_name)
        if not tool:
            return FilterResult(
                action="reject",
                error_message=f"Tool not found: {tool_name}",
                metadata={"validator": "schema", "error_type": "tool_not_found"},
            )

        # Validate required parameters
        schema = tool.parameters
        required = schema.get("required", [])
        missing = [param for param in required if param not in parameters]

        if missing:
            logger.warning(f"Missing required parameters for {tool_name}: {missing}")
            return FilterResult(
                action="reject",
                error_message=f"Missing required parameters: {', '.join(missing)}",
                metadata={
                    "validator": "schema",
                    "error_type": "missing_params",
                    "missing_params": missing,
                },
            )

        # Validate parameter types (basic validation)
        properties = schema.get("properties", {})
        invalid_params = []

        for param, value in parameters.items():
            if param in properties:
                expected_type = properties[param].get("type")
                if expected_type == "integer" and not isinstance(value, int):
                    invalid_params.append(f"{param} (expected int, got {type(value).__name__})")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    invalid_params.append(f"{param} (expected number, got {type(value).__name__})")
                elif expected_type == "string" and not isinstance(value, str):
                    invalid_params.append(f"{param} (expected string, got {type(value).__name__})")

        if invalid_params:
            logger.warning(f"Invalid parameter types for {tool_name}: {invalid_params}")
            return FilterResult(
                action="reject",
                error_message=f"Invalid parameter types: {', '.join(invalid_params)}",
                metadata={
                    "validator": "schema",
                    "error_type": "invalid_types",
                    "invalid_params": invalid_params,
                },
            )

        # Schema valid
        logger.debug(f"Schema validation passed for {tool_name}")
        return FilterResult(
            action="pass", metadata={"validator": "schema", "status": "valid"}
        )
