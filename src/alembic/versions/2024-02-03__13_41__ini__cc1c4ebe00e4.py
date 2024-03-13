"""init

Revision ID: cc1c4ebe00e4
Revises: 
Create Date: 2024-02-03 13:41:47.261252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc1c4ebe00e4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('in_search', sa.Boolean(), nullable=False),
    sa.Column('rating', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player')
    # ### end Alembic commands ###
