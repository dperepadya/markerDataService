import asyncio

import os
# from binance import AsyncClient, BinanceSocketManager
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rabbitmq_client import rabbitmq_client
from stream_msg_processor import MessageProcessor, BinanceMessageProcessor

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

class BinanceClient:
    def __init__(self):
        self.name = 'binance'
        self.client = None
        self.bm = None
        self.is_streaming = False
        self.stream_task = None
        self.message_processor = None

    def assign_message_processor(self, processor: MessageProcessor):
        self.message_processor = processor

    async def start(self):
        # self.client = UMFuturesWebsocketClient()
        self.client = await AsyncClient.create(api_key, api_secret)
        self.bm = BinanceSocketManager(self.client)
        await self.start_stream()

    async def stop(self):
        if self.bm:
            await self.bm.close()
        if self.client:
            await self.client.close_connection()

    # async def process_message(self, msg):
    #     if msg['e'] == 'trade':
    #         data = {
    #             'timestamp': msg['T'],
    #             'symbol': msg['s'],
    #             'price': msg['p'],
    #             'volume': msg['q'],
    #             'side': msg['m'],
    #             'direction': msg['M']
    #         }
    #         await rabbitmq_client.publish(data)

    async def start_stream(self):
        if not self.is_streaming:
            self.is_streaming = True
            trade_socket = self.bm.trade_socket(symbol)
            depth_socket = self.bm.depth_socket(symbol)

            self.stream_task = self.bm.trade_socket('BTCUSDT')
            async with self.stream_task as stream:
                while self.is_streaming:
                    msg = await stream.recv()
                    print(msg)
                    await self.message_processor.process_message(msg, self.name)

    async def stop_stream(self):
        if self.is_streaming:
            self.is_streaming = False
            await self.stream_task.__aexit__(None, None, None)


binance_client = BinanceClient()
binance_client.message_processor = BinanceMessageProcessor(rabbitmq_client)

