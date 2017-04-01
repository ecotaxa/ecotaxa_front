from flask import render_template, g, flash,json
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from flask_login import current_user
import appli
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
    if database.GetAll("select count(*) nbr from projectspriv where privilege='Manage' and member=%(id)s",{'id':current_user.id})[0]['nbr']>0:
        CanCreate = True

    return PrintInCharte(
        render_template('uvp/list.html',PrjList=res,CanCreate=CanCreate,AppManagerMailto=appli.GetAppManagerMailto()
                        , filt_title=gvg('filt_title'),filt_subset=gvg('filt_subset'),filt_instrum=gvg('filt_instrum')  ))

@app.route('/uvp/prj/<int:PrjId>')
@login_required
def UVP_prj_main(PrjId):
    return PrintInCharte(
        render_template('uvp/prj_index.html',PrjId=PrjId ))
