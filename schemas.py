from datetime import datetime

from pydantic import BaseModel


class MarketDataBase(BaseModel):
    symbol: str
    instrument: str
    volume: float
    last_price: float


class MarketDataCreate(MarketDataBase):
    pass


class MarketData(MarketDataBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
