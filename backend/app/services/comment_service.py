from datetime import datetime, timezone

from backend.app.schemas.comment import (
    CommentCreate,
    CommentResponse,
)


class CommentService:
    def __init__(self) -> None:
        self._comments: list[CommentResponse] = []
        self._next_id = 1

    def create_comment(
        self,
        post_id: int,
        comment: CommentCreate,
    ) -> CommentResponse:

        new_comment = CommentResponse(
            id=self._next_id,
            post_id=post_id,
            username=comment.username,
            content=comment.content,
            created_at=datetime.now(timezone.utc),
        )

        self._comments.append(new_comment)
        self._next_id += 1

        return new_comment

    def get_comments(
        self,
        post_id: int,
    ) -> list[CommentResponse]:

        return [
            comment
            for comment in self._comments
            if comment.post_id == post_id
        ]


comment_service = CommentService()