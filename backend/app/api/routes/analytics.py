from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.db.models import FollowModel, PostModel, UserModel
from backend.app.services.hashtag_service import hashtag_service


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)


@router.get(
    "/dashboard",
)
async def dashboard(db: AsyncSession = Depends(get_db)) -> dict:
    total_users = (await db.execute(select(func.count(UserModel.id)))).scalar() or 0
    total_posts = (await db.execute(select(func.count(PostModel.id)))).scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    active_today = (await db.execute(
        select(func.count(func.distinct(PostModel.author_username))).where(
            PostModel.created_at >= today_start
        )
    )).scalar() or 0

    avg_wellbeing = (await db.execute(
        select(func.avg(PostModel.wellbeing_score))
    )).scalar() or 0.0

    safe_ratio = (await db.execute(
        select(func.count(PostModel.id)).where(PostModel.is_publishable == True)
    )).scalar() or 0
    safe_pct = round((safe_ratio / max(total_posts, 1)) * 100, 1)

    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "active_today": active_today,
        "avg_wellbeing": round(float(avg_wellbeing), 1),
        "safe_content_ratio": safe_pct,
    }


@router.get(
    "/trending",
)
async def trending(
    limit: int = Query(default=10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
) -> dict:
    trending_tags = await hashtag_service.get_trending(db, limit=limit)

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_result = await db.execute(
        select(PostModel)
        .where(PostModel.created_at >= week_ago, PostModel.is_publishable == True)
        .order_by(PostModel.like_count.desc(), PostModel.wellbeing_score.desc())
        .limit(min(limit, 10))
    )
    trending_posts = []
    for post in recent_result.scalars().all():
        trending_posts.append({
            "id": post.id,
            "author_username": post.author_username,
            "display_name": post.display_name,
            "content": post.content[:200],
            "category": post.category,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "wellbeing_score": post.wellbeing_score,
            "created_at": post.created_at.isoformat(),
        })

    return {
        "trending_tags": trending_tags,
        "trending_posts": trending_posts,
    }


@router.get(
    "/user/{username}",
)
async def user_analytics(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_result = await db.execute(select(UserModel).where(UserModel.username == username))
    user = user_result.scalar_one_or_none()
    if not user:
        return {"error": "Kullanici bulunamadi."}

    post_count = (await db.execute(
        select(func.count(PostModel.id)).where(PostModel.author_username == username)
    )).scalar() or 0

    total_likes = (await db.execute(
        select(func.coalesce(func.sum(PostModel.like_count), 0)).where(
            PostModel.author_username == username
        )
    )).scalar() or 0

    avg_wellbeing = (await db.execute(
        select(func.avg(PostModel.wellbeing_score)).where(
            PostModel.author_username == username
        )
    )).scalar() or 0.0

    followers = (await db.execute(
        select(func.count(FollowModel.id)).where(FollowModel.following_username == username)
    )).scalar() or 0

    following = (await db.execute(
        select(func.count(FollowModel.id)).where(FollowModel.follower_username == username)
    )).scalar() or 0

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_count = (await db.execute(
        select(func.count(PostModel.id)).where(
            PostModel.author_username == username,
            PostModel.created_at >= thirty_days_ago,
        )
    )).scalar() or 0

    return {
        "username": username,
        "display_name": user.display_name,
        "post_count": post_count,
        "total_likes_received": int(total_likes),
        "avg_wellbeing": round(float(avg_wellbeing), 1),
        "followers": followers,
        "following": following,
        "posts_last_30_days": recent_count,
        "member_since": user.created_at.isoformat(),
    }
