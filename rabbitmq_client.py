import os

import aio_pika
import json

class RabbitMQClient:
    def __init__(self, host=os.getenv('RABBITMQ_HOST', 'localhost'), port=os.getenv('RABBITMQ_PORT', 5672)):
        self.host = host
        self.port = port
        self.connection = None
        self.channels = {}

    async def connect(self):
        self.connection = await aio_pika.connect_robust(host=self.host)

    async def get_channel(self, queue):
        if queue not in self.channels:
            if not self.connection:
                await self.connect()
            channel = await self.connection.channel()
            await channel.declare_queue(queue)
            self.channels[queue] = channel
        return self.channels[queue]

    async def publish(self, queue, message):
        if not self.connection:
            await self.connect()
        channel = await self.get_channel(queue)
        if not channel:
            return False
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode('utf-8')),
            routing_key=queue
        )

    async def consume(self, queue, callback):
        if not self.connection:
            await self.connect()
        channel = await self.get_channel(queue)
        if not channel:
            return False
        queue = await channel.declare_queue(queue)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    message_data = json.loads(message.body.decode('utf-8'))
                    await callback(message_data)
