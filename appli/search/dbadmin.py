from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage,ntcv
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli,psycopg2.extras
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc

import appli.cron


@app.route('/dbadmin/viewsizes')
@login_required
@roles_accepted(database.AdministratorLabel)
def dbadmin_viewsizes():
    g.headcenter="Database objects size (public schema only)<br><a href=/admin>Back to admin home</a>"

    sql="""SELECT c.relname, c.relkind, CASE WHEN c.relkind='i' THEN c2.tablename ELSE c.relname END fromtable,pg_relation_size(('"' || c.relname || '"')::regclass)/(1024*1024) szMB
FROM
 pg_namespace ns,
 pg_class c LEFT OUTER JOIN
 pg_indexes c2 ON c.relname = c2.indexname
WHERE c.relnamespace = ns.oid
 AND ns.nspname = 'public'
 AND c.relkind IN ('r' ,'i')
ORDER BY c.relkind DESC, pg_relation_size(('"' || c.relname || '"')::regclass) DESC
"""
    res = GetAll(sql) #,debug=True
    txt="""<table class='table table-bordered table-condensed table-hover' style="width:500px;">
            <tr><th width=200>Object</td><th witdth=200>Table</td><th width=100>Size (Mb)</td></tr>"""
    for r in res:
        txt+="""<tr><td>{0}</td>
        <td>{2}</td>
        <td>{3}</td>

        </tr>""".format(*r)
    txt+="</table>"

    return PrintInCharte(txt)


@app.route('/dbadmin/viewtaxoerror')
@login_required
@roles_accepted(database.AdministratorLabel)
def dbadmin_viewtaxoerror():
    g.headcenter="Database Taxonomy errors<br><a href=/admin>Back to admin home</a>"

    sql="""Select 'Missing parent' reason,t.id,t.parent_id,t.name,t.id_source
from taxonomy t where parent_id not in (select id from taxonomy);
"""
    cur = db.engine.raw_connection().cursor()
    try:
        txt="<table class='table table-bordered table-condensed table-hover'>"
        cur.execute(sql)
        txt+="<tr><td>"+("</td><td>".join([x[0] for x in cur.description]))+"</td></tr>"
        for r in cur:
            txt+="<tr><td>"+("</td><td>".join([str(x) for x in r]))+"</td></tr>"
        txt+="</table>"
    finally:
        cur.close()

    return PrintInCharte(txt)


@app.route('/dbadmin/viewbloat')
@login_required
@roles_accepted(database.AdministratorLabel)
def dbadmin_viewbloat():
    g.headcenter="Database objects wasted space<br><a href=/admin>Back to admin home</a>"
    sql="""SELECT
        schemaname, tablename, reltuples::bigint, relpages::bigint, otta,
        ROUND(CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::numeric END,1) AS tbloat,
        relpages::bigint - otta AS wastedpages,
        bs*(sml.relpages-otta)::bigint AS wastedbytes,
        pg_size_pretty((bs*(relpages-otta))::bigint) AS wastedsize,
        iname, ituples::bigint, ipages::bigint, iotta,
        ROUND(CASE WHEN iotta=0 OR ipages=0 THEN 0.0 ELSE ipages/iotta::numeric END,1) AS ibloat,
        CASE WHEN ipages < iotta THEN 0 ELSE ipages::bigint - iotta END AS wastedipages,
        CASE WHEN ipages < iotta THEN 0 ELSE bs*(ipages-iotta) END AS wastedibytes,
        CASE WHEN ipages < iotta THEN '0' ELSE pg_size_pretty((bs*(ipages-iotta))::bigint) END AS wastedisize
      FROM (
        SELECT
          schemaname, tablename, cc.reltuples, cc.relpages, bs,
          CEIL((cc.reltuples*((datahdr+ma-
            (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta,
          COALESCE(c2.relname,'?') AS iname, COALESCE(c2.reltuples,0) AS ituples, COALESCE(c2.relpages,0) AS ipages,
          COALESCE(CEIL((c2.reltuples*(datahdr-12))/(bs-20::float)),0) AS iotta -- very rough approximation, assumes all cols
        FROM (
          SELECT
            ma,bs,schemaname,tablename,
            (datawidth+(hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)))::numeric AS datahdr,
            (maxfracsum*(nullhdr+ma-(case when nullhdr%ma=0 THEN ma ELSE nullhdr%ma END))) AS nullhdr2
          FROM (
            SELECT
              schemaname, tablename, hdr, ma, bs,
              SUM((1-null_frac)*avg_width) AS datawidth,
              MAX(null_frac) AS maxfracsum,
              hdr+(
                SELECT 1+count(*)/8
                FROM pg_stats s2
                WHERE null_frac<>0 AND s2.schemaname = s.schemaname AND s2.tablename = s.tablename
              ) AS nullhdr
            FROM pg_stats s, (
              SELECT
                (SELECT current_setting('block_size')::numeric) AS bs,
                CASE WHEN substring(v,12,3) IN ('8.0','8.1','8.2') THEN 27 ELSE 23 END AS hdr,
                CASE WHEN v ~ 'mingw32' THEN 8 ELSE 4 END AS ma
              FROM (SELECT version() AS v) AS foo
            ) AS constants
            GROUP BY 1,2,3,4,5
          ) AS foo
        ) AS rs
        JOIN pg_class cc ON cc.relname = rs.tablename
        JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname
        LEFT JOIN pg_index i ON indrelid = cc.oid
        LEFT JOIN pg_class c2 ON c2.oid = i.indexrelid
      ) AS sml
      WHERE sml.relpages - otta > 0 OR ipages - iotta > 10
      ORDER BY wastedbytes DESC, wastedibytes DESC
"""
    cur = db.engine.raw_connection().cursor()
    try:
        txt="<table class='table table-bordered table-condensed table-hover'>"
        cur.execute(sql)
        txt+="<tr><td>"+("</td><td>".join([x[0] for x in cur.description]))+"</td></tr>"
        for r in cur:
            txt+="<tr><td>"+("</td><td>".join([str(x) for x in r]))+"</td></tr>"
        txt+="</table>"
    finally:
        cur.close()
    return PrintInCharte(txt)

@app.route('/dbadmin/recomputestat')
@login_required
@roles_accepted(database.AdministratorLabel)
def dbadmin_recomputestat():
    g.headcenter="Statistics recompute<br><a href=/admin>Back to admin home</a>"
    appli.cron.RefreshAllProjectsStat()
    appli.cron.RefreshTaxoStat()
    return PrintInCharte("Statistics recompute done")


@app.route('/dbadmin/merge2taxon')
@login_required
@roles_accepted(database.AdministratorLabel)
def dbadmin_merge2taxon():
    if gvg("src","")=="" or gvg("dest","")=="":
        txt="Select source Taxon (will be deleted after merge) :"
        txt+="<br>Select Target Taxon :"
        return render_template('search/merge2taxo.html')
    TaxoSrc=database.Taxonomy.query.filter_by(id=int(gvg("src",""))).first()
    TaxoDest=database.Taxonomy.query.filter_by(id=int(gvg("dest",""))).first()
    N1=ExecSQL("update obj_head set classif_id=%(dest)s where  classif_id=%(src)s",{"src":TaxoSrc.id,"dest":TaxoDest.id})
    N2=ExecSQL("update obj_head set classif_auto_id=%(dest)s where  classif_auto_id=%(src)s",{"src":TaxoSrc.id,"dest":TaxoDest.id})
    N3=ExecSQL("update objectsclassifhisto set classif_id=%(dest)s where  classif_id=%(src)s",{"src":TaxoSrc.id,"dest":TaxoDest.id})
    N4=ExecSQL("update taxonomy set parent_id=%(dest)s where  parent_id=%(src)s",{"src":TaxoSrc.id,"dest":TaxoDest.id})
    N5=ExecSQL("delete from taxonomy where id=%(src)s",{"src":TaxoSrc.id,"dest":TaxoDest.id})
    return PrintInCharte("""Merge of '%s' in '%s' done
    <br>%d Objects Manuel classification  updated
    <br>%d Objects Automatic classification  updated
    <br>%d Objects classification historical updated
    <br>%d Taxonomy child updated
    <br>%d Taxonomy Node deleted
    """%(TaxoSrc.name,TaxoDest.name,N1,N2,N3,N4,N5))


@app.route('/dbadmin/console', methods=['GET', 'POST'])
@login_required
@roles_accepted(database.AdministratorLabel)
def dbadmin_console():
    g.headcenter="<font color=red style='font-size:18px;'>Warning : This screen must be used only by experts</font><br><a href=/admin>Back to admin home</a>"
    txt="<form method=post>SQL : <textarea name=sql rows=15 cols=100>%s</textarea><br>"%gvp("sql")
    txt+="""<input type=submit class='btn btn-primary' name=doselect value='Execute Select'>
    <input type=submit class='btn btn-primary' name=dodml value='Execute DML'>
    Note : For DML ; can be used, but only the result of the last query dis displayed
    </form>"""
    if gvp("doselect"):
        txt+="<br>Select Result :"
        cur = db.engine.raw_connection().cursor()
        try:
            cur.execute(gvp("sql"))
            txt+="<table class='table table-condensed table-bordered'>"
            for c in cur.description:
                txt+="<td>%s</td>"%c[0]
            for r in cur:
                s="<tr>"
                for c in r:
                    s+="<td>%s</td>"%c
                txt+=s+"</tr>"
            txt+="</table>"

        except Exception as e :
            txt+="<br>Error = %s"%e
            cur.connection.rollback()
        finally:
            cur.close()
    if gvp("dodml"):
        txt+="<br>DML Result :"
        cur = db.engine.raw_connection().cursor()
        try:
            cur.execute(gvp("sql"))
            txt+="%s rows impacted"%cur.rowcount
            cur.connection.commit()
        except Exception as e :
            txt+="<br>Error = %s"%e
            cur.connection.rollback()
        finally:
            cur.close()


    return PrintInCharte(txt)