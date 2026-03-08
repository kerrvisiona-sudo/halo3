from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ...backend import Backend, get_backend
from typing import List, Optional
import time

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 50
    temperature: Optional[float] = 1.0


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: dict


class Model(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[Model]


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest, backend: Backend = Depends(get_backend)
):
    """OpenAI-compatible chat completions endpoint."""
    if request.model not in ["qwen-3.5-0.8b", "qwen"]:
        raise HTTPException(status_code=400, detail="Model not supported")

    # Format messages using chat template (if available)
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    if hasattr(backend, "format_messages"):
        prompt = backend.format_messages(messages)
    else:
        # Fallback to simple concatenation
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

    try:
        response_text = backend.generate(prompt, request.max_tokens or 50)

        # Real token counting (requires QwenBackend with count_tokens method)
        prompt_tokens = (
            backend.count_tokens(prompt)
            if hasattr(backend, "count_tokens")
            else len(prompt.split())
        )
        completion_tokens = (
            backend.count_tokens(response_text)
            if hasattr(backend, "count_tokens")
            else len(response_text.split())
        )

        # Simple response, assuming one choice
        choice = ChatCompletionChoice(
            index=0,
            message=Message(role="assistant", content=response_text),
            finish_reason="stop",
        )
        response = ChatCompletionResponse(
            id="chatcmpl-halo",
            created=int(time.time()),
            model=request.model,
            choices=[choice],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completions")
async def completions():
    """Stub for completions endpoint."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/embeddings")
async def embeddings():
    """Stub for embeddings endpoint."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/models")
async def list_models():
    """List available models."""
    model = Model(id="qwen-3.5-0.8b", created=int(time.time()), owned_by="halo")
    return ModelsResponse(data=[model])
