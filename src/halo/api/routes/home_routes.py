from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ...backend import Backend, get_backend
import json
import time

router = APIRouter()

SYSTEM_PROMPT = """Eres un asistente de hogar inteligente (como Siri, Alexa o Google Home).
Responde de forma concisa y útil.

Cuando respondas, SIEMPRE usa este formato JSON (y solo este JSON, sin texto adicional):
{
  "response": "Tu respuesta al usuario",
  "context": {"clave": "valor"} o {} si no hay contexto importante a mantener
}

El contexto debe contener solo información importante que el usuario haya mencionado
y que sea relevante para mantener en futuras conversaciones, como:
- La habitación actual (ej: "habitacion": "sala")
- Dispositivos mencionados (ej: "luz_sala": "encendida")
- Configuraciones actuales (ej: "temperatura": 22)

Ejemplos:
- Usuario: "enciende la luz" → {"response": "Luz encendida", "context": {"luz_actual": "encendida"}}
- Usuario: "bájala más" (teniendo context {"luz_actual": "encendida"}) → {"response": "Luz baixada más", "context": {"luz_actual": "encendida, nivel bajo"}}
"""


class CommandRequest(BaseModel):
    prompt: str
    context: dict = {}
    max_tokens: int = 50


class CommandResponse(BaseModel):
    response: str
    context: dict


@router.post("/command")
async def command(request: CommandRequest, backend: Backend = Depends(get_backend)):
    """Smart home assistant command endpoint with context management."""
    full_prompt = f"{SYSTEM_PROMPT}\n\nContexto actual: {json.dumps(request.context)}\n\nUsuario: {request.prompt}\n\nRespuesta JSON:"

    try:
        raw_response = backend.generate(full_prompt, request.max_tokens)

        # Try to parse JSON from response
        try:
            # Find JSON in response (may have text before/after)
            start = raw_response.find("{")
            end = raw_response.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(raw_response[start:end])
                return CommandResponse(
                    response=result.get("response", raw_response),
                    context=result.get("context", {}),
                )
        except json.JSONDecodeError:
            pass

        # Fallback: return raw response with empty context
        return CommandResponse(response=raw_response, context={})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
