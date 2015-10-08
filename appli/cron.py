from appli.database import ExecSQL


def RefreshAllProjectsStat():
    ExecSQL("UPDATE projects SET  objcount=Null,pctclassified=null,pctvalidated=NULL")
    ExecSQL("""UPDATE projects
     SET  objcount=q.nbr,pctclassified=100.0*nbrclassified/q.nbr,pctvalidated=100.0*nbrvalidated/q.nbr
     from (select projid, count(*) nbr,count(classif_id) nbrclassified,count(case when classif_qual='V' then 1 end) nbrvalidated
          from objects o
          group by projid )q
     where projects.projid=q.projid""")

def RefreshTaxoStat():
    n=ExecSQL("UPDATE taxonomy SET  nbrobj=Null,nbrobjcum=null where nbrobj is NOT NULL or nbrobjcum is not null")
    print("RefreshTaxoStat cleaned %d taxo"%n)

    n=ExecSQL("""UPDATE taxonomy
                SET  nbrobj=q.nbr
                from (select classif_id, count(*) nbr from objects o
                        join projects p on o.projid=p.projid and p.visible=true
                        where classif_qual='V' group by classif_id )q
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
            break;


if __name__ == "__main__":
    RefreshTaxoStat()