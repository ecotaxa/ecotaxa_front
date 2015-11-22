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
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title)
    txt = """<h3>Project Merge / Fusion </h3>
            <h4>Target Project : {0} - {1}</h4>
            """.format(Prj.projid,Prj.title)

    if not gvg('src'):
        txt += """<ul><li>You are allowed to merge projects that you are allowed to manage
<li>User privileges from both projects will be added
<li>This tool allow to merge two projects in a single projet (called Current project). The added project will then be automatically deleted. If object data are not consistent between both projects :
<ul><li>New data fields are added to the Current project
    <li>The resulting project will thus contain partially documented datafields.
</ul><li>Note : Next screen will indicate compatibility issues (if exists) and allow you to Confirm the merging operation.
</ul>
                """
        sql="select p.projid,title,status,coalesce(objcount,0),coalesce(pctvalidated,0),coalesce(pctclassified,0) from projects p"
        if not current_user.has_role(database.AdministratorLabel):
            sql+=" Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
        sql+=" where p.projid!=%d order by title"%Prj.projid
        res = GetAll(sql) #,debug=True
        txt+="""<table class='table table-bordered table-hover'>
                <tr><th width=120>ID</td><th>Title</td><th width=100>Status</th><th width=100>Nbr Obj</th>
            <th width=100>% Validated</th><th width=100>% Classified</th></tr>"""
        for r in res:
            txt+="""<tr><td><a class="btn btn-primary" href='/prj/merge/{0}?src={1}'>Select</a> {1}</td>
            <td>{2}</td>
            <td>{3}</td>
            <td>{4:0.0f}</td>
            <td>{5:0.2f}</td>
            <td>{6:0.2f}</td>
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
        # garde le privilege le plus elevé des 2 projets
        ExecSQL("""UPDATE projectspriv ppdst
                  set privilege=case when 'Manage' in (ppsrc.privilege,ppdst.privilege) then 'Manage'
                        when 'Annotate' in (ppsrc.privilege,ppdst.privilege) then 'Annotate'
                        else 'View' end
                from projectspriv  ppsrc
                where ppsrc.projid={1} and ppdst.projid={0} and ppsrc.member=ppdst.member""".format(Prj.projid,PrjSrc.projid),debug=True)
        # Transfere les privilege depuis le projet source
        ExecSQL("""update projectspriv
                set projid={0}
                where projid={1} and member not in (select member from projectspriv where projid={0})""".format(Prj.projid,PrjSrc.projid))
        # Efface ceux qui etait des 2 cotés
        ExecSQL("delete from projectspriv where projid={0}".format(PrjSrc.projid))
        ExecSQL("delete from projects where projid={0}".format(PrjSrc.projid))
        txt+="<div class='alert alert-success' role='alert'>Fusion Done successfully</div>"
        txt+="<br><a class='btn btn-lg btn-primary' href='/prj/%s'>Back to target project</a>"%Prj.projid
        return PrintInCharte(txt)



