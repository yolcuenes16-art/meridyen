from datetime import datetime, timezone

from backend.app.data.seed_posts import SEED_POSTS
from backend.app.schemas.post import PostCreate, PostResponse
from backend.app.services.analysis_service import content_analysis_service
from backend.app.services.ranking_service import normalize_mode, rank_content

WEEKLY_POOL_TRY = 5000.0


class PostService:
    def __init__(self) -> None:
        self._posts: list[PostResponse] = []
        self._next_id = 1
        self._likes: dict[int, set[str]] = {}
        self._seed()

    def _seed(self) -> None:
        for item in SEED_POSTS:
            self.create_post(
                PostCreate(
                    author_username=item["author_username"],
                    content=item["content"],
                    category=item["category"],
                    display_name=item.get("display_name"),
                )
            )

    def create_post(self, post: PostCreate) -> PostResponse:
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
            note = "Bu içerik güvenlik filtresi nedeniyle önerilen akışta yer almıyor."
        else:
            multiplier = analysis.visibility_multiplier
            note = None

        display_name = post.display_name or post.author_username.replace("_", " ").title()

        new_post = PostResponse(
            id=self._next_id,
            author_username=post.author_username,
            display_name=display_name,
            content=post.content,
            category=post.category,
            created_at=datetime.now(timezone.utc),
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
            analysis_reasons=analysis.reasons,
            flags=analysis.flags,
            engine=analysis.engine,
            latency_ms=analysis.latency_ms,
            is_publishable=is_publishable,
            moderation_note=note,
        )

        self._posts.append(new_post)
        self._likes[new_post.id] = set()
        self._next_id += 1
        return new_post

    def _with_rank(
        self,
        post: PostResponse,
        mode: str,
        viewer: str | None,
        share_map: dict[str, float],
    ) -> PostResponse:
        ranking = rank_content(post, mode)
        liked = False
        if viewer:
            liked = viewer.lower() in {
                name.lower() for name in self._likes.get(post.id, set())
            }

        return post.model_copy(
            update={
                **ranking,
                "like_count": len(self._likes.get(post.id, set())),
                "comment_count": post.comment_count,
                "liked_by_me": liked,
                "estimated_weekly_share": share_map.get(
                    post.author_username.lower(), 0.0
                ),
            }
        )

    def creator_share_map(self) -> dict[str, float]:
        weights: dict[str, float] = {}
        for post in self._posts:
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

    def get_feed(
        self,
        mode: str = "odak",
        viewer: str | None = None,
    ) -> list[PostResponse]:
        mode_key = normalize_mode(mode)
        shares = self.creator_share_map()
        ranked = [
            self._with_rank(post, mode_key, viewer, shares)
            for post in self._posts
        ]
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
                    "Çeşitlilik: aynı kategorinin üst üste yığılması dengelendi.",
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

    def get_post(self, post_id: int) -> PostResponse | None:
        shares = self.creator_share_map()
        post = next((item for item in self._posts if item.id == post_id), None)
        if post is None:
            return None
        return self._with_rank(post, "odak", None, shares)

    def toggle_like(self, post_id: int, username: str) -> tuple[int, bool]:
        post = next((item for item in self._posts if item.id == post_id), None)
        if post is None:
            raise KeyError("Post not found.")

        bucket = self._likes.setdefault(post_id, set())
        key = username.lower()
        if key in {name.lower() for name in bucket}:
            bucket.discard(next(name for name in bucket if name.lower() == key))
            return len(bucket), False

        bucket.add(username)
        return len(bucket), True

    def set_comment_count(self, post_id: int, count: int) -> None:
        for index, post in enumerate(self._posts):
            if post.id == post_id:
                self._posts[index] = post.model_copy(update={"comment_count": count})
                return

    def creator_board(self, mode: str = "odak") -> list[dict]:
        mode_key = normalize_mode(mode)
        shares = self.creator_share_map()
        grouped: dict[str, dict] = {}

        for post in self._posts:
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
            ranked = rank_content(post, mode_key)
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

    def wellbeing_snapshot(self, mode: str = "odak") -> dict:
        feed = self.get_feed(mode)
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
