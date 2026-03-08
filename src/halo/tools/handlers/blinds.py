"""Blinds/shades control handler (mock)."""


def blinds_handler(action: str, room: str, position: int | None = None) -> dict:
    """Handle blinds/shades control commands.

    Args:
        action: Action to perform (open, close, position)
        room: Room identifier
        position: Position 0-100 (0=closed, 100=open)

    Returns:
        Result dict with status and message
    """
    # Mock implementation - replace with real MQTT publish
    if action == "open":
        return {
            "status": "completed",
            "message": f"Persiana de {room} abierta",
            "device_state": {"room": room, "position": 100},
        }
    elif action == "close":
        return {
            "status": "completed",
            "message": f"Persiana de {room} cerrada",
            "device_state": {"room": room, "position": 0},
        }
    elif action == "position":
        pos = position or 50
        return {
            "status": "completed",
            "message": f"Persiana de {room} ajustada a {pos}%",
            "device_state": {"room": room, "position": pos},
        }
    else:
        return {"status": "error", "message": f"Acción desconocida: {action}"}
