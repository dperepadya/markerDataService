# from fastapi import WebSocket
# from typing import List, Dict, Set
# import asyncio
# from rabbitmq_client import rabbitmq_client
# import json
#
#
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[WebSocket, Set[str]] = {}
#
#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections[websocket] = set()
#
#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.pop(websocket, None)
#
#     async def send_message(self, websocket: WebSocket, message: str):
#         await websocket.send_text(message)
#
#     async def broadcast_from_queue(self):
#         def callback(message):
#             symbol = message['symbol']
#             for websocket, subscriptions in self.active_connections.items():
#                 if symbol in subscriptions:
#                     asyncio.run(self.send_message(websocket, json.dumps(message)))
#
#         rabbitmq_client.consume(callback)
#
#     async def handle_subscription(self, websocket: WebSocket, symbol: str):
#         if websocket in self.active_connections:
#             self.active_connections[websocket].add(symbol)
#
#     async def handle_unsubscription(self, websocket: WebSocket, symbol: str):
#         if websocket in self.active_connections:
#             self.active_connections[websocket].discard(symbol)
#
#
# # manager = ConnectionManager()
