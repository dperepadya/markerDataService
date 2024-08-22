from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Exchange, Symbol

exchanges_cache = {}
symbols_cache = {}

async def load_caches(session: AsyncSession):
    # Load exchanges into cache
    exchanges = await session.execute(select(Exchange))
    exchanges_cache.update({exchange.id: exchange for exchange in exchanges.scalars().all()})

    # Load symbols into cache
    symbols = await session.execute(select(Symbol))
    symbols_cache.update({symbol.id: symbol for symbol in symbols.scalars().all()})

    print("Caches loaded successfully.")