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


def RecalcProjectTaxoStat(PrjId):
    ExecSQL("""delete from projects_taxo_stat WHERE projid=%(projid)s;
        insert into projects_taxo_stat(projid, id, nbr, nbr_v, nbr_d, nbr_p) 
          select projid,coalesce(classif_id,-1) id,count(*) nbr,count(case when classif_qual='V' then 1 end) nbr_v
          ,count(case when classif_qual='D' then 1 end) nbr_d,count(case when classif_qual='P' then 1 end) nbr_p
          from objects
          where projid = %(projid)s
          GROUP BY projid,classif_id;""", {'projid': PrjId})