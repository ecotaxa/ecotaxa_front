from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections
from appli.database import GetAll,GetClassifQualClass,db,ExecSQL

@app.route('/prj/ManualClassif/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjManualClassif(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if not Prj.CheckRight(1): # Level 0 = Read, 1 = Annotate, 2 = Admin
        return "You cannot Annotate this project"

    changes={k[8:-1]:v for k,v in request.form.items() if k[0:7]=="changes"}
    sql="update objects set classif_id=%(classif_id)s,classif_qual='V',classif_who=%(classif_who)s,classif_when=now() where objid=%(objid)s "
    for k,v in changes.items():
        params={'objid':k,'classif_id':v,'classif_who':current_user.id}
        ExecSQL(sql,params,False)
    return '<span class="label label-success">Database update Successfull</span>'

