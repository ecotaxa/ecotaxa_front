from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,XSSEscape,TempTaskDir,ntcv
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli,psycopg2.extras
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc2Col

######################################################################################################################
@app.route('/prj/edit/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEdit(PrjId):
    g.useselect4 = True
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,XSSEscape(Prj.title))
    if Prj is None:
        flash("Project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot edit settings for this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")

    if gvp('save')=="Y":
        PreviousCNN=Prj.cnn_network_id
        for f in request.form:
            if f in dir(Prj):
                setattr(Prj,f,gvp(f))
        if PreviousCNN!=Prj.cnn_network_id:
            database.ExecSQL("delete from obj_cnn_features where objcnnid in (select objid from obj_head where projid=%s)",[PrjId])
            flash("SCN features erased", "success")
        Prj.visible=True if gvp('visible')=='Y' else False
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

    g.predeftaxo=GetAll("""select t.id,t.display_name as name
        from taxonomy t
        left join taxonomy t2 on t.parent_id=t2.id
        where t.id= any(%s) order by upper(t.display_name) """,(lst,))
    g.users=GetAssoc2Col("select id,name from users order by lower(name)",dicttype=collections.OrderedDict)
    g.maplist=['objtime','objdate','latitude','longitude','depth_min','depth_max']+sorted(DecodeEqualList(Prj.mappingobj).values())
    g.scn=GetSCNNetworks()
    return render_template('project/editproject.html',data=Prj)
######################################################################################################################
@app.route('/prj/popupeditpreset/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def Prjpopupeditpreset(PrjId):
    sql="""select p.projid,title,initclassiflist
                  ,(select string_agg(pts.id::varchar,',') objtaxon from projects_taxo_stat pts where pts.projid=p.projid)
            from projects p
            """
    if not current_user.has_role(database.AdministratorLabel):
        sql += "  Join projectspriv pp on p.projid = pp.projid and pp.member=%d" % (current_user.id,)
    sql += " order by upper(title) "
    Prj=GetAll(sql,cursor_factory=psycopg2.extras.RealDictCursor)
    # Prj2=Prj[:]
    # for i in range(200):Prj.extend(Prj2) # for test on bigger list
    TaxonList={-1}
    for P in Prj:
        lst=ntcv(P['initclassiflist'])+","+ntcv(P['objtaxon'])
        for t in lst.split(','):
            if t.isdecimal():
                TaxonList.add(int(t))
    # txt=",".join((str(x) for x in TaxonList))
    TaxoMap=GetAssoc2Col("select id,display_name  from taxonomy where id = any (%s)",[ [x for x in TaxonList] ])
    # txt = str(TaxoMap)
    txt =""
    for P in Prj:
        result=[]
        initclassiflist={int(x.strip()) for x in ntcv(P['initclassiflist']).split(',') if x.isdecimal()}
        objtaxon={int(x.strip()) for x in ntcv(P['objtaxon']).split(',') if x.isdecimal()}
        objtaxon.difference_update(initclassiflist)
        for t in initclassiflist:
            resolved=TaxoMap.get(int(t),None)
            if resolved:
                result.append(resolved)
        P['presetids']=",".join((str(x) for x in initclassiflist))
        P['preset']=", ".join(sorted(result))
        result=[]
        for t in objtaxon:
            resolved=TaxoMap.get(int(t),None)
            if resolved:
                result.append(resolved)
        P['objtaxonnotinpreset']=", ".join(sorted(result))
        P['objtaxonids'] = ",".join((str(x) for x in objtaxon))

    # construction de la liste distincte tous les taxon
    return render_template('project/popupeditpreset.html', Prj=Prj,txt=txt)
######################################################################################################################
def GetSCNNetworks():
    Models = {}
    ModelFolder = (Path(TempTaskDir) / "../SCN_networks")
    ModelFolder = Path(os.path.normpath(ModelFolder.as_posix()))
    if ModelFolder.exists():
        ModelFolder=ModelFolder.resolve()
        for dir in ModelFolder.glob("*"):
            if dir.is_dir() and (dir / "meta.json").is_file():
                Models[dir.name] = json.load((dir / "meta.json").open("r"))
                # Models[dir.name] = json.load((dir / "meta.json").open("r")).get('name',dir.name)
    return Models


######################################################################################################################
@app.route('/prj/editpriv/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditPriv(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,XSSEscape(Prj.title))
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
            new=database.ProjectsPriv(member=int(gvp('priv_new_member')),
                                      privilege=gvp('priv_new_privilege'),
                                      projid=PrjId)
            db.session.add(new)
        try:
            db.session.commit()
            flash("Project settings Saved successfuly","success")
        except Exception as E:
            flash("Database exception : %s"%E,"error")
            db.session.rollback()

    g.users=GetAssoc2Col("select id,name from users order by lower(name)",dicttype=collections.OrderedDict)
    return render_template('project/editprojectpriv.html',data=Prj)

