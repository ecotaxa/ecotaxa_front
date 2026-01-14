# -*- coding: utf-8 -*-
from json import JSONEncoder
from typing import List

from flask import render_template, json, jsonify, request

from appli import app, gvg, gvp
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import TaxaSearchRsp, TaxonModel


# Specialize an encoder for serializing directly the back-end response
class BackEndJSONEncoder(JSONEncoder):
    def default(self, o):
        try:
            return o.to_dict()
        except TypeError:
            return JSONEncoder.default(self, o)


@app.route("/search/taxo")
def searchtaxo():
    term = gvg("q")
    prj_id = gvg("projid")
    if not prj_id:
        prj_id = -1
    # Relay to back-end
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxaSearchRsp] = api.search_taxa(query=term, project_id=prj_id)
    # TODO: temporary until the HTML goes to /api directly
    # Filter out taxa to rename
    res = [a_taxon for a_taxon in res if a_taxon.renm_id is None and a_taxon.status!='D']
    return json.dumps(res, cls=BackEndJSONEncoder)


@app.route("/search/taxotree")
def searchtaxotree():
    # Return an initial template with root of the taxonomy tree
    # Does nothing except rendering the template with targetid
    return render_template("search/taxopopup.html", targetid=gvg("target", "taxolb"))


@app.route("/search/taxotreejson")
def taxotreerootjson():
    parent = gvg("id")
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
            )
            for r in roots
        ]
    else:
        # Children of the requested parent_id, when opening the tree
        # Fetch the parent for getting its children
        with ApiClient(TaxonomyTreeApi, request) as api:
            parents: List[TaxonModel] = api.query_taxa_set(ids=str(parent))
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
            )
            for r in children
        ]
    res.sort(key=lambda r: r[1])

    def span_for_node(rec):
        return (
            "<span class=v>"
            + rec[1]
            + "</span> ("
            + str(rec[3])
            + ") "
            + "<span class='TaxoSel label label-default'><span class='glyphicon glyphicon-ok'></span></span>"
        )

    return json.dumps(
        [
            dict(id=str(r[0]), text=span_for_node(r), parent=r[2] or "#", children=r[4])
            for r in res
        ]
    )


@app.route("/search/taxoresolve", methods=["POST"])
def taxoresolve():
    # Called from modal "Pick preset from other projects" when Close is clicked.
    # As it's possible to enter numerical taxa IDs, and the buttons to get settings from projects
    # put numerical IDs there, the lookup will be done for setting the destination select with taxa display names.
    idlist = gvp("idlist", "")
    lst = [int(x) for x in idlist.split(",") if x.isdigit()]
    node_ids = "+".join([str(x) for x in lst])
    with ApiClient(TaxonomyTreeApi, request) as api:
        nodes: List[TaxonModel] = api.query_taxa_set(ids=node_ids)
    # The sort below is a bit useless as the control (select2) has its own order
    nodes.sort(key=lambda r: r.display_name.lower())
    taxomap = {a_node.id: a_node.display_name for a_node in nodes}
    return jsonify(taxomap)
