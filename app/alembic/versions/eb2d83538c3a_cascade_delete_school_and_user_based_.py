"""cascade delete school and user based foreign keys

Revision ID: eb2d83538c3a
Revises: 7b2f235b8ffe
Create Date: 2021-03-07 17:54:17.211449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb2d83538c3a'
down_revision = '7b2f235b8ffe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('admin_ibfk_1', 'admin', type_='foreignkey')
    op.create_foreign_key(None, 'admin', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('user_ibfk_1', 'user', type_='foreignkey')
    op.create_foreign_key(None, 'user', 'school', ['school'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.create_foreign_key('user_ibfk_1', 'user', 'school', ['school'], ['id'])
    op.drop_constraint(None, 'admin', type_='foreignkey')
    op.create_foreign_key('admin_ibfk_1', 'admin', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###
