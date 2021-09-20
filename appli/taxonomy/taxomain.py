from typing import Optional

import requests
from flask import render_template, g, flash, request

import appli
import appli.part.prj
import appli.project.main
from appli import app, PrintInCharte, database, gvg, gvp, FAIcon
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import UsersApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import UserModelWithRights, TaxonModel


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
    DoFullSync(do_flash=True)
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
    sync_msg = DoFullSync(do_flash=False)
    return sync_msg


def DoFullSync(do_flash:bool):
    with ApiClient(TaxonomyTreeApi, request) as api:
        ret = api.pull_taxa_update_from_central_taxa_pull_from_central_get()
    if ret["error"]:
        msg = str(ret["error"])
        if do_flash:
            flash(msg, "error")
    else:
        ins, upd = ret["inserts"], ret["updates"]
        if ins != 0 or upd != 0:
            msg = "Taxonomy is now in sync, after {} addition(s) and {} update(s).".format(ins, upd)
        else:
            msg = "No update needed, Taxonomy was in sync already."
        if do_flash:
            flash(msg, "success")
    return msg


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
    # Complete again with usage info
    with ApiClient(TaxonomyTreeApi, request) as api:
        usage = api.query_taxa_usage_taxon_taxon_id_usage_get(taxon_id=taxoid)
        usage = usage[:20]
    g.TaxoType = database.TaxoType
    g.taxoserver_url = get_taxoserver_url()
    return render_template('taxonomy/edit.html', taxon=taxon, usage=usage)


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
