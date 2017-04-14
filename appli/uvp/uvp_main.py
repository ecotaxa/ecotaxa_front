from flask import render_template, g, flash,json
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField
from flask_login import current_user

@app.route('/uvp/')
def indexUVP():
    class FiltForm(Form):
        # TODO passer en multiselect pour les projets
        # TODO ne pas afficher tous les projets en fonction des autorisations.
        # TODO gérer popup ajax sur les samples pour afficher quelques informations
        filt_proj = SelectField(choices=[['','']]+database.GetAll(
            "SELECT projid,concat(title,' (',cast(projid AS VARCHAR),')') FROM projects ORDER BY lower(title)"))
        filt_uproj = SelectField(choices=[['','']]+database.GetAll(
            "SELECT uprojid,concat(utitle,' (',cast(uprojid AS VARCHAR),')') FROM uvp_projects ORDER BY lower(utitle)"))

    form=FiltForm()
    # data={}
    # data['filt_proj']=f()
    return PrintInCharte(
        render_template('uvp/index.html',form=form ))


def GetFilteredSamples(GetVisibleOnly=False):
    sqljoin=""
    sqlparam={}
    if current_user.has_role(database.AdministratorLabel):
        sqlvisible = "true"
    else:
        sqlvisible = "case when p.visible "
        if current_user.is_authenticated:
            sqlvisible += " or pp.member is not null "
            sqljoin ="  left Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
        sqlvisible += " then true end "

    sql="select s.usampleid,s.latitude,s.longitude,"+sqlvisible+""" as visible
    from uvp_samples s
    JOIN uvp_projects up on s.uprojid=up.uprojid
    LEFT JOIN projects p on up.projid=p.projid """
    sql +=sqljoin
    sql += " where 1=1 "

    if gvg("MapN",'')!="" and gvg("MapW",'')!="" and gvg("MapE",'')!="" and gvg("MapS",'')!="":
        sql+=" and s.latitude between %(MapS)s and %(MapN)s and s.longitude between %(MapW)s and %(MapE)s  "
        sqlparam['MapN']=gvg("MapN")
        sqlparam['MapW']=gvg("MapW")
        sqlparam['MapE']=gvg("MapE")
        sqlparam['MapS']=gvg("MapS")
    if gvg("filt_fromdate",'')!="":
        sql+=" and s.sampledate>= to_date(%(fromdate)s,'YYYY-MM-DD') "
        sqlparam['fromdate']=gvg("filt_fromdate")
    if gvg("filt_todate",'')!="":
        sql+=" and s.sampledate<= to_date(%(todate)s,'YYYY-MM-DD') "
        sqlparam['todate']=gvg("filt_todate")
    if gvg("filt_proj",'')!="":
        sql+=" and p.projid=%(proj)s "
        sqlparam['proj']=gvg("filt_proj")
    if gvg("filt_uproj",'')!="":
        sql+=" and up.uprojid=%(uproj)s "
        sqlparam['uproj']=gvg("filt_uproj")
    if gvg("filt_instrum",'')!="":
        sql+=" and lower(up.instrumtype)=lower(%(instrum)s) "
        sqlparam['instrum']=gvg("filt_instrum")

    if GetVisibleOnly:
        sql="select * from ("+sql+") s where visible=true "
    sql+=""" order by s.usampleid     """
    return database.GetAll(sql,sqlparam)

@app.route('/uvp/searchsample')
def UVPsearchsample():
    # sql="""select s.usampleid,s.uprojid,s.latitude,s.longitude
    # from uvp_samples s
    # JOIN uvp_projects up on s.uprojid=up.uprojid
    # LEFT JOIN projects p on up.projid=p.projid
    # order by s.sampleid
    # """
    # samples=database.GetAll(sql)
    samples =GetFilteredSamples()
    res=[]
    for s in samples:
        r={'id':s['usampleid'],'lat':s['latitude'],'long':s['longitude'],'visible':True}
        res.append(r)
    return json.dumps(res)
