import json

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, symbol: str):
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        await websocket.accept()
        self.active_connections[symbol].append(websocket)

    def disconnect(self, websocket: WebSocket):
        for symbol, connections in self.active_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.active_connections[symbol]
                break

    async def broadcast(self, trade: dict):
        symbol = trade["symbol"]
        if symbol in self.active_connections:
            for websocket in self.active_connections[symbol]:
                await websocket.send_text(json.dumps(trade))


websocket_manager = WebSocketManager()
