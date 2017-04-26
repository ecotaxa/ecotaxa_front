from flask import render_template, g, flash,json,request
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField,SelectMultipleField
from flask_login import current_user
# from appli.part import part_main, drawchart,PartRedClassLimit
from appli.part import PartDetClassLimit,PartRedClassLimit,GetClassLimitTxt,CTDFixedCol

@app.route('/part/')
def indexUVP():
    class FiltForm(Form):
        # TODO ne pas afficher tous les projets en fonction des autorisations.
        # TODO gérer popup ajax sur les samples pour afficher quelques informations
        filt_proj = SelectMultipleField(choices=[['','']]+database.GetAll(
            "SELECT projid,concat(title,' (',cast(projid AS VARCHAR),')') FROM projects where projid in (select projid from part_projects) ORDER BY lower(title)"))
        filt_uproj = SelectMultipleField(choices=[['','']]+database.GetAll(
            "SELECT pprojid,concat(ptitle,' (',cast(pprojid AS VARCHAR),')') FROM part_projects ORDER BY lower(ptitle)"))
        gpr = SelectMultipleField(choices=[("cl%d"%i,"#/l %02d : "%i+GetClassLimitTxt(PartRedClassLimit,i)) for i in range (1,16)]
                                          +[("bv%d"%i,"BV %02d : "%i+GetClassLimitTxt(PartRedClassLimit,i)) for i in range (1,16)])
        gpd = SelectMultipleField(choices=[("cl%d"%i,"#/l %02d : "%i+GetClassLimitTxt(PartDetClassLimit,i)) for i in range (1,46)]
                                          +[("bv%d"%i,"BV %02d : "%i+GetClassLimitTxt(PartDetClassLimit,i)) for i in range (1,46)])
        ctd = SelectMultipleField(
            choices=[(k, v) for v,k in CTDFixedCol.items()])
        filt_proftype=SelectField(choices=[('','All'),('V','Vertical'),('H','Horizontal')])

    form=FiltForm()
    # data={}
    # data['filt_proj']=f()
    g.headcenter="<h1 style='text-align: center'><b>PARTICLE</b> module <span class='glyphicon glyphicon-info-sign'></span></h2>"
    return PrintInCharte(
        render_template('part/index.html', form=form))


def GetFilteredSamples(GetVisibleOnly=False,ForceVerticalIfNotSpecified=False):
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

    sql="select s.psampleid,s.latitude,s.longitude,"+sqlvisible+""" as visible
    from part_samples s
    JOIN part_projects up on s.pprojid=up.pprojid
    LEFT JOIN projects p on up.projid=p.projid """
    sql +=sqljoin
    sql += " where 1=1 "

    if gvg("MapN",'')!="" and gvg("MapW",'')!="" and gvg("MapE",'')!="" and gvg("MapS",'')!="":
        sql+=" and s.latitude between %(MapS)s and %(MapN)s   "
        sqlparam['MapN']=gvg("MapN")
        sqlparam['MapS']=gvg("MapS")
        sqlparam['MapW']=float(gvg("MapW"))
        sqlparam['MapE']=float(gvg("MapE"))
        if sqlparam['MapW']<sqlparam['MapE']:
            sql+=" and s.longitude between %(MapW)s and %(MapE)s  "
        else:
            sql += " and  (s.longitude between %(MapW)s and 180 or s.longitude between -180 and %(MapE)s   )"

    if gvg("filt_fromdate",'')!="":
        sql+=" and s.sampledate>= to_date(%(fromdate)s,'YYYY-MM-DD') "
        sqlparam['fromdate']=gvg("filt_fromdate")
    if gvg("filt_todate",'')!="":
        sql+=" and s.sampledate<= to_date(%(todate)s,'YYYY-MM-DD') "
        sqlparam['todate']=gvg("filt_todate")
    if gvg("filt_proj",'')!="":
        sql+=" and p.projid in (%s) "%(','.join([str(int(x)) for x in request.args.getlist("filt_proj")]))
    if gvg("filt_uproj",'')!="":
        sql+=" and up.pprojid in (%s) "%(','.join([str(int(x)) for x in request.args.getlist("filt_uproj")]))
    if gvg("filt_instrum",'')!="":
        sql+=" and lower(up.instrumtype)=lower(%(instrum)s) "
        sqlparam['instrum']=gvg("filt_instrum")
    if gvg("filt_proftype", '') != "":
        sql += " and organizedbydeepth = %s "%(True if gvg("filt_proftype", '' if ForceVerticalIfNotSpecified==False else 'V')=='V' else False)



    if GetVisibleOnly:
        sql="select * from ("+sql+") s where visible=true "
    sql+=""" order by s.psampleid     """
    return database.GetAll(sql,sqlparam)

@app.route('/part/searchsample')
def UVPsearchsample():
    # sql="""select s.psampleid,s.pprojid,s.latitude,s.longitude
    # from part_samples s
    # JOIN part_projects up on s.pprojid=up.pprojid
    # LEFT JOIN projects p on up.projid=p.projid
    # order by s.sampleid
    # """
    # samples=database.GetAll(sql)
    samples =GetFilteredSamples()
    res=[]
    for s in samples:
        r={'id':s['psampleid'],'lat':s['latitude'],'long':s['longitude'],'visible':True}
        res.append(r)
    return json.dumps(res)



@app.route('/part/getsamplepopover/<int:psampleid>')
def UVPgetsamplepopover(psampleid):
    sql="""select s.psampleid,s.profileid,p.ptitle,ep.title,p.cruise,p.ship ,p.projid,p.pprojid
      from part_samples s
      LEFT JOIN part_projects p on s.pprojid=p.pprojid
      left join projects ep on p.projid = ep.projid
      where s.psampleid=%(psampleid)s
      """
    data=database.GetAll(sql,{'psampleid':psampleid})[0]
    txt="""ID : {psampleid}<br>
    Profile ID : {profileid}<br>
    Project : {ptitle} ({pprojid})<br>
    Ship : {ship}<br>
    Cruise : {cruise}<br>
    Ecotaxa Project : {title} ({projid})
    """.format(**data)
    return txt