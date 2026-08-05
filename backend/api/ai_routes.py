from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.ollama_service import OllamaError, ask_ollama


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class AIPrompt(BaseModel):
    prompt: str = Field(
        min_length=2,
        max_length=5000,
        description="Question ou instruction envoyée à l'IA locale.",
    )


class AIResponse(BaseModel):
    response: str


@router.post(
    "/test",
    response_model=AIResponse,
)
def test_ai(data: AIPrompt):
    try:
        answer = ask_ollama(data.prompt)

        return {
            "response": answer,
        }

    except OllamaError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error