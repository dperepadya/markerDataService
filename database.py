import os

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload, sessionmaker

db_user = os.environ.get('DATABASE_UN', 'postgres')
db_pass = os.environ.get('DATABASE_PWD', 'qwerty123')
db_port = 5432
db_name = "market_data"

is_async_mode = os.environ.get('IS_ASYNC_MODE', 'True')
if is_async_mode:
    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@localhost:{db_port}/{db_name}"
    engine = create_async_engine(db_url, echo=True)

    # async_session = AsyncSession(engine, expire_on_commit=False, autoflush=False, autocommit=False,
    #                                     expire_on_commit=False)
    SessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False,
                                      expire_on_commit=False)
else:
    # SYNC SETUP FOR ALEMBIC
    # DON'T FORGET MODIFY alembic.ini
    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@localhost:{db_port}/{db_name}"
    print(db_url)
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)

Base = declarative_base()

# SYNC SETUP FOR ALEMBIC
def init_db():
    Base.metadata.create_all(bind=engine)

async def init_db_async():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
