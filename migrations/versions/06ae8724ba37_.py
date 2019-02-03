"""empty message

Revision ID: 06ae8724ba37
Revises: 1cd3a6d8bef4
Create Date: 2019-01-15 17:37:08.269850

"""

# revision identifiers, used by Alembic.
revision = '06ae8724ba37'
down_revision = '1cd3a6d8bef4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('persistantdatatable',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('lastserverversioncheck_datetime', postgresql.TIMESTAMP(precision=0), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('taxonomy', sa.Column('creation_datetime', postgresql.TIMESTAMP(precision=0), nullable=True))
    op.add_column('taxonomy', sa.Column('creator_email', sa.VARCHAR(length=255), nullable=True))
    op.add_column('taxonomy', sa.Column('display_name', sa.VARCHAR(length=200), nullable=True))
    op.add_column('taxonomy', sa.Column('id_instance', sa.INTEGER(), nullable=True))
    op.add_column('taxonomy', sa.Column('lastupdate_datetime', postgresql.TIMESTAMP(precision=0), nullable=True))
    op.add_column('taxonomy', sa.Column('rename_to', sa.INTEGER(), nullable=True))
    op.add_column('taxonomy', sa.Column('source_desc', sa.VARCHAR(length=1000), nullable=True))
    op.add_column('taxonomy', sa.Column('source_url', sa.VARCHAR(length=200), nullable=True))
    op.add_column('taxonomy', sa.Column('taxostatus', sa.CHAR(length=1), server_default='A', nullable=False))
    op.add_column('taxonomy', sa.Column('taxotype', sa.CHAR(length=1), server_default='P', nullable=False))
    # ### end Alembic commands ###
    op.execute("""UPDATE taxonomy set taxotype='M'
where name in ('actinula','antenna','artefact','autotroph','badfocus','bead','bell','body','bubble','c01','c02','c03','c04',
'c05','c06','calyptopis','calyptopsis','centric','chain','chainlarge','chainthin','cirrus','clumps','collonial ','colonial',
'colony','compact','cyphonaute','cypris','cyst','dark','dead','detritus','disc','duplicate','egg','embryo','empty','ephyra',
'eudoxie','feces','fiber','filament','film','fluffy','fragment','gelatinous','geometric','glue','gonophore','head','heterotroph',
'house','htm','htm01','htm02','htm03','htm04','inter','large','larvae','leg','light','like','line','long','medium','megalopa',
'metanauplii','multiple','n01','n02','n03','n04','n05','n06','naked','nauplii','nectophore','not-living','other','othertocheck ',
'ovoid','part','pellet','pennate','phycoma ','phyllosoma','pilidium','plastic','pluteus','pollen','polystyrene','protozoea',
'puff','rectangle','ring','rods','scale','seaweed','short','silks','siphonula','siphosome','small','solitaryblack ','solitaryfuzzy ',
'solitaryglobule ','solitarygrey ','sphere','sphereeye','spherethorn','spines','spore','star','swarmers ','t001','t002','t003',
't004','t005','t006','t007','t008','t009','t010','t011','t012','t013','t014','t015','t016','t017','t018','t019','t020','tail',
'temporary','transparent','tubes','tuff','turbid','unicellular','veliger','Viruses','wing','zoea')
   """)
    op.execute("""update public.taxonomy set lastupdate_datetime ='2018-01-02',display_name=name """)
    op.execute("create index IS_TaxonomyDispNameLow on taxonomy(lower(display_name))")
    op.execute("""insert into persistantdatatable(id,lastserverversioncheck_datetime) VALUES (1,'2018-01-02')""")



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('taxonomy', 'taxotype')
    op.drop_column('taxonomy', 'taxostatus')
    op.drop_column('taxonomy', 'source_url')
    op.drop_column('taxonomy', 'source_desc')
    op.drop_column('taxonomy', 'rename_to')
    op.drop_column('taxonomy', 'lastupdate_datetime')
    op.drop_column('taxonomy', 'id_instance')
    op.drop_column('taxonomy', 'display_name')
    op.drop_column('taxonomy', 'creator_email')
    op.drop_column('taxonomy', 'creation_datetime')
    op.drop_table('persistantdatatable')
    # ### end Alembic commands ###