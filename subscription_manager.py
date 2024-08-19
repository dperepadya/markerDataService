import asyncio


class SubscriptionManager:
    def __init__(self):
        # {(exchange, symbol, channel), task}
        self.exchanges = {}
        # self.loop = asyncio.get_event_loop()

    def add_exchange(self, exchange: str, client):
        if exchange not in self.exchanges:
            self.exchanges[exchange] = client
            return True
        return False

    def start(self):
        for exchange in self.exchanges.values():
            exchange.init()

    def add_subscription(self, exchange, symbol, channel):
        key = (exchange, symbol, channel)
        if key in self.subscriptions:
            return False
        self.subscriptions[key] = None

    def subscribe(self, exchange, symbol, channel):
        key = (exchange, symbol, channel)
        if key not in self.subscriptions or self.subscriptions[key] is None:
            return False
        self.subscriptions[key] = self.loop.create_task(self.)
    def remove_subscription(self, symbol, channel=None):
        if symbol not in self.subscriptions.keys():
            return False
        if self.subscriptions[symbol] is not None:
            if channel is None:
                self.unsubscribe(symbol, channel)
            else:
                for symbol, channel in list(self.subscriptions):
                    self.unsubscribe(symbol, channel)
        del self.subscriptions[symbol]
        return True

    def unsubscribe(self, exchange, symbol, channel):
        if symbol not in self.subscriptions.keys():
            return False

    channel_map = {'trade': f"{symbol}"}
    async def run_subscription(self, exchange, symbol, channel):
        rabbitmq_url = "amqp://guest:guest@localhost:5672/"
        queue = f"{exchange}_{symbol}_{channel}"
        try:
            if stream_type == ''