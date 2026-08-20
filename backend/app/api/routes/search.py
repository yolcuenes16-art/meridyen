import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.db.models import PostModel, UserModel
from backend.app.schemas.post import PostResponse
from backend.app.services.post_service import _post_model_to_response, post_service

router = APIRouter(
    prefix="/api/v1/search",
    tags=["Search"],
)


@router.get("")
async def search(
    q: str = Query(min_length=1, max_length=200),
    category: str | None = Query(default=None),
    sort: str = Query(default="relevance"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit
    pattern = f"%{q}%"

    post_query = select(PostModel).where(
        PostModel.content.ilike(pattern),
        PostModel.is_publishable == True,
    )
    if category:
        post_query = post_query.where(PostModel.category == category)

    count_query = select(func.count(PostModel.id)).where(
        PostModel.content.ilike(pattern),
        PostModel.is_publishable == True,
    )
    if category:
        count_query = count_query.where(PostModel.category == category)

    total_result = await db.execute(count_query)
    total_posts = total_result.scalar()

    if sort == "date":
        post_query = post_query.order_by(PostModel.created_at.desc())
    elif sort == "popularity":
        post_query = post_query.order_by((PostModel.like_count + PostModel.comment_count).desc())
    else:
        post_query = post_query.order_by(PostModel.overall_score.desc(), PostModel.created_at.desc())

    post_query = post_query.offset(offset).limit(limit)
    post_result = await db.execute(post_query)
    posts = [_post_model_to_response(p) for p in post_result.scalars().all()]

    user_result = await db.execute(
        select(UserModel).where(
            or_(
                UserModel.username.ilike(pattern),
                UserModel.display_name.ilike(pattern),
            )
        ).limit(20)
    )
    users_raw = user_result.scalars().all()

    user_list = []
    for u in users_raw:
        followers_count_result = await db.execute(
            select(func.count()).select_from(
                select(PostModel).where(PostModel.author_username == u.username).subquery()
            )
        )
        user_list.append({
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "bio": u.bio,
            "category": u.category,
            "wellbeing_score": u.wellbeing_score,
            "created_at": u.created_at.isoformat(),
        })

    return {
        "posts": [p.model_dump() for p in posts],
        "users": user_list,
        "total_posts": total_posts,
        "total_users": len(user_list),
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total_posts / limit) if total_posts else 0,
    }
