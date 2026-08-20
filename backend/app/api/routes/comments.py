from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.schemas.comment import (
    CommentCreate,
    CommentResponse,
)
from backend.app.services.comment_service import comment_service
from backend.app.services.notification_service import notify_comment
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Comments"],
)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:

    post = await post_service.get_post(post_id, db)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    result = await comment_service.create_comment(
        post_id=post_id,
        comment=comment,
        db=db,
    )

    if post.author_username.lower() != comment.username.lower():
        await notify_comment(post.author_username, comment.username, post_id)

    return result


@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse],
)
async def get_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[CommentResponse]:

    post = await post_service.get_post(post_id, db)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return await comment_service.get_comments(post_id, db)
