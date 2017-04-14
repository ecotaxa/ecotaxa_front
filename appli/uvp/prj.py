from flask import render_template, g, flash,json
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from flask_login import current_user
from flask import render_template,  flash,request,g
import appli,logging,appli.uvp.sample_import as sample_import
import appli.uvp.database as uvpdatabase
from flask_security import login_required

@app.route('/uvp/prj/')
def UVP_prj():
    params={}
    sql="""select uprojid,utitle,up.ownerid,u.name,u.email,rawfolder,instrumtype,ep.title
            from uvp_projects up
            left JOIN projects ep on up.projid=ep.projid
            LEFT JOIN users u on ownerid=u.id
          """
    # if not current_user.has_role(database.AdministratorLabel):
    #     sql+="  Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
    # sql += " where 1=1 "
    # if gvg('filt_title','')!='':
    #     sql +=" and (  title ilike '%%'||%(title)s ||'%%' or to_char(p.projid,'999999') like '%%'||%(title)s ) "
    #     params['title']=gvg('filt_title')
    # if gvg('filt_instrum','')!='':
    #     sql +=" and p.projid in (select distinct projid from acquisitions where instrument ilike '%%'||%(filt_instrum)s ||'%%' ) "
    #     params['filt_instrum']=gvg('filt_instrum')
    # if gvg('filt_subset', '') == 'Y':
    #     sql += " and not title ilike '%%subset%%'  "
    sql+=" order by lower(ep.title),lower(utitle)"
    res = GetAll(sql,params) #,debug=True
    app.logger.info("res=",res)
    CanCreate=False
    if current_user.has_role(database.AdministratorLabel):
        CanCreate=True
    if getattr(current_user,'id',None) is not None: # correspond à anonymous
        if database.GetAll("select count(*) nbr from projectspriv where privilege='Manage' and member=%(id)s",{'id':current_user.id})[0]['nbr']>0:
            CanCreate = True

    return PrintInCharte(
        render_template('uvp/list.html',PrjList=res,CanCreate=CanCreate,AppManagerMailto=appli.GetAppManagerMailto()
                        , filt_title=gvg('filt_title'),filt_subset=gvg('filt_subset'),filt_instrum=gvg('filt_instrum')  ))

@app.route('/uvp/prj/<int:PrjId>')
@login_required
def UVP_prj_main(PrjId):
    Prj = uvpdatabase.uvp_projects.query.filter_by(uprojid=PrjId).first()
    g.headcenter="<h4>UVP Project %s : %s</h4><a href='/uvp/'>UVP Home</a>"%(Prj.projid,Prj.utitle)
    # TODO securité
    dbsample = database.GetAll("""select profileid,usampleid,filename,stationid,firstimage,lastimg,lastimgused,sampleid
          ,histobrutavailable,comment,daterecalculhistotaxo,ctd_import_datetime
          ,(select count(*) from uvp_histopart_det where usampleid=s.usampleid) nbrlinedet
          ,(select count(*) from uvp_histopart_reduit where usampleid=s.usampleid) nbrlinereduit
          ,(select count(*) from uvp_histocat where usampleid=s.usampleid) nbrlinetaxo
          ,(select count(*) from uvp_ctd where usampleid=s.usampleid) nbrlinectd
          from uvp_samples s
          where uprojid=%s""" % (PrjId))

    return PrintInCharte(
        render_template('uvp/prj_index.html',PrjId=PrjId,dbsample=dbsample,Prj=Prj ))

@app.route('/uvp/prjcalc/<int:PrjId>',methods=['post'])
@login_required
def UVP_prjcalc(PrjId):
    Prj = uvpdatabase.uvp_projects.query.filter_by(uprojid=PrjId).first()
    # TODO securité
    txt=""
    CheckedSampleList=[]
    for f in request.form:
        if f[0:2] == "s_" and request.form.get(f)=='Y':
            CheckedSampleList.append(int(f[2:]))

    app.logger.info("request.form=%s", request.form)
    app.logger.info("CheckedSampleList=%s", CheckedSampleList)
    app.logger.info("dohistodet=%s,domatchecotaxa=%s,dohistotaxo=%s", gvp('dohistodet'), gvp('domatchecotaxa'), gvp('dohistotaxo'))
    dbsample = database.GetAll("""select profileid,usampleid,filename,sampleid,histobrutavailable
          ,(select count(*) from uvp_histopart_det where usampleid=s.usampleid) nbrlinedet
          from uvp_samples s
          where uprojid=%s and usampleid = any (%s)""" , (PrjId,CheckedSampleList))
    for S in dbsample:
        prefix="<br>{profileid} :".format(**S)
        if gvp('dohistodet')=='Y':
            if S['histobrutavailable']:
                sample_import.GenerateParticleHistogram(S['usampleid'])
                txt+=prefix+" Detailled & reduced Histogram computed"
            else:
                txt += prefix + " <span style='color: red;'>Raw Histogram can't be computer without Raw histogram</span>"
        if gvp('dohistored')=='Y':
            if S['histobrutavailable']:
                sample_import.GenerateReducedParticleHistogram(S['usampleid'])
                txt+=prefix+" reduced Histogram computed"
            else:
                txt += prefix + " <span style='color: red;'>Raw Histogram can't be computer without Raw histogram</span>"
        if gvp('domatchecotaxa') == 'Y':
            if Prj.projid is not None:
                ecosample=database.GetAll("""select sampleid from samples where projid=%s and orig_id=%s""",(int(Prj.projid),S['profileid']))
                if len(ecosample)==1:
                    database.ExecSQL("update uvp_samples set sampleid=%s where usampleid=%s",(ecosample[0]['sampleid'],S['usampleid']))
                    txt += prefix + " Matched"
                else:
                    txt += prefix + " <span style='color: orange;'>No match found in Ecotaxa</span>"
            else:
                txt += prefix + " <span style='color: red;'>Ecotaxa sample matching impossible if UVP project not linked to an Ecotaxa project</span>"
        if gvp('dohistotaxo') == 'Y':
            if S['sampleid']:
                sample_import.GenerateTaxonomyHistogram(S['usampleid'])
                txt += prefix + " Taxonomy Histogram computed"
            else:
                txt += prefix + " <span style='color: red;'>Taxonomy Histogram can't be computer without link with Ecotaxa sample</span>"
    if gvp('doctdimport') == 'Y':
        if sample_import.ImportCTD(S['usampleid']):
            txt += prefix + " CTD imported"
        else:
            txt += prefix + " <span style='color: red;'>CTD No file</span>"
    #
    # txt+="CheckedSampleList=%s"%(CheckedSampleList)
    # txt+="<br>dbsample = %s"%(dbsample)
    txt += "<br><br><a href=/uvp/prj/%s class='btn btn-primary'><span class='glyphicon glyphicon-arrow-left'></span> Back to project samples list</a>"%PrjId
    return PrintInCharte(txt)
