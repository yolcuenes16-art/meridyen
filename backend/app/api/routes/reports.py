from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Reports"],
)


class ReportCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    reason: str = Field(min_length=3, max_length=500)


@router.post(
    "/{post_id}/reports",
    status_code=status.HTTP_201_CREATED,
)
async def report_post(post_id: int, payload: ReportCreate, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        return await post_service.report_post(post_id, payload.username, payload.reason, db)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        ) from exc
