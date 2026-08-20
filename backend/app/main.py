import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.db.init_db import init_db


def _setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    logging.getLogger("meridyen.access").setLevel(logging.INFO)
    logging.getLogger("meridyen.errors").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _setup_logging()
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Meridyen; rizaya dayali kullanim modu, Turkce guvenlik/refah skorlamasi, "
        "seffaf akis yeniden siralama ve gorunurluk carpanli gelir paylasimini "
        "birlestiren NSosyal katmani API'sidir. Gizli duygu cikarimi yoktur."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

from backend.app.middleware.error_handler import ErrorHandlerMiddleware
from backend.app.middleware.logging_middleware import RequestLoggingMiddleware
from backend.app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://192.168.1.193:5173",
        "http://192.168.1.193:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.app.api.routes.analysis import router as analysis_router
from backend.app.api.routes.ai import router as ai_router
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.bookmarks import router as bookmarks_router
from backend.app.api.routes.comments import router as comments_router
from backend.app.api.routes.content import router as content_router
from backend.app.api.routes.economy import router as economy_router
from backend.app.api.routes.analytics import router as analytics_router
from backend.app.api.routes.follows import router as follows_router
from backend.app.api.routes.gamification import router as gamification_router
from backend.app.api.routes.hashtags import router as hashtags_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.likes import router as likes_router
from backend.app.api.routes.posts import router as posts_router
from backend.app.api.routes.reports import router as reports_router
from backend.app.api.routes.search import router as search_router
from backend.app.api.routes.users import router as users_router
from backend.app.api.routes.websocket import router as websocket_router

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(content_router)
app.include_router(analysis_router)
app.include_router(ai_router)
app.include_router(posts_router)
app.include_router(likes_router)
app.include_router(bookmarks_router)
app.include_router(reports_router)
app.include_router(comments_router)
app.include_router(users_router)
app.include_router(economy_router)
app.include_router(gamification_router)
app.include_router(websocket_router)
app.include_router(search_router)
app.include_router(hashtags_router)
app.include_router(analytics_router)
app.include_router(follows_router)
