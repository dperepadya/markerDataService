from datetime import datetime

from pydantic import BaseModel

class SubscriptionForm(BaseModel):
    name: str
    type: str
    symbol_id: int
    exchange_id: int

class ExchangeModel(BaseModel):
    id: int
    name: str

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
