# -*- coding: utf-8 -*-
from json import JSONEncoder
from typing import List
from flask import render_template, json, jsonify, request, make_response
from flask_login import current_user, login_required
from appli import app, gvg, gvp
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import TaxaSearchRsp, TaxonModel


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
            )
            for r in res
        ]
    )


@login_required
@app.route("/gui/taxonomy/graph")
def gui_taxonomy_graph():
    import csv
    from pathlib import Path

    dirpath = "appli/static/gui/data/"
    csvpath = dirpath + "worms.csv"
    jsonpath = dirpath + "graphsmall_worms.json"

    if not Path(jsonpath).is_file():
        nodes = []
        data = {"nodes": [], "edges": []}
        {
            "nodes": [{"id": "node1"}, {"id": "node2"}],
            "edges": [{"source": "node1", "target": "node2"}],
        }
        with open(csvpath, encoding="utf-8") as csvf:
            csvreader = csv.DictReader(csvf)
            i = 0
            for rows in csvreader:
                key = rows["aphia_id"]
                data["nodes"].append({"id": key, "name": rows["name"]})
                i = i + 1
                nodes.append(key)
                if i == 10000:
                    break
            for rows in csvreader:
                key = rows["aphia_id"]
                if rows["parent_aphia_id"] != "NA" and key in nodes:
                    data["edges"].append(
                        {"source": key, "target": rows["parent_aphia_id"]}
                    )

        with open(jsonpath, "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(data, indent=4))
    with open(jsonpath, encoding="utf-8") as json_file:
        content = json_file.read()
    response = make_response(content)
    response.headers["Content-length"] = len(content)
    response.headers["Content-Encoding"] = "utf-8"
    response.headers["Content-Type"] = "application/json"
    return response


@login_required
@app.route("/gui/taxonomy/worms")
def gui_taxonomy_worms():
    return render_template("v2/taxonomy/worms.html")
