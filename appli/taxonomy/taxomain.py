import datetime
import sys
from typing import Optional

import requests
from flask import render_template, g, flash, json, request

import appli
import appli.part.prj
import appli.project.main
from appli import app, PrintInCharte, database, gvg, gvp, ntcv, FAIcon
from appli.database import ExecSQL, db
######################################################################################################################
from appli.project.stats import RecalcProjectTaxoStat
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UsersApi, UserModelWithRights, ApiException, TaxonomyTreeApi, TaxonModel


def get_taxoserver_url():
    return app.config.get('TAXOSERVER_URL')


def get_login() -> Optional[UserModelWithRights]:
    with ApiClient(UsersApi, request) as api:
        try:
            return api.show_current_user_users_me_get()
        except ApiException as _ae:
            return None


def is_admin_or_project_creator(user: UserModelWithRights) -> bool:
    return (1 in user.can_do) or (2 in user.can_do)


@app.route('/taxo/browse/', methods=['GET', 'POST'])
def routetaxobrowse():
    """
        Browse, i.e. display local taxa. This is a dynamic API-based table.
    """
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    BackProjectBtn = ''
    if gvp('updatestat') == 'Y':
        DoFullSync()
    if gvg('fromprj'):
        BackProjectBtn = "<a href='/prj/{}' class='btn btn-default btn-primary'>{} Back to project</a> ".format(
            int(gvg('fromprj')), FAIcon('arrow-left'))
    if gvg('fromtask'):
        BackProjectBtn = "<a href='/Task/Question/{}' class='btn btn-default btn-primary'>{} Back to importation task</a> ".format(
            int(gvg('fromtask')), FAIcon('arrow-left'))

    g.taxoserver_url = get_taxoserver_url()

    return PrintInCharte(render_template('taxonomy/browse.html',
                                         BackProjectBtn=BackProjectBtn,
                                         create_ok=is_admin_or_project_creator(user)))


def request_withinstanceinfo(urlend, params):
    """
        Issue a REST query on EcoTaxoServer
    """
    params['id_instance'] = app.config.get('TAXOSERVER_INSTANCE_ID')
    params['sharedsecret'] = app.config.get('TAXOSERVER_SHARED_SECRET')
    params['ecotaxa_version'] = appli.ecotaxa_version

    r = requests.post(get_taxoserver_url() + urlend, params)
    return r.json()


def DoSyncStatUpdate():
    """
        Update EcoTaxoServer with statistics about current node usage.
    """
    with ApiClient(TaxonomyTreeApi, request) as api:
        ret = api.push_taxa_stats_in_central_taxa_stats_push_to_central_get()
    return ret["msg"]


@app.route('/taxo/dosync', methods=['POST'])
def routetaxodosync():
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    if not is_admin_or_project_creator(user):
        return PrintInCharte("Insufficient rights")
    return DoFullSync()


def DoFullSync():
    txt = ""
    try:
        UpdatableCols = ['parent_id', 'name', 'taxotype', 'taxostatus', 'id_source', 'id_instance', 'rename_to',
                         'display_name', 'source_desc', 'source_url', 'creation_datetime', 'creator_email']
        MaxUpdate = database.GetAll(
            "select coalesce(max(lastupdate_datetime),to_timestamp('2000-01-01','YYYY-MM-DD')) lastupdate from taxonomy")
        MaxUpdateDate = MaxUpdate[0]['lastupdate']

        j = request_withinstanceinfo("/gettaxon/", {'filtertype': 'since', 'startdate': MaxUpdateDate})
        if 'msg' in j:
            return appli.ErrorFormat("Sync Error :" + j['msg'])
        NbrRow = len(j)
        NbrUpdate = NbrInsert = 0
        txt += "Received {} rows<br>".format(NbrRow)
        if (NbrRow > 0):
            txt += "Taxo 0 = {}<br>".format(j[0])
        for jtaxon in j:
            taxon = database.Taxonomy.query.filter_by(id=int(jtaxon['id'])).first()
            lastupdate_datetime = datetime.datetime.strptime(jtaxon['lastupdate_datetime'], '%Y-%m-%d %H:%M:%S')
            if taxon:
                if taxon.lastupdate_datetime == lastupdate_datetime:
                    continue  # already up to date
                NbrUpdate += 1
            else:
                if ntcv(jtaxon['rename_to']) != '':
                    continue  # don't insert taxon that should be renamed
                if ntcv(jtaxon['taxostatus']) == 'D':
                    continue  # don't insert taxon that are deprecated and planned to be deleted
                NbrInsert += 1
                taxon = database.Taxonomy()
                taxon.id = int(jtaxon['id'])
                db.session.add(taxon)

            for c in UpdatableCols:
                setattr(taxon, c, jtaxon[c])
            taxon.lastupdate_datetime = lastupdate_datetime
            db.session.commit()
        # Manage rename_to
        sqlbase = "with taxorename as (select id,rename_to from taxonomy where rename_to is not null) "
        sql = sqlbase + """select distinct obj.projid from objects obj join taxorename tr on obj.classif_id=tr.id """
        ProjetsToRecalc = database.GetAll(sql)
        sql = sqlbase + """update obj_head obh set classif_id=tr.rename_to 
              from taxorename tr  where obh.classif_id=tr.id """
        NbrRenamedObjects = ExecSQL(sql)
        sql = sqlbase + """update obj_head obh set classif_auto_id=tr.rename_to 
              from taxorename tr  where obh.classif_auto_id=tr.id """
        ExecSQL(sql)
        sql = sqlbase + """update objectsclassifhisto och set classif_id=tr.rename_to 
              from taxorename tr  where och.classif_id=tr.id """
        ExecSQL(sql)
        # on efface les taxon qui doivent être renommés car ils l'ont normalement été
        sql = """delete from taxonomy where rename_to is not null """
        ExecSQL(sql)
        sql = """delete from taxonomy t where taxostatus='D' 
                  and not exists(select 1 from projects_taxo_stat where id=t.id) """
        ExecSQL(sql)
        # il faut recalculer projects_taxo_stat et part_histocat,part_histocat_lst pour ceux qui referencaient un
        # taxon renomé et donc disparu
        if NbrRenamedObjects > 0:
            # cron.RefreshTaxoStat() operation trés longue (env 5 minutes en prod, il faut être plus selectif)
            # permet de recalculer projects_taxo_stat
            for Projet in ProjetsToRecalc:
                RecalcProjectTaxoStat(Projet['projid'])
            # recalcul part_histocat,part_histocat_lst
            appli.part.prj.GlobalTaxoCompute()

        flash("Received {} rows,Insertion : {} Update :{}".format(NbrRow, NbrInsert, NbrUpdate), "success")
        if gvp('updatestat') == 'Y':
            msg = DoSyncStatUpdate()
            flash("Taxon statistics update : " + msg, "success" if msg == 'ok' else 'error')

        # txt="<script>location.reload(true);</script>" # non car ça reprovoque le post de l'arrivée initiale
        txt = "<script>window.location=window.location;</script>"
    except:
        msg = "Error while syncing {}".format(sys.exc_info())
        app.logger.error(msg)
        txt += appli.ErrorFormat(msg)

    return txt

# Below fields are not provided via back-end API call, because they are useless in most contexts
FIELDS_IN_CENTRAL_ONLY = ["source_url", "source_desc", "creator_email", "creation_datetime"]


@app.route('/taxo/view/<int:taxoid>')
def route_view_taxon(taxoid):
    """
        View the local taxon.
    """
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    # Get local data
    with ApiClient(TaxonomyTreeApi, request) as api:
        taxon: TaxonModel = api.query_taxa_taxon_taxon_id_get(taxon_id=taxoid)
    # Complete with centralized info
    with ApiClient(TaxonomyTreeApi, request) as api:
        on_central = api.get_taxon_in_central_taxon_central_taxon_id_get(taxon_id=taxoid)
    for a_field in FIELDS_IN_CENTRAL_ONLY:
        setattr(taxon, a_field, on_central[0][a_field])
    g.TaxoType = database.TaxoType
    g.taxoserver_url = get_taxoserver_url()
    return render_template('taxonomy/edit.html', taxon=taxon)


@app.route('/taxo/new')
def route_add_taxon():
    """
        Creation of a new taxon, step 0 initial form.
    """
    # Security barrier...
    # We don't write anything so we could display the form and wait for the "save" to fail.
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    if not is_admin_or_project_creator(user):
        return PrintInCharte("Insufficient rights")
    # Create a blank taxon
    taxon = {'id': 0, 'creator_email': user.email, 'tree': '', 'creation_datetime': ''}
    g.TaxoType = database.TaxoType
    g.taxoserver_url = get_taxoserver_url()
    return render_template('taxonomy/edit.html', taxon=taxon)


@app.route('/taxo/save/', methods=['POST'])
def route_save_taxon():
    """
        Saving of the centralized taxon.
        Collect data from the form and send to back-end, which will relay to centralized server.
    """
    try:
        params = {}
        for c in ['parent_id', 'name', 'taxotype', 'source_desc', 'source_url', 'creator_email']:
            params[c] = gvp(c)
        with ApiClient(TaxonomyTreeApi, request) as api:
            crea_rsp = api.add_taxon_in_central_taxon_central_put(**params)
        if crea_rsp['msg'] != 'ok':
            return appli.ErrorFormat("settaxon Error :" + crea_rsp['msg'])
        txt = """<script> DoSync(); At2PopupClose(0); </script>"""
        return txt
    except Exception as e:
        import traceback
        tb_list = traceback.format_tb(e.__traceback__)
        return appli.FormatError("Saving Error : {}\n{}", e, "__BR__".join(tb_list[::-1]))
