"""update tables

Revision ID: 9a7e6bc41013
Revises: c4f3d42458d3
Create Date: 2024-08-22 11:59:11.480740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9a7e6bc41013'
down_revision: Union[str, None] = 'c4f3d42458d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('subscriptions_exchange_id_fkey', 'subscriptions', type_='foreignkey')
    op.drop_constraint('subscriptions_symbol_id_fkey', 'subscriptions', type_='foreignkey')
    op.drop_constraint('tickers_exchange_id_fkey', 'tickers', type_='foreignkey')
    op.drop_constraint('tickers_symbol_id_fkey', 'tickers', type_='foreignkey')
    op.drop_constraint('market_depth_exchange_id_fkey', 'market_depth', type_='foreignkey')
    op.drop_constraint('market_depth_symbol_id_fkey', 'market_depth', type_='foreignkey')

    op.create_foreign_key('subscriptions_exchange_id_fkey', 'subscriptions',
                          'exchanges', ['exchange_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('subscriptions_symbol_id_fkey', 'subscriptions',
                          'symbols', ['symbol_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('tickers_exchange_id_fkey', 'tickers', 'exchanges',
                          ['exchange_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('tickers_symbol_id_fkey', 'tickers', 'symbols',
                          ['symbol_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('market_depth_exchange_id_fkey', 'market_depth', 'exchanges',
                          ['exchange_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('market_depth_symbol_id_fkey', 'market_depth', 'symbols',
                          ['symbol_id'], ['id'], ondelete='CASCADE')

    op.add_column('symbols', sa.Column('exchange_id', sa.Integer(), nullable=False))

    op.create_foreign_key('fk_symbols_exchange_id', 'symbols',
                          'exchanges', ['exchange_id'], ['id'], ondelete='CASCADE')

def downgrade() -> None:
    op.drop_constraint('fk_symbols_exchange_id', 'symbols', type_='foreignkey')
    op.drop_column('symbols', 'exchange_id')

    op.drop_constraint('subscriptions_exchange_id_fkey', 'subscriptions', type_='foreignkey')
    op.drop_constraint('subscriptions_symbol_id_fkey', 'subscriptions', type_='foreignkey')
    op.drop_constraint('tickers_exchange_id_fkey', 'tickers', type_='foreignkey')
    op.drop_constraint('tickers_symbol_id_fkey', 'tickers', type_='foreignkey')
    op.drop_constraint('market_depth_exchange_id_fkey', 'market_depth', type_='foreignkey')
    op.drop_constraint('market_depth_symbol_id_fkey', 'market_depth', type_='foreignkey')

    # Re-add the original foreign key constraints without ondelete='CASCADE'
    op.create_foreign_key('subscriptions_exchange_id_fkey', 'subscriptions', 'exchanges', ['exchange_id'], ['id'])
    op.create_foreign_key('subscriptions_symbol_id_fkey', 'subscriptions', 'symbols', ['symbol_id'], ['id'])
    op.create_foreign_key('tickers_exchange_id_fkey', 'tickers', 'exchanges', ['exchange_id'], ['id'])
    op.create_foreign_key('tickers_symbol_id_fkey', 'tickers', 'symbols', ['symbol_id'], ['id'])
    op.create_foreign_key('market_depth_exchange_id_fkey', 'market_depth', 'exchanges', ['exchange_id'], ['id'])
    op.create_foreign_key('market_depth_symbol_id_fkey', 'market_depth', 'symbols', ['symbol_id'], ['id'])