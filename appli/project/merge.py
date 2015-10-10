from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc2Col

######################################################################################################################
@app.route('/prj/merge/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjMerge(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        flash("Project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot edit settings for this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")

    txt = """<h3>Project Merge / Fusion </h3>
            <h4>Target Project : {0} - {1}</h4>
            """.format(Prj.projid,Prj.title)

    if not gvg('src'):
        txt += """<h4>Select the project to merge with this project, this project will be destroy.<br>Next screen will check for compatibility.</h4>
                """
        sql="select p.projid,title,status,pctvalidated from projects p"
        if not current_user.has_role(database.AdministratorLabel):
            sql+=" Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
        sql+=" where p.projid!=%d order by title"%Prj.projid
        res = GetAll(sql) #,debug=True
        txt+="""<table class='table table-bordered table-hover'>
                <tr><th width=120>ID</td><th>Title</td><th width=100>Status</td></tr>"""
        for r in res:
            txt+="""<tr><td><a class="btn btn-primary" href='/prj/merge/{0}?src={1}'>Select</a> {1}</td>
            <td>{2}</td>
            <td>{3}</td>
            </tr>""".format(Prj.projid,*r)
        txt+="</table>"
        return PrintInCharte(txt)

    PrjSrc=database.Projects.query.filter_by(projid=int(gvg('src'))).first()
    if PrjSrc is None:
        flash("Source project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not PrjSrc.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot merge for this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    txt += """<h4>Source Project : {0} - {1} (This project will be destroyed)</h4>
            """.format(PrjSrc.projid,PrjSrc.title)
    if not gvg('merge'): # Ici la src à été choisie et vérifiée
        if PrjSrc.mappingobj!=Prj.mappingobj:
            flash("Object mapping differ With source project ","warning")
        if PrjSrc.mappingsample!=Prj.mappingsample:
            flash("Sample mapping differ With source project ","warning")
        if PrjSrc.mappingacq!=Prj.mappingacq:
            flash("Acquisition mapping differ With source project ","warning")
        if PrjSrc.mappingprocess!=Prj.mappingprocess:
            flash("Process mapping differ With source project ","warning")
        txt+="""<p style='font-size: 18px;color:red;'><span class='glyphicon glyphicon-warning-sign'></span>
        Warning project {1} - {2}<br>
        Will be destroyed, its content will be transfered in the target project.<br>
        This operation is irreversible</p>

        <br><a class='btn btn-lg btn-warning' href='/prj/merge/{0}?src={1}&merge=Y'>Start Project Fusion</a>
        """.format(Prj.projid,PrjSrc.projid,PrjSrc.title)
        return PrintInCharte(txt)

    if gvg('merge')=='Y':
        ExecSQL("update acquisitions set projid={0} where projid={1}".format(Prj.projid,PrjSrc.projid))
        ExecSQL("update process set projid={0} where projid={1}".format(Prj.projid,PrjSrc.projid))
        ExecSQL("update samples set projid={0} where projid={1}".format(Prj.projid,PrjSrc.projid))
        ExecSQL("update obj_head set projid={0} where projid={1}".format(Prj.projid,PrjSrc.projid))
        ExecSQL("delete from projectspriv where projid={0}".format(PrjSrc.projid))
        ExecSQL("delete from projects where projid={0}".format(PrjSrc.projid))
        txt+="<div class='alert alert-success' role='alert'>Fusion Done successfully</div>"
        txt+="<br><a class='btn btn-lg btn-primary' href='/prj/%s'>Back to target project</a>"%Prj.projid
        return PrintInCharte(txt)



