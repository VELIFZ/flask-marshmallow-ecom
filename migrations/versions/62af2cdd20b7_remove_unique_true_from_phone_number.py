"""Remove unique= True from phone number

Revision ID: 62af2cdd20b7
Revises: 099a2334fe61
Create Date: 2025-02-26 16:32:49.530797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62af2cdd20b7'
down_revision = '099a2334fe61'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('phone_number')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index('phone_number', ['phone_number'], unique=True)

    # ### end Alembic commands ###
