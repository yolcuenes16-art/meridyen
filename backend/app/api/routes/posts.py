from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.db.models import PostModel
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
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)) -> PostResponse:
    created = await post_service.create_post(post, db)

    from backend.app.services.hashtag_service import hashtag_service
    await hashtag_service.process_post_hashtags(created.id, post.content, db)

    feed = await post_service.get_feed(db, mode="odak", viewer=post.author_username)
    return next(item for item in feed if item.id == created.id)


@router.get(
    "/feed",
    response_model=list[PostResponse],
)
async def get_feed(
    mode: str = Query(default="odak"),
    viewer: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    all_posts = await post_service.get_feed(db, mode=mode, viewer=viewer)
    start = (page - 1) * limit
    return all_posts[start : start + limit]


@router.get(
    "/trending",
    response_model=list[PostResponse],
)
async def get_trending(
    mode: str = Query(default="odak"),
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    feed = await post_service.get_feed(db, mode=mode)
    return feed[:5]


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)) -> PostResponse:
    post = await post_service.get_post(post_id, db)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return post


class PostUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    category: str = Field(min_length=2, max_length=50)
    username: str = Field(min_length=3, max_length=30)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gonderi bulunamadi.")

    if post.author_username.lower() != payload.username.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu gonderiyi duzenleme yetkiniz yok.")

    post.content = payload.content
    post.category = payload.category
    await db.commit()

    from backend.app.services.hashtag_service import hashtag_service
    await hashtag_service.update_post_hashtags(post_id, payload.content, db)

    response = await post_service.get_post(post_id, db)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gonderi bulunamadi.")
    return response


class PostDelete(BaseModel):
    username: str = Field(min_length=3, max_length=30)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: int,
    payload: PostDelete,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gonderi bulunamadi.")

    if post.author_username.lower() != payload.username.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu gonderiyi silme yetkiniz yok.")

    from backend.app.services.hashtag_service import hashtag_service
    await hashtag_service.remove_post_hashtags(post_id, db)

    await db.delete(post)
    await db.commit()
