from fastapi import APIRouter, HTTPException, Query, status

from backend.app.schemas.post import PostCreate, PostResponse
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Posts"],
)


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: PostCreate) -> PostResponse:
    created = post_service.create_post(post)
    feed = post_service.get_feed(mode="odak", viewer=post.author_username)
    return next(item for item in feed if item.id == created.id)


@router.get(
    "/feed",
    response_model=list[PostResponse],
)
async def get_feed(
    mode: str = Query(default="odak"),
    viewer: str | None = Query(default=None),
) -> list[PostResponse]:
    return post_service.get_feed(mode=mode, viewer=viewer)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post(post_id: int) -> PostResponse:
    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return post
