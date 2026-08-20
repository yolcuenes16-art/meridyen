from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import PostModel
from backend.app.schemas.post import PostCreate, PostResponse
from backend.app.services.analysis_service import content_analysis_service
from backend.app.services.gamification_service import gamification_service
from backend.app.services.ranking_service import normalize_mode, rank_content


WEEKLY_POOL_TRY = 5000.0


def _post_model_to_response(post: PostModel) -> PostResponse:
    import json
    return PostResponse(
        id=post.id,
        author_username=post.author_username,
        display_name=post.display_name,
        content=post.content,
        category=post.category,
        image_url=post.image_url,
        created_at=post.created_at,
        quality_score=post.quality_score,
        educational_score=post.educational_score,
        safety_score=post.safety_score,
        spam_score=post.spam_score,
        wellbeing_score=post.wellbeing_score,
        overall_score=post.overall_score,
        focus_fit=post.focus_fit,
        learn_fit=post.learn_fit,
        fun_fit=post.fun_fit,
        visibility_multiplier=post.visibility_multiplier,
        estimated_weekly_share=post.estimated_weekly_share,
        analysis_reasons=json.loads(post.analysis_reasons) if isinstance(post.analysis_reasons, str) else post.analysis_reasons,
        flags=json.loads(post.flags) if isinstance(post.flags, str) else post.flags,
        engine=post.engine,
        latency_ms=post.latency_ms,
        is_publishable=post.is_publishable,
        moderation_note=post.moderation_note,
        rank_score=post.rank_score,
        rank_reasons=json.loads(post.rank_reasons) if isinstance(post.rank_reasons, str) else post.rank_reasons,
        rank_breakdown=json.loads(post.rank_breakdown) if isinstance(post.rank_breakdown, str) else post.rank_breakdown,
        active_mode=post.active_mode,
        like_count=post.like_count,
        comment_count=post.comment_count,
        liked_by_me=False,
    )


class PostService:
    def __init__(self) -> None:
        pass

    async def create_post(self, post: PostCreate, db: AsyncSession) -> PostResponse:
        analysis = content_analysis_service.analyze(
            title=post.content[:120],
            description=post.content,
            category=post.category,
        )

        is_publishable = (
            analysis.safety_score >= 60
            and analysis.spam_score < 60
            and "toksik" not in analysis.flags
        )

        if not is_publishable:
            multiplier = round(min(analysis.visibility_multiplier, 0.35), 3)
            note = "Bu icerik guvenlik filtresi nedeniyle onerilen akista yer almıyor."
        else:
            multiplier = analysis.visibility_multiplier
            note = None

        display_name = post.display_name or post.author_username.replace("_", " ").title()

        import json
        new_post = PostModel(
            author_username=post.author_username,
            display_name=display_name,
            content=post.content,
            category=post.category,
            image_url=post.image_url,
            quality_score=analysis.quality_score,
            educational_score=analysis.educational_score,
            safety_score=analysis.safety_score,
            spam_score=analysis.spam_score,
            wellbeing_score=analysis.wellbeing_score,
            overall_score=analysis.overall_score,
            focus_fit=analysis.focus_fit,
            learn_fit=analysis.learn_fit,
            fun_fit=analysis.fun_fit,
            visibility_multiplier=multiplier,
            analysis_reasons=json.dumps(analysis.reasons),
            flags=json.dumps(analysis.flags),
            engine=analysis.engine,
            latency_ms=analysis.latency_ms,
            is_publishable=is_publishable,
            moderation_note=note,
        )

        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        gamification_service.record_post(
            username=post.author_username,
            is_safe=is_publishable,
            wellbeing_score=analysis.wellbeing_score,
        )

        return _post_model_to_response(new_post)

    async def _with_rank(
        self,
        post: PostModel,
        mode: str,
        viewer: str | None,
        share_map: dict[str, float],
        liked_by_me: bool = False,
    ) -> PostResponse:
        resp = _post_model_to_response(post)
        ranking = rank_content(resp, mode)
        return resp.model_copy(
            update={
                **ranking,
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "liked_by_me": liked_by_me,
                "estimated_weekly_share": share_map.get(
                    post.author_username.lower(), 0.0
                ),
            }
        )

    async def creator_share_map(self, db: AsyncSession) -> dict[str, float]:
        result = await db.execute(select(PostModel))
        posts = result.scalars().all()
        weights: dict[str, float] = {}
        for post in posts:
            key = post.author_username.lower()
            weights[key] = weights.get(key, 0.0) + max(
                post.visibility_multiplier * (post.wellbeing_score / 100),
                0.01,
            )
        total = sum(weights.values()) or 1.0
        return {
            author: round(WEEKLY_POOL_TRY * weight / total, 2)
            for author, weight in weights.items()
        }

    async def get_feed(
        self,
        db: AsyncSession,
        mode: str = "odak",
        viewer: str | None = None,
    ) -> list[PostResponse]:
        mode_key = normalize_mode(mode)
        shares = await self.creator_share_map(db)

        result = await db.execute(select(PostModel))
        all_posts = result.scalars().all()

        liked_ids: set[int] = set()
        if viewer:
            from backend.app.db.models import LikeModel
            like_result = await db.execute(
                select(LikeModel.post_id).where(
                    func.lower(LikeModel.username) == viewer.lower()
                )
            )
            liked_ids = {row[0] for row in like_result.all()}

        ranked = []
        for post in all_posts:
            resp = await self._with_rank(post, mode_key, viewer, shares, post.id in liked_ids)
            ranked.append(resp)

        ranked.sort(
            key=lambda item: (
                item.is_publishable,
                item.rank_score,
                item.created_at,
            ),
            reverse=True,
        )
        return self._apply_diversity(ranked)

    def _apply_diversity(
        self,
        posts: list[PostResponse],
    ) -> list[PostResponse]:
        if len(posts) < 3:
            return posts

        adjusted = posts[:]
        for index in range(2, len(adjusted)):
            if not adjusted[index].is_publishable:
                continue
            previous = {
                adjusted[index - 1].category,
                adjusted[index - 2].category,
            }
            if (
                adjusted[index].category in previous
                and len(previous) == 1
            ):
                reasons = list(adjusted[index].rank_reasons)
                reasons.insert(
                    1,
                    "Cesitlilik: ayni kategorinin ust uste yigilmasi dengelendi.",
                )
                adjusted[index] = adjusted[index].model_copy(
                    update={
                        "rank_score": round(adjusted[index].rank_score * 0.96, 2),
                        "rank_reasons": reasons[:5],
                    }
                )
        adjusted.sort(
            key=lambda item: (
                item.is_publishable,
                item.rank_score,
                item.created_at,
            ),
            reverse=True,
        )
        return adjusted

    async def get_post(self, post_id: int, db: AsyncSession) -> PostResponse | None:
        result = await db.execute(select(PostModel).where(PostModel.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            return None
        shares = await self.creator_share_map(db)
        return await self._with_rank(post, "odak", None, shares)

    async def toggle_like(self, post_id: int, username: str, db: AsyncSession) -> tuple[int, bool]:
        from backend.app.db.models import LikeModel

        result = await db.execute(select(PostModel).where(PostModel.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            raise KeyError("Post not found.")

        like_result = await db.execute(
            select(LikeModel).where(
                LikeModel.post_id == post_id,
                func.lower(LikeModel.username) == username.lower(),
            )
        )
        existing_like = like_result.scalar_one_or_none()

        if existing_like:
            await db.delete(existing_like)
            post.like_count = max(post.like_count - 1, 0)
            await db.commit()
            return post.like_count, False

        new_like = LikeModel(post_id=post_id, username=username)
        db.add(new_like)
        post.like_count += 1
        await db.commit()

        gamification_service.record_like_received(post.author_username)
        return post.like_count, True

    async def set_comment_count(self, post_id: int, count: int, db: AsyncSession) -> None:
        result = await db.execute(select(PostModel).where(PostModel.id == post_id))
        post = result.scalar_one_or_none()
        if post:
            post.comment_count = count
            await db.commit()

    async def creator_board(self, db: AsyncSession, mode: str = "odak") -> list[dict]:
        mode_key = normalize_mode(mode)
        shares = await self.creator_share_map(db)
        result = await db.execute(select(PostModel))
        all_posts = result.scalars().all()

        grouped: dict[str, dict] = {}
        for post in all_posts:
            key = post.author_username.lower()
            entry = grouped.setdefault(
                key,
                {
                    "author_username": post.author_username,
                    "display_name": post.display_name,
                    "post_count": 0,
                    "avg_wellbeing": 0.0,
                    "avg_multiplier": 0.0,
                    "estimated_weekly_share": shares.get(key, 0.0),
                    "top_rank_score": 0.0,
                },
            )
            resp = _post_model_to_response(post)
            ranked = rank_content(resp, mode_key)
            entry["post_count"] += 1
            entry["avg_wellbeing"] += post.wellbeing_score
            entry["avg_multiplier"] += post.visibility_multiplier
            entry["top_rank_score"] = max(
                entry["top_rank_score"],
                ranked["rank_score"],
            )

        board = []
        for entry in grouped.values():
            count = max(entry["post_count"], 1)
            board.append(
                {
                    **entry,
                    "avg_wellbeing": round(entry["avg_wellbeing"] / count, 2),
                    "avg_multiplier": round(entry["avg_multiplier"] / count, 3),
                    "top_rank_score": round(entry["top_rank_score"], 2),
                    "weekly_pool_try": WEEKLY_POOL_TRY,
                    "active_mode": mode_key,
                }
            )

        board.sort(key=lambda item: item["estimated_weekly_share"], reverse=True)
        return board

    async def toggle_bookmark(self, post_id: int, username: str, db: AsyncSession) -> bool:
        from backend.app.db.models import BookmarkModel

        result = await db.execute(select(PostModel).where(PostModel.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            raise KeyError("Post not found.")

        bm_result = await db.execute(
            select(BookmarkModel).where(
                BookmarkModel.post_id == post_id,
                func.lower(BookmarkModel.username) == username.lower(),
            )
        )
        existing = bm_result.scalar_one_or_none()

        if existing:
            await db.delete(existing)
            await db.commit()
            return False

        db.add(BookmarkModel(post_id=post_id, username=username))
        await db.commit()
        return True

    async def get_user_bookmarks(self, username: str, db: AsyncSession) -> list[int]:
        from backend.app.db.models import BookmarkModel
        result = await db.execute(
            select(BookmarkModel.post_id).where(
                func.lower(BookmarkModel.username) == username.lower()
            )
        )
        return [row[0] for row in result.all()]

    async def report_post(self, post_id: int, username: str, reason: str, db: AsyncSession) -> dict:
        from backend.app.db.models import ReportModel

        result = await db.execute(select(PostModel).where(PostModel.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            raise KeyError("Post not found.")

        report = ReportModel(post_id=post_id, username=username, reason=reason)
        db.add(report)
        await db.commit()
        await db.refresh(report)

        return {
            "post_id": post_id,
            "username": username,
            "reason": reason,
            "created_at": report.created_at.isoformat(),
        }

    async def wellbeing_snapshot(self, db: AsyncSession, mode: str = "odak") -> dict:
        feed = await self.get_feed(db, mode)
        if not feed:
            return {
                "score": 0,
                "safe_ratio": 0,
                "avg_wellbeing": 0,
                "suppressed_count": 0,
            }

        suppressed = [item for item in feed if not item.is_publishable]
        avg = sum(item.wellbeing_score for item in feed) / len(feed)
        safe = sum(1 for item in feed if item.safety_score >= 80) / len(feed)
        return {
            "score": round(avg, 1),
            "safe_ratio": round(safe * 100, 1),
            "avg_wellbeing": round(avg, 1),
            "suppressed_count": len(suppressed),
            "post_count": len(feed),
            "active_mode": normalize_mode(mode),
        }


post_service = PostService()
