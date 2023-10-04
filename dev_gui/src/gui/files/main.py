import flask
from flask import request, render_template
from flask_login import login_required
from appli import app, gvp


@app.route("/gui/files/upload", defaults={"sub_path": ""}, methods=["POST"])
@app.route("/gui/files/upload/<path:sub_path>", methods=["POST"])
@login_required
def gui_files_upload(sub_path: str = ""):
    from appli.gui.files.tools import upload_file

    print("----UPLOAD--")
    print(sub_path)
    if sub_path == "":
        sub_path = "/ecotaxa_import"
    else:
        sub_path = "/ecotaxa_import/" + sub_path

    response = upload_file(sub_path)
    print(response)
    return response


@app.route("/gui/files/list", defaults={"sub_path": ""}, methods=["GET"])
@app.route("/gui/files/list/<path:sub_path>", methods=["GET"])
@login_required
def gui_files_dirlist(sub_path: str = ""):
    if request.method == "GET":
        from appli.gui.files.tools import dir_list

        if sub_path == "":
            sub_path = "/ecotaxa_import"
        else:
            sub_path = "/ecotaxa_import/" + sub_path
            print("------")
            print(sub_path)
        dirlist, err = dir_list(sub_path)
        from appli.gui.commontools import todict

        response = todict(dirlist)
    return response
