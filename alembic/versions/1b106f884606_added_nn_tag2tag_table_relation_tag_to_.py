"""Added nn_tag2tag table & relation Tag to Tag

Revision ID: 1b106f884606
Revises: 24862df4fb7b
Create Date: 2013-12-06 18:24:02.699945

"""

# revision identifiers, used by Alembic.
revision = '1b106f884606'
down_revision = '24862df4fb7b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('nn_tag2tag',
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.Column('child_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['child_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('parent_id', 'child_id')
    )


def downgrade():
    op.drop_table('nn_tag2tag')
