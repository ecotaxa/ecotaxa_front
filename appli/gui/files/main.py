import flask
from flask import request, render_template
from flask_login import login_required
from appli import app, gvp
from appli.gui.commontools import make_response


@app.route("/gui/files/upload", methods=["POST"])
@login_required
def gui_files_upload():
    from appli.gui.files.tools import upload_file

    response = upload_file()
    return response


@app.route("/gui/files/list", defaults={"subpath": None}, methods=["GET"])
@app.route("/gui/files/list/<path:subpath>", methods=["GET"])
@login_required
def gui_files_dirlist(subpath: str = None):
    from appli.gui.files.tools import dir_list
    from appli.gui.commontools import todict

    dirlist, err = dir_list(subpath)
    response = todict(dirlist)
    return response


@app.route("/gui/files/create", methods=["POST"])
@login_required
def gui_files_create() -> str:
    entry = gvp("entry", None)
    if entry == None:
        return ""
    from appli.gui.files.tools import create_dir_file

    ret = create_dir_file(entry)
    return make_response(200, ret)


@app.route("/gui/files/remove", methods=["POST"])
@login_required
def gui_files_remove() -> int:
    entry = gvp("entry", None)
    if entry == None:
        return 1
    from appli.gui.files.tools import remove_dir_file

    ret = remove_dir_file(entry)
    return make_response(200, ret)


@app.route("/gui/files/rename", methods=["POST"])
@app.route("/gui/files/move", methods=["POST"])
@login_required
def gui_files_move() -> str:
    entry = gvp("entry", None)
    dest = gvp("dest", None)
    if entry == None or dest == None:
        return None
    from appli.gui.files.tools import move_dir_file

    ret = move_dir_file(entry, dest)
    return make_response(200, ret)
