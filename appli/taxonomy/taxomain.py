from flask import render_template, g, flash,json,session,request
from flask_login import current_user
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv,cron,FormatError,FAIcon
import appli.project.main,appli.part.prj
from pathlib import Path
from flask_security import login_required,roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,math,collections,appli,psycopg2.extras,urllib.parse,time,requests,datetime,sys
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
import appli.project.sharedfilter as sharedfilter

######################################################################################################################

SQLTreeSelect="""concat(t14.name||'>',t13.name||'>',t12.name||'>',t11.name||'>',t10.name||'>',t9.name||'>',t8.name||'>',t7.name||'>',
     t6.name||'>',t5.name||'>',t4.name||'>',t3.name||'>',t2.name||'>',t1.name||'>',t.name) tree"""
SQLTreeJoin="""left join taxonomy t1 on t.parent_id=t1.id
      left join taxonomy t2 on t1.parent_id=t2.id
      left join taxonomy t3 on t2.parent_id=t3.id
      left join taxonomy t4 on t3.parent_id=t4.id
      left join taxonomy t5 on t4.parent_id=t5.id
      left join taxonomy t6 on t5.parent_id=t6.id
      left join taxonomy t7 on t6.parent_id=t7.id
      left join taxonomy t8 on t7.parent_id=t8.id
      left join taxonomy t9 on t8.parent_id=t9.id
      left join taxonomy t10 on t9.parent_id=t10.id
      left join taxonomy t11 on t10.parent_id=t11.id
      left join taxonomy t12 on t11.parent_id=t12.id
      left join taxonomy t13 on t12.parent_id=t13.id
      left join taxonomy t14 on t13.parent_id=t14.id"""


@app.route('/taxo/browse/',methods=['GET','POST'])
def routetaxobrowse():
    BackProjectBtn=''
    if gvp('updatestat')=='Y':
        # DoSyncStatUpdate()
        DoFullSync()
    if gvg('fromprj'):
        BackProjectBtn="<a href='/prj/{}' class='btn btn-default btn-primary'>{} Back to project</a> ".format(int(gvg('fromprj')),FAIcon('arrow-left'))
    if gvg('fromtask'):
        BackProjectBtn = "<a href='/Task/Question/{}' class='btn btn-default btn-primary'>{} Back to importation task</a> ".format(int(gvg('fromtask')), FAIcon('arrow-left'))


    if not (current_user.has_role(database.AdministratorLabel) or current_user.has_role(database.ProjectCreatorLabel) ) :
        # /prj/653
        txt= "You cannot create tanonomy category, you must request to your project manager (check project page)"
        if gvg('fromprj'):
            txt +="<br>"+BackProjectBtn

        return PrintInCharte(FormatError(txt,DoNotEscape=True))
    g.taxoserver_url=app.config.get('TAXOSERVER_URL')

    if current_user.has_role(database.AdministratorLabel):
        ExtraWehereClause=""
    else :
        ExtraWehereClause="and t.creator_email='{}'".format(current_user.email)
    lst=GetAll("""select t.id,t.parent_id,t.display_name as name,case t.taxotype when 'M' then 'Morpho' when 'P' then 'Phylo' else t.taxotype end taxotype,t.taxostatus,t.creator_email,t.id_source
      ,to_char(t.creation_datetime,'yyyy-mm-dd hh24:mi') creation_datetime,to_char(t.lastupdate_datetime,'yyyy-mm-dd hh24:mi') lastupdate_datetime,{}
    from taxonomy t
    {}
    where t.id_instance ={} {}
    order by case t.taxostatus when 'N' then 1 else 2 end,t.id
    LIMIT 400
    """.format(SQLTreeSelect,SQLTreeJoin,app.config.get('TAXOSERVER_INSTANCE_ID'),ExtraWehereClause))
    for lstitem in lst:
        # lstitem['tree']=PackTreeTxt(lstitem['tree']) #evite les problèmes de safe
        if lstitem['parent_id'] is None:
            lstitem['parent_id']=""

    # nbrtaxon=GetAll("select count(*) from taxonomy")[0][0]
    # return render_template('browsetaxo.html',lst=lst,nbrtaxon=nbrtaxon)

    return PrintInCharte(render_template('taxonomy/browse.html',lst=lst,BackProjectBtn=BackProjectBtn))


def request_withinstanceinfo(urlend,params,id_instance=1):
    params['id_instance']=app.config.get('TAXOSERVER_INSTANCE_ID')
    params['sharedsecret']=app.config.get('TAXOSERVER_SHARED_SECRET')
    params['ecotaxa_version']=appli.ecotaxa_version

    r=requests.post(app.config.get('TAXOSERVER_URL')+urlend,params)
    return r.json()


def DoSyncStatUpdate():
    Stats=database.GetAssoc2Col("""select id,sum(nbr) nbr from projects_taxo_stat group by id""")
    j = request_withinstanceinfo("/setstat/", {'data': json.dumps(Stats)})
    if j.get('msgversion','ok')!='ok':
        flash(j['msgversion'],'warning')
    if 'msg' in j:
        PDT = database.PersistantDataTable.query.first()
        if PDT is None: # si record manquant
            PDT = database.PersistantDataTable()
            PDT.id=1
            db.session.add(PDT)
        PDT.lastserverversioncheck_datetime = datetime.datetime.now()
        db.session.commit()
        return j['msg']
    return 'DoSyncStatUpdate : NetWork Error'


@app.route('/taxo/dosync',methods=['POST'])
@login_required
@roles_accepted(database.AdministratorLabel,database.ProjectCreatorLabel)
def routetaxodosync():
    return DoFullSync()

def DoFullSync():
    txt = ""
    try:
        UpdatableCols = ['parent_id', 'name', 'taxotype', 'taxostatus', 'id_source', 'id_instance', 'rename_to',
                         'display_name','source_desc','source_url','creation_datetime','creator_email']
        MaxUpdate=database.GetAll("select coalesce(max(lastupdate_datetime),to_timestamp('2000-01-01','YYYY-MM-DD')) lastupdate from taxonomy")
        MaxUpdateDate=MaxUpdate[0]['lastupdate']

        j = request_withinstanceinfo("/gettaxon/", {'filtertype': 'since', 'startdate': MaxUpdateDate})
        if 'msg' in j:
            return appli.ErrorFormat("Sync Error :"+j['msg'])
        NbrRow=len(j)
        NbrUpdate=NbrInsert=0
        txt+="Received {} rows<br>".format(NbrRow)
        if(NbrRow>0):
            txt += "Taxo 0 = {}<br>".format(j[0])
        for jtaxon in j:
            taxon=database.Taxonomy.query.filter_by(id=int(jtaxon['id'])).first()
            lastupdate_datetime=datetime.datetime.strptime(jtaxon['lastupdate_datetime'], '%Y-%m-%d %H:%M:%S')
            if taxon :
                if taxon.lastupdate_datetime==lastupdate_datetime:
                    continue #already up to date
                NbrUpdate += 1
            else:
                if ntcv(jtaxon['rename_to'])!='':
                    continue # don't insert taxon that should be renamed
                if ntcv(jtaxon['taxostatus']) =='D':
                    continue # don't insert taxon that are deprecated and planned to be deleted
                NbrInsert += 1
                taxon = database.Taxonomy()
                taxon.id=int(jtaxon['id'])
                db.session.add(taxon)

            for c in UpdatableCols:
                setattr(taxon,c,jtaxon[c])
            taxon.lastupdate_datetime=lastupdate_datetime
            db.session.commit()
        # Manage rename_to
        sqlbase="with taxorename as (select id,rename_to from taxonomy where rename_to is not null) "
        sql=sqlbase+"""select distinct projid from obj_head o join taxorename tr  on o.classif_id=tr.id """
        ProjetsToRecalc=database.GetAll(sql)
        sql=sqlbase+"""update obj_head o set classif_id=tr.rename_to 
              from taxorename tr  where o.classif_id=tr.id """
        NbrRenamedObjects=ExecSQL(sql)
        sql=sqlbase+"""update obj_head o set classif_auto_id=tr.rename_to 
              from taxorename tr  where o.classif_auto_id=tr.id """
        ExecSQL(sql)
        sql=sqlbase+"""update objectsclassifhisto o set classif_id=tr.rename_to 
              from taxorename tr  where o.classif_id=tr.id """
        ExecSQL(sql)
        # on efface les taxon qui doivent être renomé car ils l'ont normalement été
        sql="""delete from taxonomy where rename_to is not null """
        ExecSQL(sql)
        sql="""delete from taxonomy t where taxostatus='D' 
                  and not exists(select 1 from projects_taxo_stat where id=t.id) """
        ExecSQL(sql)
        # il faut recalculer projects_taxo_stat et part_histocat,part_histocat_lst pour ceux qui referencaient un
        # taxon renomé et donc disparu
        if NbrRenamedObjects>0:
            # cron.RefreshTaxoStat() operation trés longue (env 5 minutes en prod, il faut être plus selectif)
            # permet de recalculer projects_taxo_stat
            for Projet in ProjetsToRecalc:
                appli.project.main.RecalcProjectTaxoStat(Projet['projid'])
            #recalcul part_histocat,part_histocat_lst
            appli.part.prj.GlobalTaxoCompute()

        flash("Received {} rows,Insertion : {} Update :{}".format(NbrRow,NbrInsert,NbrUpdate),"success")
        if gvp('updatestat')=='Y':
            msg=DoSyncStatUpdate()
            flash("Taxon statistics update : "+msg,"success" if msg=='ok' else 'error')

        # txt="<script>location.reload(true);</script>" # non car ça reprovoque le post de l'arrivée initiale
        txt="<script>window.location=window.location;</script>"
    except:
        msg="Error while syncing {}".format(sys.exc_info())
        app.logger.error(msg)
        txt+=appli.ErrorFormat(msg)

    return txt

@app.route('/taxo/edit/<int:taxoid>')
@login_required
@roles_accepted(database.AdministratorLabel,database.ProjectCreatorLabel)
def routetaxoedit(taxoid):
    sql = """select t.*
            ,p.display_name parentname,to_char(t.creation_datetime,'YYYY-MM-DD HH24:MI:SS') creationdatetimefmt,{}
        from taxonomy t 
        {}
        left join taxonomy p on t.parent_id=p.id
        where t.id = %(id)s
        """.format(SQLTreeSelect, SQLTreeJoin)
    if taxoid>0:
        taxon= GetAll(sql,{'id':taxoid})[0]
    else:
        taxon={'id':0,'creator_email':current_user.email,'tree':''
            ,'creationdatetimefmt':datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
               }
    g.TaxoType=database.TaxoType
    g.taxoserver_url = app.config.get('TAXOSERVER_URL')
    return render_template('taxonomy/edit.html', taxon=taxon)

@app.route('/taxo/save/',methods=['POST'])
@login_required
@roles_accepted(database.AdministratorLabel,database.ProjectCreatorLabel)
def routetaxosave():
    txt=""
    try:
        params={}
        for c in ['parent_id', 'name', 'taxotype', 'source_desc','source_url','creation_datetime','creator_email']:
            params[c]=gvp(c)
        if int(gvp('id'))>0:
            params['id']=int(gvp('id'))
        params['taxostatus']='N'
        j = request_withinstanceinfo("/settaxon/", params)
        if j['msg']!='ok':
            return appli.ErrorFormat("settaxon Error :"+j['msg'])
        txt="""<script> DoSync(); At2PopupClose(0); </script>"""
        return txt
    except Exception as e:
        import traceback
        tb_list = traceback.format_tb(e.__traceback__)
        return appli.FormatError("Saving Error : {}\n{}",e,"__BR__".join(tb_list[::-1]))

@app.route('/taxo/del/',methods=['POST'])
@login_required
@roles_accepted(database.AdministratorLabel,database.ProjectCreatorLabel)
def routetaxodel():
    txt=""
    try:
        taxoid=int(gvp('id'))
        params = dict(id=taxoid)
        UsedTaxon=database.GetAll("""select 1 from taxonomy t where id=(%s)
          and (
              exists(select 1 from taxonomy p where p.parent_id=t.id)
          or  exists(select 1 from obj_head where classif_id=t.id) )
        """,[taxoid])
        if len(UsedTaxon)>0:
            return appli.ErrorFormat("This Taxon is used locally, you cannot remove it")
        database.ExecSQL("delete from taxonomy t where id=%s",[taxoid])

        j = request_withinstanceinfo("/deltaxon/", params)
        if j['msg']!='ok':
            return appli.ErrorFormat("deltaxon Error :"+j['msg'])
        txt="""<script> DoSync(); At2PopupClose(0); </script>"""
        return txt
    except Exception as e:
        import traceback
        tb_list = traceback.format_tb(e.__traceback__)
        return appli.FormatError("Saving Error : {}\n{}",e,"__BR__".join(tb_list[::-1]))
