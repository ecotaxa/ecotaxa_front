# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp
from appli.database import GetAll
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask_security.decorators import roles_accepted
import os,time


@app.route('/search/mappopup/')
def search_mappopup():
    if gvg('projid'):
        g.Projid=gvg('projid')
    return render_template('search/mappopup.html')

@app.route('/search/mappopup/samples/')
def search_mappopup_samples():
    app.logger.info(request.args)
    if gvg('projid'):
        res=GetAll("SELECT distinct longitude,latitude from samples where latitude is not NULL and longitude is not NULL  and projid=%s",(gvg('projid'),))
    else:
        res=GetAll("""SELECT distinct cast(round(CAST (s.longitude AS numeric),1) as double PRECISION)
                      ,cast(round(cast(s.latitude AS numeric) ,1)as double PRECISION)
                      from samples s
                       join projects p on s.projid=p.projid and p.visible=true
                      where s.latitude is not NULL and s.longitude is not NULL  """)
    return json.dumps(res)


def getcommonfilters(data):
    return render_template('search/commonfilters.html',data=data)
