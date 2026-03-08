"""Home status query handler (mock)."""


def status_handler(
    scope: str = "all", room: str | None = None, device: str | None = None
) -> dict:
    """Handle home status queries.

    Args:
        scope: Query scope (all, room, device)
        room: Room identifier (for room/device scope)
        device: Device identifier (for device scope)

    Returns:
        Result dict with status and current state
    """
    # Mock implementation - replace with real MQTT query
    if scope == "all":
        return {
            "status": "completed",
            "message": "Estado general del hogar",
            "device_state": {
                "rooms": ["sala", "cocina", "dormitorio"],
                "active_devices": 5,
                "temperature": 21,
            },
        }
    elif scope == "room" and room:
        return {
            "status": "completed",
            "message": f"Estado de {room}",
            "device_state": {
                "room": room,
                "lights": "on",
                "temperature": 22,
                "blinds": "open",
            },
        }
    elif scope == "device" and device:
        return {
            "status": "completed",
            "message": f"Estado de {device}",
            "device_state": {"device": device, "status": "active", "room": room},
        }
    else:
        return {"status": "error", "message": "Parámetros inválidos para consulta"}
