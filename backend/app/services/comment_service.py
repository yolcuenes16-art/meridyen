from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import CommentModel, PostModel
from backend.app.schemas.comment import CommentCreate, CommentResponse
from backend.app.services.post_service import post_service


class CommentService:
    def __init__(self) -> None:
        pass

    async def create_comment(
        self,
        post_id: int,
        comment: CommentCreate,
        db: AsyncSession,
    ) -> CommentResponse:
        new_comment = CommentModel(
            post_id=post_id,
            username=comment.username,
            content=comment.content,
        )
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)

        count_result = await db.execute(
            select(func.count(CommentModel.id)).where(CommentModel.post_id == post_id)
        )
        count = count_result.scalar()
        await post_service.set_comment_count(post_id, count, db)

        return CommentResponse(
            id=new_comment.id,
            post_id=new_comment.post_id,
            username=new_comment.username,
            content=new_comment.content,
            created_at=new_comment.created_at,
        )

    async def get_comments(
        self,
        post_id: int,
        db: AsyncSession,
    ) -> list[CommentResponse]:
        result = await db.execute(
            select(CommentModel).where(CommentModel.post_id == post_id)
        )
        comments = result.scalars().all()
        return [
            CommentResponse(
                id=c.id,
                post_id=c.post_id,
                username=c.username,
                content=c.content,
                created_at=c.created_at,
            )
            for c in comments
        ]


comment_service = CommentService()
