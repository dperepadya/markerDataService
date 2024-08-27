import os

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


from sqlalchemy.orm import sessionmaker

db_user = os.environ.get('DATABASE_UN', 'postgres')
db_pass = os.environ.get('DATABASE_PWD', 'qwerty123')
db_port = 5432
db_name = "market_data"

Base = declarative_base()

is_async_mode = os.environ.get('IS_ASYNC_MODE', 'True')
if is_async_mode:
    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@localhost:{db_port}/{db_name}"
    # db_url = "postgresql+asyncpg://postgres:qwerty123@localhost:5432/market_data"
    engine = create_async_engine(db_url, echo=True)
    SessionFactory = async_sessionmaker(bind=engine, autoflush=False, autocommit=False,
                                        expire_on_commit=False)
else:
    # SYNC SETUP FOR ALEMBIC
    # DON'T FORGET MODIFY alembic.ini
    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@localhost:{db_port}/{db_name}"
    print(db_url)
    engine = create_engine(db_url)
    SessionFactory = sessionmaker(engine, autoflush=False, autocommit=False)


# SYNC SETUP FOR ALEMBIC
def init_db():
    Base.metadata.create_all(bind=engine)

async def init_db_async():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    # await engine.dispose()

async def get_db() -> AsyncSession:
    async with SessionFactory() as session:
        try:
            # print(f"ASYNC Pool: {engine.pool.status()}")
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

