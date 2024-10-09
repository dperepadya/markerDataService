import os
import json
import asyncio
import logging
import traceback
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage, DeliveryMode
from sqlalchemy.ext.asyncio import AsyncSession
from crud import add_ticker
from database import SessionFactory
from websocket_manager import websocket_manager

logging.basicConfig(level=logging.INFO)

class RabbitMQClient:
    def __init__(self, host=os.getenv('RABBITMQ_HOST', 'localhost'), port=int(os.getenv('RABBITMQ_PORT', 5672))):
        self.host = host
        self.port = port
        self.url = f'amqp://guest:guest@{host}:{port}/'
        # self.url = 'amqp://guest:guest@localhost:5672/'
        self.publisher_connection = None
        self.consumer_connection = None
        self.channels = {}
        self.workers = {}
        self.last_message = None

    async def connect_publisher(self):
        if self.publisher_connection is None or self.publisher_connection.is_closed:
            self.publisher_connection = await connect_robust(self.url)
        return self.publisher_connection

    async def connect_consumer(self):
        if self.consumer_connection is None or self.consumer_connection.is_closed:
            self.consumer_connection = await connect_robust(self.url)
        return self.consumer_connection

    async def publish(self, message, queue_name: str):
        try:
            connection = await self.connect_publisher()
            channel = await connection.channel()
            await channel.declare_queue(queue_name)
            msg = Message(body=json.dumps(message).encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT)
            await channel.default_exchange.publish(msg, routing_key=queue_name)
            print('publish', message)
        except RuntimeError as e:
            logging.error('Runtime error: %s', e)
            logging.error('publisher connection is closed', self.publisher_connection.is_closed)
        except Exception as e:
            logging.error('Publish error: %s', e)
            traceback.print_exc()
            return
        # finally:
        #     await self.publisher_connection.close()

    async def run_consume_worker(self, channel: str, sender: str):
        queue_name = f'{sender}_{channel}'
        if queue_name in self.workers:
            return
        logging.info(f'Starting worker {queue_name}')

        async with SessionFactory() as session:
            task = asyncio.create_task(self.consume_worker(channel, sender, session))
            self.workers[queue_name] = task

    async def stop_all_workers(self):
        for task in self.workers.values():
            task.cancel()
        self.workers.clear()
        await self.consumer_connection.close()
        await self.publisher_connection.close()

    async def consume_worker(self, channel: str, sender: str, session: AsyncSession):
        connection = await self.connect_consumer()
        queue_name = sender + '_' + channel
        logging.info(f'Running worker {queue_name}')
        channel_obj = await connection.channel()
        await channel_obj.set_qos(prefetch_count=1)

        queue = await channel_obj.declare_queue(queue_name, durable=False, auto_delete=False)
        await queue.purge()
        logging.info(f'Starting {channel} Channel consumer')

        async def process_message(message: AbstractIncomingMessage):
            await self.process_trade_message(message, session)

        try:
            if channel == 'trades':
                # await queue.consume(lambda message: self.process_trade_message(message, session))
                await queue.consume(process_message)
            elif channel == 'order_book':
                # await queue.consume(lambda message: self.process_dom_message(message, session))
                await queue.consume(process_message)
            else:
                logging.info("There is no channels to be handled")
                return
            logging.info(f'Waiting for messages {queue_name}')
            await asyncio.Future()
        except Exception as e:
            logging.error(f'Error: {e}')
        finally:
            await connection.close()
            logging.info(f'Consumer Connection closed')

    async def process_trade_message(self, message: AbstractIncomingMessage, session: AsyncSession):
        async with message.process():
            data_dict = json.loads(message.body.decode('utf-8'))
            data_dict = json.loads(data_dict)
            logging.info(f'try to save{data_dict}')
            await add_ticker(session, data_dict)
            await websocket_manager.broadcast(data_dict)

    async def process_dom_message(self, message: AbstractIncomingMessage, session):
        # await add_dom(session, trade_data)
        pass

# async def get_channel(self, queue_name: str):
#     if queue_name not in self.channels:
#         self.channels[queue_name] = await self.connection.channel()
#         # await self.channels[queue_name].declare_queue(queue_name)
#     return self.channels[queue_name]

# async def consume(self, queue_name: str, callback):
#     try:
#         # channel = await self.get_channel(queue_name)
#         if self.connection is None or self.connection.is_closed:
#             await self.connect()
#         channel = await self.connection.channel()
#         await channel.set_qos(prefetch_count=10)
#         queue = await channel.declare_queue(queue_name, durable=True)  # , auto_delete=False)
#         await queue.consume(lambda message: callback(message, channel))
#         await asyncio.Future()
#     except Exception as e:
#         logging.error('Consume error: %s', e)