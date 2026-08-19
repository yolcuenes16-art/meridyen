from datetime import datetime, timezone

from backend.app.schemas.content import ContentCreate, ContentResponse
from backend.app.services.analysis_service import content_analysis_service

class ContentService:
    def __init__(self) -> None:
        self._contents: list[ContentResponse] = []
        self._next_id = 1

    def create_content(self, content: ContentCreate) -> ContentResponse:
        new_content = ContentResponse(
            id=self._next_id,
            title=content.title,
            description=content.description,
            category=content.category,
            source=content.source,
            created_at=datetime.now(timezone.utc),
        )

        self._contents.append(new_content)
        self._next_id += 1

        return new_content

    def get_contents(self) -> list[ContentResponse]:
        return self._contents


content_service = ContentService()