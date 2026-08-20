import json
import random
from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from backend.app.core.auth import hash_password
from backend.app.db.database import AsyncSessionLocal, Base, engine
from backend.app.db.models import FollowModel, PostModel, UserModel
from backend.app.data.seed_posts import SEED_POSTS
from backend.app.services.analysis_service import content_analysis_service


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


DEMO_USERS = [
    {"username": "meridyen_user", "display_name": "Enes Yolcu", "bio": "Refah oncelikli akista bilincli zaman geciriyorum.", "category": "Teknoloji", "password": "meridyen123"},
    {"username": "elif_kaya", "display_name": "Elif Kaya", "bio": "Egitim teknolojileri uzmani. Ogrenmeyi kolaylastiran araclar gelistiriyorum.", "category": "Egitim", "password": "demo1234"},
    {"username": "kerem_yilmaz", "display_name": "Kerem Yilmaz", "bio": "NLP ve Turkce isleme uzerine calisiyorum. Yapay zeka meraklisi.", "category": "Teknoloji", "password": "demo1234"},
    {"username": "ayse_demir", "display_name": "Ayse Demir", "bio": "Bilim insanı. Psikoloji ve dijital refah arastirmalariyla ilgileniyorum.", "category": "Bilim", "password": "demo1234"},
    {"username": "can_ozkan", "display_name": "Can Ozkan", "bio": "Fotografci ve muzisyen. Guzellikleri paylasmayi seviyorum.", "category": "Sanat", "password": "demo1234"},
    {"username": "selin_arslan", "display_name": "Selin Arslan", "bio": "Ogretmen. Ogrencilerin potansiyellerini ortaya cikarmak icin calisiyorum.", "category": "Egitim", "password": "demo1234"},
    {"username": "mert_kaya", "display_name": "Mert Kaya", "bio": "Kondisyon antrenoru. Saglikli yasam ve spor uzerine paylasimlar.", "category": "Spor", "password": "demo1234"},
    {"username": "nisa_polat", "display_name": "Nisa Polat", "bio": "Sosyal medya arastirmacisi. Dijital etik uzerine calisiyorum.", "category": "Teknoloji", "password": "demo1234"},
    {"username": "baris_tun", "display_name": "Baris Tunc", "bio": "Minimalist yasam taraftari. Kucuk sevinc buyuk mutluluk.", "category": "Genel", "password": "demo1234"},
    {"username": "berk_yildiz", "display_name": "Berk Yildiz", "bio": "ML engineer. Veri bilimi ve model egitimi uzerine paylasimlar.", "category": "Teknoloji", "password": "demo1234"},
    {"username": "zeynep_ak", "display_name": "Zeynep Aksoy", "bio": "Universite ogrencisi. TEKNOFEST catısı altinda projeler geliştiriyorum.", "category": "Egitim", "password": "demo1234"},
    {"username": "emre_dogan", "display_name": "Emre Dogan", "bio": "Girisimci ve AR-GE meraklısı. Teknolojiyi toplum faydasina donusturuyorum.", "category": "Teknoloji", "password": "demo1234"},
]

DEMO_FOLLOWS = [
    ("meridyen_user", "elif_kaya"), ("meridyen_user", "kerem_yilmaz"), ("meridyen_user", "can_ozkan"),
    ("elif_kaya", "meridyen_user"), ("elif_kaya", "selin_arslan"),
    ("kerem_yilmaz", "berk_yildiz"), ("kerem_yilmaz", "meridyen_user"),
    ("ayse_demir", "elif_kaya"), ("ayse_demir", "meridyen_user"),
    ("can_ozkan", "baris_tun"), ("can_ozkan", "meridyen_user"),
    ("selin_arslan", "elif_kaya"), ("selin_arslan", "meridyen_user"),
    ("mert_kaya", "can_ozkan"),
    ("nisa_polat", "kerem_yilmaz"), ("nisa_polat", "meridyen_user"),
    ("baris_tun", "can_ozkan"),
    ("berk_yildiz", "kerem_yilmaz"), ("berk_yildiz", "nisa_polat"),
    ("zeynep_ak", "meridyen_user"), ("zeynep_ak", "elif_kaya"),
    ("emre_dogan", "kerem_yilmaz"), ("emre_dogan", "meridyen_user"),
]


async def seed_demo_users(db_session):
    result = await db_session.execute(select(UserModel))
    if result.scalars().first():
        return

    for u in DEMO_USERS:
        user = UserModel(
            username=u["username"],
            display_name=u["display_name"],
            bio=u["bio"],
            category=u["category"],
            password_hash=hash_password(u["password"]),
            wellbeing_score=random.uniform(75.0, 100.0),
        )
        db_session.add(user)
    await db_session.commit()


async def seed_follows(db_session):
    result = await db_session.execute(select(FollowModel).limit(1))
    if result.scalar_one_or_none():
        return
    for follower, following in DEMO_FOLLOWS:
        db_session.add(FollowModel(
            follower_username=follower.lower(),
            following_username=following.lower(),
        ))
    await db_session.commit()


async def seed_posts():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PostModel))
        if result.scalars().first():
            return

        now = datetime.now(timezone.utc)
        for i, item in enumerate(SEED_POSTS):
            analysis = content_analysis_service.analyze(
                title=item["content"][:120],
                description=item["content"],
                category=item["category"],
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

            display_name = item.get("display_name") or item["author_username"].replace("_", " ").title()

            time_offset = timedelta(hours=random.randint(0, 168), minutes=random.randint(0, 59))
            like_count = item.get("like_count", random.randint(0, 45))
            comment_count = item.get("comment_count", random.randint(0, 12))

            post = PostModel(
                author_username=item["author_username"],
                display_name=display_name,
                content=item["content"],
                category=item["category"],
                image_url=item.get("image_url"),
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
                like_count=like_count,
                comment_count=comment_count,
                created_at=now - time_offset,
            )
            db.add(post)

        await db.commit()

        from backend.app.services.hashtag_service import hashtag_service
        result = await db.execute(select(PostModel))
        all_posts = result.scalars().all()
        for post in all_posts:
            await hashtag_service.process_post_hashtags(post.id, post.content, db)


async def init_db():
    await create_tables()
    async with AsyncSessionLocal() as db:
        await seed_demo_users(db)
        await seed_follows(db)
    await seed_posts()
