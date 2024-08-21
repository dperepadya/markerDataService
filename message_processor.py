import aio_pika
import json

class MessageProcessor:
    def __init__(self, queue_manager):
        self.queue_manager = queue_manager
        # self.channels = {}

    # def set_channels(self, channels):
         # self.channels = channels

    async def process_message(self, message, sender):
        raise NotImplementedError("Subclasses must implement")

    async def publish_message(self, data, channel, sender):
        raise NotImplementedError("Subclasses must implement")


class BinanceMessageProcessor(MessageProcessor):
    def __init__(self, queue_manager):
        super().__init__(queue_manager)

    async def publish_message(self, data, channel, sender):
        queue = sender + '_' + channel
        await self.queue_manager.publish(json.dumps(data), queue)

    def parse_trade_message(self, msg):
        return {
            'timestamp': msg['T'],
            'symbol': msg['s'],
            'price': msg['p'],
            'volume': msg['q'],
            'side': msg['m'],
            'direction': msg['M']
        }

    def parse_order_book_message(self, msg, depth=5):
        bids = sorted(msg['bids'], key=lambda k: k[0], reverse=True)[:depth]
        asks = sorted(msg['asks'], key=lambda k: k[0])[:depth]
        return {
            "timestamp": msg['E'],
            "symbol": msg['s'],
            "bids": json.dumps(bids),
            "asks": json.dumps(asks)
        }

    async def process_message(self, msg, sender):
        if sender is None:
            return None
        data = None
        channel = None
        if msg['e'] == 'trade':
            channel = msg['e']
            data = self.parse_trade_message(msg)
        elif msg['e'] == 'depthUpdate':
            channel = msg['e']
            data = self.parse_order_book_message(msg)
        if data is not None:
            # await self.publish_message(data, channel, sender)
            print(data)


# # Example usage
# rabbitmq_client = RabbitMQClient("amqp://guest:guest@localhost/")
# await rabbitmq_client.connect()
# processor = MessageProcessor(rabbitmq_client)
#
# # Assuming msg is the message you received from Binance
# await processor.process_message(msg)
