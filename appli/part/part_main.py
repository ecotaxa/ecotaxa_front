from flask import render_template, g, flash,json,request
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField,SelectMultipleField
from flask_login import current_user
# from appli.part import part_main, drawchart,PartRedClassLimit
from appli.part import PartDetClassLimit,PartRedClassLimit,GetClassLimitTxt,CTDFixedCol
import operator

@app.route('/part/')
def indexPart():
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
            choices=sorted([(k, v) for v,k in CTDFixedCol.items()], key=operator.itemgetter(1)))
        filt_proftype=SelectField(choices=[('','All'),('V','Vertical'),('H','Horizontal')])

    form=FiltForm()
    g.headcenter="""<h1 style='text-align: center;cursor: pointer;' onclick="$('#particleinfodiv').toggle()"><b>PARTICLE</b> module <span class='glyphicon glyphicon-info-sign'></span></h2>"""
    return PrintInCharte(
        render_template('part/index.html', form=form,LocalGIS=app.config.get("LOCALGIS",False)))


def GetFilteredSamples(Filter=None,GetVisibleOnly=False,ForceVerticalIfNotSpecified=False):
    sqljoin=""
    sqlparam={}
    if Filter is None: # si filtre non spécifié on utilise GET
        Filter=request.args
    if current_user.has_role(database.AdministratorLabel):
        sqlvisible = "true"
    else:
        sqlvisible = "case when p.visible "
        if current_user.is_authenticated:
            sqlvisible += " or pp.member is not null "
            sqljoin ="  left Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
        sqlvisible += " then true end "

    sql="select s.psampleid,s.latitude,s.longitude,"+sqlvisible+""" as visible,s.pprojid,up.ptitle
    from part_samples s
    JOIN part_projects up on s.pprojid=up.pprojid
    LEFT JOIN projects p on up.projid=p.projid """
    sql +=sqljoin
    sql += " where 1=1 "

    if Filter.get("MapN",'')!="" and Filter.get("MapW",'')!="" and Filter.get("MapE",'')!="" and Filter.get("MapS",'')!="":
        sql+=" and s.latitude between %(MapS)s and %(MapN)s   "
        sqlparam['MapN']=Filter.get("MapN")
        sqlparam['MapS']=Filter.get("MapS")
        sqlparam['MapW']=float(Filter.get("MapW"))
        sqlparam['MapE']=float(Filter.get("MapE"))
        if sqlparam['MapW']<sqlparam['MapE']:
            sql+=" and s.longitude between %(MapW)s and %(MapE)s  "
        else:
            sql += " and  (s.longitude between %(MapW)s and 180 or s.longitude between -180 and %(MapE)s   )"

    if Filter.get("filt_fromdate",'')!="":
        sql+=" and s.sampledate>= to_date(%(fromdate)s,'YYYY-MM-DD') "
        sqlparam['fromdate']=Filter.get("filt_fromdate")
    if Filter.get("filt_todate",'')!="":
        sql+=" and s.sampledate<= to_date(%(todate)s,'YYYY-MM-DD') "
        sqlparam['todate']=Filter.get("filt_todate")
    if Filter.get("filt_proj",'')!="":
        sql+=" and p.projid in (%s) "%(','.join([str(int(x)) for x in request.args.getlist("filt_proj")]))
    if Filter.get("filt_uproj",'')!="":
        sql+=" and up.pprojid in (%s) "%(','.join([str(int(x)) for x in request.args.getlist("filt_uproj")]))
    if Filter.get("filt_instrum",'')!="":
        sql+=" and lower(up.instrumtype)=lower(%(instrum)s) "
        sqlparam['instrum']=Filter.get("filt_instrum")
    if Filter.get("filt_proftype", '') != "":
        sql += " and organizedbydeepth = %s "%(True if Filter.get("filt_proftype", '' if ForceVerticalIfNotSpecified==False else 'V')=='V' else False)



    if GetVisibleOnly:
        sql="select * from ("+sql+") s where visible=true "
    sql+=""" order by s.psampleid     """
    return database.GetAll(sql,sqlparam)

@app.route('/part/searchsample')
def Partsearchsample():
    samples =GetFilteredSamples()
    res=[]
    for s in samples:
        r={'id':s['psampleid'],'lat':s['latitude'],'long':s['longitude'],'visible':s['visible']}
        res.append(r)
    return json.dumps(res)

@app.route('/part/statsample')
def Partstatsample():
    samples =GetFilteredSamples()
    if len(samples )==0:
        return "No Data selected"
    sampleinclause=",".join([str(x[0]) for x in samples])
    data={'nbrsample':len(samples),'nbrvisible':sum(1 for x in samples if x['visible'])}
    data['nbrnotvisible']=data['nbrsample']-data['nbrvisible']
    data['partprojcount']=database.GetAll("""SELECT pp.ptitle,count(*) nbr,pp.do_email,do_name,email,name
        ,p.visible
        from part_samples ps
        join part_projects pp on ps.pprojid=pp.pprojid        
        left join ( select * from (
            select u.email,u.name,pp.projid,rank() OVER (PARTITION BY pp.projid ORDER BY pp.id) rang
            from projectspriv pp join users u on pp.member=u.id
            where pp.privilege='Manage' and u.active=true ) q where rang=1
          ) qpp on qpp.projid=pp.projid
        LEFT JOIN projects p on pp.projid = p.projid
        where ps.psampleid in ({0} )
        group by pp.ptitle,pp.do_email,do_name,email,name,p.visible
        order by pp.ptitle""".format(sampleinclause))
    data['instrumcount']=database.GetAll("""SELECT coalesce(pp.instrumtype,'not defined') instrum,count(*) nbr
        from part_samples ps
        join part_projects pp on ps.pprojid=pp.pprojid
        where ps.psampleid in ({0} )
        group by pp.instrumtype
        order by pp.instrumtype""".format(sampleinclause))
    data['taxoprojcount']=database.GetAll("""SELECT coalesce(p.title,'not associated') title,p.projid,count(*) nbr
        from part_samples ps
        join part_projects pp on ps.pprojid=pp.pprojid
        left join projects p on pp.projid=p.projid
        where ps.psampleid in ({0} )
        group by p.title,p.projid
        order by p.title""".format(sampleinclause))
    data['taxostat']=database.GetAll("""select round(100*count(case when nbr=nbrval then 1 end)/count(*),1) pctval100pct
          ,round(100*count(case when nbrval>0 and nbr=nbrval then 1 end)/count(*),1) pctpartval
          ,round(100*sum(nbrval)/sum(nbr),1) as pctobjval
        from (SELECT ps.sampleid,count(*) nbr,count(case when classif_qual='V' then 1 end) nbrval
            from part_samples ps
            join obj_head oh on oh.sampleid=ps.sampleid
            where ps.psampleid in ({0})
            group by ps.sampleid )q
            having count(*)>0
            """.format(sampleinclause))
    if len(data['taxostat'])==0:
        data['taxostat'] ={}
    else:
        data['taxostat']={k: float(v) for k, v in data['taxostat'][0].items()}
    data['depthhisto']=database.GetAll("""SELECT coalesce(case when bottomdepth<500 then '0- 500' else trunc(bottomdepth,-3)||'-'||(trunc(bottomdepth,-3)+1000) end,'Not defined') slice
      , count(*) nbr
      from (select ps.psampleid,cast(coalesce(max(depth),ps.bottomdepth) as NUMERIC) bottomdepth
            from part_samples ps
            left join part_histopart_reduit phr on ps.psampleid = phr.psampleid
            where ps.psampleid in ({0})
            group by ps.psampleid) ps
group by slice order by slice""".format(sampleinclause))
    data['taxolist']=database.GetAll("""
        select classif_id,t.name nom 
        ,concat(t14.name||'>',t13.name||'>',t12.name||'>',t11.name||'>',t10.name||'>',t9.name||'>',t8.name||'>',t7.name||'>',
     t6.name||'>',t5.name||'>',t4.name||'>',t3.name||'>',t2.name||'>',t1.name||'>',t.name) tree
        from (SELECT distinct hl.classif_id
            from part_samples ps
            join part_histocat_lst hl on ps.psampleid = hl.psampleid
            where ps.psampleid in ({0} ) ) cat
        join taxonomy t on cat.classif_id=t.id
        left join taxonomy t1 on t.parent_id=t1.id
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
        left join taxonomy t14 on t13.parent_id=t14.id                
        order by tree""".format(sampleinclause))

    return render_template('part/stats.html', data=data,raw=json.dumps(data))
    # return json.dumps(data)


@app.route('/part/getsamplepopover/<int:psampleid>')
def Partgetsamplepopover(psampleid):
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