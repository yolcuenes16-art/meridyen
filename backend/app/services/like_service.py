from datetime import datetime, timezone

from backend.app.schemas.like import LikeCreate, LikeResponse


class LikeService:
    def __init__(self) -> None:
        self._likes: list[LikeResponse] = []

    def create_like(
        self,
        post_id: int,
        like: LikeCreate,
    ) -> LikeResponse:

        already_liked = any(
            existing.post_id == post_id
            and existing.username.lower() == like.username.lower()
            for existing in self._likes
        )

        if already_liked:
            raise ValueError(
                "User has already liked this post."
            )

        new_like = LikeResponse(
            post_id=post_id,
            username=like.username,
            created_at=datetime.now(timezone.utc),
        )

        self._likes.append(new_like)

        return new_like

    def get_like_count(self, post_id: int) -> int:
        return sum(
            1
            for like in self._likes
            if like.post_id == post_id
        )

    def get_likes(self, post_id: int) -> list[LikeResponse]:
        return [
            like
            for like in self._likes
            if like.post_id == post_id
        ]


like_service = LikeService()