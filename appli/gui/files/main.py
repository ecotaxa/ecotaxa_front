import flask
from flask import request, render_template
from flask_login import login_required
from appli import app, gvp


@app.route("/gui/files/upload", defaults={"subpath": None}, methods=["POST"])
@app.route("/gui/files/upload/<path:subpath>", methods=["POST"])
@login_required
def gui_files_upload(subpath: str = None):
    from appli.gui.files.tools import upload_file

    response = upload_file(subpath)
    return response


@app.route("/gui/files/list", defaults={"subpath": None}, methods=["GET"])
@app.route("/gui/files/list/<path:subpath>", methods=["GET"])
@login_required
def gui_files_dirlist(subpath: str = None):
    if request.method == "GET":
        from appli.gui.files.tools import dir_list

        dirlist, err = dir_list(subpath)
        from appli.gui.commontools import todict

        response = todict(dirlist)
    return response
