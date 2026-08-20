from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.services.hashtag_service import hashtag_service
from backend.app.services.post_service import post_service

router = APIRouter(
    prefix="/api/v1/hashtags",
    tags=["Hashtags"],
)


@router.get("/trending")
async def trending_hashtags(db: AsyncSession = Depends(get_db)):
    tags = await hashtag_service.get_trending(db)
    return {"hashtags": tags, "count": len(tags)}


@router.get("/search")
async def search_hashtags(
    q: str = Query(min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    tags = await hashtag_service.search_tags(q, db)
    return {"hashtags": tags, "count": len(tags)}


@router.get("/{tag}/posts")
async def posts_by_hashtag(
    tag: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit
    post_ids, total = await hashtag_service.get_posts_by_tag(tag, db, offset=offset, limit=limit)

    posts = []
    for pid in post_ids:
        post = await post_service.get_post(pid, db)
        if post is not None:
            posts.append(post)

    import math
    return {
        "tag": tag,
        "posts": [p.model_dump() for p in posts],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if total else 0,
    }
