"""Climate control handler (mock)."""


def climate_handler(
    action: str,
    room: str | None = None,
    temperature: float | None = None,
    mode: str | None = None,
) -> dict:
    """Handle climate control commands.

    Args:
        action: Action to perform (set_temp, mode, status)
        room: Room identifier (optional, defaults to all)
        temperature: Target temperature in Celsius
        mode: Climate mode (heat, cool, auto, off)

    Returns:
        Result dict with status and message
    """
    # Mock implementation - replace with real MQTT publish
    if action == "set_temp":
        temp = temperature or 22
        room_desc = room or "toda la casa"
        return {
            "status": "completed",
            "message": f"Temperatura de {room_desc} ajustada a {temp}°C",
            "device_state": {
                "room": room,
                "target_temperature": temp,
                "mode": mode or "auto",
            },
        }
    elif action == "mode":
        room_desc = room or "toda la casa"
        mode_desc = mode or "auto"
        return {
            "status": "completed",
            "message": f"Modo de clima de {room_desc} cambiado a {mode_desc}",
            "device_state": {"room": room, "mode": mode_desc},
        }
    elif action == "status":
        # Mock status query
        return {
            "status": "completed",
            "message": "Estado del clima",
            "device_state": {
                "room": room or "all",
                "current_temperature": 21,
                "target_temperature": 22,
                "mode": "auto",
            },
        }
    else:
        return {"status": "error", "message": f"Acción desconocida: {action}"}
