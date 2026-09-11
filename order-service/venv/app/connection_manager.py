from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections = {}

    async def connect(self, order_id: int, websocket: WebSocket):
        await websocket.accept()

        if order_id not in self.active_connections:
            self.active_connections[order_id] = []

        self.active_connections[order_id].append(websocket)

    def disconnect(self, order_id: int, websocket: WebSocket):
        if order_id in self.active_connections:
            self.active_connections[order_id].remove(websocket)

            if not self.active_connections[order_id]:
                del self.active_connections[order_id]

    async def broadcast(self, order_id: int, message: dict):
        connections = self.active_connections.get(order_id, [])

        for websocket in connections:
            await websocket.send_json(message)


manager = ConnectionManager()