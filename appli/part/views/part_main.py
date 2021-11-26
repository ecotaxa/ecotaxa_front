import operator

from flask import render_template, g, json, request
from wtforms import Form, SelectField, SelectMultipleField

from appli import app
from .. import GetClassLimitTxt
from ..constants import PartDetClassLimit, PartRedClassLimit, CTDFixedCol
from ..db_utils import GetAll
from ..ecopart_blueprint import part_app, part_PrintInCharte, ECOTAXA_URL
from ..remote import EcoTaxaInstance


@part_app.route('/')
def indexPart():
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)

    # Liste des projets liés _et visibles_
    linked_prjs = set([a_ref for a_ref, in GetAll("select distinct projid from part_projects")])
    prjs = ecotaxa_if.get_visible_projects()
    prjs.sort(key=lambda p: p.title.lower())
    prjs = [[prj.projid, "%s(%d)" % (prj.title, prj.projid)]
            for prj in prjs
            if prj.projid in linked_prjs]

    class FiltForm(Form):
        filt_proj = SelectMultipleField(choices=[['', '']] + prjs)
        # Tous les projets EcoPart
        filt_uproj = SelectMultipleField(choices=[['', '']] + GetAll(
            "SELECT pprojid,concat(ptitle,' (',cast(pprojid AS VARCHAR),')') "
            "FROM part_projects ORDER BY lower(ptitle)"))
        gpr = SelectMultipleField(
            choices=[("cl%d" % i, "# l-1 %02d : " % i + GetClassLimitTxt(PartRedClassLimit, i)) for i in range(1, 16)]
                    + [("bv%d" % i, "BV %02d : " % i + GetClassLimitTxt(PartRedClassLimit, i)) for i in range(1, 16)])
        gpd = SelectMultipleField(
            choices=[("cl%d" % i, "# l-1 %02d : " % i + GetClassLimitTxt(PartDetClassLimit, i)) for i in range(1, 46)]
                    + [("bv%d" % i, "BV %02d : " % i + GetClassLimitTxt(PartDetClassLimit, i)) for i in range(1, 46)])
        ctd = SelectMultipleField(
            choices=sorted([(k, v) for v, k in CTDFixedCol.items()], key=operator.itemgetter(1)))
        filt_proftype = SelectField(choices=[['', 'All'], ['V', 'DEPTH casts'], ['H', 'TIME series']])
        filt_instrum = SelectField(
            choices=[['', 'All'], ('lisst', 'lisst'), ('uvp5', 'uvp5'), ('uvp6', 'uvp6'), ('uvp6remote', 'uvp6remote')])
        taxolb = SelectMultipleField(choices=[['', '']])

    filt_data = request.args
    form = FiltForm(filt_data)
    form.taxolb.choices = [['', '']]
    if (len(request.args.getlist('taxolb'))):
        # Si l'on a passé la liste des catégories, la rajouter dans le select2 au chargement de la page
        classif_ids = [int(x) for x in request.args.getlist('taxolb')]
        form.taxolb.choices += ecotaxa_if.get_taxo(classif_ids)
    g.headcenter = """<h1 style='text-align: center;cursor: pointer;' >
      <span onclick="$('#particleinfodiv').toggle()"><b>PARTICLE</b> module <span class='glyphicon glyphicon-info-sign'></span> </span> 
      <a href='%s' style='font-size:medium;margin-left: 50px;'>Go to Ecotaxa</a></h2>""" % ECOTAXA_URL
    return part_PrintInCharte(ecotaxa_if,
                              render_template('part/index.html', form=form, LocalGIS=app.config.get("LOCALGIS", False),
                                              reqfields=request.args, ecotaxa=ECOTAXA_URL))


def _GetSQLVisibility(ecotaxa_if: EcoTaxaInstance):
    # Génère le SQL qui donne la visiblité des projets EcoPart
    # Il est supposé que l'alias 'pp' est la table part_projects
    ecotaxa_user = ecotaxa_if.get_current_user()

    SQL_PART_PRJ_VISIBLE = "pp.oldestsampledate+make_interval(0,pp.public_visibility_deferral_month)<=current_date"
    SQL_PART_PRJ_EXPORTABLE = "pp.oldestsampledate+make_interval(0,pp.public_partexport_deferral_month)<=current_date"
    SQL_ZOO_PRJ_EXPORTABLE = "pp.oldestsampledate+make_interval(0,pp.public_zooexport_deferral_month)<=current_date"

    # Détermination du droit pour le projet EcoPart
    sql_case = []
    if ecotaxa_user is not None:
        if 2 in ecotaxa_user.can_do:
            # Administrateur EcoTaxa
            sql_case.append(" when true then 'Y' ")
        else:
            # Utilisateur EcoTaxa ayant crée le projet EcoPart
            sql_case.append(" when pp.ownerid=%d then 'Y' " % ecotaxa_user.id)
    # Règles de visibilité par date
    sql_case.append(""" when """ + SQL_PART_PRJ_VISIBLE + """ 
                          and """ + SQL_PART_PRJ_EXPORTABLE + """  
                         then 'Y' """)
    sql_case.append(""" when """ + SQL_PART_PRJ_VISIBLE + """ 
                         then 'V' """)
    sql_case.append(" else 'N' ")

    sqlvisible = "case " + "".join(sql_case) + "end"
    # if ecotaxa_user is not None and 2 in ecotaxa_user.can_do:
    #     # Connected and Admin
    #     sqlvisible = "'YY'"
    # else:
    #     sqlvisible = "case "
    #     if ecotaxa_user is not None:
    #         # Project owner can access, shortcut-ting date constraints
    #         sqlvisible += " when pp.ownerid=%d then 'YY' " % (ecotaxa_user.id)
    #         # Allow EcoTaxa users to export the whole if they can modify the corresponding EcoTaxa project
    #         sqlvisible += " when ppriv.privilege in('Manage','Annotate') then 'YY' "
    #         sqljoin = "  left Join projectspriv ppriv on pp.projid = ppriv.projid and ppriv.member=%d" % \
    #                   (ecotaxa_user.id,)
    #     # Cas général, si le projet EcoTaxa est visible c'est bon
    #     sqlvisible += """ when """ + SQL_PART_PRJ_VISIBLE + """
    #                        and """ + SQL_PART_PRJ_EXPORTABLE + """
    #                        and """ + SQL_ZOO_PRJ_EXPORTABLE + """
    #                        and p.visible then 'YY' """
    #     if ecotaxa_user is not None:
    #         # Any right on the associated EcoTaxa project means 'V'iew on it.
    #         sqlvisible += """ when ppriv.member is not null -- i.e. 'View' as the 2 other rights are managed above
    #                             and """ + SQL_PART_PRJ_VISIBLE + """
    #                             then
    #                             case when """ + SQL_PART_PRJ_EXPORTABLE + """
    #                             then 'YV'
    #                             else 'VV' end """
    #     # If SQL 'when' arrives here, it's that all special grants above did not match
    #     sqlvisible += """ when """ + SQL_PART_PRJ_VISIBLE + """
    #                        and """ + SQL_PART_PRJ_EXPORTABLE + """
    #                       then case when p.visible then 'YV' else 'YN' end  """
    #     sqlvisible += """ when """ + SQL_PART_PRJ_VISIBLE + """
    #                       then case when p.visible then 'VV' else 'VN' end  """
    #     sqlvisible += " else 'NN' end "
    return sqlvisible


# Retourne la liste des samples correspondant à un des filtres.
# La colonne calculée visibility est la synthèse des règles du projet associé
# 2 Lettre Visibilité Part et Zoo pouvant être N=>No , V=>Visibilité simple, Y=>Export
# Note: On utilise l'ordre alphabétique pour la hiérachie des droits: Y > V > N
# La colonne calculée visible le résultat de la comparaison entre visibility et MinimumPart&ZooVisibility
def GetFilteredSamples(ecotaxa_if: EcoTaxaInstance, Filter=None, GetVisibleOnly=False,
                       ForceVerticalIfNotSpecified=False,
                       MinimumPartVisibility='N', MinimumZooVisibility='N'):
    sqlparam = {}
    if Filter is None:  # si filtre non spécifié on utilise GET
        Filter = request.args
    sqlvisible = _GetSQLVisibility(ecotaxa_if)
    sql = "select s.psampleid, s.latitude, s.longitude,cast (" + sqlvisible + """ as varchar(2) ) as visibility, 
            s.profileid, s.pprojid, pp.ptitle, pp.projid
            from part_samples s
            join part_projects pp on s.pprojid = pp.pprojid """
    sql += " where 1=1 "

    if Filter.get("MapN", '') != "" and Filter.get("MapW", '') != "" and Filter.get("MapE", '') != "" and Filter.get(
            "MapS", '') != "":
        sql += " and s.latitude between %(MapS)s and %(MapN)s   "
        sqlparam['MapN'] = Filter.get("MapN")
        sqlparam['MapS'] = Filter.get("MapS")
        sqlparam['MapW'] = float(Filter.get("MapW"))
        sqlparam['MapE'] = float(Filter.get("MapE"))
        if sqlparam['MapW'] < sqlparam['MapE']:
            sql += " and s.longitude between %(MapW)s and %(MapE)s  "
        else:
            sql += " and  (s.longitude between %(MapW)s and 180 or s.longitude between -180 and %(MapE)s   )"

    if Filter.get("filt_fromdate", '') != "":
        sql += " and s.sampledate>= to_date(%(fromdate)s,'YYYY-MM-DD') "
        sqlparam['fromdate'] = Filter.get("filt_fromdate")
    if Filter.get("filt_todate", '') != "":
        sql += " and s.sampledate< to_date(%(todate)s,'YYYY-MM-DD')+1 "
        sqlparam['todate'] = Filter.get("filt_todate")
    if Filter.get("filt_proj", '') != "":
        sql += " and pp.projid in (%s) " % (','.join([str(int(x)) for x in request.args.getlist("filt_proj")]))
    if Filter.get("filt_uproj", '') != "":
        sql += " and pp.pprojid in (%s) " % (','.join([str(int(x)) for x in request.args.getlist("filt_uproj")]))
    if Filter.get("filt_instrum", '') != "":
        sql += " and lower(pp.instrumtype)=lower(%(instrum)s) "
        sqlparam['instrum'] = Filter.get("filt_instrum")
    if Filter.get("filt_proftype", '') != "":
        sql += " and organizedbydeepth = %s " % (
            True if Filter.get("filt_proftype", '' if ForceVerticalIfNotSpecified == False else 'V') == 'V' else False)

    sql = """select s.*, case when substr(visibility,1,1)>='%s' then true end as visible from (%s) s """ % \
          (MinimumPartVisibility, sql)
    if GetVisibleOnly:
        sql = "select * from (" + sql + ") s where visible=true "
    sql += """ order by s.psampleid     """
    ret = GetAll(sql, sqlparam)
    # Enrichissement avec les infos des projets EcoTaxa
    visible_prjids = set([prj.projid for prj in ecotaxa_if.get_visible_projects()])
    for a_line in ret:
        ecotaxa_prjid = a_line["projid"]
        ecotaxa_proj_visible = 'Y' if ecotaxa_prjid in visible_prjids else 'V' if ecotaxa_prjid is None else 'N'
        a_line["visibility"] += ecotaxa_proj_visible
        # On peut simplifier, mais comme ça on voit la similarité avec le test SQL + haut
        if not (ecotaxa_proj_visible >= MinimumZooVisibility):
            a_line["visible"] = False
    # Re-filtrage si voulu
    if GetVisibleOnly:
        ret = [a_line for a_line in ret
               if a_line["visible"]]
    return ret


@part_app.route('/searchsample')
def Partsearchsample():
    # Utilisé pour remplir la carte de la home page
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    samples = GetFilteredSamples(ecotaxa_if)
    res = []
    for s in samples:
        r = {'id': s['psampleid'], 'lat': s['latitude'], 'long': s['longitude'], 'visibility': s['visibility']}
        res.append(r)
    return json.dumps(res)


# @part_app.route('/statsample')
def PartstatsampleGetData(ecotaxa_if: EcoTaxaInstance):
    samples = GetFilteredSamples(ecotaxa_if)
    if len(samples) == 0:
        return "No Data selected"
    sampleinclause = ",".join([str(x[0]) for x in samples])
    data = {'nbrsample': len(samples), 'nbrvisible': sum(1 for x in samples if x['visible'])}
    data['nbrnotvisible'] = data['nbrsample'] - data['nbrvisible']
    sqlvisible = _GetSQLVisibility(ecotaxa_if)
    part_proj_count_SQL = """
    select pp.ptitle, count(*) nbr,
           count(case when organizedbydeepth then 1 end) nbrdepth,
           count(case when not organizedbydeepth then 1 end) nbrtime,
           pp.do_email, do_name, qpp.email, qpp.name, pp.instrumtype, pp.pprojid,
           count(ps.sampleid ) nbrtaxo, p.visible, visibility,
           uppowner.name uppowner_name,uppowner.email uppowner_email
      from part_samples ps
      join (select pp.*, cast ({1} as varchar(2) ) as visibility
              from part_projects pp
           ) pp on ps.pprojid = pp.pprojid
      -- Récupération du premier manager par projet EcoTaxa
      left join ( select * from ( select u.email, u.name, pp.projid, rank() OVER (PARTITION BY pp.projid ORDER BY pp.id) rang
                                    from projectspriv pp join users u on pp.member=u.id
                                   where pp.privilege='Manage' and u.active=true 
                                ) q where rang=1 
                ) qpp on qpp.projid=pp.projid
      left join projects p on pp.projid = p.projid
      left join users uppowner on pp.ownerid=uppowner.id         
      where ps.psampleid in ({0})
      group by pp.ptitle, pp.do_email, do_name, qpp.email, qpp.name, 
               p.visible, pp.instrumtype, pp.pprojid, visibility, 
               uppowner.name, uppowner.email
      order by pp.ptitle""".format(sampleinclause, sqlvisible)
    data['partprojcount'] = GetAll(part_proj_count_SQL)
    data['instrumcount'] = GetAll("""
        select coalesce(pp.instrumtype,'not defined') instrum,count(*) nbr
          from part_samples ps
          join part_projects pp on ps.pprojid=pp.pprojid
         where ps.psampleid in ({0} )
         group by pp.instrumtype
         order by pp.instrumtype""".format(sampleinclause))
    data['taxoprojcount'] = GetAll("""
        select coalesce(p.title,'not associated') title, p.projid, count(*) nbr
          from part_samples ps
          join part_projects pp on ps.pprojid = pp.pprojid
          left join projects p on pp.projid = p.projid
          where ps.psampleid in ({0} )
          group by p.title,p.projid
          order by p.title""".format(sampleinclause))

    TaxoStat = GetAll("""SELECT ps.sampleid,count(*) nbr,count(case when classif_qual='V' then 1 end) nbrval,ps.pprojid
            from part_samples ps
            join objects oh on oh.sampleid=ps.sampleid
            where ps.psampleid in ({0})
            group by ps.sampleid,ps.pprojid  """.format(sampleinclause))
    ResultTaxoStat = {'nbrobj': 0, 'nbrobjval': 0, 'pctval100pct': 0, 'pctpartval': 0, 'pctobjval': 0}
    TaxoStatByProj = {}
    for r in TaxoStat:
        ResultTaxoStat['nbrobj'] += r['nbr']
        ResultTaxoStat['nbrobjval'] += r['nbrval']
        if r['pprojid'] not in TaxoStatByProj:
            TaxoStatByProj[r['pprojid']] = {'nbrobj': 0, 'nbrobjval': 0, 'pctobjval': 0}
        TaxoStatByProj[r['pprojid']]['nbrobj'] += r['nbr']
        TaxoStatByProj[r['pprojid']]['nbrobjval'] += r['nbrval']
        if r['nbr'] == r['nbrval']: ResultTaxoStat['pctval100pct'] += 1
        if r['nbr'] > r['nbrval']: ResultTaxoStat['pctpartval'] += 1
    if len(TaxoStat) > 0:
        ResultTaxoStat['pctval100pct'] = round(100 * ResultTaxoStat['pctval100pct'] / len(TaxoStat), 1)
        ResultTaxoStat['pctpartval'] = round(100 * ResultTaxoStat['pctpartval'] / len(TaxoStat), 1)
    if ResultTaxoStat['nbrobj'] > 0:
        ResultTaxoStat['pctobjval'] = round(100 * ResultTaxoStat['nbrobjval'] / ResultTaxoStat['nbrobj'], 1)
    data['taxostat'] = ResultTaxoStat
    data['taxostatbyproj'] = {}
    for k, r in TaxoStatByProj.items():
        if r['nbrobj']:
            data['taxostatbyproj'][k] = round(100 * r['nbrobjval'] / r['nbrobj'], 1)
    print(data['taxostatbyproj'])

    data['depthhisto'] = GetAll("""SELECT coalesce(case when bottomdepth<500 then '0- 500' else trunc(bottomdepth,-3)||'-'||(trunc(bottomdepth,-3)+1000) end,'Not defined') slice
      , count(*) nbr
      from (select ps.psampleid,cast(coalesce(max(depth),ps.bottomdepth) as NUMERIC) bottomdepth
              from part_samples ps
              left join part_histopart_reduit phr on ps.psampleid = phr.psampleid
             where ps.psampleid in ({0})
             group by ps.psampleid) ps
group by slice order by slice""".format(sampleinclause))
    # On récupère la liste des catégories pour les samples concernés
    classif_ids = GetAll("""
        SELECT distinct hl.classif_id
            from part_samples ps
            join part_histocat_lst hl on ps.psampleid = hl.psampleid
            where ps.psampleid in ({0})""".format(sampleinclause))
    # Format retourné, par exemple: [ [85061], [85039] ....]
    classif_ids = [an_id[0] for an_id in classif_ids]
    data['taxolist'] = ecotaxa_if.get_taxo2(classif_ids)
    data['taxolist'].sort(key=lambda r: r['tree'])
    return data


@part_app.route('/statsample')
def Partstatsample():
    # Button "Display selection statistics"
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    data = PartstatsampleGetData(ecotaxa_if)
    if isinstance(data, str):
        return data
    return render_template('part/stats.html', data=data, raw=json.dumps(data), ecotaxa=ECOTAXA_URL)
    # return json.dumps(data)


@part_app.route('/getsamplepopover/<int:psampleid>')
def Partgetsamplepopover(psampleid):
    sql = """select s.psampleid, s.profileid, p.ptitle, ep.title, p.cruise, p.ship, p.projid, p.pprojid,
      round(cast(s.latitude as NUMERIC),4) latitude,round(cast(s.longitude as NUMERIC),4) longitude,
      to_char(s.sampledate,'YYYY-MM-DD HH24:MI') sampledate
      from part_samples s
      LEFT JOIN part_projects p on s.pprojid=p.pprojid
      left join projects ep on p.projid = ep.projid
      where s.psampleid=%(psampleid)s
      """
    data = GetAll(sql, {'psampleid': psampleid})[0]
    txt = """ID : {psampleid}<br>
    Profile ID : {profileid}<br>
    Project : {ptitle} ({pprojid})<br>
    Ship : {ship}<br>
    Cruise : {cruise}<br>
    Ecotaxa Project : {title} ({projid})<br>
    Lat/Lon : {latitude}/{longitude}<br>
    Date/Time : {sampledate}
    """.format(**data)
    return txt
