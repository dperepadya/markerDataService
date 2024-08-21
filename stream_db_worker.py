import aio_pika
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from models import Ticker, Base

class DatabaseWorker:
    def __init__(self, rabbitmq_client, db_session: sessionmaker):
        self.rabbitmq_client = rabbitmq_client
        self.db_session = db_session

    async def start(self):
        await self.rabbitmq_client.connect()
        await self.consume()

    async def consume(self):
        async with self.rabbitmq_client.channel:
            queue = await self.rabbitmq_client.channel.declare_queue("trade_queue", durable=True)
            await queue.consume(self.process_message, no_ack=False)

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            data = json.loads(message.body)
            async with self.db_session() as session:
                async with session.begin():
                    ticker = Ticker(
                        timestamp=data['timestamp'],
                        instrument=data['symbol'],
                        symbol=data['symbol'],
                        volume=float(data['volume']),
                        last_price=float(data['price']),
                        side=data['side'],
                        direction=data['direction']
                    )
                    session.add(ticker)
                await session.commit()

# Example usage
# db_session = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)
# worker = DatabaseWorker(rabbitmq_client, db_session)
# await worker.start()
