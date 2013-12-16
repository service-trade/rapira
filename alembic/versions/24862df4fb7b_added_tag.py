"""Added Tag

Revision ID: 24862df4fb7b
Revises: cee34cc6ffb
Create Date: 2013-12-06 17:41:22.468248

"""

# revision identifiers, used by Alembic.
revision = '24862df4fb7b'
down_revision = 'cee34cc6ffb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('tag')

