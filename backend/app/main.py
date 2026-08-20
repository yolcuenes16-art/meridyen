from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.analysis import router as analysis_router
from backend.app.api.routes.comments import router as comments_router
from backend.app.api.routes.content import router as content_router
from backend.app.api.routes.economy import router as economy_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.likes import router as likes_router
from backend.app.api.routes.posts import router as posts_router
from backend.app.api.routes.users import router as users_router
from backend.app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "Meridyen; rızaya dayalı kullanım modu, Türkçe güvenlik/refah skorlaması, "
        "şeffaf akış yeniden sıralama ve görünürlük çarpanlı gelir paylaşımını "
        "birleştiren NSosyal katmanı API'sidir. Gizli duygu çıkarımı yoktur."
    ),
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(content_router)
app.include_router(analysis_router)
app.include_router(posts_router)
app.include_router(likes_router)
app.include_router(comments_router)
app.include_router(users_router)
app.include_router(economy_router)