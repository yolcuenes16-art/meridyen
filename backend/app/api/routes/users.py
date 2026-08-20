from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.db.models import FollowModel, PostModel, UserModel
from backend.app.core.auth import get_current_user
from backend.app.schemas.user import (
    UserCreate,
    UserPreferences,
    UserResponse,
)
from backend.app.services.user_service import (
    create_user,
    get_preferences,
    get_user_by_id,
    get_user_by_username,
    get_users,
    update_preferences,
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


@router.get("/search/autocomplete")
async def search_users(
    q: str = Query(..., min_length=1, max_length=50),
    db: AsyncSession = Depends(get_db),
):
    pattern = f"%{q}%"
    result = await db.execute(
        select(UserModel).where(
            or_(
                UserModel.username.ilike(pattern),
                UserModel.display_name.ilike(pattern),
            )
        ).limit(10)
    )
    users = result.scalars().all()
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "display_name": u.display_name,
                "bio": u.bio,
                "category": u.category,
            }
            for u in users
        ],
        "count": len(users),
    }


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_user(data, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[UserResponse],
)
async def list_users(db: AsyncSession = Depends(get_db)):
    return await get_users(db)


@router.get(
    "/username/{username}",
    response_model=UserResponse,
)
async def get_user_by_name(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(username, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.get(
    "/{username}/preferences",
    response_model=UserPreferences,
)
async def get_user_preferences(username: str):
    preferences = await get_preferences(username)

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found.",
        )

    return preferences


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    category: str | None = None


@router.put(
    "/me",
)
async def update_profile_me(
    update: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(select(UserModel).where(UserModel.username == current_user))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanici bulunamadi.")

    if update.display_name is not None:
        user.display_name = update.display_name
    if update.bio is not None:
        user.bio = update.bio
    if update.category is not None:
        user.category = update.category

    await db.commit()
    await db.refresh(user)

    return {
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "category": user.category,
    }


@router.put(
    "/{username}/preferences",
    response_model=UserPreferences,
)
async def update_user_preferences(
    username: str,
    preferences: UserPreferences,
):
    updated = await update_preferences(username, preferences)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return updated


@router.get("/me/notifications")
async def get_my_notifications(current_user: str = Depends(get_current_user)):
    from backend.app.services.notification_store import notification_store
    return {"notifications": notification_store.get_all(current_user)}


@router.delete("/me/notifications")
async def clear_my_notifications(current_user: str = Depends(get_current_user)):
    from backend.app.services.notification_store import notification_store
    notification_store.clear(current_user)
    return {"message": "Bildirimler temizlendi."}
