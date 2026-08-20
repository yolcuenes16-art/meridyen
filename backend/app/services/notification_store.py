from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone


MAX_NOTIFICATIONS_PER_USER = 50


@dataclass
class Notification:
    type: str
    message: str
    from_user: str | None = None
    post_id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NotificationStore:
    def __init__(self) -> None:
        self._store: dict[str, deque[Notification]] = {}

    def _get_queue(self, username: str) -> deque[Notification]:
        if username not in self._store:
            self._store[username] = deque(maxlen=MAX_NOTIFICATIONS_PER_USER)
        return self._store[username]

    def add(self, username: str, notification: Notification) -> None:
        queue = self._get_queue(username)
        queue.appendleft(notification)

    def get_all(self, username: str) -> list[dict]:
        queue = self._get_queue(username)
        return [
            {
                "type": n.type,
                "message": n.message,
                "from_user": n.from_user,
                "post_id": n.post_id,
                "created_at": n.created_at,
            }
            for n in queue
        ]

    def clear(self, username: str) -> None:
        self._store.pop(username, None)


notification_store = NotificationStore()
