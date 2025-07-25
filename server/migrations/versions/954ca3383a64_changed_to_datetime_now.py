"""changed to datetime.now

Revision ID: 954ca3383a64
Revises: 4d26ee409f4e
Create Date: 2025-07-13 15:22:49.395668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '954ca3383a64'
down_revision = '4d26ee409f4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profile_match', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profile_match', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
