from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.comment import (
    CommentCreate,
    CommentResponse,
)
from backend.app.services.comment_service import comment_service
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
) -> CommentResponse:

    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return comment_service.create_comment(
        post_id=post_id,
        comment=comment,
    )


@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse],
)
async def get_comments(
    post_id: int,
) -> list[CommentResponse]:

    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return comment_service.get_comments(post_id)