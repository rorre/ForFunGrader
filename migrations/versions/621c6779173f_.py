"""empty message

Revision ID: 621c6779173f
Revises: 92210a6fa34b
Create Date: 2019-11-16 14:58:11.820312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '621c6779173f'
down_revision = '92210a6fa34b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('me', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'me')
    # ### end Alembic commands ###
