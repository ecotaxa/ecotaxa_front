from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections,psycopg2.extras
from appli.database import GetAll,GetClassifQualClass,db,ExecSQL

@app.route('/prj/ManualClassif/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjManualClassif(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if not Prj.CheckRight(1): # Level 0 = Read, 1 = Annotate, 2 = Admin
        return "You cannot Annotate this project"

    changes={k[8:-1]:v for k,v in request.form.items() if k[0:7]=="changes"}
    if len(changes)==0:
        return '<span class="label label-warning">No pending change to update</span>'

    sql="""select o.objid,o.classif_auto_id,o.classif_auto_when,o.classif_auto_score,o.classif_id,o.classif_qual,o.classif_when,o.classif_who
          from objects o
          where o.objid in ("""+",".join(changes.keys())+")"
    prev={r['objid']:r for r in GetAll(sql,debug=False)}
    sql="update objects set classif_id=%(classif_id)s,classif_qual=%(classif_qual)s,classif_who=%(classif_who)s,classif_when=now() where objid=%(objid)s "
    sqli="""INSERT INTO objectsclassifhisto (objid, classif_date, classif_type, classif_id, classif_qual, classif_who)
            VALUES (%(objid)s,%(classif_when)s,'M',%(classif_id)s,%(classif_qual)s,%(classif_who)s )"""
    for k,v in changes.items():
        ki=int(k)
        if v=="-1" or v=="" : # utilisé dans validate all
            v=prev[ki]['classif_id']
        if prev[ki]['classif_qual']!=gvp('qual') or prev[ki]['classif_who']!=current_user.id or prev[ki]['classif_id']!=int(v):
            # il y a eu au moins un changement
            params={'objid':k,'classif_id':v,'classif_who':current_user.id,'classif_qual':gvp('qual')}
            ExecSQL(sql,params,False)
            params={'objid':k,'classif_id':prev[ki]['classif_id'],'classif_who':prev[ki]['classif_who']
                ,'classif_qual':prev[ki]['classif_qual'],'classif_when':prev[ki]['classif_when']}
            try:
                ExecSQL(sqli,params,True)
            except:
                app.logger.warning("Unable to add historical information, non-blocking %s"%(prev,))

    return '<span class="label label-success">Database update Successfull</span>'

