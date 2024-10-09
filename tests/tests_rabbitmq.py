import asyncio
import datetime
import json
import os
import unittest

import pytest
import uuid
from unittest.mock import AsyncMock, patch

from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

import main
import logging
from database import SessionFactory
from db_models import Ticker
from rabbitmq_client import RabbitMQClient
logger = logging.getLogger(__name__)

async def process_trade_message_mock(self, message: AbstractIncomingMessage, session: AsyncSession):
    self.last_message = {
        "timestamp": 1724939412887,
        "symbol": "ETHBTC",
        "price": 0.04241,
        "volume": 0.1,
        "side": False,
        "direction": True,
        "sender": "binance"
    }

async def run_consume_worker_mock(self, channel: str, sender: str):
    queue_name = f'{sender}_{channel}'
    self.last_message = {
        "timestamp": 1724939412887,
        "symbol": "ETHBTC",
        "price": 0.04241,
        "volume": 0.1,
        "side": False,
        "direction": True,
        "sender": "binance"
    }

async def consume_worker_mock(self, channel: str, sender: str, session: AsyncSession):
    queue_name = f'{sender}_{channel}'
    self.last_message = {
        "timestamp": 1724939412887,
        "symbol": "ETHBTC",
        "price": 0.04241,
        "volume": 0.1,
        "side": False,
        "direction": True,
        "sender": "binance"
    }

class TestRabbitMQ(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.app = main.app
        pass

    test_message = {
        "timestamp": 1724939412887,
        "symbol": "ETHBTC",
        "price": 0.04241,
        "volume": 0.1,
        "side": False,
        "direction": True,
        "sender": "binance"
    }

    sender = 'binance'
    channel = 'trades'

    queue_name = f'{sender}_{channel}'

    # 1. run_consume_worker -> asyncio.create_task(consume_worker(..)) -> 2. consume_worker ->
    # 3. process_trade_message
    # 1. passed:
    # @patch('rabbitmq_client.RabbitMQClient.run_consume_worker', new=run_consume_worker_mock)
    # 2. passed:
    # @patch('rabbitmq_client.RabbitMQClient.consume_worker', new=consume_worker_mock)
    # 3. final:
    @patch('rabbitmq_client.RabbitMQClient.process_trade_message', new=process_trade_message_mock)

    async def test_rabbitmq(self):
        rmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
        rmq_port = os.getenv('RABBITMQ_PORT', 5672)

        rabbitmq_client = RabbitMQClient(host=rmq_host, port=rmq_port)
        await rabbitmq_client.publish(json.dumps(self.test_message), self.queue_name)

        await asyncio.sleep(0.1)

        await rabbitmq_client.run_consume_worker(self.channel, self.sender)

        result = rabbitmq_client.last_message

        logger.debug(result)

        self.assertEqual(result, self.test_message)

        await rabbitmq_client.stop_all_workers()


if __name__ == '__main__':
    unittest.main()

def get_ticker_data_mock(*args, **kwargs):
    ticker = Ticker(
        id=uuid.uuid4().hex,
        timestamp= datetime.datetime.utcnow(),
        instrument="BTCUSDT",
        exchange_id=1,
        symbol_id=1,
        option_type=None,
        option_strike=None,
        expiry=None,
        volume=1,
        last_price=50000,
        side=False,
        direction=False
    )
    return ticker



