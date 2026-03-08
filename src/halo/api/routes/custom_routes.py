from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ...backend import Backend, get_backend

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 50
    backend: str = "qwen"


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.post("/generate")
async def generate_text(
    request: GenerateRequest, backend: Backend = Depends(get_backend)
):
    """Generate text using the specified backend."""
    if request.backend == "qwen":
        try:
            response = backend.generate(request.prompt, request.max_new_tokens)
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Unsupported backend")
