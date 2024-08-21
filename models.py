from sqlalchemy import Column, Integer, String, Text, Float, SmallInteger, Date, ForeignKey, Index, TIMESTAMP, \
    PrimaryKeyConstraint, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from database import Base
import datetime


class Exchange(Base):
    __tablename__ = 'exchanges'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)

    subscriptions = relationship('Subscription', back_populates='exchange')
    tickers = relationship('Ticker', back_populates='exchange')
    market_depth = relationship('OrderBook', back_populates='exchange')

class Symbol(Base):
    __tablename__ = 'symbols'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    tick_size = Column(Float, nullable=False)
    point_value = Column(Float, nullable=False)
    min_size = Column(Float, nullable=False)
    max_size = Column(Float, nullable=False)
    price_step = Column(Float, nullable=False)

    subscriptions = relationship('Subscription', back_populates='symbol')
    tickers = relationship('Ticker', back_populates='symbol')
    market_depth = relationship('OrderBook', back_populates='symbol')

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    exchange_id = Column(Integer, ForeignKey('exchanges.id'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), nullable=False)

    exchange = relationship('Exchange', back_populates='subscriptions')
    symbol = relationship('Symbol', back_populates='subscriptions')

class Ticker(Base):
    __tablename__ = 'tickers'
    id = Column(Integer, unique=True, nullable=False)  # t
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)  # T
    instrument = Column(Text, nullable=False)  # s
    # symbol = Column(Text, nullable=False)  # split
    exchange_id = Column(Integer, ForeignKey('exchanges.id'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), index=True)
    option_type = Column(String)  # e.g., "CALL", "PUT"
    option_strike = Column(Float)  # e.g., 1500.0 for options
    expiry = Column(TIMESTAMP(timezone=True))  # expiration date
    volume = Column(Float, nullable=False)  #
    last_price = Column(Float, nullable=False)  # l
    side = Column(Boolean, nullable=False)  # m - market maker flag
    direction = Column(Boolean, nullable=False)  # M - match type flag
    __table_args__ = (
        PrimaryKeyConstraint('timestamp', 'exchange_id', 'instrument', name='tickers_pkey'),
    )
    exchange = relationship("Exchange", back_populates="tickers")
    symbol = relationship("Symbol", back_populates="tickers")

class OrderBook(Base):
    __tablename__ = 'market_depth'
    id = Column(Integer, unique=True, nullable=False)  # t
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    exchange_id = Column(Integer, ForeignKey('exchanges.id'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), index=True)
    # symbol = Column(Text, nullable=False)
    instrument = Column(Text, nullable=False)
    # side = Column(String, nullable=False)
    best_bid = Column(Float, nullable=False)
    best_ask = Column(Float, nullable=False)
    best_bid_volume = Column(Float, nullable=False)
    best_bask_volume = Column(Float, nullable=False)
    bids = Column(JSONB, nullable=False),
    asks = Column(JSONB, nullable=False),
    __table_args__ = (
        PrimaryKeyConstraint('timestamp', 'exchange_id', 'instrument', name='market_depth_pkey'),
    )
    exchange = relationship("Exchange", back_populates="market_depth")
    symbol = relationship("Symbol", back_populates="market_depth")


# class Instrument(Base):
#     __tablename__ = 'instruments'
#     id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
#     name = Column(String, index=True, unique=True, nullable=False)
#     expiration_date = Column(Date, index=True, nullable=False)
#     point_size = Column(Float, nullable=False)
#     min_step_size = Column(Float, nullable=False)

    # tickers = relationship("Ticker", back_populates="instrument")
