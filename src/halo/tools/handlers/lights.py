"""Light control handler (mock)."""


def light_handler(action: str, room: str, level: int | None = None) -> dict:
    """Handle light control commands.

    Args:
        action: Action to perform (on, off, dim, brightness)
        room: Room identifier
        level: Brightness level 0-100 (for dim/brightness actions)

    Returns:
        Result dict with status and message
    """
    # Mock implementation - replace with real MQTT publish
    if action == "on":
        return {
            "status": "completed",
            "message": f"Luz de {room} encendida",
            "device_state": {"room": room, "light": "on", "brightness": level or 100},
        }
    elif action == "off":
        return {
            "status": "completed",
            "message": f"Luz de {room} apagada",
            "device_state": {"room": room, "light": "off", "brightness": 0},
        }
    elif action in ["dim", "brightness"]:
        level = level or 50
        return {
            "status": "completed",
            "message": f"Luz de {room} ajustada a {level}%",
            "device_state": {"room": room, "light": "on", "brightness": level},
        }
    else:
        return {"status": "error", "message": f"Acción desconocida: {action}"}
