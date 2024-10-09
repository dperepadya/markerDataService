
import os
import cache
import asyncio
import database
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from api_data_manager import data_manager
from binance_client.binance_client import BinanceClient
from binance_client.binance_message_processor import BinanceMessageProcessor
from rabbitmq_client import RabbitMQClient
from controllers import exchange_controllers, subscription_controllers, ws_controllers

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

app = FastAPI()

is_async_mode = os.environ.get('IS_ASYNC_MODE', 'True')
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
rmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rmq_port = os.getenv('RABBITMQ_PORT', 5672)

rmq_client = RabbitMQClient(host=rmq_host, port=rmq_port)

binance_client = BinanceClient(api_key=api_key, api_secret=api_secret)
binance_client.message_processor = BinanceMessageProcessor(queue_manager=rmq_client)

app.include_router(subscription_controllers.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(exchange_controllers.router, prefix="/exchanges", tags=["exchanges"])
app.include_router(ws_controllers.router, prefix="/ws", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logging.info("Init DB")
    if is_async_mode:
        await database.init_db_async()
    else:
        database.init_db()
    logging.info("Init RabbitMQ")
    await rmq_client.run_consume_worker('trades', 'binance')

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
    # await asyncio.sleep(5)
    # await data_manager.unsubscribe("binance", "BTCUSDT", "trades")

@app.get('/')
def landing():
    return RedirectResponse('/subscriptions/')

@app.on_event("shutdown")
async def shutdown_event():
    await rmq_client.stop_all_workers()
    await asyncio.sleep(1)
    async with database.SessionFactory() as session:
        await data_manager.stop(session)
    await binance_client.stop()
    logging.info("API Data Manager has been shut down")

async def main() -> None:
    pass

if __name__ == "__main__":
    asyncio.run(main())
