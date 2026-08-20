from backend.app.api.routes.websocket import manager
from backend.app.services.notification_store import Notification, notification_store


async def notify_like(username: str, from_user: str, post_id: int):
    notification_store.add(username, Notification(
        type="like",
        message=f"{from_user} gonderini begendi.",
        from_user=from_user,
        post_id=post_id,
    ))
    await manager.send_to_user(username, {
        "type": "like",
        "message": f"{from_user} gonderini begendi.",
        "post_id": post_id,
    })


async def notify_comment(username: str, from_user: str, post_id: int):
    notification_store.add(username, Notification(
        type="comment",
        message=f"{from_user} gonderine yorum yapti.",
        from_user=from_user,
        post_id=post_id,
    ))
    await manager.send_to_user(username, {
        "type": "comment",
        "message": f"{from_user} gonderine yorum yapti.",
        "post_id": post_id,
    })


async def notify_follow(username: str, from_user: str):
    notification_store.add(username, Notification(
        type="follow",
        message=f"{from_user} seni takip etti.",
        from_user=from_user,
    ))
    await manager.send_to_user(username, {
        "type": "follow",
        "message": f"{from_user} seni takip etti.",
    })


async def notify_post_published(username: str, post_id: int):
    notification_store.add(username, Notification(
        type="post_published",
        message="Takip ettigin bir kullanici yeni icerik paylasti.",
        post_id=post_id,
    ))
    await manager.send_to_user(username, {
        "type": "post_published",
        "message": "Takip ettigin bir kullanici yeni icerik paylasti.",
        "post_id": post_id,
    })


async def notify_mention(username: str, from_user: str, post_id: int):
    notification_store.add(username, Notification(
        type="mention",
        message=f"{from_user} seni iceriginde bahsetti.",
        from_user=from_user,
        post_id=post_id,
    ))
    await manager.send_to_user(username, {
        "type": "mention",
        "message": f"{from_user} seni iceriginde bahsetti.",
        "post_id": post_id,
    })


async def notify_system(username: str, message: str):
    notification_store.add(username, Notification(
        type="system",
        message=message,
    ))
    await manager.send_to_user(username, {
        "type": "system",
        "message": message,
    })
