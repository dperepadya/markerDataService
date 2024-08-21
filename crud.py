from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import SessionLocal
from models import Ticker, OrderBook, Exchange, Symbol, Subscription
import schemas
from utils.parsers import SymbolParser


# async def get_tickers(session: AsyncSession):
#     result = await session.execute(select(models.Ticker))
#     return result.scalars().all()
#

async def get_exchanges(db: AsyncSession):
    res = await db.execute(select(Exchange))
    return res.scalars().all()

async def get_exchange_by_id(db: AsyncSession, exchange_id: int):
    return await db.get(Exchange, exchange_id)

async def create_exchange(db: AsyncSession, exchange_data):
    exchange = Exchange(
        name=exchange_data['name']
    )
    db.add(exchange)
    await db.commit()
    await db.refresh(exchange)
    return exchange

async def create_symbol(session, symbol_data):
    symbol = Symbol(
    )

async def create_ticker(db: AsyncSession, ticker_data):
    instrument = ticker_data['symbol']
    instrument_info = SymbolParser.parse(instrument)
    symbol = instrument_info['symbol']
    strike = instrument_info.get('strike', None)
    expiry = instrument_info.get('expiry', None)
    option_type = instrument_info.get('option_type', None)
    ticker = Ticker(
        timestamp=datetime.utcfromtimestamp(ticker_data['timestamp'] / 1000),
        instrument=instrument,
        option_type=option_type,  # e.g., "CALL", "PUT"
        option_strike = strike,
        expiry = expiry,  # expiration date
        volume=ticker_data['volume'],
        last_price=ticker_data['price'],
        side=Column(Boolean, nullable=False)  # m - market maker flag
        direction = ticker_data['side']
    )
    session.add(ticker)
    await session.commit()
    # await session.refresh(ticker)


# async def get_aggregated_data(db: AsyncSession):
#     # Example aggregation logic
#     return db.query(
#         models.Ticker.instrument,
#         func.avg(models.Ticker.volume).label('avg_volume'),
#         func.avg(models.Ticker.last_price).label('avg_price')
#     ).group_by(models.Ticker.instrument).all()
