import logging
import asyncio
from functools import wraps

from exchange_client import ExchangeClient
import MetaTrader5 as mt5

from utils.decorators import multi_try


def run_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

class Metatrader5Client(ExchangeClient):
    def __init__(self, login: str, password: str, host: str):
        super().__init__(login, password, host)
        self.name = 'metatrader5'
        self.host = host
        self.login = login
        self.password = password
        self.initialized = False
        self.bm = None
        self.is_running = False
        self.stream_tasks = {}
        self.message_processor = None
        self.depth = 5
        self.interval = 100

    async def init_client(self):
        if not await asyncio.to_thread(mt5.initialize, login=int(self.login), password=self.password, server=self.host):
            return
        self.initialized = True
        self.symbols = await self.get_symbols()

    @multi_try
    async def get_symbols(self):
        if not self.initialized:
            await self.init_client()
        symbols = await asyncio.to_thread(mt5.symbols_get)
        if symbols is None:
            return
        symbols_info = []
        for symbol in symbols:
            symbol_data = {
                'name': symbol['symbol'],
                'type': 's',
                'point_value': 1.0,
                'tick_size': float(symbol['filters'][0]['tickSize']),
                'min_size': float(symbol['filters'][1]['minQty']),
                'max_size': float(symbol['filters'][1]['maxQty']),
                'step_size': float(symbol['filters'][1]['stepSize'])
            }
            symbols_info.append(symbol_data)
        return symbols_info

    async def subscribe(self, symbol, channel):
        if symbol is None or channel is None:
            return False
        if self.client is None:
            await self.init_client()
        key = (symbol, channel)
        if key in self.stream_tasks:
            return True
        logging.info(f"Create new task for {symbol} {channel}")
        task = asyncio.create_task(self.start_listener(symbol, channel))
        self.stream_tasks[key] = task
        return True

    async def unsubscribe(self, symbol=None, channel=None):
        if self.client is None or not self.is_running:
            return True
        # keys_to_remove = []
        if channel is None:
            if symbol is None:
                # unsubscribe from all
                keys_to_remove = list(self.stream_tasks.keys())
            else:
                # unsubscribe from all symbol channels
                keys_to_remove = [(sym, chan) for (sym, chan) in self.stream_tasks.keys() if sym == symbol]
        else:
            if symbol is None:
                # unsubscribe from all such channels
                keys_to_remove = [(sym, chan) for (sym, chan) in self.stream_tasks.keys() if chan == channel]
            else:
                # unsubscribe from specific symbol and channel
                key = (symbol, channel)
                if key not in self.stream_tasks:
                    raise KeyError(f'Symbol {symbol} and channel {channel} not found in stream tasks')
                keys_to_remove = [key]

        for key in keys_to_remove:
            task = self.stream_tasks.get(key)
            if task:
                task.cancel()
            del self.stream_tasks[key]

    async def stop(self):
        if self.client is None:
            raise ValueError("Binance API Client is not connected")
        if not self.is_running:
            return
        self.is_running = False
        for key in self.stream_tasks.keys():
            task = self.stream_tasks.pop(key)
            task.cancel()
        await self.client.close_connection()

    async def start_listener(self, symbol: str, channel: str):
        if self.client is None:
            await self.init_client()
        if not self.is_running:
            self.is_running = True
        if channel == 'trades':
            socket = self.bm.trade_socket(symbol)
        elif channel == 'order_book':
            socket = self.bm.depth_socket(symbol)  # , self.depth, self.interval)
        # elif:
        # elif
        else:
            raise ValueError("Unsupported channel")

        # buffer = []
        while self.is_running:
            try:
                async with socket as stream:
                    while self.is_running:
                        if stream._queue.qsize() < 100:
                            msg = await asyncio.wait_for(stream.recv(), 60)
                        else:
                            await asyncio.sleep(1)
                        if not self.is_running:
                            break
                        print(msg)
                        await self.message_processor.process_message(msg, self.name)
                        await asyncio.sleep(1)
            except asyncio.CancelledError:
                # print(f'Task {self.name} {symbol} {channel} is cancelled')
                # traceback.print_exc()
                await asyncio.sleep(3)
            except Exception as e:
                print(f'Unexpected error: {e}')
                self.is_running = False
                return
            finally:
                print(f'Task {self.name} {symbol} {channel} stopped')
                return
        print(f'Listener loop {self.name} {symbol} {channel} stopped')

