import asyncio
import os

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

import cache
from controllers import exchange_controllers, subscription_controllers, ws_controllers

import database
from binance_client import BinanceClient
from crud import add_ticker
from rabbitmq_client import RabbitMQClient
from message_processor import BinanceMessageProcessor
from api_data_manager import data_manager

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

ASYNC_MODE = False

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
rmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rmq_port = os.getenv('RABBITMQ_PORT', 5672)

# data_manager = APIDataManager()
rabbitmq_client = RabbitMQClient(host=rmq_host, port=rmq_port)


binance_client = BinanceClient(api_key=api_key, api_secret=api_secret)
binance_client.message_processor = BinanceMessageProcessor(queue_manager=rabbitmq_client)

is_async_mode = os.environ.get('IS_ASYNC_MODE', 'True')

app.include_router(exchange_controllers.router, prefix="/exchanges", tags=["exchanges"])
app.include_router(ws_controllers.router, prefix="/ws", tags=["websocket"])
app.include_router(subscription_controllers.router, prefix="/subscriptions", tags=["subscriptions"])

async def handle_message(message_data):
    async with database.SessionFactory() as session:
        await add_ticker(session, message_data)

@app.on_event("startup")
async def startup_event():
    logging.info("Init DB")
    if is_async_mode:
        await database.init_db_async()
        pass
    else:
        database.init_db()
    logging.info("Init RabbitMQ")
    #await rabbitmq_client.connect()
    await rabbitmq_client.run_db_worker('trades', 'binance')

    # Temporary hashtags storage
    async with database.SessionFactory() as session:
        await cache.load_caches(session)

    logging.info("Starting API Data Manager")
    await data_manager.add_exchange("binance", binance_client)
    logging.info("Connected to Binance")
    # symbols = await data_manager.get_symbols("binance")
    # print("Spot Market Symbols:", symbols)
    # await data_manager.subscribe("binance", "BTCUSDT", "trades")
    # await asyncio.sleep(3)
    # await data_manager.subscribe("binance", "ETHUSDT", "trades")
    # await data_manager.subscribe("binance", "BTCUSDT", "order_book")

    # await asyncio.sleep(5)
    # await data_manager.unsubscribe("binance", "BTCUSDT", "trades")
    # await data_manager.unsubscribe("binance", "BTCUSDT", "order_book")
    await asyncio.sleep(5)
    async with database.SessionFactory() as session:
        await data_manager.stop(session)

    # await asyncio.sleep(5)
    # await data_manager.subscribe("binance", "BTCUSDT", "trades")
    # await data_manager.subscribe("binance", "BTCUSDT", "order_book")

@app.get('/')
def landing():
    return RedirectResponse('/subscriptions/')


@app.on_event("shutdown")
async def shutdown_event():
    await rabbitmq_client.stop_all_workers()
    await asyncio.sleep(1)
    async with database.SessionFactory() as session:
        await data_manager.stop(session)
    binance_client.is_running = False
    logging.info("API Data Manager has been shut down")

# @app.websocket("/ws/")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_json()
#             action = data.get("action")
#             symbol = data.get("symbol")
#             if action == "subscribe":
#                 await manager.handle_subscription(websocket, symbol)
#             elif action == "unsubscribe":
#                 await manager.handle_unsubscription(websocket, symbol)
#     except:
#         manager.disconnect(websocket)
#
#
# @app.post("/start_stream/")
# async def start_stream():
#     if binance_client.is_streaming:
#         raise HTTPException(status_code=400, detail="Stream already started")
#     await binance_client.start_stream()
#     return {"message": "Stream started"}
#
#
# @app.post("/stop_stream/")
# async def stop_stream():
#     if not binance_client.is_streaming:
#         raise HTTPException(status_code=400, detail="Stream not started")
#     await binance_client.stop_stream()
#     return {"message": "Stream stopped"}
async def main() -> None:
    pass

if __name__ == "__main__":
    asyncio.run(main())
    # uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
