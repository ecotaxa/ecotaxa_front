from appli.database import ExecSQL


def UpdateProjectStat(PrjId):
    ExecSQL("""UPDATE projects
         SET  objcount=q.nbr,pctclassified=100.0*nbrclassified/q.nbr,pctvalidated=100.0*nbrvalidated/q.nbr
         from projects p
         left join
         (SELECT  projid,sum(nbr) nbr,sum(case when id>0 then nbr end) nbrclassified,sum(nbr_v) nbrvalidated
              from projects_taxo_stat
              where projid=%(projid)s
              group by projid )q on p.projid=q.projid
         where projects.projid=%(projid)s and p.projid=%(projid)s""", {'projid': PrjId})
