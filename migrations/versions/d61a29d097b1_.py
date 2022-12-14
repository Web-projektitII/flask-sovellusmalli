"""empty message

Revision ID: d61a29d097b1
Revises: bb2c6e73cbe4
Create Date: 2022-11-04 17:23:32.876717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd61a29d097b1'
down_revision = 'bb2c6e73cbe4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Huom. manuaalisesti lisätty server_default='1'.
    op.add_column('users', sa.Column('active', sa.Boolean(), nullable=True, server_default='1'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'active')
    # ### end Alembic commands ###
