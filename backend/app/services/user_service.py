from datetime import datetime, timezone

from backend.app.schemas.user import UserCreate, UserPreferences


_users: list[dict] = []
_preferences: dict[str, UserPreferences] = {}
_next_user_id = 1


def create_user(data: UserCreate) -> dict:
    global _next_user_id

    if get_user_by_username(data.username):
        raise ValueError("Username already exists.")

    user = {
        "id": _next_user_id,
        "username": data.username,
        "display_name": data.display_name,
        "bio": data.bio,
        "category": data.category,
        "followers_count": 0,
        "following_count": 0,
        "post_count": 0,
        "wellbeing_score": 100.0,
        "created_at": datetime.now(timezone.utc),
    }

    _users.append(user)

    _preferences[data.username] = UserPreferences(
        preferred_categories=[data.category],
        wellbeing_mode=True,
        safe_content=True,
    )

    _next_user_id += 1

    return user


def get_users() -> list[dict]:
    return _users


def get_user_by_username(username: str) -> dict | None:
    return next(
        (user for user in _users if user["username"] == username),
        None,
    )


def get_user_by_id(user_id: int) -> dict | None:
    return next(
        (user for user in _users if user["id"] == user_id),
        None,
    )


def get_preferences(username: str) -> UserPreferences | None:
    return _preferences.get(username)


def update_preferences(
    username: str,
    preferences: UserPreferences,
) -> UserPreferences | None:
    if not get_user_by_username(username):
        return None

    _preferences[username] = preferences
    return preferences