from flask import render_template, g, flash,json
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from flask_login import current_user
from flask import render_template,  flash,request,g
import appli,logging,appli.part.uvp_sample_import as uvp_sample_import
import appli.part.common_sample_import as common_import
import appli.part.lisst_sample_import as lisst_sample_import
import appli.part.database as partdatabase
import appli.part.sampleedit as sampleedit
from flask_security import login_required

@app.route('/part/prj/')
def part_prj():
    params={}
    sql="""select pprojid,ptitle,up.ownerid,u.name,u.email,rawfolder,instrumtype,ep.title
            ,(select count(*) from part_samples where pprojid=up.pprojid) samplecount
            from part_projects up
            left JOIN projects ep on up.projid=ep.projid
            LEFT JOIN users u on ownerid=u.id
          """
    # if not current_user.has_role(database.AdministratorLabel):
    #     sql+="  Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
    sql += " where 1=1 "
    if gvg('filt_title','')!='':
        sql +=" and (  up.ptitle ilike '%%'||%(title)s ||'%%' or to_char(up.pprojid,'999999') like '%%'||%(title)s or ep.title ilike '%%'||%(title)s ||'%%' or to_char(ep.projid,'999999') like '%%'||%(title)s) "
        params['title']=gvg('filt_title')
    if gvg('filt_instrum','')!='':
        sql +=" and up.instrumtype ilike '%%'||%(filt_instrum)s ||'%%'  "
        params['filt_instrum']=gvg('filt_instrum')
    sql+=" order by lower(ep.title),lower(ptitle)"
    res = GetAll(sql,params) #,debug=True
    app.logger.info("res=%s",res)
    CanCreate=False
    if current_user.has_role(database.AdministratorLabel):
        CanCreate=True
    if getattr(current_user,'id',None) is not None: # correspond à anonymous
        if database.GetAll("select count(*) nbr from projectspriv where privilege='Manage' and member=%(id)s",{'id':current_user.id})[0]['nbr']>0:
            CanCreate = True
    g.headcenter = "<h4>Particle Projects management</h4><a href='/part/'>Particle Module Home</a>"
    return PrintInCharte(
        render_template('part/list.html', PrjList=res, CanCreate=CanCreate, AppManagerMailto=appli.GetAppManagerMailto()
                        , filt_title=gvg('filt_title'), filt_subset=gvg('filt_subset'), filt_instrum=gvg('filt_instrum')))

@app.route('/part/prj/<int:PrjId>')
@login_required
def part_prj_main(PrjId):
    Prj = partdatabase.part_projects.query.filter_by(pprojid=PrjId).first()
    g.headcenter="<h4>Particle Project %s : %s</h4><a href='/part/'>Particle Module Home</a>"%(Prj.projid,Prj.ptitle)
    # TODO securité
    dbsample = database.GetAll("""select profileid,psampleid,filename,stationid,firstimage,lastimg,lastimgused,sampleid
          ,histobrutavailable,comment,daterecalculhistotaxo,ctd_import_datetime
          ,(select count(*) from part_histopart_det where psampleid=s.psampleid) nbrlinedet
          ,(select count(*) from part_histopart_reduit where psampleid=s.psampleid) nbrlinereduit
          ,(select count(*) from part_histocat where psampleid=s.psampleid) nbrlinetaxo
          ,(select count(*) from part_ctd where psampleid=s.psampleid) nbrlinectd
          from part_samples s
          where pprojid=%s""" % (PrjId))

    return PrintInCharte(
        render_template('part/prj_index.html', PrjId=PrjId, dbsample=dbsample, Prj=Prj))

@app.route('/part/prjcalc/<int:PrjId>',methods=['post'])
@login_required
def part_prjcalc(PrjId):
    Prj = partdatabase.part_projects.query.filter_by(pprojid=PrjId).first()
    # TODO securité
    txt=""
    CheckedSampleList=[]
    for f in request.form:
        if f[0:2] == "s_" and request.form.get(f)=='Y':
            CheckedSampleList.append(int(f[2:]))

    app.logger.info("request.form=%s", request.form)
    app.logger.info("CheckedSampleList=%s", CheckedSampleList)
    app.logger.info("dohistodet=%s,domatchecotaxa=%s,dohistotaxo=%s", gvp('dohistodet'), gvp('domatchecotaxa'), gvp('dohistotaxo'))
    dbsample = database.GetAll("""select profileid,psampleid,filename,sampleid,histobrutavailable
          ,(select count(*) from part_histopart_det where psampleid=s.psampleid) nbrlinedet
          from part_samples s
          where pprojid=%s and psampleid = any (%s)""" , (PrjId,CheckedSampleList))
    for S in dbsample:
        prefix="<br>{profileid} :".format(**S)
        if gvp('delete') == 'Y':
            sampleedit.delete_sample(S['psampleid'])
            txt += prefix + " deleted"
            continue
        if gvp('dohistodet')=='Y':
            if Prj.instrumtype=='uvp5' and S['histobrutavailable']:
                uvp_sample_import.GenerateParticleHistogram(S['psampleid'])
                txt+=prefix+" Detailled & reduced Histogram computed"
            elif Prj.instrumtype == 'lisst':
                lisst_sample_import.GenerateParticleHistogram(S['psampleid'])
                txt += prefix + " Detailled & reduced Histogram computed"
            else:
                txt += prefix + " <span style='color: red;'>Raw Histogram can't be computer without Raw histogram</span>"
        if gvp('dohistored')=='Y':
            if S['histobrutavailable']:
                uvp_sample_import.GenerateReducedParticleHistogram(S['psampleid'])
                txt+=prefix+" reduced Histogram computed"
            else:
                txt += prefix + " <span style='color: red;'>Raw Histogram can't be computer without Raw histogram</span>"
        if gvp('domatchecotaxa') == 'Y':
            if Prj.projid is not None:
                ecosample=database.GetAll("""select sampleid from samples where projid=%s and orig_id=%s""",(int(Prj.projid),S['profileid']))
                if len(ecosample)==1:
                    database.ExecSQL("update part_samples set sampleid=%s where psampleid=%s",(ecosample[0]['sampleid'],S['psampleid']))
                    txt += prefix + " Matched"
                else:
                    txt += prefix + " <span style='color: orange;'>No match found in Ecotaxa</span>"
            else:
                txt += prefix + " <span style='color: red;'>Ecotaxa sample matching impossible if Particle project not linked to an Ecotaxa project</span>"
        if gvp('dohistotaxo') == 'Y':
            # if S['sampleid']:
            try:
                uvp_sample_import.GenerateTaxonomyHistogram(S['psampleid'])
                txt += prefix + " Taxonomy Histogram computed"
            # else:
            except Exception as E:
                txt += prefix + " <span style='color: red;'>Taxonomy Histogram can't be computed : %s </span>"%(E)
        if gvp('doctdimport') == 'Y':
            if common_import.ImportCTD(S['psampleid'],current_user.name,current_user.email):
                txt += prefix + " CTD imported"
            else:
                txt += prefix + " <span style='color: red;'>CTD No file</span>"
    #
    # txt+="CheckedSampleList=%s"%(CheckedSampleList)
    # txt+="<br>dbsample = %s"%(dbsample)
    txt += "<br><br><a href=/part/prj/%s class='btn btn-primary'><span class='glyphicon glyphicon-arrow-left'></span> Back to project samples list</a>"%PrjId
    return PrintInCharte(txt)
