import aio_pika
import json

class MessageProcessor:
    def __init__(self, rabbitmq_client):
        self.rabbitmq_client = rabbitmq_client

    async def process_message(self, msg):
        if msg['e'] == 'trade':
            data = {
                'timestamp': msg['T'],
                'symbol': msg['s'],
                'price': msg['p'],
                'volume': msg['q'],
                'side': msg['m'],
                'direction': msg['M']
            }
            await self.rabbitmq_client.publish(json.dumps(data))

class RabbitMQClient:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.connection_string)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue("trade_queue", durable=True)

    async def publish(self, message):
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key="trade_queue"
        )

# # Example usage
# rabbitmq_client = RabbitMQClient("amqp://guest:guest@localhost/")
# await rabbitmq_client.connect()
# processor = MessageProcessor(rabbitmq_client)
#
# # Assuming msg is the message you received from Binance
# await processor.process_message(msg)
