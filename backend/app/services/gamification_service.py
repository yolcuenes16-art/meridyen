"""Gamification service: streaks, badges, and levels."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta


BADGES = [
    {"id": "ilk_adim", "name": "Ilk Adim", "desc": "Ilk iceriginizi paylastiniz", "icon": "✦", "threshold": 1},
    {"id": "dusunceli", "name": "Dusunceli", "desc": "5 icerik paylastiniz", "icon": "◈", "threshold": 5},
    {"id": "uretici", "name": "Uretici", "desc": "10 icerik paylastiniz", "icon": "◉", "threshold": 10},
    {"id": "tutkulu", "name": "Tutkulu", "desc": "25 icerik paylastiniz", "icon": "◆", "threshold": 25},
    {"id": "yildiz", "name": "Yildiz Uretici", "desc": "50 icerik paylastiniz", "icon": "★", "threshold": 50},
    {"id": "temiz_ortam", "name": "Temiz Ortam", "desc": "Tum icerikleriniz guvenli", "icon": "◎", "threshold": -1},
    {"id": "sakin_ruh", "name": "Sakin Ruh", "desc": "Ortalama denge 80 uzerinde", "icon": "◉", "threshold": -1},
    {"id": "odak_makinesi", "name": "Odak Makinesi", "desc": "Odak modunda 10 icerik", "icon": "◎", "threshold": 10},
    {"id": "ogretmen", "name": "Ogretmen", "desc": "Ogrenme modunda 10 icerik", "icon": "◈", "threshold": 10},
    {"id": "eglence_sefi", "name": "Eglence Sefi", "desc": "Eglence modunda 10 icerik", "icon": "✦", "threshold": 10},
    {"id": "3_gun_streak", "name": "3 Gun Streak", "desc": "3 gun ustuste paylastiniz", "icon": "▲", "threshold": 3},
    {"id": "7_gun_streak", "name": "7 Gun Streak", "desc": "7 gun ustuste paylastiniz", "icon": "△", "threshold": 7},
    {"id": "etkileyici", "name": "Etkileyici", "desc": "100 begeni topladiniz", "icon": "♦", "threshold": 100},
    {"id": "konuşmaci", "name": "Konuşmaci", "desc": "20 yorum yaptiniz", "icon": "◇", "threshold": 20},
]


class GamificationService:
    def __init__(self) -> None:
        self._user_data: dict[str, dict] = {}

    def _ensure(self, username: str) -> dict:
        if username not in self._user_data:
            self._user_data[username] = {
                "post_count": 0,
                "total_likes": 0,
                "comment_count": 0,
                "safe_post_count": 0,
                "daily_posts": {},
                "mode_posts": {"odak": 0, "ogrenme": 0, "eglence": 0},
                "avg_wellbeing": 0.0,
                "_wellbeing_sum": 0.0,
            }
        return self._user_data[username]

    def record_post(self, username: str, is_safe: bool, wellbeing_score: float, mode: str = "odak") -> None:
        data = self._ensure(username)
        data["post_count"] += 1
        if is_safe:
            data["safe_post_count"] += 1
        data["_wellbeing_sum"] += wellbeing_score
        data["avg_wellbeing"] = data["_wellbeing_sum"] / data["post_count"]

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data["daily_posts"][today] = data["daily_posts"].get(today, 0) + 1

        mode_key = mode if mode in data["mode_posts"] else "odak"
        data["mode_posts"][mode_key] += 1

    def record_like_received(self, username: str) -> None:
        data = self._ensure(username)
        data["total_likes"] += 1

    def record_comment(self, username: str) -> None:
        data = self._ensure(username)
        data["comment_count"] += 1

    def _calculate_streak(self, data: dict) -> int:
        daily = data.get("daily_posts", {})
        if not daily:
            return 0

        streak = 0
        today = datetime.now(timezone.utc).date()
        check_date = today

        while True:
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in daily:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return streak

    def _calculate_level(self, post_count: int, total_likes: int, streak: int) -> tuple[int, int, int]:
        xp = post_count * 10 + total_likes * 5 + streak * 15
        level = 1
        xp_for_next = 50

        while xp >= xp_for_next:
            xp -= xp_for_next
            level += 1
            xp_for_next = int(xp_for_next * 1.5)

        return level, xp, xp_for_next

    def _check_badges(self, data: dict, streak: int) -> list[dict]:
        earned = []
        post_count = data["post_count"]
        safe_count = data["safe_post_count"]
        avg_wb = data["avg_wellbeing"]
        modes = data["mode_posts"]

        checks = {
            "ilk_adim": post_count >= 1,
            "dusunceli": post_count >= 5,
            "uretici": post_count >= 10,
            "tutkulu": post_count >= 25,
            "yildiz": post_count >= 50,
            "temiz_ortam": post_count >= 3 and safe_count == post_count,
            "sakin_ruh": post_count >= 3 and avg_wb >= 80,
            "odak_makinesi": modes.get("odak", 0) >= 10,
            "ogretmen": modes.get("ogrenme", 0) >= 10,
            "eglence_sefi": modes.get("eglence", 0) >= 10,
            "3_gun_streak": streak >= 3,
            "7_gun_streak": streak >= 7,
            "etkileyici": data["total_likes"] >= 100,
            "konuşmaci": data["comment_count"] >= 20,
        }

        for badge in BADGES:
            if checks.get(badge["id"]):
                earned.append(badge)

        return earned

    def get_user_stats(self, username: str) -> dict:
        data = self._ensure(username)
        streak = self._calculate_streak(data)
        level, xp, xp_next = self._calculate_level(data["post_count"], data["total_likes"], streak)
        badges = self._check_badges(data, streak)

        return {
            "username": username,
            "post_count": data["post_count"],
            "total_likes": data["total_likes"],
            "comment_count": data["comment_count"],
            "streak": streak,
            "level": level,
            "xp": xp,
            "xp_for_next": xp_next,
            "avg_wellbeing": round(data["avg_wellbeing"], 1),
            "badges": badges,
            "badge_count": len(badges),
            "mode_posts": data["mode_posts"],
        }


gamification_service = GamificationService()
