"""MQTT topic naming conventions.

Following Home Assistant / Zigbee2MQTT patterns:
- halo/command/{room}/{device} - Publish commands
- halo/state/{room}/{device} - Subscribe to device states
- halo/response/{correlation_id} - Correlated responses
"""


class Topics:
    """MQTT topic builder."""

    BASE = "halo"

    @classmethod
    def command(cls, room: str | None = None, device: str | None = None) -> str:
        """Build command topic.

        Args:
            room: Room identifier (optional)
            device: Device identifier (optional)

        Returns:
            MQTT topic string
        """
        parts = [cls.BASE, "command"]
        if room:
            parts.append(room)
        if device:
            parts.append(device)
        return "/".join(parts)

    @classmethod
    def state(cls, room: str | None = None, device: str | None = None) -> str:
        """Build state topic.

        Args:
            room: Room identifier (optional for wildcard subscription)
            device: Device identifier (optional for wildcard subscription)

        Returns:
            MQTT topic string
        """
        parts = [cls.BASE, "state"]
        if room:
            parts.append(room)
        if device:
            parts.append(device)
        return "/".join(parts)

    @classmethod
    def response(cls, correlation_id: str) -> str:
        """Build response topic for correlation.

        Args:
            correlation_id: Unique correlation identifier

        Returns:
            MQTT topic string
        """
        return f"{cls.BASE}/response/{correlation_id}"

    @classmethod
    def state_wildcard(cls) -> str:
        """Get wildcard topic for all state updates.

        Returns:
            MQTT topic with wildcard
        """
        return f"{cls.BASE}/state/#"
