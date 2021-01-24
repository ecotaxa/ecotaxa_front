"""parent objects ids

Revision ID: 15cad3c0948e
Revises: af87eb95cafc
Create Date: 2020-10-30 07:09:50.978241

"""

# revision identifiers, used by Alembic.
from sqlalchemy import INTEGER, BIGINT

revision = '15cad3c0948e'
down_revision = 'af87eb95cafc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('samples', 'sampleid', type_=INTEGER)
    op.alter_column('acquisitions', 'acquisid', type_=INTEGER)
    op.alter_column('process', 'processid', type_=INTEGER)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('samples', 'sampleid', type_=BIGINT)
    op.alter_column('acquisitions', 'acquisid', type_=BIGINT)
    op.alter_column('process', 'processid', type_=BIGINT)
    # ### end Alembic commands ###