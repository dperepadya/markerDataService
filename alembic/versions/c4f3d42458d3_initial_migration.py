"""Initial migration

Revision ID: c4f3d42458d3
Revises: 
Create Date: 2024-08-21 18:41:30.089523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4f3d42458d3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('exchanges',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )

    op.create_table('symbols',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('type', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('tick_size', sa.Float(), nullable=False),
                    sa.Column('point_value', sa.Float(), nullable=False),
                    sa.Column('min_size', sa.Float(), nullable=False),
                    sa.Column('max_size', sa.Float(), nullable=False),
                    sa.Column('price_step', sa.Float(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )

    op.create_table('subscriptions',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('exchange_id', sa.Integer(), nullable=False),
                    sa.Column('symbol_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['exchange_id'], ['exchanges.id'], ),
                    sa.ForeignKeyConstraint(['symbol_id'], ['symbols.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )

    op.create_table('tickers',
                    sa.Column('id', sa.TEXT(), nullable=False),
                    sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('instrument', sa.Text(), nullable=False),
                    sa.Column('exchange_id', sa.Integer(), nullable=False),
                    sa.Column('symbol_id', sa.Integer(), nullable=True),
                    sa.Column('option_type', sa.String(), nullable=True),
                    sa.Column('option_strike', sa.Float(), nullable=True),
                    sa.Column('expiry', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('volume', sa.Float(), nullable=False),
                    sa.Column('last_price', sa.Float(), nullable=False),
                    sa.Column('side', sa.Boolean(), nullable=False),
                    sa.Column('direction', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['exchange_id'], ['exchanges.id'], ),
                    sa.ForeignKeyConstraint(['symbol_id'], ['symbols.id'], ),
                    # sa.PrimaryKeyConstraint('timestamp', 'symbol', name='tickers_pkey')
                    sa.PrimaryKeyConstraint('timestamp', 'exchange_id', 'instrument', name='tickers_pkey')
                    )
    op.create_index('tickers_timestamp_idx', 'tickers', [sa.text('timestamp DESC')], unique=False)

    op.create_table('market_depth',
                    sa.Column('id', sa.TEXT(), nullable=False),
                    sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('exchange_id', sa.Integer(), nullable=False),
                    sa.Column('symbol_id', sa.Integer(), nullable=True),
                    sa.Column('instrument', sa.Text(), nullable=False),
                    sa.Column('best_bid', sa.Float(), nullable=False),
                    sa.Column('best_ask', sa.Float(), nullable=False),
                    sa.Column('best_bid_volume', sa.Float(), nullable=False),
                    sa.Column('best_bask_volume', sa.Float(), nullable=False),
                    sa.Column('bids', sa.JSON(), nullable=False),
                    sa.Column('asks', sa.JSON(), nullable=False),
                    sa.ForeignKeyConstraint(['exchange_id'], ['exchanges.id'], ),
                    sa.ForeignKeyConstraint(['symbol_id'], ['symbols.id'], ),
                    sa.PrimaryKeyConstraint('timestamp', 'exchange_id', 'instrument', name='market_depth_pkey')
                    )
    op.create_index('market_depth_timestamp_idx', 'market_depth', [sa.text('timestamp DESC')], unique=False)

def downgrade() -> None:
    op.drop_index('tickers_timestamp_idx', table_name='tickers')
    op.drop_table('tickers')
    op.drop_index('market_depth_timestamp_idx', table_name='tickers')
    op.drop_table('market_depth')
    op.drop_table('subscriptions')
    op.drop_table('symbols')
    op.drop_table('exchanges')

