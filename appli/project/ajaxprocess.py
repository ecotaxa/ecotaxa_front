from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections,psycopg2.extras,sys
from appli.database import GetAll,GetClassifQualClass,db,ExecSQL

@app.route('/prj/ManualClassif/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjManualClassif(PrjId):
    request.form  # Force la lecture des données POST sinon il y a une erreur 504
    Changement=[]
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if not Prj.CheckRight(1): # Level 0 = Read, 1 = Annotate, 2 = Admin
        return '<span class="label label-danger">You cannot Annotate this project</span>'

    changes={k[8:-1]:v for k,v in request.form.items() if k[0:7]=="changes"}
    if len(changes)==0:
        return '<span class="label label-warning">No pending change to update</span>'

    sql="""select o.objid,o.classif_auto_id,o.classif_auto_when,o.classif_auto_score,o.classif_id,o.classif_qual,o.classif_when,o.classif_who
          from obj_head o
          where o.objid in ("""+",".join(changes.keys())+")"
    prev={r['objid']:r for r in GetAll(sql,debug=False)}
    sql="update obj_head set classif_id=%(classif_id)s,classif_qual=%(classif_qual)s,classif_who=%(classif_who)s,classif_when=now() where objid=%(objid)s "
    # sqli="""INSERT INTO objectsclassifhisto (objid, classif_date, classif_type, classif_id, classif_qual, classif_who)
    #         VALUES (%(objid)s,%(classif_when)s,'M',%(classif_id)s,%(classif_qual)s,%(classif_who)s )"""
    # Traitement global de l'historisation afin de réduire les commandes SQL + test qu'il n'y a pas de doublons
    sqli="""INSERT INTO objectsclassifhisto(objid, classif_date, classif_type, classif_id, classif_qual, classif_who, classif_score)
            SELECT  objid, classif_when, 'M' classif_type, classif_id, classif_qual, classif_who, null classif_score
            from obj_head oh
            where objid= any(%s)
            and classif_when is not null
            and not exists(select 1 from objectsclassifhisto och where oh.objid=och.objid and oh.classif_when=och.classif_date )"""
    try:
        params=[[int(x) for x in changes.keys()] ]
        ExecSQL(sqli, params, True)
    except:
        app.logger.warning("Unable to add historical information, non-blocking %s" % (sys.exc_info(),))
    BatchParam=[]
    for k,v in changes.items():
        ki=int(k)
        if v=="-1" or v=="" : # utilisé dans validate all
            v=prev[ki]['classif_id']
        if prev[ki]['classif_qual']!=gvp('qual') or prev[ki]['classif_who']!=current_user.id or prev[ki]['classif_id']!=int(v):
            # il y a eu au moins un changement
            params={'objid':k,'classif_id':v,'classif_who':current_user.id,'classif_qual':gvp('qual')}
            BatchParam.append(params)
            # ExecSQL(sql,params,False)
            Changement.append({'prev_id':prev[ki]['classif_id'],'prev_qual':prev[ki]['classif_qual']
                                  ,'id':int(v),'qual':gvp('qual')})
            # params={'objid':k,'classif_id':prev[ki]['classif_id'],'classif_who':prev[ki]['classif_who']
            #     ,'classif_qual':prev[ki]['classif_qual'],'classif_when':prev[ki]['classif_when']}
            # try:
            #     if ntcv(params['classif_when']) !="" : # si pas de date, violation PK
            #         ExecSQL(sqli,params,True)
            # except:
            #     app.logger.warning("Unable to add historical information, non-blocking %s"%(prev,))
            if prev[ki]['classif_id']!=int(v): # il y a eu un changement de classif on maintient la liste des classifs MRU
                with app.MRUClassif_lock:
                    tbl=app.MRUClassif.get(current_user.id,[])
                    for i,t in enumerate(tbl):
                        if t["id"]==int(v):
                            if i>0: # on met cet item au début pour gérer un MRU
                                tbl=[t]+tbl[0:i]+tbl[i+1:]
                            break
                    else: # si pas trouvé dans la liste des MRU on l'ajoute au début si on trouve bien son nom dans la taxo
                        Taxon=GetAll("""select tf.name||case when p1.name is not null and tf.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name
                            from taxonomy tf
                             left join taxonomy p1 on tf.parent_id=p1.id
                            where tf.id=%(id)s """,{"id":v})
                        if len(Taxon)==1:
                            Taxon=Taxon[0].get('name', "")
                            tbl.insert(0,{"id": int(v), "pr": 0, "text": Taxon})
                            if len(tbl)>10:
                                tbl=tbl[0:10]
                    app.MRUClassif[current_user.id]=tbl
    if len(BatchParam)>0:
        upcur = db.engine.raw_connection().cursor()
        try:
            upcur.executemany(sql, BatchParam)
            upcur.connection.commit()
        except:
            upcur.close()
            app.logger.warning("Unable to save changes %s" % (sys.exc_info(),))
            return '<span class="label label-danger">Unable to save changes</span>'
        upcur.close()

    app.logger.info("Changement = %s",Changement)
    # applique les changements dans projects_taxo_stat
    Empty = {'n': 0, 'V': 0, 'P': 0, 'D': 0}
    Changes = {}
    for c in Changement:
        if c['prev_id'] is None: c['prev_id'] = -1
        if c['prev_id'] not in Changes: Changes[c['prev_id']] = Empty.copy()
        if c['id'] is None: c['id'] = -1
        if c['id'] not in Changes: Changes[c['id']] = Empty.copy()
        Changes[c['prev_id']]['n'] -= 1
        Changes[c['id']]['n'] += 1
        if c['prev_qual'] in ('V', 'P', 'D'):
            Changes[c['prev_id']][c['prev_qual']] -= 1
        if c['qual'] in ('V', 'P', 'D'):
            Changes[c['id']][c['qual']] += 1
    LstIdInDB=[x[0] for x in database.GetAll("select id from projects_taxo_stat where projid=%s",[PrjId])]
    for k,c in Changes.items():
        if k not in LstIdInDB:
            database.ExecSQL("insert into projects_taxo_stat(projid, id, nbr, nbr_v, nbr_d, nbr_p) values (%s,%s,0,0,0,0)",[PrjId,k])
        sqlparam={'projid':PrjId,'id':k,'n':c['n'],'v':c['V'],'d':c['D'],'p':c['P']}
        database.ExecSQL("""update projects_taxo_stat set 
                              nbr=nbr+%(n)s, nbr_v=nbr_v+%(v)s, nbr_d=nbr_d+%(d)s, nbr_p=nbr_p+%(p)s 
                              where projid=%(projid)s and id=%(id)s""",sqlparam)

    return '<span class="label label-success">Database update Successfull</span>'


@app.route('/prj/UpdateComment/<int:ObjId>', methods=['GET', 'POST'])
@login_required
def PrjUpdateComment(ObjId):
    Obj=database.Objects.query.filter_by(objid=ObjId).first()
    if Obj is None:
        return "Object doesnt exists"
    Prj=database.Projects.query.filter_by(projid=Obj.projid).first()
    if not Prj.CheckRight(1): # Level 0 = Read, 1 = Annotate, 2 = Admin
        return "You cannot Annotate this project"

    Obj.complement_info=gvp('comment')
    db.session.commit()

    return '<span class="label label-success">Database update Successfull</span>'

