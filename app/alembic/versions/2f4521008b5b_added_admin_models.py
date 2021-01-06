"""Added admin models

Revision ID: 2f4521008b5b
Revises: d4867f3a4c0a
Create Date: 2021-01-04 19:24:13.786274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f4521008b5b'
down_revision = 'd4867f3a4c0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('permissions', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_admin_user_id'), 'admin', ['user_id'], unique=False)
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_admin_user_id'), table_name='admin')
    op.drop_table('admin')
    op.drop_column('user', 'is_admin')
    # ### end Alembic commands ###
