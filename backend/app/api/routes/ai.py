from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.schemas.analysis import ContentAnalysis
from backend.app.services.analysis_service import (
    BERT_SWAP_NOTE,
    ENGINE_NAME,
    content_analysis_service,
)
from backend.app.services.llm_service import chat_with_llm, summarize_with_llm
from backend.app.services.ranking_service import MODE_WEIGHTS, rank_content


router = APIRouter(
    prefix="/api/v1/ai",
    tags=["AI"],
)


class AnalysisRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = "Genel"
    mode: str = "odak"


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
    username: str | None = None


class ChatResponse(BaseModel):
    reply: str
    model: str


class SummarizeRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    method: str


def _build_context(username: str | None) -> str:
    """Build platform context for the LLM."""
    parts = []
    if username:
        parts.append(f"Kullanici: {username}")
    return " | ".join(parts) if parts else ""


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(payload: ChatRequest) -> ChatResponse:
    context = _build_context(payload.username)
    messages = [{"role": m.role, "content": m.content} for m in payload.messages]
    reply = await chat_with_llm(messages, context=context)
    return ChatResponse(reply=reply, model="local-fallback" if not _has_api_key() else "llm")


@router.post("/summarize", response_model=SummarizeResponse)
async def ai_summarize(payload: SummarizeRequest) -> SummarizeResponse:
    original_length = len(payload.content)
    summary = await summarize_with_llm(payload.content)
    method = "llm" if _has_api_key() else "extractive"
    return SummarizeResponse(
        summary=summary,
        original_length=original_length,
        summary_length=len(summary),
        method=method,
    )


@router.post(
    "/analyze",
    response_model=ContentAnalysis,
)
async def analyze_content(payload: AnalysisRequest) -> ContentAnalysis:
    return content_analysis_service.analyze(
        title=payload.title,
        description=payload.description,
        category=payload.category,
    )


@router.post("/preview")
async def analyze_and_rank(payload: AnalysisRequest):
    analysis = content_analysis_service.analyze(
        title=payload.title,
        description=payload.description,
        category=payload.category,
    )
    ranking = rank_content(analysis, payload.mode)
    return {
        "analysis": analysis,
        "ranking": ranking,
        "privacy": "Mod kullanici tarafindan secilir; gizli ruh hali tahmini yoktur.",
        "engine": ENGINE_NAME,
        "nlp_roadmap": BERT_SWAP_NOTE,
        "mode_weights": {
            key: [
                {"label": label, "field": field, "weight": weight}
                for label, field, weight in weights
            ]
            for key, weights in MODE_WEIGHTS.items()
        },
    }


def _has_api_key() -> bool:
    from backend.app.core.config import settings
    return bool(settings.openai_api_key)
