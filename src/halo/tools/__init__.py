"""Function tools framework for home automation."""

from .registry import Tool, TOOLS, get_tool, get_tools_schema
from .executor import execute_tool
from .dispatcher import dispatch

__all__ = ["Tool", "TOOLS", "get_tool", "get_tools_schema", "execute_tool", "dispatch"]
