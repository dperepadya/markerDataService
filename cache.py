import logging
from models import Exchange, Symbol
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

# {exchange_name, exchange_id}
exchanges_cache = {}
# {{exchange_id , {symbol_name, symbol_id}}
symbols_cache = {}

async def load_caches(session: AsyncSession):
    # Load exchanges into cache
    exchanges = await session.execute(select(Exchange))
    exchanges_cache.update({exchange.name: exchange.id for exchange in exchanges.scalars().all()})

    # Load symbols into cache
    symbols = await session.execute(select(Symbol))
    for symbol in symbols.scalars().all():
        if symbol.exchange_id not in symbols_cache:
            symbols_cache[symbol.exchange_id] = {}
        symbols_cache[symbol.exchange_id][symbol.name] = symbol.id

    # symbols_cache.update({symbol.name: symbol.id for symbol in symbols.scalars().all()})

    print("Caches loaded successfully.")