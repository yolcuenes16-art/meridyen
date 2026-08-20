import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import HashtagModel, PostHashtagModel, PostModel

TAG_PATTERN = re.compile(r"#([\w\u00C0-\u024F]{1,99})")
MENTION_PATTERN = re.compile(r"@([\w\u00C0-\u024F]{1,30})")


def extract_hashtags(text: str) -> list[str]:
    return list({m.lower() for m in TAG_PATTERN.findall(text)})


def extract_mentions(text: str) -> list[str]:
    return list({m.lower() for m in MENTION_PATTERN.findall(text)})


class HashtagService:
    async def process_post_hashtags(self, post_id: int, content: str, db: AsyncSession) -> None:
        tags = extract_hashtags(content)
        for tag in tags:
            result = await db.execute(select(HashtagModel).where(HashtagModel.tag == tag))
            hashtag = result.scalar_one_or_none()
            if hashtag is None:
                hashtag = HashtagModel(tag=tag, post_count=1)
                db.add(hashtag)
                await db.flush()
            else:
                hashtag.post_count += 1

            existing = await db.execute(
                select(PostHashtagModel).where(
                    PostHashtagModel.post_id == post_id,
                    PostHashtagModel.hashtag_id == hashtag.id,
                )
            )
            if not existing.scalar_one_or_none():
                db.add(PostHashtagModel(post_id=post_id, hashtag_id=hashtag.id))
        await db.commit()

    async def remove_post_hashtags(self, post_id: int, db: AsyncSession) -> None:
        result = await db.execute(
            select(PostHashtagModel).where(PostHashtagModel.post_id == post_id)
        )
        associations = result.scalars().all()
        for assoc in associations:
            tag_result = await db.execute(
                select(HashtagModel).where(HashtagModel.id == assoc.hashtag_id)
            )
            hashtag = tag_result.scalar_one_or_none()
            if hashtag and hashtag.post_count > 0:
                hashtag.post_count -= 1
            await db.delete(assoc)
        await db.commit()

    async def update_post_hashtags(self, post_id: int, content: str, db: AsyncSession) -> None:
        await self.remove_post_hashtags(post_id, db)
        await self.process_post_hashtags(post_id, content, db)

    async def get_trending(self, db: AsyncSession, limit: int = 10) -> list[dict]:
        result = await db.execute(
            select(HashtagModel).order_by(HashtagModel.post_count.desc()).limit(limit)
        )
        hashtags = result.scalars().all()
        return [
            {"tag": h.tag, "post_count": h.post_count, "created_at": h.created_at.isoformat()}
            for h in hashtags
        ]

    async def get_posts_by_tag(self, tag: str, db: AsyncSession, offset: int = 0, limit: int = 20) -> tuple[list[int], int]:
        tag_result = await db.execute(select(HashtagModel).where(HashtagModel.tag == tag.lower()))
        hashtag = tag_result.scalar_one_or_none()
        if not hashtag:
            return [], 0

        count_result = await db.execute(
            select(func.count(PostHashtagModel.post_id)).where(PostHashtagModel.hashtag_id == hashtag.id)
        )
        total = count_result.scalar()

        result = await db.execute(
            select(PostHashtagModel.post_id)
            .where(PostHashtagModel.hashtag_id == hashtag.id)
            .order_by(PostHashtagModel.post_id.desc())
            .offset(offset)
            .limit(limit)
        )
        post_ids = [row[0] for row in result.all()]
        return post_ids, total

    async def search_tags(self, q: str, db: AsyncSession, limit: int = 20) -> list[dict]:
        result = await db.execute(
            select(HashtagModel)
            .where(HashtagModel.tag.contains(q.lower()))
            .order_by(HashtagModel.post_count.desc())
            .limit(limit)
        )
        hashtags = result.scalars().all()
        return [
            {"tag": h.tag, "post_count": h.post_count}
            for h in hashtags
        ]


hashtag_service = HashtagService()
