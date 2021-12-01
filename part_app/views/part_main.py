import operator

from flask import render_template, g, json, request
from wtforms import Form, SelectField, SelectMultipleField

from to_back.ecotaxa_cli_py import ProjectModel
from . import part_PrintInCharte
from ..app import part_app
from ..constants import PartDetClassLimit, PartRedClassLimit, CTDFixedCol
from ..db_utils import GetAll
from ..remote import EcoTaxaInstance
from ..txt_utils import GetClassLimitTxt
from ..urls import ECOTAXA_URL


@part_app.route('/')
def indexPart():
    ecotaxa_if = EcoTaxaInstance(request)

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
                              render_template('part/index.html', form=form,
                                              LocalGIS=part_app.config.get("LOCALGIS", False),
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
    #
    # CODE PRECEDENT AU CAS OU
    #
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
    sql = "select s.psampleid, s.latitude, s.longitude, cast (" + sqlvisible + """ as varchar(2) ) as visibility, 
            s.profileid, s.pprojid, s.sampleid, pp.ptitle, pp.projid
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
    visible_prjs = ecotaxa_if.get_visible_projects()
    visible_prjids = set([prj.projid for prj in visible_prjs])
    for a_line in ret:
        ecotaxa_prjid = a_line["projid"]
        ecotaxa_proj_visible = 'Y' if ecotaxa_prjid in visible_prjids \
            else 'V' if ecotaxa_prjid is None \
            else 'N'
        a_line["visibility"] += ecotaxa_proj_visible
        # On peut simplifier, mais comme ça on voit la similarité avec le test SQL + haut
        if not (ecotaxa_proj_visible >= MinimumZooVisibility):
            a_line["visible"] = False
    # Re-filtrage si voulu
    if GetVisibleOnly:
        ret = [a_line for a_line in ret
               if a_line["visible"]]
    return ret, visible_prjs


@part_app.route('/searchsample')
def Partsearchsample():
    # Utilisé pour remplir la carte de la home page
    ecotaxa_if = EcoTaxaInstance(request)
    samples, _ignored = GetFilteredSamples(ecotaxa_if)
    res = []
    for s in samples:
        r = {'id': s['psampleid'], 'lat': s['latitude'], 'long': s['longitude'], 'visibility': s['visibility']}
        res.append(r)
    return json.dumps(res)


def _getZooProjectManager(prj: ProjectModel):
    # Recherche du Contact ou premier Manager pour le projet
    if prj.contact is not None:
        return prj.contact
    prj.managers.sort(key=lambda u: u.id)
    if len(prj.managers) > 0:
        return prj.managers[0]
    else:
        return None


# @part_app.route('/statsample')
def PartstatsampleGetData(ecotaxa_if: EcoTaxaInstance):
    # Button "Display selection statistics"
    samples, zoo_projects = GetFilteredSamples(ecotaxa_if)
    if len(samples) == 0:
        return "No Data selected"

    # On stocke les infos sorties du filtrage, pour éviter de re-quérir des data qu'on a déjà
    samples_per_id = {s['psampleid']: s for s in samples}
    # /!\, en théorie c'est une _liste_ de samples pour chaque projet, là on en stocke un seul, au pif
    samples_per_project = {s['pprojid']: s for s in samples}
    zoo_per_projid = {p.projid: p for p in zoo_projects}

    sampleinclause = ",".join([str(k) for k in samples_per_id.keys()])

    # Tableau "Sample statistics"
    data = {'nbrsample': len(samples),
            'nbrvisible': sum(1 for x in samples if x['visible'])}
    data['nbrnotvisible'] = data['nbrsample'] - data['nbrvisible']

    # Tableau "TABLE of PROJECT STATS"
    part_proj_count_SQL = """
    select pp.ptitle, pp.ownerid, pp.do_email, pp.do_name, pp.instrumtype, pp.pprojid, pp.projid, -- part_projects infos
           count(case when ps.organizedbydeepth then 1 end) nbrdepth, -- aggregates
           count(case when not ps.organizedbydeepth then 1 end) nbrtime,
           count(ps.sampleid) nbrtaxo, 
           null::varchar as visibility, -- placeholders for completing from API info
           null::varchar as name, null::varchar as email,
           null::varchar as zoo_owner_name, null::varchar as zoo_owner_email
      from part_samples ps
      join part_projects pp on ps.pprojid = pp.pprojid
     where ps.psampleid in ({0})
     group by pp.ptitle, pp.ownerid, pp.do_email, pp.do_name, pp.instrumtype, pp.pprojid, pp.projid
     order by pp.ptitle""".format(sampleinclause)
    projects_stats = GetAll(part_proj_count_SQL)
    for a_line in projects_stats:
        # La visibilité est celle d'un sample quelconque puisqu'elle est basée sur les projets
        pprojid = a_line["pprojid"]
        a_line["visibility"] = samples_per_project[pprojid]["visibility"]
        # Récupération des infos utilisateur
        ownerid = a_line["ownerid"]
        usr = ecotaxa_if.get_user_by_id(ownerid)
        if usr is not None:
            a_line["name"] = usr.name
            a_line["email"] = usr.email
        # Extraction des infos du projet Zoo
        zoo_projid = a_line["projid"]
        if zoo_projid is None:
            continue
        zoo_proj: ProjectModel = zoo_per_projid.get(zoo_projid)
        if zoo_proj is None:
            continue
        zoo_proj_mgr = _getZooProjectManager(zoo_proj)
        if zoo_proj_mgr is not None:
            a_line["zoo_owner_name"] = zoo_proj_mgr.name
            a_line["zoo_owner_email"] = zoo_proj_mgr.email
        else:
            a_line["zoo_owner_name"] = 'private'
    data['partprojcount'] = projects_stats

    # Tableau "Sample count per instrument"
    data['instrumcount'] = GetAll("""
        select coalesce(pp.instrumtype, 'not defined') instrum, count(*) nbr
          from part_samples ps
          join part_projects pp on ps.pprojid=pp.pprojid
         where ps.psampleid in ({0} )
         group by pp.instrumtype
         order by pp.instrumtype""".format(sampleinclause))

    # Tableau "Sample per Taxonomy project"
    per_zoo_proj_stats = {}
    NO_ZOO = "not associated"
    NOT_VISIBLE_ZOO = "not visible"
    for a_line in samples:
        zoo_projid = a_line["projid"]
        if zoo_projid is None:
            title = NO_ZOO
        else:
            zoo_proj: ProjectModel = zoo_per_projid.get(zoo_projid)
            if zoo_proj is None:
                title = NOT_VISIBLE_ZOO
            else:
                title = zoo_proj.title
        zoo_4_sample = per_zoo_proj_stats.setdefault(zoo_projid, {'title': title, 'projid': zoo_projid, 'nbr': 0})
        zoo_4_sample['nbr'] += 1
    data['taxoprojcount'] = [val for val in per_zoo_proj_stats.values()]

    ResultTaxoStat = {'nbrobj': 0, 'nbrobjval': 0, 'pctval100pct': 0, 'pctpartval': 0, 'pctobjval': 0}
    TaxoStatByProj = {}  # clef: part proj id,
    # Récupération des stats sur EcoTaxa
    zoo_sample_ids = [a_line['sampleid'] for a_line in samples if a_line['sampleid'] is not None]
    zoo_stats = {s.sample_id: s for s in ecotaxa_if.get_samples_stats(zoo_sample_ids)}
    nb_stats = 0
    # Calcul des aggrégats
    for a_line in samples:
        zoo_sample_id = a_line['sampleid']
        if zoo_sample_id is None:  # Pas lié à un sample
            continue
        try:
            zoo_sample = zoo_stats[zoo_sample_id]
        except KeyError:
            # Référence invalide à un sample EcoTaxa
            continue
        # Aggrégats globaux
        nb_stats += 1
        not_validated = zoo_sample.nb_unclassified + zoo_sample.nb_dubious + zoo_sample.nb_predicted
        total_obj = not_validated + zoo_sample.nb_validated
        ResultTaxoStat['nbrobj'] += total_obj
        ResultTaxoStat['nbrobjval'] += zoo_sample.nb_validated
        if not_validated == 0:
            ResultTaxoStat['pctval100pct'] += 1
        else:
            ResultTaxoStat['pctpartval'] += 1
        # Aggrégats par projet EcoPart
        pprojid = a_line['pprojid']
        stats_4_proj = TaxoStatByProj.setdefault(pprojid, {'nbrobj': 0, 'nbrobjval': 0})
        stats_4_proj['nbrobj'] += total_obj
        stats_4_proj['nbrobjval'] += zoo_sample.nb_validated

    if nb_stats > 0:
        ResultTaxoStat['pctval100pct'] = round(100 * ResultTaxoStat['pctval100pct'] / nb_stats, 1)
        ResultTaxoStat['pctpartval'] = round(100 * ResultTaxoStat['pctpartval'] / nb_stats, 1)
    if ResultTaxoStat['nbrobj'] > 0:
        ResultTaxoStat['pctobjval'] = round(100 * ResultTaxoStat['nbrobjval'] / ResultTaxoStat['nbrobj'], 1)

    data['taxostat'] = ResultTaxoStat
    data['taxostatbyproj'] = {}
    for k, r in TaxoStatByProj.items():
        if r['nbrobj']:
            data['taxostatbyproj'][k] = round(100 * r['nbrobjval'] / r['nbrobj'], 1)

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
    ecotaxa_if = EcoTaxaInstance(request)
    data = PartstatsampleGetData(ecotaxa_if)
    if isinstance(data, str):
        return data
    return render_template('part/stats.html', data=data, raw=json.dumps(data), ecotaxa=ECOTAXA_URL)
    # return json.dumps(data)


@part_app.route('/getsamplepopover/<int:psampleid>')
def Partgetsamplepopover(psampleid):
    ecotaxa_if = EcoTaxaInstance(request)
    sql = """select s.psampleid, s.profileid, p.ptitle, p.cruise, p.ship, p.projid, p.pprojid,
      round(cast(s.latitude as NUMERIC),4) latitude,round(cast(s.longitude as NUMERIC),4) longitude,
      to_char(s.sampledate,'YYYY-MM-DD HH24:MI') sampledate,
      null::varchar as title -- placeholder
      from part_samples s
      left join part_projects p on s.pprojid=p.pprojid
      where s.psampleid=%(psampleid)s
      """
    data = GetAll(sql, {'psampleid': psampleid})[0]
    zoo_projid = data['projid']
    if zoo_projid is not None:
        zoo_proj = ecotaxa_if.get_project(zoo_projid)
        if zoo_proj is None:
            data['title'] = "Not visible"
        else:
            data['title'] = zoo_proj.title
    else:
        data['title'] = "Absent"
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
