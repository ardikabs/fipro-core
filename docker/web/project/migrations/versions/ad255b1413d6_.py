"""empty message

Revision ID: ad255b1413d6
Revises: 
Create Date: 2018-06-24 20:55:21.059334

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad255b1413d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensor', sa.Column('string_id', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensor', 'string_id')
    # ### end Alembic commands ###
