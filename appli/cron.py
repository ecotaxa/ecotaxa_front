# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from appli.database import ExecSQL,GetAll
from appli.part.database import ComputeOldestSampleDateOnProject
from appli.project.main import RecalcProjectTaxoStat
import appli.part.prj

def RefreshAllProjectsStat():
    # Tout les objets validés sans classifications sont repassés en non validés
    ExecSQL("update obj_head oh set classif_qual=NULL where classif_qual='V' and classif_id is null ")
    ExecSQL("UPDATE projects SET  objcount=Null,pctclassified=null,pctvalidated=NULL")
    ExecSQL("""UPDATE projects
     SET  objcount=q.nbr,pctclassified=100.0*nbrclassified/q.nbr,pctvalidated=100.0*nbrvalidated/q.nbr
     from (SELECT  projid,sum(nbr) nbr,sum(case when id>0 then nbr end) nbrclassified,sum(nbr_v) nbrvalidated
          from projects_taxo_stat
          group by projid  )q
     where projects.projid=q.projid""")
    ExecSQL("""delete from samples s
              where not exists (select 1 from objects o where o.sampleid=s.sampleid )
              and not exists (select 1 from part_samples o where o.sampleid=s.sampleid ) """)
    ComputeOldestSampleDateOnProject()

def RefreshTaxoStat():
    n=ExecSQL("UPDATE taxonomy SET  nbrobj=Null,nbrobjcum=null where nbrobj is NOT NULL or nbrobjcum is not null")
    print("RefreshTaxoStat cleaned %d taxo"%n)

    print("Refresh projects_taxo_stat")
    for r in GetAll('select projid from projects'):
        RecalcProjectTaxoStat(r['projid'])

    n=ExecSQL("""UPDATE taxonomy
                SET  nbrobj=q.nbr
                from (select id classif_id, sum(nbr_v) nbr 
                from projects_taxo_stat pts
                        join projects p on pts.projid=p.projid and p.visible=true
                        where nbr_v>0 group by id )q
                where taxonomy.id=q.classif_id""")
    print("RefreshTaxoStat updated %d 1st level taxo"%(n))

    n=ExecSQL("""UPDATE taxonomy
                SET  nbrobjcum=q.nbr
                from (select parent_id,sum(nbrobj) nbr from taxonomy
                      where nbrobj is NOT NULL
                      group by parent_id ) q
                where taxonomy.id=q.parent_id""")
    print("RefreshTaxoStat updated %d 2st level taxo"%(n))
    for i in range(50):
        n=ExecSQL("""UPDATE taxonomy
                    SET  nbrobjcum=q.nbr
                    from (select parent_id,sum(nbrobjcum+coalesce(nbrobj,0)) nbr from taxonomy
                          where nbrobjcum is NOT NULL
                          group by parent_id  ) q
                    where taxonomy.id=q.parent_id
                    and coalesce(taxonomy.nbrobjcum,0)<>q.nbr""")
        print("RefreshTaxoStat updated %d level %d taxo"%(n,i))
        if n==0:
            break
    appli.part.prj.GlobalTaxoCompute()

if __name__ == "__main__":
    # RefreshTaxoStat()
    from appli import app
    from flask import g
    import traceback,appli.tasks,logging

    app.logger.setLevel(logging.DEBUG)
    for h in app.logger.handlers:
        h.setLevel(logging.DEBUG)
    app.logger.info("Start Daily Task")
    try:
        with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
            g.db = None
            RefreshAllProjectsStat()
            RefreshTaxoStat()
            app.logger.info(appli.tasks.taskmanager.AutoClean())
    except Exception as e:
        s=str(e)
        tb_list = traceback.format_tb(e.__traceback__)
        for i in tb_list[::-1]:
            s += "\n" + i
        app.logger.error("Exception on Daily Task : %s"%s)
    app.logger.info("End Daily Task")