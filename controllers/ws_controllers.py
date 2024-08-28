import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from starlette.templating import Jinja2Templates
from websocket_manager import websocket_manager

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.websocket("/trades/")
async def websocket_endpoint(websocket: WebSocket, symbol: str = Query(...)):
    await websocket_manager.connect(websocket, symbol)
    try:
        while True:
            data = await websocket.receive_text()
            trade = json.loads(data)
            if symbol is None or trade["symbol"] == symbol:
                print('massage for', symbol)
                await websocket.send_text(trade)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

