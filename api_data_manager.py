import logging
from sqlalchemy.ext.asyncio import AsyncSession
import cache
import crud
from binance_client import ExchangeClient

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

class APIDataManager:
    def __init__(self):
        # {exchange, provider}
        self.exchanges_providers = {}
        # {exchange, [symbols]}
        self.exchanges_symbols = {}

    def get_exchange_symbols(self, exchange_id):
        exchange_name = next((name for name, id_ in cache.exchanges_cache.items() if id_ == exchange_id), None)
        # print(cache.exchanges_cache)
        # print(exchange_id)
        # print(type(exchange_id))
        # print(exchange_name)
        if exchange_name is None or exchange_name not in self.exchanges_providers:
            raise ValueError(f"Exchange with Id {exchange_id} is not registered")
        print(exchange_name)
        symbols = self.exchanges_symbols[exchange_name]
        if symbols is None:
            raise ValueError(f"Cannot load symbols for {exchange_name} ")
        return symbols

    def get_exchange_symbol_by_id(self, exchange_id, symbol_name):
        symbols = self.get_exchange_symbols(exchange_id)
        if symbols is None:
            raise ValueError(f"Cannot load symbols for exchange with Id {exchange_id} ")
        # symbol_name = next((name for name, id_ in cache.symbols_cache.items() if id_ == symbol_id), None)
        symbol = next((s for s in symbols if s['name'] == symbol_name), None)
        symbol['exchange_id'] = exchange_id
        return symbol

    async def add_exchange(self, exchange: str, provider: ExchangeClient):
        if exchange not in self.exchanges_providers:
            self.exchanges_providers[exchange] = provider
            await provider.init_client()
            symbols_info = await provider.get_symbols()
            self.exchanges_symbols[exchange] = symbols_info

    async def remove_exchange(self, exchange: str):
        if exchange not in self.exchanges_providers:
            raise ValueError(f"Exchange {exchange} is not registered")
        provider = self.exchanges_providers[exchange]
        if provider is None:
            raise ValueError(f"Exchange {exchange} API provider is not assigned")
        provider.unsubscribe()

    async def subscribe(self, exchange, symbol, channel):
        if exchange not in self.exchanges_providers:
            raise ValueError(f"Exchange {exchange} is not registered")
        provider = self.exchanges_providers[exchange]
        if provider is None:
            raise ValueError(f"Exchange {exchange} API provider is not assigned")
        await provider.subscribe(symbol, channel)

    async def unsubscribe(self, exchange, symbol=None, channel=None, stop=False):
        if exchange not in self.exchanges_providers:
            raise ValueError(f"Exchange {exchange} is not registered")
        provider = self.exchanges_providers[exchange]
        if provider is None:
            raise ValueError(f"Exchange {exchange} API provider is not assigned")
        await provider.unsubscribe(symbol, channel)

    async def unsubscribe_all(self, session: AsyncSession):
        subscriptions = await crud.get_subscriptions(session)
        for subscription in subscriptions:
            if subscription.is_active:
                await self.unsubscribe(subscription.exchange.name, subscription.symbol.name, subscription.type)
                await crud.update_status(session, subscription, False)
                logging.info(f'Subscription for {subscription.exchange.name} {subscription.symbol.name} {subscription.type}'
                             f' has been stopped')

    def start(self):
        for exchange in self.exchanges_providers.values():
            exchange.init()

    async def stop(self, session: AsyncSession):
        # for exchange in self.exchanges_providers.keys():
        #     provider = self.exchanges_providers[exchange]
        #     if provider is None:
        #         raise ValueError(f"Exchange {exchange} API provider is not assigned")
        #     await provider.unsubscribe()
        await self.unsubscribe_all(session)


data_manager = APIDataManager()
