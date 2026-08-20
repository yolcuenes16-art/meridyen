from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.schemas.post import PostResponse
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1",
    tags=["Bookmarks"],
)


class BookmarkToggle(BaseModel):
    username: str = Field(min_length=3, max_length=30)


@router.post(
    "/posts/{post_id}/bookmarks",
)
async def toggle_bookmark(post_id: int, payload: BookmarkToggle, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        bookmarked = await post_service.toggle_bookmark(post_id, payload.username, db)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        ) from exc

    return {
        "post_id": post_id,
        "username": payload.username,
        "bookmarked": bookmarked,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/users/{username}/bookmarks",
    response_model=list[PostResponse],
)
async def get_user_bookmarks(username: str, db: AsyncSession = Depends(get_db)) -> list[PostResponse]:
    bookmark_ids = await post_service.get_user_bookmarks(username, db)
    posts = []
    for pid in bookmark_ids:
        post = await post_service.get_post(pid, db)
        if post is not None:
            posts.append(post)
    return posts
