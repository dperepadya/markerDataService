import uuid
import logging
from typing import cast
from datetime import datetime
from utils.parsers import SymbolParser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from cache import exchanges_cache, symbols_cache
from models import Ticker, OrderBook, Exchange, Symbol, Subscription

logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

async def get_exchanges(db: AsyncSession):
    res = await db.execute(select(Exchange))
    exchanges = res.scalars().all()
    return exchanges

async def get_exchange_by_id(db: AsyncSession, exchange_id: int):
    res = await db.execute(select(Exchange).filter(exchange_id == Exchange.id))
    exchange = res.scalars().first()
    return exchange

async def add_exchange(db: AsyncSession, exchange_data):
    if exchange_data is None:
        return False
    exchange = Exchange(
        name=exchange_data['name']
    )
    db.add(exchange)
    await db.commit()
    await db.refresh(exchange)
    exchanges_cache[exchange.name] = exchange.id
    return True

async def delete_exchange(db: AsyncSession, exchange_id: int):
    exchange = await get_exchange_by_id(db, exchange_id)
    if exchange is not None:
        await db.delete(exchange)
        await db.commit()
        # await db.refresh(exchange)
        exchanges_cache.pop(exchange.id, None)
        return True
    return False

async def add_exchange_symbol(db: AsyncSession, symbol_data):
    symbol = Symbol(
        # id=symbol_data['id'],
        name=symbol_data['name'],
        exchange_id=symbol_data['exchange_id'],
        type=symbol_data['type'],
        description=symbol_data['name'],
        tick_size=symbol_data['tick_size'],
        point_value=symbol_data['point_value'],
        min_size=symbol_data['min_size'],
        max_size=symbol_data['max_size'],
        step_size=symbol_data['step_size']
    )
    db.add(symbol)
    await db.commit()
    await db.refresh(symbol)
    symbols_cache[symbol.exchange_id][symbol.name] = symbol.id
    print('updated symbols cache', symbols_cache)
    return True

async def get_exchange_symbols(db: AsyncSession, exchange_id: int):
    res = await db.execute(select(Symbol)
                           .options(selectinload(Symbol.exchange))  # .where(Symbol.exchange_id == exchange_id)
                           .where(cast("ColumnElement[bool]", Symbol.exchange_id == exchange_id))
                           )
    symbols = res.scalars().all()
    return symbols

async def get_exchange_symbol_by_id(db: AsyncSession, exchange_id: int, symbol_id: int):
    res = await db.execute(select(Symbol)
                           .options(selectinload(Symbol.exchange))
                           .where(exchange_id == Symbol.exchange_id, symbol_id == Symbol.id))
    symbol = res.scalars().first()
    return symbol

async def delete_exchange_symbol(db: AsyncSession, exchange_id: int, symbol_id: int):
    symbol = await get_exchange_symbol_by_id(db, exchange_id, symbol_id)
    if symbol is not None:
        await db.delete(symbol)
        await db.commit()
        # await db.refresh(symbol)
        symbols_cache[exchange_id].pop(symbol.id, None)
        print('updated symbols cache', symbols_cache)
        return True

async def get_exchange_cache_id(cache, name: str):
    return cache.get(name, None)

async def get_symbol_cache_id(cache, exchange_id: int, name: str):
    cache_ = cache.get(exchange_id, None)
    if cache_ is None or name is None:
        return None
    return cache_.get(name, None)

async def get_subscriptions(db: AsyncSession):
    res = await db.execute(select(Subscription)
                           .options(selectinload(Subscription.exchange), selectinload(Subscription.symbol)))
    subscriptions = res.scalars().all()
    return subscriptions


async def get_subscription_by_id(db: AsyncSession, subscription_id: int):
    res = await db.execute(select(Subscription)
                           .options(selectinload(Subscription.exchange), selectinload(Subscription.symbol))
                           .where(subscription_id == Subscription.id))
    subscription = res.scalars().first()
    return subscription

async def add_subscription(db: AsyncSession, subscription_data):
    if subscription_data is None:
        return False
    subscription = Subscription(
        name=subscription_data['name'],
        type=subscription_data['type'],
        exchange_id=subscription_data['exchange_id'],
        symbol_id=subscription_data['symbol_id'],
        is_active=subscription_data['is_active']
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return True

async def update_status(db: AsyncSession, subscription: int, status: bool):
    # subscription = await get_subscription_by_id(db, subscription_id)
    subscription.is_active = status
    await db.commit()
    await db.refresh(subscription)
    return True

# async def reset_status(db: AsyncSession, subscription: int, status: bool):
#     subscriptions = await get_subscriptions(db)
#     for subscription in subscriptions:
#         subscription.is_active = False
#     await db.commit()
#     await db.refresh(subscription)
#     return True

async def delete_subscription(db: AsyncSession, subscription_id: int):
    subscription = await get_subscription_by_id(db, subscription_id)
    if subscription is None:
        return False
    await db.delete(subscription)
    await db.commit()
    await db.refresh(subscription)
    return True

async def get_tickers(db: AsyncSession):
    result = await db.execute(select(Ticker))
    res = result.scalars().all()
    return res

async def get_ticker_by_id(db: AsyncSession, ticker_id: int):
    res = await db.execute(select(Ticker).filter(ticker_id == Ticker.id))
    ticker = res.scalars().first()
    return ticker


async def add_ticker(db: AsyncSession, ticker_data):
    instrument = ticker_data['symbol']
    instrument_info = SymbolParser.parse(instrument)
    symbol_name = instrument_info['symbol']
    exchange_id = await get_exchange_cache_id(exchanges_cache, ticker_data['sender'])
    symbol_id = await get_symbol_cache_id(symbols_cache, exchange_id, symbol_name)
    strike = instrument_info.get('strike', None)
    expiry = instrument_info.get('expiry', None)
    option_type = instrument_info.get('option_type', None)
    ticker = Ticker(
        id=uuid.uuid4().hex,
        timestamp=datetime.utcfromtimestamp(ticker_data['timestamp'] / 1000),
        instrument=instrument,
        exchange_id=exchange_id,
        symbol_id=symbol_id,
        option_type=option_type,  # e.g., "CALL", "PUT"
        option_strike=strike,
        expiry=expiry,  # expiration date
        volume=ticker_data['volume'],
        last_price=ticker_data['price'],
        side=ticker_data['side'],  # m - market maker flag
        direction=ticker_data['direction']
    )
    db.add(ticker)
    await db.commit()
    await db.refresh(ticker)
    return True

# async def get_aggregated_data(db: AsyncSession):
#     # Example aggregation logic
#     return db.query(
#         models.Ticker.instrument,
#         func.avg(models.Ticker.volume).label('avg_volume'),
#         func.avg(models.Ticker.last_price).label('avg_price')
#     ).group_by(models.Ticker.instrument).all()
