import json
from typing import Optional, List, Any

from flask import render_template, g, flash, request
from flask_login import current_user

import appli
import appli.project.main
from appli import app, PrintInCharte, gvg, gvp, FAIcon
from appli.back_config import get_back_constants
from appli.constants import TaxoType
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import AddWormsTaxonModel
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import UserModelWithRights, TaxonModel


def get_taxoserver_url():
    return get_back_constants("TAXOSERVER_URL")


def get_login() -> Optional[UserModelWithRights]:
    # current_user is either an ApiUserWrapper or an anonymous one from flask
    if current_user.is_authenticated:
        return current_user.api_user
    return None


def is_admin_or_project_creator(user: UserModelWithRights) -> bool:
    return (1 in user.can_do) or (2 in user.can_do)


@app.route("/taxo/browse/", methods=["GET", "POST"])
def routetaxobrowse():
    """
    Browse, i.e. display local taxa. This is a dynamic API-based table.
    """
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    BackProjectBtn = ""
    DoFullSync(do_flash=True)
    if gvg("fromprj"):
        BackProjectBtn = "<a href='/prj/{}' class='btn btn-default btn-primary'>{} Back to project</a> ".format(
            int(gvg("fromprj")), FAIcon("arrow-left")
        )
    if gvg("fromtask"):
        BackProjectBtn = "<a href='/Task/Question/{}' class='btn btn-default btn-primary'>{} Back to importation task</a> ".format(
            int(gvg("fromtask")), FAIcon("arrow-left")
        )

    g.taxoserver_url = get_taxoserver_url()

    return PrintInCharte(
        render_template(
            "taxonomy/browse.html",
            BackProjectBtn=BackProjectBtn,
            create_ok=is_admin_or_project_creator(user),
        )
    )


def DoSyncStatUpdate():
    """
    Update EcoTaxoServer with statistics about current node usage.
    """
    with ApiClient(TaxonomyTreeApi, request) as api:
        ret = api.push_taxa_stats_in_central()
    return ret["msg"]


@app.route("/taxo/search/<name>", methods=["GET"])
def routetaxosearch(name) -> List[Any]:
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    with ApiClient(TaxonomyTreeApi, request) as api:
        results = api.search_taxa(name + "*")
        renames = list(set([str(r.renm_id) for r in results if r.renm_id is not None]))
        taxons = [
            {
                "id": r.id,
                "aphia_id": r.aphia_id,
                "name": r.text,
            }
            for r in results
            if r.renm_id == 0 or r.renm_id is None
        ]

        def get_renames(arr, taxons):
            rsp = api.query_taxa_set(",".join(arr))
            rnmtaxons = [
                {
                    "id": r.id,
                    "aphia_id": r.aphia_id,
                    "name": r.display_name,
                }
                for r in rsp
                if r.renm_id is None
            ]
            renames = list(set([str(r.renm_id) for r in rsp if r.renm_id is not None]))
            taxons.extend(rnmtaxons)
            if len(renames):
                get_renames(renames, taxons)
            return taxons

        if len(renames):
            taxons = get_renames(renames, taxons)
    return json.dumps(taxons)


@app.route("/taxo/searchworms/", methods=["GET"])
@app.route("/taxo/searchworms/<name>", methods=["GET"])
def routetaxosearchworms(name=""):
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    if not is_admin_or_project_creator(user):
        return PrintInCharte("Insufficient rights")
    if len(name) > 3:
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxons = api.search_worms_name(name)
    else:
        taxons = []

    return render_template("taxonomy/create.html", searchname=name, taxons=taxons)


@app.route("/taxo/addworms/", methods=["POST"])
def addtaxoworms():
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    if not is_admin_or_project_creator(user):
        return PrintInCharte("Insufficient rights")
    aphia_id = gvp("aphia_id")
    addtaxon = AddWormsTaxonModel(aphia_id=int(aphia_id))
    with ApiClient(TaxonomyTreeApi, request) as api:
        rsp = api.add_worms_taxon(addtaxon)
    with ApiClient(TaxonomyTreeApi, request) as api:
        # Ensure the new taxon flows to backend
        api.pull_taxa_update_from_central()
    return json.dumps(rsp)


@app.route("/taxo/dosync", methods=["POST"])
def routetaxodosync():
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    if not is_admin_or_project_creator(user):
        return PrintInCharte("Insufficient rights")
    sync_msg = DoFullSync(do_flash=False)
    return sync_msg


def DoFullSync(do_flash: bool):
    with ApiClient(TaxonomyTreeApi, request) as api:
        ret = api.pull_taxa_update_from_central()
    if ret["error"]:
        msg = str(ret["error"])
        if do_flash:
            flash(msg, "error")
    else:
        ins, upd = ret["inserts"], ret["updates"]
        if ins != 0 or upd != 0:
            msg = "Taxonomy is now in sync, after {} addition(s) and {} update(s).".format(
                ins, upd
            )
        else:
            msg = "No update needed, Taxonomy was in sync already."
        if do_flash:
            flash(msg, "success")
    return msg


# Below fields are not provided via back-end API call, because they are useless in most contexts
FIELDS_IN_CENTRAL_ONLY = [
    "source_url",
    "source_desc",
    "creator_email",
    "creation_datetime",
]


@app.route("/taxo/view/<int:taxoid>")
def route_view_taxon(taxoid):
    """
    View the local taxon.
    """
    user = get_login()
    if user is None:
        return PrintInCharte("Please login to access this page")
    # Get local data
    with ApiClient(TaxonomyTreeApi, request) as api:
        taxon: TaxonModel = api.query_taxa(taxon_id=taxoid)
    # Complete with centralized info
    with ApiClient(TaxonomyTreeApi, request) as api:
        on_central = api.get_taxon_in_central(taxon_id=taxoid)
    taxon = taxon.to_dict()  # booster gives read-only models
    taxon_on_central = on_central[0].to_dict()
    for a_field in FIELDS_IN_CENTRAL_ONLY:
        taxon[a_field] = taxon_on_central[a_field]
    # Complete again with usage info
    with ApiClient(TaxonomyTreeApi, request) as api:
        usage = api.query_taxa_usage(taxon_id=taxoid)
        usage = usage[:20]
    # Transform lineage into a list of HTML spans
    lineage = taxon["lineage"]
    lineage_status = taxon["lineage_status"]
    new_lineage = []
    sep = ''
    for i in range(len(lineage)):
        name = lineage[i]
        depre = ""
        if lineage_status[i] == "D":
            depre = ' class="deprecated"'
        new_lineage.append(f'{sep}<span{depre}>{name}</span>')
        sep = " < "
    taxon["lineage"] = new_lineage

    g.TaxoType = TaxoType
    return render_template("taxonomy/edit.html", taxon=taxon, usage=usage)


@app.route("/taxo/new")
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
    taxon = {"id": 0, "creator_email": user.email, "tree": "", "creation_datetime": ""}
    g.TaxoType = TaxoType
    return render_template("taxonomy/edit.html", taxon=taxon)


@app.route("/taxo/save/", methods=["POST"])
def route_save_taxon():
    """
    Saving of the centralized taxon.
    Collect data from the form and send to back-end, which will relay to centralized server.
    """
    try:
        params = {}
        for c in [
            "parent_id",
            "name",
            "taxotype",
            "source_desc",
            "source_url",
            "creator_email",
        ]:
            params[c] = gvp(c)
        try:
            with ApiClient(TaxonomyTreeApi, request) as api:
                crea_rsp = api.add_taxon_in_central(**params)
        except Exception as e:
            crea_rsp = {"msg": str(e)}
        if crea_rsp["msg"] != "ok":
            return appli.ErrorFormat("settaxon Error :" + crea_rsp["msg"])
        txt = """<script> DoSync(); At2PopupClose(0); </script>"""
        return txt
    except Exception as e:
        import traceback

        tb_list = traceback.format_tb(e.__traceback__)
        return appli.FormatError(
            "Saving Error : {}\n{}", e, "__BR__".join(tb_list[::-1])
        )
