"""Tool execution coordinator."""

import json
from .registry import get_tool


class ToolCallError(Exception):
    """Error during tool execution."""

    pass


def execute_tool(tool_name: str, parameters: dict) -> dict:
    """Execute a tool with given parameters.

    Args:
        tool_name: Name of the tool to execute
        parameters: Parameters dict matching tool's JSON Schema

    Returns:
        Result dict with status, message, and optional device_state

    Raises:
        ToolCallError: If tool not found or execution fails
    """
    tool = get_tool(tool_name)
    if not tool:
        raise ToolCallError(f"Tool not found: {tool_name}")

    try:
        # Call handler with unpacked parameters
        result = tool.handler(**parameters)
        return result
    except TypeError as e:
        raise ToolCallError(f"Invalid parameters for {tool_name}: {e}")
    except Exception as e:
        raise ToolCallError(f"Tool execution failed: {e}")


def parse_tool_call(llm_output: str) -> tuple[str, dict] | None:
    """Parse tool call from LLM output.

    Expected format (JSON):
    {
        "tool": "tool_name",
        "parameters": {...}
    }

    Args:
        llm_output: Raw LLM output string (may contain <think> tags)

    Returns:
        Tuple of (tool_name, parameters) or None if no tool call found
    """
    # Clean up thinking tags that Qwen generates
    cleaned = llm_output
    if "<think>" in cleaned:
        # Remove everything between <think> and </think>
        import re

        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL)

    cleaned = cleaned.strip()

    try:
        # Try to find JSON in output
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = cleaned[start:end]
            data = json.loads(json_str)
            if "tool" in data and "parameters" in data:
                return data["tool"], data["parameters"]
    except json.JSONDecodeError:
        pass
    return None
