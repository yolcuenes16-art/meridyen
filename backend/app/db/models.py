import json
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    display_name = Column(String(50), nullable=False)
    bio = Column(String(160), nullable=False, default="")
    category = Column(String(50), nullable=False, default="Genel")
    password_hash = Column(String(200), nullable=False)
    wellbeing_score = Column(Float, nullable=False, default=100.0)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_username = Column(String(30), nullable=False, index=True)
    display_name = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    quality_score = Column(Float, nullable=False, default=0)
    educational_score = Column(Float, nullable=False, default=0)
    safety_score = Column(Float, nullable=False, default=0)
    spam_score = Column(Float, nullable=False, default=0)
    wellbeing_score = Column(Float, nullable=False, default=0)
    overall_score = Column(Float, nullable=False, default=0)
    focus_fit = Column(Float, nullable=False, default=0)
    learn_fit = Column(Float, nullable=False, default=0)
    fun_fit = Column(Float, nullable=False, default=0)
    visibility_multiplier = Column(Float, nullable=False, default=0.55)
    estimated_weekly_share = Column(Float, nullable=False, default=0)
    rank_score = Column(Float, nullable=False, default=0)
    engine = Column(String(50), nullable=False, default="heuristic-v1")
    latency_ms = Column(Float, nullable=False, default=0)
    is_publishable = Column(Boolean, nullable=False, default=True)
    moderation_note = Column(String(500), nullable=True)
    analysis_reasons = Column(Text, nullable=False, default="[]")
    flags = Column(Text, nullable=False, default="[]")
    rank_reasons = Column(Text, nullable=False, default="[]")
    rank_breakdown = Column(Text, nullable=False, default="[]")
    active_mode = Column(String(20), nullable=False, default="odak")
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)

    likes = relationship("LikeModel", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("CommentModel", back_populates="post", cascade="all, delete-orphan")
    bookmarks = relationship("BookmarkModel", back_populates="post", cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="post", cascade="all, delete-orphan")


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    username = Column(String(30), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    post = relationship("PostModel", back_populates="comments")


class LikeModel(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("post_id", "username", name="uq_like_post_user"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    username = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    post = relationship("PostModel", back_populates="likes")


class BookmarkModel(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("post_id", "username", name="uq_bookmark_post_user"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    username = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    post = relationship("PostModel", back_populates="bookmarks")


class ReportModel(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    username = Column(String(30), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    post = relationship("PostModel", back_populates="reports")


class GamificationEventModel(Base):
    __tablename__ = "gamification_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class HashtagModel(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(100), unique=True, index=True, nullable=False)
    post_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class PostHashtagModel(Base):
    __tablename__ = "post_hashtags"

    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True, nullable=False)
    hashtag_id = Column(Integer, ForeignKey("hashtags.id"), primary_key=True, nullable=False)


class FollowModel(Base):
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_username", "following_username", name="uq_follow"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_username = Column(String(30), nullable=False, index=True)
    following_username = Column(String(30), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
