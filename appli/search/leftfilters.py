# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp
from appli.database import GetAll
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.decorators import roles_accepted
import os,time


@app.route('/search/mappopup/')
def search_mappopup():
    g.filtertxt=""
    if gvg('projid'):
        g.Projid=gvg('projid')
        sqlparam={'projid': [int(x) for x in gvg("projid").split(',')]};
        g.filtertxt+="Project = "+",".join((x[0] for x in GetAll("select title from projects where projid=any (%(projid)s) ",sqlparam)))

    if gvg('taxoid'):
        g.taxoid=gvg('taxoid')
        sqlparam={'taxoid': [int(x) for x in gvg("taxoid").split(',')]};
        g.filtertxt+=" ,Taxonomy = "+",".join((x[0] for x in GetAll("select name from taxonomy where id=any (%(taxoid)s) ",sqlparam)))
        if gvg('taxochild'):
            g.taxochild=gvg('taxochild')
            g.filtertxt += "(with child)"
    return render_template('search/mappopup.html')

@app.route('/search/mappopup/samples/')
def search_mappopup_samples():
    app.logger.info(request.args)
    if gvg('projid') or gvg('taxoid'):
        sqlparam={}
        sql="SELECT distinct longitude,latitude from samples where latitude is not NULL and longitude is not NULL "
        if gvg('projid'):
            sql+=" and projid=any (%(projid)s) "
            sqlparam['projid'] = [int(x) for x in gvg("projid").split(',')];
        if gvg('taxoid'):
            sql+=" and sampleid in (select sampleid from obj_head where classif_id=any (%(taxoid)s) "
            sqlparam['taxoid'] = [int(x) for x in gvg("taxoid").split(',')];
            if gvg("taxochild") == "1":
                sqlparam['taxoid'] = [int(x[0]) for x in GetAll("""WITH RECURSIVE rq(id) as ( select id FROM taxonomy where id =any (%(taxoid)s)
                                        union
                                        SELECT t.id FROM rq JOIN taxonomy t ON rq.id = t.parent_id and (t.nbrobjcum>0 or t.nbrobj>0)
                                        ) select id from rq """ ,{"taxoid":sqlparam['taxoid']})]

            if gvg('projid'): sql+=" and projid=any (%(projid)s) "
            sql += " ) ";

        res=GetAll(sql,sqlparam);
    else:
        res=GetAll("""SELECT distinct cast(round(CAST (s.longitude AS numeric),1) as double PRECISION)
                      ,cast(round(cast(s.latitude AS numeric) ,1)as double PRECISION)
                      from samples s
                       join projects p on s.projid=p.projid and p.visible=true
                      where s.latitude is not NULL and s.longitude is not NULL  """)
    return json.dumps(res)


def getcommonfilters(data):
    return render_template('search/commonfilters.html',data=data)
