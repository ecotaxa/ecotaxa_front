from flask import request, render_template, make_response
from flask_login import login_required
from appli import app, gvg
from appli.gui.commontools import is_partial_request
from appli.gui.collection.settings import collection_about

@app.route("/gui/collection/noright/<int:collection_id>")
# TODO - fresh_login_required
@login_required
def gui_collection_noright(collection_id):
    return render_template("v2/collection/noright.html", collection=collection_id)


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
def gui_collection_aggregated():
    from appli.gui.collection.settings import collection_aggregated

    project_ids = gvg("project_ids")
    simulate = gvg("simulate", "")
    aggregated = collection_aggregated(project_ids, simulate)
    if simulate == "y":
        import json

        return json.dumps(aggregated)
    else:
        partial = is_partial_request()
        return render_template(
            "v2/collection/_settings_aggregated.html", agg=aggregated, partial=partial
        )

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


@app.route("/gui/collection/erase/<int:collection_id>", methods=["GET", "POST"])
# TODO - fresh_login_required
@login_required
def gui_collection_erase(collection_id):
    from appli.gui.collection.settings import collection_erase

    erase = False
    if request.method == "POST":
        erase = True
    return collection_erase(collection_id, erase=erase)


@app.route("/gui/collection/about/<int:collection_id>", methods=["GET"])
@login_required
def gui_collection_about(collection_id):
    partial = is_partial_request()

    return collection_about(collection_id, partial=partial)
