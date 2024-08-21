import asyncio

from binance_client import ExchangeClient
from rabbitmq_client import RabbitMQClient
from message_processor import MessageProcessor


class SubscriptionManager:
    def __init__(self):
        self.subscriptions = {}

    async def add_exchange(self, exchange: str, provider: ExchangeClient):
        if exchange not in self.subscriptions:
            self.subscriptions[exchange] = provider
            await provider.init_client()

    async def remove_exchange(self, exchange: str):
        if exchange not in self.subscriptions:
            raise ValueError(f"Exchange {exchange} is not registered")
        provider = self.subscriptions[exchange]
        if provider is None:
            raise ValueError(f"Exchange {exchange} API provider is not assigned")
        provider.unsubscribe()

    async def subscribe(self, exchange, symbol, channel):
        if exchange not in self.subscriptions:
            raise ValueError(f"Exchange {exchange} is not registered")
        provider = self.subscriptions[exchange]
        if provider is None:
            raise ValueError(f"Exchange {exchange} API provider is not assigned")
        await provider.subscribe(symbol, channel)

    async def unsubscribe(self, exchange, symbol=None, channel=None):
        if exchange not in self.subscriptions:
            raise ValueError(f"Exchange {exchange} is not registered")
        provider = self.subscriptions[exchange]
        if provider is None:
            raise ValueError(f"Exchange {exchange} API provider is not assigned")
        await provider.unsubscribe(symbol, channel)

    def start(self):
        for exchange in self.subscriptions.values():
            exchange.init()

    async def stop(self):
        for exchange in self.subscriptions.keys():
            provider = self.subscriptions[exchange]
            if provider is None:
                raise ValueError(f"Exchange {exchange} API provider is not assigned")
            await provider.unsubscribe()

