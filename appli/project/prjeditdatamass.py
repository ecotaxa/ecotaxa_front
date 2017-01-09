from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli,appli.project.sharedfilter as sharedfilter
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc2Col


def GetFieldList(Prj):
    fieldlist = []
    MapList = (('f', 'mappingobj'), ('s', 'mappingsample'), ('a', 'mappingacq'), ('p', 'mappingprocess'))
    MapPrefix =  {'f': 'object.', 's': 'sample.', 'a': 'acquis.', 'p': 'process.'}
    for mapk, mapv in MapList:
        for k, v in sorted(DecodeEqualList(getattr(Prj, mapv, "")).items(), key=lambda t: t[1]):
            fieldlist.append({'id': mapk + k, 'text': MapPrefix[mapk] + v})
    return fieldlist



######################################################################################################################
@app.route('/prj/editdatamass/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditDataMass(PrjId):
    request.form  # Force la lecture des données POST sinon il y a une erreur 504
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        flash("Project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot edit settings for this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title)
    txt = "<h3>Project Mass data edition </h3>"
    sql = "select objid FROM objects o where projid=" + str(Prj.projid)
    sqlparam = {}
    filtres = {}
    for k in sharedfilter.FilterList:
        if gvg(k):
            filtres[k] = gvg(k, "")
    if len(filtres):
        sql += sharedfilter.GetSQLFilter(filtres, sqlparam, str(current_user.id))
        ObjList = GetAll(sql, sqlparam)
        ObjListTxt = "\n".join((str(r['objid']) for r in ObjList))
        txt += "<span style='color:red;weight:bold;font-size:large;'>USING Active Project Filters, {0} objects</span>".format(
            len(ObjList))
    else:
        txt += "<span style='color:red;weight:bold;font-size:large;'>Apply to ALL OBJETS OF THE PROJECT (NO Active Filters)</span>"
    Lst=GetFieldList(Prj)
    # txt+="%s"%(Lst,)

    return PrintInCharte(render_template("project/prjeditdatamass.html",Lst=Lst,header=txt))