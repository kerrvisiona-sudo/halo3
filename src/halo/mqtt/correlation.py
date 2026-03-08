"""Request/Response correlation store for MQTT."""

import asyncio
from uuid import uuid4
from typing import Dict, Any


class CorrelationStore:
    """Store for correlating MQTT requests with responses."""

    def __init__(self):
        self._pending: Dict[str, asyncio.Future] = {}

    def create_id(self) -> str:
        """Generate a new correlation ID.

        Returns:
            UUID string
        """
        return str(uuid4())

    async def wait(self, correlation_id: str, timeout: float = 3.0) -> Any:
        """Wait for a response with given correlation ID.

        Args:
            correlation_id: Correlation identifier
            timeout: Timeout in seconds (default 3.0 for edge)

        Returns:
            Response data

        Raises:
            asyncio.TimeoutError: If timeout expires before response
        """
        future = asyncio.Future()
        self._pending[correlation_id] = future
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self._pending.pop(correlation_id, None)

    def resolve(self, correlation_id: str, data: Any) -> bool:
        """Resolve a pending correlation with response data.

        Args:
            correlation_id: Correlation identifier
            data: Response data

        Returns:
            True if correlation was pending, False otherwise
        """
        future = self._pending.get(correlation_id)
        if future and not future.done():
            future.set_result(data)
            return True
        return False

    def cancel(self, correlation_id: str) -> bool:
        """Cancel a pending correlation.

        Args:
            correlation_id: Correlation identifier

        Returns:
            True if correlation was cancelled, False if not found
        """
        future = self._pending.pop(correlation_id, None)
        if future and not future.done():
            future.cancel()
            return True
        return False

    def clear(self):
        """Clear all pending correlations."""
        for future in self._pending.values():
            if not future.done():
                future.cancel()
        self._pending.clear()
