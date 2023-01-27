# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os
from typing import List
from flask import request, url_for, render_template
from flask_security import login_required
from flask_login import current_user
from appli import app, gvg, gvp

from to_back.ecotaxa_cli_py.exceptions import ApiException
from werkzeug.exceptions import HTTPException
from flask_babel import _
from appli.gui.staticlistes import py_messages

import appli.gui.jobs.main


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
    # if current_user.is_authenticated:
    #    return redirect("/gui/prj")
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

    return render_template("v2/privacy.html")


@app.route("/gui/prj/", methods=["GET"])
@login_required
def gui_prj(listall: bool = False) -> str:
    partial = False

    from appli.gui.commontools import last_taxo_refresh

    last_taxo_refresh(partial)
    from appli.gui.project.projects_list import projects_list_page

    return projects_list_page(listall=listall, partial=partial)


@app.route("/gui/prjlist/", methods=["GET"])
@login_required
def gui_prjlist(listall: bool = False) -> str:
    # gzip not really necessary - jsonifiy with separators
    from flask import make_response
    import json
    from appli.gui.project.projects_list import projects_list

    typeimport = gvg("typeimport")
    gz = gvg("gzip")

    content = json.dumps(
        projects_list(listall=listall, typeimport=typeimport), separators=[",", ":"]
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


@app.route("/gui/prj/importsettings", methods=["GET", "POST"])
@login_required
def gui_importsettings(prjid: int = 0) -> str:
    typeimport = gvg("typeimport")
    from appli.gui.project.projects_list import projects_list_page

    partial = request.headers.get("X-Requested-With") and (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )
    return projects_list_page(listall=False, partial=partial, typeimport=typeimport)


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
    return gui_prj(listall=True)


@app.route("/gui/prj/about/<int:prjid>")
@login_required
def gui_prj_about(prjid):
    from appli.gui.project.project_stats import prj_stats

    params = dict({"limit": "5000"})
    partial = request.headers.get("X-Requested-With") and (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )

    return prj_stats(prjid, partial=partial, params=params)


@app.route("/gui/prjsamplestats/<int:prjid>")
@login_required
def gui_prj_aboutsamples(prjid):
    from flask import make_response
    import json
    from appli.gui.project.project_stats import prj_samples_stats

    partial = request.headers.get("X-Requested-With") and (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )
    format = gvg("format", "json")
    content = prj_samples_stats(prjid, partial=partial, format=format)
    if format == "json":
        content = json.dumps(content, separators=[",", ":"]).encode("utf-8")
        encoding = "utf-8"
        response = make_response(content)
        response.headers["Content-length"] = len(content)
        response.headers["Content-Encoding"] = encoding
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        return content


# help
@app.route("/gui/help/<path:filename>")
@login_required
def gui_help(filename):
    from os.path import exists
    from markupsafe import escape

    filename = escape(filename)
    if filename[0:1] != "_":
        return render_template(".v2/help.html", filename=filename)
    filename = "/v2/help/" + filename + ".html"
    if not exists("appli/templates" + filename):
        return render_template(
            "./v2/partials/_error.html",
            title="404",
            message=py_messages["notfound"] + filename,
        )
    partial = request.headers.get("X-Requested-With") and (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )
    return render_template("." + filename, partial=partial)


# alert boxes xhr
@app.route("/gui/alertbox", methods=["GET", "POST"])
def gui_alert():
    from appli import gvp
    from appli.gui.staticlistes import py_messages

    inverse = gvp("inverse")
    dismissible = gvp("dismissible")
    codemessage = gvp("codemessage")
    if inverse == "true":
        inverse = True
    else:
        inverse = False
    if dismissible == "true":
        dismissible = True
    else:
        dismissible = False
    message = gvp("message")

    return render_template(
        "v2/partials/_alertbox.html",
        type=gvp("type"),
        title=gvp("title"),
        message=message,
        codemessage=codemessage,
        inverse=inverse,
        dismissible=dismissible,
        extra=gvp("extra"),
        partial=True,
    )


@app.route("/gui/<path:filename>")
@login_required
def gui_other(filename):
    from markupsafe import escape

    filename = escape(filename)
    filename = filename.replace("/", "")
    if os.path.isfile("v2/" + filename):
        return render_template("v2/" + filename)
    elif os.path.isfile("v2/_" + filename):
        return render_template("v2/_" + filename)
    else:
        return render_template(
            "v2/error.html", title="404", message=py_messages["page404"]
        )


# @app.route("/gui/adminstream/", methods=["GET", "POST"])
@app.route("/gui/jobssummary/", methods=["GET", "POST"])
@login_required
def gui_stream():
    from appli.gui.commontools import jobs_summary_data

    return render_template(
        "./v2/partials/_notifications.html", notifs=jobs_summary_data()
    )


# utility display functions for jinja template
@app.template_filter("urlencode")
def urlencode_filter(s):
    import urllib
    from markupsafe import Markup

    if type(s) == "Markup":
        s = s.unescape()
    s = s.encode("utf8")
    s = urllib.parse.quote_plus(s)
    return Markup(s)


@app.context_processor
def utility_processor():
    def message_translation(message: str, type: str, is_safe: bool = False) -> dict:
        from appli.gui.staticlistes import py_messages

        if message in py_messages:
            return py_messages[message]
        if is_safe:
            return message
        return type

    def unique_id():
        import uuid

        return str(uuid.uuid1())

    def def_language():
        from appli import get_locale

        return get_locale()

    def g_status(key: str = None) -> dict:
        # vars for google and other global data previously stored in g
        g_data = dict(
            {
                "google_analytics_id": app.config.get("GOOGLE_ANALYTICS_ID", ""),
                "cookieGAOK": request.cookies.get("GAOK", ""),
            }
        )
        if key != None:
            if key in g_data:
                return g_data[key]
            else:
                return ""
        return g_data

    def gui_breadcrumbs() -> list:
        from appli.gui.commontools import breadcrumbs

        return breadcrumbs()

    return dict(
        message_translation=message_translation,
        unique_id=unique_id,
        breadcrumbs=gui_breadcrumbs,
        g_status=g_status,
        def_language=def_language,
    )


@app.errorhandler(ApiException)
def handle_exception(e):
    # pass through HTTP errors

    if isinstance(e, HTTPException):
        return e
    # non-HTTP exceptions only
    partial = request.headers.get("X-Requested-With") and (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )
    return (
        render_template(
            "./v2/error.html",
            title=e.status,
            partial=partial,
            message=e.reason,
            is_safe=True,
        ),
        e.status,
    )
