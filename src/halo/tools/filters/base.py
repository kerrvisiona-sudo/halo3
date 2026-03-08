"""Base classes for tool execution filters.

Intercepting Filter Pattern: cada request/response pasa por una cadena de filtros.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Any
from enum import Enum


class FilterStage(Enum):
    """When the filter runs."""

    PRE_EXECUTION = "pre_execution"  # Before tool execution
    POST_EXECUTION = "post_execution"  # After tool execution


@dataclass
class FilterResult:
    """Result from a filter.

    Filters pueden:
    - PASS: Continuar al siguiente filtro
    - MODIFY: Modificar parámetros/resultado y continuar
    - REJECT: Rechazar ejecución con error
    """

    action: str  # "pass", "modify", "reject"
    modified_data: Optional[dict] = None  # Modified params or result
    error_message: Optional[str] = None  # Error if rejected
    metadata: dict = None  # Extra info (logging, metrics)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ToolFilter(ABC):
    """Abstract base for tool execution filters.

    Similar a Express middleware o FastAPI dependencies.
    """

    def __init__(self, name: str, stage: FilterStage):
        self.name = name
        self.stage = stage
        self._next_filter: Optional["ToolFilter"] = None

    def set_next(self, filter: "ToolFilter") -> "ToolFilter":
        """Set next filter in chain.

        Returns:
            Next filter for chaining
        """
        self._next_filter = filter
        return filter

    def apply(self, data: dict, context: dict = None) -> FilterResult:
        """Apply filter to data.

        Args:
            data: Tool parameters (pre) or result (post)
            context: Conversation context

        Returns:
            FilterResult indicating what to do next
        """
        result = self._do_filter(data, context or {})

        # If rejected, stop chain
        if result.action == "reject":
            return result

        # If modified, use modified data for next filter
        next_data = result.modified_data if result.action == "modify" else data

        # Continue to next filter
        if self._next_filter:
            next_result = self._next_filter.apply(next_data, context)

            # Merge metadata from chain
            if next_result.metadata:
                result.metadata.update(next_result.metadata)

            return next_result

        # End of chain
        return result

    @abstractmethod
    def _do_filter(self, data: dict, context: dict) -> FilterResult:
        """Implement filter logic.

        Args:
            data: Data to filter
            context: Conversation context

        Returns:
            FilterResult
        """
        pass


class FilterChain:
    """Chain of filters for a specific stage."""

    def __init__(self, stage: FilterStage, filters: List[ToolFilter] = None):
        self.stage = stage
        self.filters = filters or []
        self._build_chain()

    def add_filter(self, filter: ToolFilter, position: int = -1):
        """Add filter to chain.

        Args:
            filter: Filter to add
            position: Position in chain (-1 = end)
        """
        if filter.stage != self.stage:
            raise ValueError(f"Filter stage mismatch: {filter.stage} != {self.stage}")

        if position == -1:
            self.filters.append(filter)
        else:
            self.filters.insert(position, filter)
        self._build_chain()

    def remove_filter(self, name: str):
        """Remove filter by name."""
        self.filters = [f for f in self.filters if f.name != name]
        self._build_chain()

    def _build_chain(self):
        """Build chain by linking filters."""
        for i in range(len(self.filters) - 1):
            self.filters[i].set_next(self.filters[i + 1])

    def apply(self, data: dict, context: dict = None) -> FilterResult:
        """Apply all filters in chain.

        Args:
            data: Data to filter
            context: Conversation context

        Returns:
            Final FilterResult
        """
        if not self.filters:
            return FilterResult(action="pass", modified_data=data)

        return self.filters[0].apply(data, context)
