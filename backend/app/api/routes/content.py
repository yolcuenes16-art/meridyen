from fastapi import APIRouter, status

from backend.app.schemas.content import ContentCreate, ContentResponse
from backend.app.services.content_service import content_service


router = APIRouter(
    prefix="/api/v1/content",
    tags=["Content"],
)


@router.post(
    "",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_content(content: ContentCreate) -> ContentResponse:
    return content_service.create_content(content)


@router.get(
    "",
    response_model=list[ContentResponse],
)
async def list_contents() -> list[ContentResponse]:
    return content_service.get_contents()