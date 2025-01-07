from typing import List
from flask import flash, request, render_template, redirect, url_for, make_response
from flask_login import current_user, login_required, fresh_login_required
from werkzeug.exceptions import NotFound, Unauthorized, Forbidden
from appli import app, gvp, gvg
from appli.project import sharedfilter
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import CollectionsApi, ProjectsApi
from to_back.ecotaxa_cli_py.models import CollectionModel

from appli.gui.commontools import is_partial_request, py_get_messages
from appli.gui.collection.settings import get_collection
from appli.gui.staticlistes import py_messages


@app.route("/gui/collection/noright/<int:collection_id>")
# TODO - fresh_login_required
@login_required
def gui_collection_noright(collection_id):
    return render_template("v2/collection/noright.html", collection=collection)


@app.route("/gui/collection/<int:collection_id>", methods=["GET", "POST"])
# TODO - fresh_login_required
@login_required
def gui_collection_view(collection_id):
    from appli.gui.collection.settings import collection_edit

    return collection_edit(collection_id)


@app.route("/collection/", methods=["GET"])
@app.route("/gui/collection/", methods=["GET"])
@login_required
def gui_collection() -> str:
    partial = False

    from appli.gui.collection.collections_list import collections_list_page

    return collections_list_page(partial=partial)


@app.route("/gui/collectionlist/", methods=["GET"])
@login_required
def gui_collections_list() -> str:
    # gzip not really necessary - jsonifiy with separators
    import json
    from appli.gui.collection.collections_list import collections_list

    project_ids = gvg("project_ids", None)
    gz = gvg("gzip")
    gz = True
    content = json.dumps(
        collections_list(project_ids),
        separators=[",", ":"],
    ).encode("utf-8")
    encoding = "utf-8"
    if gz:
        import gzip

        content = gzip.compress(content, 7)
        encoding = "gzip"
    response = make_response(content)

    response.headers["Content-length"] = len(content)
    response.headers["Content-Encoding"] = encoding
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/gui/collection/create", methods=["GET", "POST"])
@login_required
def gui_collection_create():
    from appli.gui.collection.settings import collection_create

    return collection_create()


@app.route("/gui/collection/aggregated", methods=["GET"])
@login_required
def gui_collection_simulate():
    from appli.gui.collection.settings import collection_aggregated

    project_ids = gvg("project_ids")

    content = collection_aggregated(project_ids)
    import json

    ret = json.dumps(content)
    return ret


@app.route("/gui/collection/edit/<int:collection_id>", methods=["GET", "POST"])
# TODO - fresh_login_required
@login_required
def gui_collection_edit(collection_id):
    from appli.gui.collection.settings import collection_edit

    return collection_edit(collection_id)


@app.route("/gui/collection/<int:collection_id>", methods=["GET"])
# TODO - fresh_login_required
@login_required
def gui_collection_classify(collection_id):
    from appli.gui.collection.settings import collection_classify

    return collection_classify(collection_id)


@app.route("/gui/collection/export_darwin_core/<int:collection_id>", methods=["GET"])
# TODO - fresh_login_required
@login_required
def gui_collection_export_darwin_core(collection_id):
    from appli.gui.collection.settings import collection_export_darwin_core

    return collection_export_darwin_core(collection_id)


@app.route("/gui/collection/purge/<int:collection_id>", methods=["GET", "POST"])
# TODO - fresh_login_required
@login_required
def gui_collection_purge(collection_id):
    from appli.gui.collection.settings import collection_purge

    return collection_purge(collection_id)


@app.route("/gui/collection/about/<int:collection_id>", methods=["GET"])
@login_required
def gui_collection_about(collection_id):
    params = dict({"limit": "5000"})
    partial = is_partial_request(request)

    return collection_stats(projid, partial=partial, params=params)
