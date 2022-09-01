# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os
from typing import List
from flask import request, redirect, url_for, render_template
from flask_security import login_required
from flask_login import current_user
from appli import app, gvg, gvp


from to_back.ecotaxa_cli_py.exceptions import ApiException
from werkzeug.exceptions import HTTPException


@app.route("/gui")
@app.route("/gui/home")
@app.route("/gui/index")
def gui_index():
    from appli.gui.commontools import RenderTemplate, webstats

    wstats = webstats(app)
    if current_user.is_authenticated:
        filename = "index"
        bg = False
    else:
        filename = "login"
        bg = True
    return RenderTemplate(filename, webstats=wstats, bg=bg)


@app.route("/gui/login")
@app.route("/gui/login/")
def gui_login() -> str:
    if current_user.is_authenticated:
        return redirect("/gui/prj")
    from appli.gui.commontools import RenderTemplate, webstats

    wstats = webstats(app)
    return render_template("v2/login.html", webstats=wstats, bg=True)


@app.route("/gui/about")
@app.route("/gui/about/")
def gui_about() -> str:
    from appli.gui.staticlistes import sponsors

    return render_template("v2/about.html", sponsors=sponsors, bg=True)


@app.route("/gui/privacy")
@app.route("/gui/privacy/")
def gui_privacy() -> str:
    google_analytics_id = app.config.get("GOOGLE_ANALYTICS_ID", "")
    cookieGAOK = request.cookies.get("GAOK", "")
    return render_template(
        "v2/privacy.html",
        cookieGAOK=cookieGAOK,
        google_analytics_id=google_analytics_id,
    )
    return render_template("v2/privacy.html")


@app.route("/gui/prj/", methods=["GET"])
@login_required
def gui_prj(listall: bool = False) -> str:
    partial = gvg("partial")
    partial = partial == "true"

    from appli.gui.commontools import last_taxo_refresh

    last_taxo_refresh(partial)
    from appli.gui.project.projects_list import projects_list

    return projects_list(listall=listall, partial=partial)


@app.route("/gui/prj/create", methods=["GET", "POST"])
@login_required
def gui_prj_create():
    from appli.gui.project.projectsettings import prj_create

    return prj_create()


@app.route("/gui/prj/edit/<int:prjid>", methods=["GET", "POST"])
@login_required
def gui_prj_edit(prjid):
    from appli.gui.project.projectsettings import prj_edit

    return prj_edit(prjid)


@app.route("/gui/prj/listall", methods=["GET"])
@app.route("/gui/prj/listall/", methods=["GET"])
@login_required
def gui_prj_all():
    filt_subset = gvg("filt_subset")  # Get subset filter from posted
    return gui_prj(listall=True)


@app.route("/gui/prj/about/<int:prjid>")
@login_required
def gui_prj_about(prjid):
    partial = gvg("partial")
    partial = partial == "true"

    from appli.gui.project.project_stats import prj_stats

    params = {"limit": "5000"}
    return prj_stats(prjid, partial, params)


@app.route("/gui/prj/importsettings", methods=["GET", "POST"])
@login_required
def gui_importsettings(prjid: int = 0):
    prjid = gvg("prjid")
    typeimport = gvg("typeimport")

    if typeimport == "taxo":
        from appli.gui.project.projectsettings import prj_import_taxo

        return prj_import_taxo(prjid)

    else:
        from appli.gui.project.projects_list import projects_list

        return projects_list(
            listall=False, partial=True, action="importsettings", typeimport=typeimport
        )


# taxo search taxo by IDs
@app.route("/gui/search/taxoset", methods=["GET", "POST"])
@app.route("/gui/search/taxoset/", methods=["GET", "POST"])
@login_required
def gui_search_taxoset():
    ids = gvp("ids")
    if len(ids):
        from appli.gui.search.search_taxo import search_taxoset

        return search_taxoset(ids)
    else:
        return None


# help
@app.route("/gui/help/<path:filename>")
@login_required
def gui_help(filename):
    from os.path import exists

    if filename[0:1] != "_":
        return render_template(".v2/help.html", filename=filename)
    filename = "/v2/help/" + filename + ".html"
    if not exists("appli/templates" + filename):
        return render_template(
            "./v2/partials/_error.html", title="404", message=filename + "not found"
        )
    return render_template("." + filename, partial=True)


# alert boxes xhr
@app.route("/gui/alertbox", methods=["GET", "POST"])
def gui_alert():
    from appli import gvp
    import uuid
    from appli.gui.commontools import get_error_message

    id = str(uuid.uuid1())
    inverse = gvp("inverse")
    dismissible = gvp("dismissible")
    if inverse == "true":
        inverse = True
    else:
        inverse = False
    if dismissible == "true":
        dismissible = True
    else:
        dismissible = False
    message = get_error_message(gvp("message"))
    return render_template(
        "v2/partials/_alertbox.html",
        type=gvp("type"),
        title=gvp("title"),
        message=message,
        inverse=inverse,
        dismissible=dismissible,
        extra=gvp("extra"),
        partial=True,
        relid=id,
    )


@app.route("/gui/<path:filename>")
@login_required
def gui_other(filename):
    filename = filename.replace("/", "")
    if os.path.isfile("v2/" + filename):
        return render_template("v2/" + filename)
    elif os.path.isfile("v2/_" + filename):
        return render_template("v2/_" + filename)
    else:
        return render_template(
            "v2/error.html", title="404", message=_("The page does not exists.")
        )


# push special infos to admins ( daily maintenance credentials expired to begin with)
def nightly_jobs_stream(type=None, user_id=None):
    from to_back.ecotaxa_cli_py.api import AdminApi
    from appli.utils import ApiClient
    import json, datetime

    format = "%Y-%m-%d"
    pgformat = "YYYY-MM-DD"
    dt = datetime.date.today().strftime(format)
    sql = (
        "SELECT job.type,job.state,job.creation_date,job.owner_id FROM job WHERE to_char(job.creation_date,'"
        + pgformat
        + "') != '"
        + dt
        + "'"
    )
    if type != None:
        sql += " AND job.type NOT LIKE '" + type + "'"
    if user_id != None:
        sql += " AND job.owner_id != " + user_id

    with ApiClient(AdminApi, request) as api:
        res = api.db_direct_query(q=sql)
        return json.dumps(res["data"])


@app.route("/adminstream/", methods=["GET", "POST"])
@login_required
def gui_stream():
    from to_back.ecotaxa_cli_py.models import UserModelWithRights

    user: UserModelWithRights = current_user.api_user
    if user and (2 in user.can_do):
        return nightly_jobs_stream(type="NightlyMaintenance", user_id=None)
    return ""


# utility display functions for jinja template
@app.context_processor
def utility_processor():
    def format_all(value, f="number", locale="fr_FR"):

        if f == "number":
            if value == None:
                return "0"
            return "{0:0.0f}".format(value)
            # return format_number(number, format, locale)
        elif f == "decimal":
            if value == None:
                return ""
            elif int(value) == 100 or int(value) == 0:
                return "{0:0.0f}".format(value)
            return "{0:0.2f}".format(value)

        elif f == "html":
            if value == None:
                return ""
            return value.replace("<", "&#60;")

        else:
            return number

    return dict(format_all=format_all)


@app.errorhandler(ApiException)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    # non-HTTP exceptions only
    return (
        render_template("./v2/error.html", title=e.status, message=e.reason),
        e.status,
    )
