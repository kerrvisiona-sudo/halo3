"""Mock handlers for home automation tools."""

from .lights import light_handler
from .climate import climate_handler
from .blinds import blinds_handler
from .status import status_handler

__all__ = ["light_handler", "climate_handler", "blinds_handler", "status_handler"]
