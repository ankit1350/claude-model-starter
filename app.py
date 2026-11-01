import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="Claude Model Starter", version="1.0.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=100_000)
    model: str | None = None
    max_tokens: int | None = Field(default=None, ge=1, le=8192)


class ChatResponse(BaseModel):
    provider: Literal["anthropic", "local"]
    model: str
    response: str


def _anthropic_chat(request: ChatRequest) -> ChatResponse:
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not configured")

    model = request.model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    client = Anthropic(api_key=api_key)
    result = client.messages.create(
        model=model,
        max_tokens=request.max_tokens or int(os.getenv("MAX_TOKENS", "1024")),
        messages=[{"role": "user", "content": request.message}],
    )
    text = "".join(block.text for block in result.content if getattr(block, "type", None) == "text")
    return ChatResponse(provider="anthropic", model=model, response=text)


@lru_cache(maxsize=1)
def _local_pipeline():
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Local inference requires transformers and torch to be installed",
        ) from exc
    model_id = os.getenv("LOCAL_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
    return model_id, pipeline("text-generation", model=model_id)


def _local_chat(request: ChatRequest) -> ChatResponse:
    model_id, generator = _local_pipeline()
    result = generator(
        request.message,
        max_new_tokens=request.max_tokens or int(os.getenv("MAX_TOKENS", "256")),
        return_full_text=False,
    )
    return ChatResponse(provider="local", model=model_id, response=result[0]["generated_text"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": os.getenv("MODEL_PROVIDER", "anthropic")}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    provider = os.getenv("MODEL_PROVIDER", "anthropic").lower()
    if provider == "anthropic":
        return _anthropic_chat(request)
    if provider == "local":
        return _local_chat(request)
    raise HTTPException(status_code=500, detail=f"Unsupported MODEL_PROVIDER: {provider}")
