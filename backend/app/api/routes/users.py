from fastapi import APIRouter, HTTPException, status

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


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_user(data: UserCreate):
    try:
        return create_user(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[UserResponse],
)
async def list_users():
    return get_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(user_id: int):
    user = get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.get(
    "/username/{username}",
    response_model=UserResponse,
)
async def get_user_by_name(username: str):
    user = get_user_by_username(username)

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
    preferences = get_preferences(username)

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found.",
        )

    return preferences


@router.put(
    "/{username}/preferences",
    response_model=UserPreferences,
)
async def update_user_preferences(
    username: str,
    preferences: UserPreferences,
):
    updated = update_preferences(username, preferences)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return updated