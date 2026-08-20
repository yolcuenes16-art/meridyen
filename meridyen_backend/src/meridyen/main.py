from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict

from meridyen.api.schemas import AggregateRequest, AnalyzeRequest, ConsentRequest, RankRequest, RewardRequest
from meridyen.domain.math import quality, safety, visibility_multiplier, wellbeing
from meridyen.ml.onnx import MultiTaskInference
from meridyen.privacy.dp import DifferentialPrivacyAggregator
from meridyen.services.consent import ConsentService
from meridyen.services.economy import CreatorEconomyService
from meridyen.services.ranking import RankingService


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MERIDYEN_", env_file=".env", extra="ignore")
    env: str = "development"
    model_path: str | None = None
    dp_epsilon: float = 1.0
    cors_origins: str = "http://localhost:5173"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.inference = MultiTaskInference(settings.model_path)
    app.state.ranking = RankingService(app.state.inference)
    app.state.economy = CreatorEconomyService()
    app.state.consent = ConsentService()
    app.state.dp = DifferentialPrivacyAggregator(settings.dp_epsilon)
    yield


app = FastAPI(title="Meridyen Social AI API", version="1.0.0", lifespan=lifespan)
settings = Settings()
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["content-type", "authorization"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": app.state.inference.fallback.version}


@app.post("/v1/analyze")
def analyze(payload: AnalyzeRequest):
    sig = app.state.inference.predict(payload.text)
    return {"signals": sig, "wellbeing_score": wellbeing(sig), "safety_score": safety(sig), "quality_score": quality(sig),
            "visibility_multiplier_preview": visibility_multiplier(sig, 0)}


@app.post("/v1/feed/rank")
def rank(payload: RankRequest):
    return {"mode": payload.mode, "items": app.state.ranking.rank(payload.content, payload.mode)}


@app.post("/v1/rewards/distribute")
def distribute(payload: RewardRequest):
    ranked = app.state.ranking.rank(payload.content, payload.mode)
    return {"entries": app.state.economy.distribute(payload.pool_amount, ranked)}


@app.post("/v1/privacy/consent")
def consent(payload: ConsentRequest):
    record = app.state.consent.set_mode_consent(payload.user_id, payload.mode, payload.consent)
    return {"consent_active": record is not None, "record": record}


@app.post("/v1/privacy/aggregate")
def aggregate(payload: AggregateRequest):
    # Only an aggregate value enters this endpoint; identity and content text are never accepted.
    if payload.count > 10_000_000:
        raise HTTPException(422, "count is outside aggregation policy")
    return {"metric": payload.metric, "noisy_count": app.state.dp.noisy_count(payload.count, payload.metric), "epsilon": app.state.dp.epsilon}


def run() -> None:
    uvicorn.run("meridyen.main:app", host="0.0.0.0", port=8000, reload=False)
