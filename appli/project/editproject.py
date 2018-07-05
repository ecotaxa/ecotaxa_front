from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc2Col

######################################################################################################################
@app.route('/prj/edit/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEdit(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title)
    if Prj is None:
        flash("Project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot edit settings for this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")

    if gvp('save')=="Y":
        for f in request.form:
            if f in dir(Prj):
                setattr(Prj,f,gvp(f))
        Prj.visible=gvp('visible',False)
        # print(request.form)
        for m in Prj.projmembers:
            if gvp('priv_%s_delete'%m.id)=='Y':
                db.session.delete(m)
            elif gvp('priv_%s_member'%m.id)!='': # si pas delete c'est update
                m.member=int(gvp('priv_%s_member'%m.id))
                m.privilege=gvp('priv_%s_privilege'%m.id)
        if gvp('priv_new_member')!='':
            new=database.ProjectsPriv(member=int(gvp('priv_new_member')),privilege=gvp('priv_new_privilege'),projid=PrjId)
            db.session.add(new)
        try:
            db.session.commit()
            flash("Project settings Saved successfuly","success")
        except Exception as E:
            flash("Database exception : %s"%E,"error")
            db.session.rollback()

    if Prj.initclassiflist is None:
        lst=[]
    else:
        lst=[int(x) for x in Prj.initclassiflist.split(",") if x.isdigit()]

    g.predeftaxo=GetAll("""select t.id,concat(t.name,' (',t2.name,')') as name
        from taxonomy t
         left join taxonomy t2 on t.parent_id=t2.id
        where t.id= any(%s) order by name """,(lst,))
    g.users=GetAssoc2Col("select id,name from users order by lower(name)",dicttype=collections.OrderedDict)
    g.maplist=['objtime','depth_min','depth_max']+sorted(DecodeEqualList(Prj.mappingobj).values())
    return render_template('project/editproject.html',data=Prj)

######################################################################################################################
@app.route('/prj/editpriv/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditPriv(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title)
    if Prj is None:
        flash("Project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot edit settings for this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")

    if gvp('save')=="Y":
        # print(request.form)
        for m in Prj.projmembers:
            if gvp('priv_%s_delete'%m.id)=='Y':
                db.session.delete(m)
            elif gvp('priv_%s_member'%m.id)!='': # si pas delete c'est update
                m.member=int(gvp('priv_%s_member'%m.id))
                m.privilege=gvp('priv_%s_privilege'%m.id)
        if gvp('priv_new_member')!='':
            new=database.ProjectsPriv(member=int(gvp('priv_new_member')),privilege=gvp('priv_new_privilege'),projid=PrjId)
            db.session.add(new)
        try:
            db.session.commit()
            flash("Project settings Saved successfuly","success")
        except Exception as E:
            flash("Database exception : %s"%E,"error")
            db.session.rollback()

    g.users=GetAssoc2Col("select id,name from users order by lower(name)",dicttype=collections.OrderedDict)
    return render_template('project/editprojectpriv.html',data=Prj)

