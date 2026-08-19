from datetime import datetime, timezone

from backend.app.schemas.post import PostCreate, PostResponse
from backend.app.services.analysis_service import content_analysis_service


class PostService:
    def __init__(self) -> None:
        self._posts: list[PostResponse] = []
        self._next_id = 1

    def create_post(self, post: PostCreate) -> PostResponse:
        analysis = content_analysis_service.analyze(
            title=post.content[:100],
            description=post.content,
            category=post.category,
        )

        is_publishable = (
            analysis.safety_score >= 70
            and analysis.spam_score < 70
        )

        new_post = PostResponse(
            id=self._next_id,
            author_username=post.author_username,
            content=post.content,
            category=post.category,
            created_at=datetime.now(timezone.utc),
            quality_score=analysis.quality_score,
            educational_score=analysis.educational_score,
            safety_score=analysis.safety_score,
            spam_score=analysis.spam_score,
            wellbeing_score=analysis.wellbeing_score,
            overall_score=analysis.overall_score,
            is_publishable=is_publishable,
        )

        if is_publishable:
            self._posts.append(new_post)

        self._next_id += 1

        return new_post

    def get_feed(self) -> list[PostResponse]:
        return sorted(
            self._posts,
            key=lambda post: (
                post.overall_score,
                post.created_at,
            ),
            reverse=True,
        )

    def get_post(self, post_id: int) -> PostResponse | None:
        return next(
            (
                post
                for post in self._posts
                if post.id == post_id
            ),
            None,
        )


post_service = PostService()