from fastapi import FastAPI

from backend.app.api.routes.analysis import router as analysis_router
from backend.app.api.routes.comments import router as comments_router
from backend.app.api.routes.content import router as content_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.likes import router as likes_router
from backend.app.api.routes.posts import router as posts_router
from backend.app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "Meridyen; dijital refahı, sosyal etkileşimi, "
        "içerik güvenliğini ve kişiselleştirilmiş "
        "içerik deneyimini bir araya getiren akıllı platform API'sidir."
    ),
    version=settings.app_version,
)

app.include_router(health_router)
app.include_router(content_router)
app.include_router(analysis_router)
app.include_router(posts_router)
app.include_router(likes_router)
app.include_router(comments_router)