# -*- coding: utf-8 -*-
from json import JSONEncoder
from typing import List
from flask import render_template, json, flash, request, make_response,url_for
from flask_login import current_user, login_required
from appli import app, gvg
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import TaxonModel


@login_required
@app.route("/gui/search/taxotreejson")
def gui_taxotree_root_json():
    parent = gvg("id", "")
    if parent == "#":
        # Root nodes
        with ApiClient(TaxonomyTreeApi, request) as api:
            roots: List[TaxonModel] = api.query_root_taxa()
        res = [
            (
                r.id,
                r.name,
                None,
                r.nb_objects + r.nb_children_objects,
                len(r.children) > 0,
                r.status
            )
            for r in roots
        ]
    elif parent.strip() == "":
        res = []
    else:
        # Children of the requested parent_id, when opening the tree
        # Fetch the parent for getting its children
        children_ids = ""
        with ApiClient(TaxonomyTreeApi, request) as api:
            parents: List[TaxonModel] = api.query_taxa_set(ids=str(parent))
        if len(parents):
            children_ids = "+".join([str(child_id) for child_id in parents[0].children])
        # Fetch children, for their names and to know if they have children
        with ApiClient(TaxonomyTreeApi, request) as api:
            children: List[TaxonModel] = api.query_taxa_set(ids=children_ids)
        res = [
            (
                r.id,
                r.name,
                parent,
                r.nb_objects + r.nb_children_objects,
                len(r.children) > 0,
                r.status
            )
            for r in children
        ]
    res.sort(key=lambda r: r[1])
    return json.dumps(
        [
            dict(
                id=str(r[0]),
                parent=r[2] or "#",
                name=r[1],
                num=r[3],
                children=r[4],
                status=r[5]
            )
            for r in res
        ]
    )


@login_required
@app.route("/gui/taxonomy/worms")
def gui_taxonomy_worms():
    return render_template("v2/taxonomy/worms.html")


@app.route("/gui/taxo/browse/", methods=["GET", "POST"])
@login_required
def gui_taxo_browse():
    """
    Browse, i.e. display local taxa. This is a dynamic API-based table.
    """
    do_full_sync(do_flash=True)
    fromurl = ""
    fromtext = ""
    if gvg("fromprj"):
        fromurl = url_for("gui_prj_classif", projid=gvg("fromprj"))
        fromtext = "Back to project %s" % gvg("fromprj")
    elif gvg("fromtask"):
        fromurl = url_for("gui_job_question", job_id=gvg("fromtask"))
        fromtext = "Back to importation task %s" % gvg("fromtask")

    return render_template(
        "/v2/taxonomy/browse.html",
        fromurl=fromurl,
        fromtext=fromtext,
        create_ok=_admin_or_project_creator(),
    )


def _admin_or_project_creator() -> bool:
    user = current_user.api_user
    return (1 in user.can_do) or (2 in user.can_do)



def do_full_sync(do_flash: bool):
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
