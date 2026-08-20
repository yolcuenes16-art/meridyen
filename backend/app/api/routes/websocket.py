from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, username: str):
        await ws.accept()
        self.active.setdefault(username, []).append(ws)

    def disconnect(self, ws: WebSocket, username: str):
        if username in self.active:
            self.active[username] = [w for w in self.active[username] if w != ws]
            if not self.active[username]:
                del self.active[username]

    async def send_to_user(self, username: str, data: dict):
        for ws in self.active.get(username, []):
            try:
                await ws.send_json(data)
            except Exception:
                pass

    def is_online(self, username: str) -> bool:
        return bool(self.active.get(username))


manager = ConnectionManager()


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, username)
