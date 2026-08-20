from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.db.models import FollowModel, UserModel
from backend.app.services.notification_service import notify_follow

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Follows"],
)


class FollowRequest(BaseModel):
    follower_username: str = Field(min_length=3, max_length=30)


@router.post("/{username}/follow")
async def follow_user(
    username: str,
    payload: FollowRequest,
    db: AsyncSession = Depends(get_db),
):
    follower_username = payload.follower_username

    if follower_username.lower() == username.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kendinizi takip edemezsiniz.")

    target = await db.execute(select(UserModel).where(UserModel.username == username))
    if not target.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanici bulunamadi.")

    existing = await db.execute(
        select(FollowModel).where(
            FollowModel.follower_username == follower_username.lower(),
            FollowModel.following_username == username.lower(),
        )
    )
    if existing.scalar_one_or_none():
        return {"following": True, "message": "Zaten takip ediyorsunuz."}

    follow = FollowModel(
        follower_username=follower_username.lower(),
        following_username=username.lower(),
    )
    db.add(follow)
    await db.commit()

    if follower_username.lower() != username.lower():
        await notify_follow(username, follower_username)

    return {"following": True, "message": "Takip edildi."}


@router.delete("/{username}/unfollow")
async def unfollow_user(
    username: str,
    payload: FollowRequest,
    db: AsyncSession = Depends(get_db),
):
    follower_username = payload.follower_username

    result = await db.execute(
        select(FollowModel).where(
            FollowModel.follower_username == follower_username.lower(),
            FollowModel.following_username == username.lower(),
        )
    )
    follow = result.scalar_one_or_none()
    if not follow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Takip iliskisi bulunamadi.")

    await db.delete(follow)
    await db.commit()
    return {"following": False, "message": "Takip birakildi."}


@router.get("/{username}/followers")
async def get_followers(
    username: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit

    count_result = await db.execute(
        select(func.count(FollowModel.id)).where(FollowModel.following_username == username.lower())
    )
    total = count_result.scalar()

    result = await db.execute(
        select(FollowModel)
        .where(FollowModel.following_username == username.lower())
        .order_by(FollowModel.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    follows = result.scalars().all()

    followers = []
    for f in follows:
        user_result = await db.execute(select(UserModel).where(UserModel.username == f.follower_username))
        user = user_result.scalar_one_or_none()
        if user:
            followers.append({
                "username": user.username,
                "display_name": user.display_name,
                "bio": user.bio,
                "category": user.category,
                "followed_at": f.created_at.isoformat(),
            })

    import math
    return {
        "username": username,
        "followers": followers,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if total else 0,
    }


@router.get("/{username}/following")
async def get_following(
    username: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit

    count_result = await db.execute(
        select(func.count(FollowModel.id)).where(FollowModel.follower_username == username.lower())
    )
    total = count_result.scalar()

    result = await db.execute(
        select(FollowModel)
        .where(FollowModel.follower_username == username.lower())
        .order_by(FollowModel.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    follows = result.scalars().all()

    following = []
    for f in follows:
        user_result = await db.execute(select(UserModel).where(UserModel.username == f.following_username))
        user = user_result.scalar_one_or_none()
        if user:
            following.append({
                "username": user.username,
                "display_name": user.display_name,
                "bio": user.bio,
                "category": user.category,
                "followed_at": f.created_at.isoformat(),
            })

    import math
    return {
        "username": username,
        "following": following,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if total else 0,
    }
