"""empty message

Revision ID: 35b3703b42c9
Revises: cfee269c21de
Create Date: 2019-11-17 10:38:27.076171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35b3703b42c9'
down_revision = 'cfee269c21de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('verified')

    # ### end Alembic commands ###
