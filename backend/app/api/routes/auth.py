from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.app.db.database import get_db
from backend.app.db.models import UserModel
from backend.app.schemas.user import UserResponse

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=100)
    display_name: str = Field(min_length=2, max_length=50)
    bio: str = Field(default="", max_length=160)
    category: str = Field(default="Genel", max_length=50)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    user = UserModel(
        username=payload.username,
        display_name=payload.display_name,
        bio=payload.bio,
        category=payload.category,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            bio=user.bio,
            category=user.category,
            followers_count=0,
            following_count=0,
            post_count=0,
            wellbeing_score=user.wellbeing_score,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.username == payload.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            bio=user.bio,
            category=user.category,
            followers_count=0,
            following_count=0,
            post_count=0,
            wellbeing_score=user.wellbeing_score,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        display_name=current_user.display_name,
        bio=current_user.bio,
        category=current_user.category,
        followers_count=0,
        following_count=0,
        post_count=0,
        wellbeing_score=current_user.wellbeing_score,
        created_at=current_user.created_at,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: UserModel = Depends(get_current_user)):
    token = create_access_token(data={"sub": current_user.username})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=current_user.id,
            username=current_user.username,
            display_name=current_user.display_name,
            bio=current_user.bio,
            category=current_user.category,
            followers_count=0,
            following_count=0,
            post_count=0,
            wellbeing_score=current_user.wellbeing_score,
            created_at=current_user.created_at,
        ),
    )
