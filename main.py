import asyncio
import os

from fastapi import FastAPI
from starlette.templating import Jinja2Templates

import database
from binance_client import BinanceClient
from rabbitmq_client import RabbitMQClient
from message_processor import BinanceMessageProcessor
from subscription_manager import SubscriptionManager

ASYNC_MODE = False

app = FastAPI()


api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
rmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rmq_port = os.getenv('RABBITMQ_PORT', 5672)

subscription_manager = SubscriptionManager()
rabbitmq_client = RabbitMQClient(host=rmq_host, port=rmq_port)
# await rabbitmq_client.connect()
binance_client = BinanceClient(api_key=api_key, api_secret=api_secret)
binance_client.message_processor = BinanceMessageProcessor(queue_manager=rabbitmq_client)

is_async_mode = os.environ.get('IS_ASYNC_MODE', 'True')

app.include_router(exchange_router)

@app.on_event("startup")
async def startup_event():
    print("Init DB")
    if is_async_mode:
        await database.init_db_async()
    else:
        database.init_db()
    print("Starting Subscription Manager")
    await subscription_manager.add_exchange("binance", binance_client)
    print("Subscribed to Binance")
    # await subscription_manager.subscribe("binance", "BTCUSDT", "trades")
    await subscription_manager.subscribe("binance", "BTCUSDT", "order_book")

    await asyncio.sleep(5)
    #await subscription_manager.unsubscribe("binance", "BTCUSDT", "trades")
    #await subscription_manager.unsubscribe("binance", "BTCUSDT", "order_book")
    #await asyncio.sleep(5)
    await subscription_manager.stop()
    # await asyncio.sleep(5)
    # await subscription_manager.subscribe("binance", "BTCUSDT", "trades")
    # await subscription_manager.subscribe("binance", "BTCUSDT", "order_book")



# @app.get("/tickers")
# async def read_tickers(db: AsyncSession = Depends(database.get_db)):
#     tickers = await crud.get_tickers(db)
#     return tickers


@app.on_event("shutdown")
async def shutdown_event():
    await subscription_manager.stop()

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
async def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
