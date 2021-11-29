from typing import List

from flask import render_template, request, g

import appli
import appli.part.database as partdatabase
from appli import app, gvg, gvp, ErrorFormat
from to_back.ecotaxa_cli_py import SampleModel
from . import sampleedit
from ..db_utils import ExecSQL, GetAll
from ..ecopart_blueprint import part_app, part_PrintInCharte, PART_STORAGE_URL, PART_URL, ECOTAXA_URL
from ..funcs import common_sample_import as common_import
from ..funcs import uvp_sample_import
from ..funcs.histograms import ComputeHistoDet, ComputeHistoRed, ComputeZooHisto
from ..remote import EcoTaxaInstance


@part_app.route('/prj/')
def part_prj():
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    ecotaxa_user = ecotaxa_if.get_current_user()
    assert ecotaxa_user is not None  # i.e. @login_required
    params = {}
    sql = """select up.pprojid, up.ptitle, up.ownerid, up.rawfolder, up.instrumtype, up.projid,
                    (select count(*) from part_samples ps where ps.pprojid = up.pprojid) as samplecount,
                    null::varchar as name, null::varchar as email, -- placeholders 
                    null::varchar as title
               from part_projects up
          """
    sql += " where 1=1 "
    if 2 in ecotaxa_user.can_do:
        # Les admins EcoTaxa peuvent tout voir
        pass
    else:
        # Filtrage des projets appartenant à l'utilisateur courant
        sql += "  and up.ownerid = %d" % (ecotaxa_user.id,)
    # Si filtrage, c'est un "OU" sur le titre des projets des 2 modules
    zoo_projects = {p.projid: p for p in ecotaxa_if.search_projects(title=gvg('filt_title', ''))}
    if gvg('filt_title', '') != '':
        sql += " and ( up.ptitle ilike '%%'||%(title)s ||'%%' or to_char(up.pprojid,'999999') like '%%'||%(title)s " \
               "       or up.projid = any(%(zoo_projs)s) ) "
        params['title'] = gvg('filt_title')
        params['zoo_projs'] = [projid for projid in zoo_projects.keys()]
    if gvg('filt_instrum', '') != '':
        sql += " and up.instrumtype ilike '%%'||%(filt_instrum)s ||'%%'  "
        params['filt_instrum'] = gvg('filt_instrum')
    res = GetAll(sql, params)
    # On complète les trous des 'placeholders'.
    for a_line in res:
        projid = a_line['projid']
        if projid is not None:
            zoo_proj = zoo_projects.get(projid)
            if zoo_proj is None:
                # Un appel par projet manquant. Pas mieux avec l'API au 28/11/2021.
                zoo_proj = ecotaxa_if.get_project(projid)
                if zoo_proj is not None:
                    zoo_projects[projid] = zoo_proj
            if zoo_proj is not None:
                a_line['title'] = zoo_proj.title
        ownerid = a_line['ownerid']
        if ownerid is not None:
            user = ecotaxa_if.get_user_by_id(ownerid)
            if user is not None:
                a_line['name'] = user.name
                a_line['email'] = user.email
    # Tri en mémoire
    res.sort(key=lambda r: (r['title'] if r['title'] else chr(256))+r['ptitle'])
    CanCreate = False
    if (2 in ecotaxa_user.can_do) or (1 in ecotaxa_user.can_do):  # User can Administrate or create projects in EcoTaxa
        CanCreate = True
    g.headcenter = "<h4>Particle Projects management</h4><a href='%s'>Particle Module Home</a>" % PART_URL
    return part_PrintInCharte(ecotaxa_if,
                              render_template('part/list.html', PrjList=res, CanCreate=CanCreate,
                                              AppManagerMailto=appli.GetAppManagerMailto()
                                              , filt_title=gvg('filt_title'), filt_subset=gvg('filt_subset'),
                                              filt_instrum=gvg('filt_instrum')))


@part_app.route('/prj_uvpgraph/<int:PrjId>/<int:offset>')
def part_prj_vpgraph(PrjId, offset):
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    ecotaxa_user = ecotaxa_if.get_current_user()
    assert ecotaxa_user is not None  # i.e. @login_required
    Prj = GetAll("""select pp.* from part_projects pp where pprojid=%s""", (PrjId,))
    if len(Prj) != 1:
        return part_PrintInCharte(ecotaxa_if, ErrorFormat("Project doesn't exists"))
    Prj = Prj[0]
    if Prj['ownerid'] != ecotaxa_user.id and not (2 in ecotaxa_user.can_do):
        return part_PrintInCharte(ecotaxa_if, ErrorFormat("Access Denied"))
    g.headcenter = "<h4>Particle Project %s : %s</h4><a href='%sprj/%s'>Project home</a>" % (
        Prj['projid'], Prj['ptitle'], PART_URL, Prj['pprojid'],)
    dbsample = GetAll("""select psampleid,filename,profileid from part_samples s where pprojid=%s
          ORDER BY filename desc limit 50 OFFSET %s 
          """ % (PrjId, offset))
    txt = """<style>
    .idepth,.ipart {height: auto}
    </style>
    <button class='btn' onclick='dozoom(50);'>50%</button>
    <button class='btn' onclick='dozoom(75);'>75%</button>
    <button class='btn' onclick='dozoom(100);'>100%</button>
    <script>
    function dozoom(z) {
      $('.idepth').css('width',(800*z/100).toFixed().toString()+"px");
      $('.ipart').css('width',(1600*z/100).toFixed().toString()+"px");
    }
</script>
    """
    for s in dbsample:
        txt += """<p class='ghead'>Graph for {psampleid} - {filename} - {profileid} - </p>
          <img src='{vault}{idepth}' class='idepth'> <img src='{vault}{ipart}' class='ipart'>
          """.format(psampleid=s['psampleid'], filename=s['filename'], profileid=s['profileid'],
                     vault=PART_STORAGE_URL
                     , idepth=uvp_sample_import.GetPathForImportGraph(s['psampleid'], 'depth', True)
                     , ipart=uvp_sample_import.GetPathForImportGraph(s['psampleid'], 'particle', True))
    return part_PrintInCharte(ecotaxa_if, txt)


@part_app.route('/prj/<int:PrjId>')
def part_prj_main(PrjId):
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    ecotaxa_user = ecotaxa_if.get_current_user()
    assert ecotaxa_user is not None  # i.e. @login_required
    # Prj = partdatabase.part_projects.query.filter_by(pprojid=PrjId).first()
    Prj = GetAll("""select pp.*
                    ,oldestsampledate+make_interval(0,public_visibility_deferral_month) visibility_date  
                    ,oldestsampledate+make_interval(0,public_partexport_deferral_month) partexport_date 
                    ,oldestsampledate+make_interval(0,public_zooexport_deferral_month) zooexport_date 
                    from part_projects pp where pprojid=%s""", (PrjId,))
    if len(Prj) != 1:
        return part_PrintInCharte(ecotaxa_if, ErrorFormat("Project doesn't exists"))
    Prj = Prj[0]
    if Prj['ownerid'] != ecotaxa_user.id and not (2 in ecotaxa_user.can_do):
        return part_PrintInCharte(ecotaxa_if, ErrorFormat("Access Denied"))
    g.headcenter = "<h4>Particle Project %s : %s</h4><a href='%s'>Particle Module Home</a>" % (
        Prj['projid'], Prj['ptitle'], PART_URL)
    dbsample = GetAll("""select profileid,psampleid,organizedbydeepth,filename,stationid,firstimage,lastimg,lastimgused,sampleid
          ,histobrutavailable,comment,daterecalculhistotaxo,ctd_import_datetime,sampledate,imp_descent_filtered_row,imp_removed_empty_slice
          ,(select count(*) from part_histopart_det where psampleid=s.psampleid) nbrlinedet
          ,(select count(*) from part_histopart_reduit where psampleid=s.psampleid) nbrlinereduit
          ,(select count(*) from part_histocat where psampleid=s.psampleid) nbrlinetaxo
          ,(select count(*) from part_ctd where psampleid=s.psampleid) nbrlinectd
          from part_samples s
          where pprojid=%s
          ORDER BY filename desc
          """ % (PrjId))
    MinSampleDate = Prj['oldestsampledate']
    VisibilityText = ""
    if MinSampleDate is not None:
        VisibilityText += """<br> Oldest sample date is {0:%Y-%m-%d}, Visibility date is {1}
          , Particule export date is {2}, Zooplankton classification export date is {3} 
          """.format(MinSampleDate
                     , "Not Defined" if Prj['visibility_date'] is None else Prj['visibility_date'].strftime("%Y-%m-%d")
                     , "Not Defined" if Prj['partexport_date'] is None else Prj['partexport_date'].strftime("%Y-%m-%d")
                     , "Not Defined" if Prj['zooexport_date'] is None else Prj['zooexport_date'].strftime("%Y-%m-%d"))

    return part_PrintInCharte(ecotaxa_if,
                              render_template('part/prj_index.html', PrjId=PrjId, dbsample=dbsample, Prj=Prj,
                                              VisibilityText=VisibilityText))


def ComputeZooMatch(ecotaxa_if: EcoTaxaInstance, psampleid, projid):
    """ On essaie de raccrocher un sample EcoTaxa à ce sample EcoPart
        La règle: orig_id EcoTaxa identique au profileid EcoPart, dans le projet lié -> C'est bon """
    if projid is not None:
        profileid, = GetAll("""select profileid from part_samples ps where psampleid=%d""" % psampleid)[0]
        ecosample = ecotaxa_if.search_samples(projid, profileid)
        if len(ecosample) == 1:
            ExecSQL("update part_samples set sampleid=%s where psampleid=%s",
                    (ecosample[0].sampleid, psampleid))
            return " Matched"
        else:
            return " <span style='color: orange;'>%d match found in EcoTaxa</span>" % len(ecosample)
    else:
        return " <span style='color: red;'>Ecotaxa sample matching impossible if Particle project not linked to an Ecotaxa project</span>"


def GlobalTaxoCompute(ecotaxa_if: EcoTaxaInstance, logger):
    # cron nightly
    # Détermination des samples orphelins, i.e.:
    # - dont les projets sont rattachés à un projet EcoTaxa
    # - mais dont les samples ne sont pas (ou pas correctement) rattachés à un sample EcoTaxa
    linked_samples = GetAll("""select pp.projid, ps.sampleid, ps.psampleid, ps.profileid 
                                 from part_samples ps
                                 join part_projects pp on ps.pprojid = pp.pprojid 
                                where pp.projid is not null""")
    fetched_samples = {}
    logger.info("Ensuring consistency of links to EcoTaxa")
    for to_check in linked_samples:
        ecotaxa_projid = to_check["projid"]
        samples_for_proj: List[SampleModel] = fetched_samples.get(ecotaxa_projid)
        if samples_for_proj is None:
            samples_for_proj = ecotaxa_if.all_samples_for_project(ecotaxa_projid)  # La totale
            fetched_samples[ecotaxa_projid] = samples_for_proj
        # Correspondance
        sampleid = to_check["sampleid"]
        profileid = to_check["profileid"]
        for a_sample in samples_for_proj:
            if a_sample.sampleid == sampleid and a_sample.orig_id == profileid:
                break
        else:
            # TODO: pas super efficace mais ça arrive rarement et puis c'est un job
            psampleid = to_check["psampleid"]
            logger.info("Matching %s %s", psampleid, ComputeZooMatch(ecotaxa_if, psampleid, ecotaxa_projid))
    # sample ayant un objet qui a été classifié depuis le dernier calcul de l'histogramme
    logger.info("Refreshing histograms if needed")
    Samples = GetAll("""select ps.psampleid, ps.daterecalculhistotaxo, pp.instrumtype
                from part_samples ps
                join part_projects pp on ps.pprojid = pp.pprojid 
                where ps.sampleid is not null
                and (exists (select 1 from objects obj
                              where obj.sampleid = ps.sampleid 
                                and obj.classif_when > ps.daterecalculhistotaxo)
                    or ps.daterecalculhistotaxo is null 
                    or exists (select 1 from part_histocat_lst hc 
                                where hc.psampleid = ps.psampleid and hc.classif_id not in (select id from taxonomy)) 
                )""")
    for S in Samples:
        psampleid, instrumtype = S['psampleid'], S['instrumtype']
        logger.info("Computing histogram for %s (%)", psampleid, instrumtype)
        ComputeZooHisto(ecotaxa_if, psampleid, instrumtype)


@part_app.route('/prjcalc/<int:PrjId>', methods=['post'])
def part_prjcalc(PrjId):
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    ecotaxa_user = ecotaxa_if.get_current_user()
    assert ecotaxa_user is not None  # i.e. @login_required
    Prj = partdatabase.part_projects.query.filter_by(pprojid=PrjId).first()
    if Prj.ownerid != ecotaxa_user.id and not (2 in ecotaxa_user.can_do):
        return part_PrintInCharte(ecotaxa_if, ErrorFormat("Access Denied"))
    txt = ""
    CheckedSampleList = []
    for f in request.form:
        if f[0:2] == "s_" and request.form.get(f) == 'Y':
            CheckedSampleList.append(int(f[2:]))

    app.logger.info("request.form=%s", request.form)
    app.logger.info("CheckedSampleList=%s", CheckedSampleList)
    app.logger.info("dohistodet=%s,domatchecotaxa=%s,dohistotaxo=%s", gvp('dohistodet'), gvp('domatchecotaxa'),
                    gvp('dohistotaxo'))
    dbsample = GetAll("""select profileid,psampleid,filename,sampleid,histobrutavailable
          ,(select count(*) from part_histopart_det where psampleid=s.psampleid) nbrlinedet
          from part_samples s
          where pprojid=%s and psampleid = any (%s)""", (PrjId, CheckedSampleList))
    for S in dbsample:
        prefix = "<br>{profileid} :".format(**S)
        if gvp('delete') == 'Y':
            sampleedit.delete_sample(S['psampleid'])
            txt += prefix + " deleted"
            continue
        if gvp('dohistodet') == 'Y':
            txt += prefix + ComputeHistoDet(S['psampleid'], Prj.instrumtype)
        if gvp('dohistored') == 'Y':
            txt += prefix + ComputeHistoRed(S['psampleid'], Prj.instrumtype)
        if gvp('domatchecotaxa') == 'Y':
            txt += prefix + ComputeZooMatch(ecotaxa_if, S['psampleid'], Prj.projid)
        if gvp('dohistotaxo') == 'Y':
            txt += prefix + ComputeZooHisto(ecotaxa_if, S['psampleid'], Prj.instrumtype)
            # try:
            #     uvp_sample_import.GenerateTaxonomyHistogram(S['psampleid'])
            #     txt += prefix + " Taxonomy Histogram computed"
            # except Exception as E:
            #     txt += prefix + " <span style='color: red;'>Taxonomy Histogram can't be computed : %s </span>"%(E)
        if gvp('doctdimport') == 'Y':
            if common_import.ImportCTD(S['psampleid'], ecotaxa_user.name, ecotaxa_user.email):
                txt += prefix + " CTD imported"
            else:
                txt += prefix + " <span style='color: red;'>CTD No file</span>"
    #
    # txt+="CheckedSampleList=%s"%(CheckedSampleList)
    # txt+="<br>dbsample = %s"%(dbsample)
    txt += "<br><br><a href=%sprj/%s class='btn btn-primary'><span class='glyphicon glyphicon-arrow-left'>" \
           "</span> Back to project samples list</a>" % (PART_URL, PrjId)
    return part_PrintInCharte(ecotaxa_if, txt)
