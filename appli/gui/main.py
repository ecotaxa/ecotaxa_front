# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os
from typing import List
from flask import request, url_for, render_template, flash, redirect
from flask_security import login_required
from flask_login import current_user
from appli import app, gvg, gvp, constants
from appli.gui.commontools import is_partial_request
from to_back.ecotaxa_cli_py.exceptions import ApiException
from werkzeug.exceptions import HTTPException
from flask_babel import _
from appli.gui.staticlistes import py_messages


@app.route("/gui")
@app.route("/gui/")
@app.route("/gui/home")
@app.route("/gui/index")
def gui_index():
    if current_user.is_authenticated:
        return gui_prj()
    else:
        return gui_login()


@app.route(
    "/gui/forgotten", defaults={"instid": None, "token": None}, methods=["GET", "POST"]
)
@app.route(
    "/gui/forgotten/", defaults={"instid": None, "token": None}, methods=["GET", "POST"]
)
@app.route("/gui/forgotten/<instid>", defaults={"token": None}, methods=["GET", "POST"])
@app.route("/gui/forgotten/<instid>/<token>", methods=["GET", "POST"])
def gui_forgotten(instid=None, token=None) -> str:
    err = None
    email = None
    sentmail = gvg("sentmail", None)
    if instid == None and token == None:
        if request.method == "POST":
            email = gvp("request_email", None)
            if email != None:
                from appli.gui.users.commontools import (
                    send_mail,
                    reset_password_message,
                )

                msg = reset_password_message(email)
                err = send_mail(email, msg)
                if err == None:
                    return redirect(url_for("gui_forgotten", sentmail=email))
                else:
                    flash(err, "error")
                    return redirect(url_for("gui_forgotten"))
    elif instid != None and token != None:
        if request.method == "POST":
            from appli.gui.users.commontools import reset_password

            email = get_mail_from_token(token, True)
            if email == False:
                return redirect(url_for("gui_forgotten"))
            pwd = gvp("request_pwd")
            if pwd != None:
                [redir, err] = reset_password(email, token, pwd)
                if err == None:
                    return redirect(url_for(redir))

        elif token != None:
            from appli.gui.users.commontools import get_mail_from_token

            if get_mail_from_token(token, True) == False:
                token = None

    return render_template("v2/security/forgotten.html", bg=True, token=token)


@app.route("/gui/login", methods=["GET", "POST"])
@app.route("/gui/login/", methods=["GET", "POST"])
def gui_login() -> str:
    # if current_user.is_authenticated:
    #    return redirect("/gui/prj")

    return render_template("v2/login.html", bg=True)


@app.route(
    "/gui/register", defaults={"instid": None, "token": None}, methods=["GET", "POST"]
)
@app.route(
    "/gui/register/", defaults={"instid": None, "token": None}, methods=["GET", "POST"]
)
@app.route("/gui/register/<instid>", defaults={"token": None}, methods=["GET", "POST"])
@app.route("/gui/register/<instid>/<token>", methods=["GET", "POST"])
def gui_register(instid=None, token=None) -> str:
    # if current_user.is_authenticated:
    # return redirect("/gui/prj")
    err = None
    email = None
    sentmail = gvg("sentmail", None)
    if instid == None and token == None:
        createaccount = False
        if request.method == "POST":
            # validate email
            email = gvp("register_email")
            from appli.gui.users.commontools import send_mail, validation_message

            msg = validation_message(email)
            err = send_mail(email, msg)
            if err == None:
                return redirect(url_for("gui_register", sentmail=email))
            else:
                flash(err, "error")
                return redirect(url_for("gui_register"))
    elif instid != None and token != None:
        createaccount = True
        if request.method == "POST":
            from appli.gui.users.commontools import user_create, ACCOUNT_USER_CREATE

            [redir, err] = user_create(-1, isfrom=None)
            if err == None:
                return redirect(url_for(redir))

        elif token != None:
            from appli.gui.users.commontools import account_page, ACCOUNT_USER_CREATE

            return account_page(
                action=ACCOUNT_USER_CREATE,
                usrid=-1,
                isfrom=None,
                template="v2/register.html",
                token=token,
            )

    return render_template(
        "v2/register.html",
        bg=True,
        sentmail=sentmail,
        createaccount=createaccount,
    )


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
def gui_prjlist() -> str:
    # gzip not really necessary - jsonifiy with separators
    from flask import make_response
    import json
    from appli.gui.project.projects_list import projects_list

    listall = gvg("listall", False)
    typeimport = gvg("typeimport")
    gz = gvg("gzip")
    gz = True
    content = json.dumps(
        projects_list(listall=listall, typeimport=typeimport),
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


@app.route("/gui/prj/importsettings", methods=["GET"])
@login_required
def gui_importsettings(prjid: int = 0) -> str:
    typeimport = gvg("typeimport")
    from appli.gui.project.projects_list import projects_list_page

    partial = is_partial_request(request)
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


@app.route("/gui/prj/listall/", methods=["GET"])
@login_required
def gui_prj_all():
    return gui_prj(listall=True)


@app.route("/gui/prj/about/<int:prjid>")
@login_required
def gui_prj_about(prjid):
    from appli.gui.project.project_stats import prj_stats

    params = dict({"limit": "5000"})
    partial = is_partial_request(request)

    return prj_stats(prjid, partial=partial, params=params)


@app.route("/gui/prjsamplestats/<int:prjid>")
@login_required
def gui_prj_aboutsamples(prjid):
    from flask import make_response
    import json
    from appli.gui.project.project_stats import prj_samples_stats

    partial = is_partial_request(request)
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
            message=py_messages["page404"] + filename,
        )
    partial = is_partial_request(request)
    return render_template("." + filename, partial=partial)


# alert boxes xhr
@app.route("/gui/alertbox", methods=["GET", "POST"])
def gui_alert():
    inverse = gvp("inverse")
    dismissible = gvp("dismissible")
    codemessage = gvp("codemessage")
    is_safe = gvp("is_safe")
    if is_safe:
        is_safe = True
    else:
        is_safe = False
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
        is_safe=is_safe,
        extra=gvp("extra"),
        partial=True,
    )


@app.route("/gui/<path:filename>")
@login_required
def gui_other(filename):
    from markupsafe import escape

    partial = is_partial_request(request)
    filename = escape(filename)
    filename = filename.replace("/", "")
    if os.path.isfile("v2/" + filename):
        return render_template("v2/" + filename)
    elif os.path.isfile("v2/_" + filename):
        return render_template("v2/_" + filename)
    else:
        return render_template(
            "v2/error.html",
            title="404",
            message=py_messages["page404"],
            partial=partial,
        )


@app.route("/gui/jobssummary/", methods=["GET", "POST"])
@login_required
def gui_stream():
    from appli.gui.commontools import jobs_summary_data

    return render_template(
        "./v2/partials/_notifications.html", notifs=jobs_summary_data()
    )


# @app.route("/gui/adminstream/", methods=["GET", "POST"])
@app.route("/gui/colors/", methods=["GET"])
def gui_graphicpalette():
    return render_template("./v2/palette.html")


import appli.gui.project.main
import appli.gui.jobs.main
import appli.gui.me.main
import appli.gui.admin.main

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
        else:
            from appli.gui.jobs.staticlistes import py_messages

            if message in py_messages["messages"]:
                return py_messages["messages"][message]
        if is_safe:
            return message
        return type

    def unique_id():
        import uuid

        return str(uuid.uuid1())

    def cap_words(str):
        return str.title()

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
        cap_words=cap_words,
    )


@app.errorhandler(ApiException)
def handle_exception(e):
    # pass through HTTP errors

    if isinstance(e, HTTPException):
        return e
    # non-HTTP exceptions only
    partial = is_partial_request(request)
    return (
        render_template(
            "/v2/error.html",
            title=e.status,
            partial=partial,
            message=e.reason,
            is_safe=True,
        ),
        e.status,
    )


@app.errorhandler(404)
def not_found(e):
    return handle_exception(e)


@app.errorhandler(403)
def forbidden(e):
    return handle_exception(e)


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.exception(e)
    return handle_exception(e)
