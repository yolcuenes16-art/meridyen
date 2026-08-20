from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import FollowModel, PostModel, UserModel
from backend.app.schemas.user import UserCreate, UserPreferences

_user_preferences: dict[str, UserPreferences] = {}


async def _follow_counts(username: str, db: AsyncSession) -> tuple[int, int]:
    followers = (await db.execute(
        select(func.count(FollowModel.id)).where(FollowModel.following_username == username)
    )).scalar() or 0
    following = (await db.execute(
        select(func.count(FollowModel.id)).where(FollowModel.follower_username == username)
    )).scalar() or 0
    return followers, following


async def _post_count(username: str, db: AsyncSession) -> int:
    return (await db.execute(
        select(func.count(PostModel.id)).where(PostModel.author_username == username)
    )).scalar() or 0


async def create_user(data: UserCreate, db: AsyncSession, password_hash: str = "") -> dict:
    result = await db.execute(select(UserModel).where(UserModel.username == data.username))
    if result.scalar_one_or_none():
        raise ValueError("Username already exists.")

    user = UserModel(
        username=data.username,
        display_name=data.display_name,
        bio=data.bio,
        category=data.category,
        password_hash=password_hash,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    _user_preferences[data.username] = UserPreferences(
        preferred_categories=[data.category],
        wellbeing_mode=True,
        safe_content=True,
        usage_mode="odak",
    )

    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "category": user.category,
        "followers_count": 0,
        "following_count": 0,
        "post_count": 0,
        "wellbeing_score": user.wellbeing_score,
        "created_at": user.created_at,
    }


async def get_users(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    out = []
    for u in users:
        fc, fg = await _follow_counts(u.username, db)
        pc = await _post_count(u.username, db)
        out.append({
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "bio": u.bio,
            "category": u.category,
            "followers_count": fc,
            "following_count": fg,
            "post_count": pc,
            "wellbeing_score": u.wellbeing_score,
            "created_at": u.created_at,
        })
    return out


async def get_user_by_username(username: str, db: AsyncSession) -> dict | None:
    result = await db.execute(select(UserModel).where(UserModel.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    fc, fg = await _follow_counts(user.username, db)
    pc = await _post_count(user.username, db)
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "category": user.category,
        "followers_count": fc,
        "following_count": fg,
        "post_count": pc,
        "wellbeing_score": user.wellbeing_score,
        "created_at": user.created_at,
    }


async def get_user_by_id(user_id: int, db: AsyncSession) -> dict | None:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    fc, fg = await _follow_counts(user.username, db)
    pc = await _post_count(user.username, db)
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "category": user.category,
        "followers_count": fc,
        "following_count": fg,
        "post_count": pc,
        "wellbeing_score": user.wellbeing_score,
        "created_at": user.created_at,
    }


async def get_preferences(username: str) -> UserPreferences | None:
    return _user_preferences.get(username)


async def update_preferences(
    username: str,
    preferences: UserPreferences,
) -> UserPreferences | None:
    if username not in _user_preferences:
        return None
    _user_preferences[username] = preferences
    return preferences
