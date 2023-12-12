# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os

from flask import request, url_for, render_template, redirect, flash
from flask_login import current_user, login_required
from appli import app, gvg, gvp, constants
from appli.gui.commontools import is_partial_request
from to_back.ecotaxa_cli_py.exceptions import ApiException
from werkzeug.exceptions import NotFound
from flask_babel import _
from appli.gui.staticlistes import py_messages, py_user

login_required.login_view = "gui/login"

HOMEPAGE = "/gui/"


@app.route("/")
@app.route("/gui")
@app.route("/gui/")
@app.route("/gui/home")
@app.route("/gui/index")
def gui_index():
    ecoparturl = app.config.get("ECOPART_URL", "")
    return render_template("v2/index.html", ecoparturl=ecoparturl)


@app.route("/gui/logout", methods=["GET", "POST"])
@app.route("/gui/logout/", methods=["GET", "POST"])
@login_required
def gui_logout():
    from flask_login import logout_user

    logout_user()
    return redirect(url_for("gui_login"))


@app.route("/gui/login", methods=["GET", "POST"])
@app.route("/gui/login/", methods=["GET", "POST"])
def gui_login() -> str:
    if current_user.is_authenticated:
        # return old interface projects list
        # return redirect(url_for("gui_prj"))
        return redirect(HOMEPAGE)

    if request.method == "POST":
        from appli.security_on_backend import login_validate
        from appli.gui.commontools import safe_url_redir

        email = gvp("email", None)
        password = gvp("password", None)
        remember = gvp("remember", None)
        if email == None or password == None:
            flash(py_user["invaliddata"], "error")
        else:
            resp, userdata = login_validate(email, password, (remember == "y"))
            if resp:
                next = gvp("next", None)
                if next != None:
                    if next.strip() != "":
                        next = safe_url_redir(next)
                        return redirect(next)
            elif isinstance(userdata, dict):
                redir = url_for("gui_me_activate", token="no")
                return redirect(redir)
            else:
                return redirect(url_for("gui_login"))
    return render_template("v2/login.html", bg=True)


@app.route("/gui/register", defaults={"token": None}, methods=["GET", "POST"])
@app.route("/gui/register/", defaults={"token": None}, methods=["GET", "POST"])
@app.route("/gui/register/<token>", methods=["GET", "POST"])
def gui_register(token=None) -> str:

    if current_user.is_authenticated:
        return redirect(url_for("index"))
    partial = is_partial_request(request)
    from appli.gui.users.users import user_register

    return user_register(token, partial=partial)


@app.route("/gui/about/")
def gui_about() -> str:
    from appli.gui.sponsorslist import sponsors

    return render_template("v2/about.html", sponsors=sponsors, bg=True)


@app.route("/gui/checkcaptcha")
def gui_check_captcha() -> str:
    from appli.gui.users.users import check_homecaptcha

    token = gvg("r", None)
    return check_homecaptcha(token)


@app.route("/gui/privacy")
@app.route("/gui/privacy/")
def gui_privacy() -> str:

    return render_template("v2/privacy.html")


@app.route("/prj/", methods=["GET"])
@app.route("/gui/prj/", methods=["GET"])
@login_required
def gui_prj(listall: bool = False) -> str:
    partial = False

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
    if listall == "False" or not listall:
        listall = False
    else:
        listall = True
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
# TODO - fresh_login_required
@login_required
def gui_prj_edit(prjid):
    from appli.gui.project.projectsettings import prj_edit

    return prj_edit(prjid)


@app.route("/gui/prj/listall/", methods=["GET"])
@login_required
def gui_prj_all():
    return gui_prj(listall=True)


@app.route("/gui/prj/about/<int:projid>")
@login_required
def gui_prj_about(projid):
    from appli.gui.project.project_stats import prj_stats

    params = dict({"limit": "5000"})
    partial = is_partial_request(request)

    return prj_stats(projid, partial=partial, params=params)


@app.route("/gui/prjsamplestats/<int:projid>")
@login_required
def gui_prj_aboutsamples(projid):
    from flask import make_response
    import json
    from appli.gui.project.project_stats import prj_samples_stats

    partial = is_partial_request(request)
    format = gvg("format", "json")
    content = prj_samples_stats(projid, partial=partial, format=format)
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
@app.route("/gui/help/register")
def gui_help_nologin():
    return render_template(".v2/help/help_register.html")


@app.route("/gui/help/<path:filename>")
@login_required
def gui_help(filename):
    from os.path import exists
    from markupsafe import escape

    partial = is_partial_request(request)
    filename = escape(filename)
    if filename[0:1] != "_":
        return render_template(".v2/help.html", filename=filename)
    filename = "/v2/help/" + filename + ".html"
    if not exists("appli/templates" + filename):
        return render_template("v2/help/index.html", notfound=filename, partial=partial)
    return render_template("." + filename, partial=partial)


# alert boxes xhr
@app.route("/gui/alertbox", methods=["GET", "POST"])
def gui_alert():
    inverse = gvp("inverse", False)
    dismissible = gvp("dismissible", False)
    codemessage = gvp("codemessage")
    is_safe = gvp("is_safe", False)
    is_safe = bool(is_safe)
    inverse = bool(inverse)
    dismissible = bool(dismissible)
    message = gvp("message")
    type = gvp("type")
    title = gvp("title")
    from appli.gui.commontools import alert_box

    return alert_box(
        type=type,
        title=title,
        inverse=inverse,
        dismissible=dismissible,
        codemessage=str(codemessage),
        is_safe=is_safe,
        message=message,
    )


@app.route("/gui/<path:filename>")
@login_required
def gui_other(filename):
    from markupsafe import escape
    from os.path import exists

    partial = is_partial_request(request)
    if partial:
        template = "partials/_error"
    else:
        template = "error"
    if filename:
        filename = escape(filename)
        filename = filename.replace("/", "")
        if exists("templates/v2/" + filename):
            return render_template("v2/" + filename)
    return render_template("v2/" + template + ".html", error=404, message="page404")


@app.route("/gui/jobssummary/", methods=["GET", "POST"])
@login_required
def gui_stream():
    from appli.gui.commontools import jobs_summary_data

    return render_template(
        "./v2/partials/_notifications.html", notifs=jobs_summary_data()
    )


# cookie for sitemessaging
@app.route("/gui/setmsgcookie", methods=["POST"])
def gui_setmsgcookie():
    cookiename = gvp("name")
    cookievalue = gvp("value")
    from flask import make_response

    response = make_response("")
    if cookiename != "" and cookievalue != "":
        response.set_cookie(cookiename, cookievalue)
    return response, 302


# @app.route("/gui/adminstream/", methods=["GET", "POST"])
@app.route("/gui/colors/", methods=["GET"])
def gui_graphicpalette():
    return render_template("./v2/palette.html")


import appli.gui.project.main
import appli.gui.jobs.main
import appli.gui.me.main
import appli.gui.files.main
import appli.gui.admin.main
import appli.gui.taxonomy.main

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

    def get_referrer() -> str:
        import functools

        GO_INDEX = ["gui_login", "gui_forgotten", "gui_register"]
        referrer = gvp("next", request.referrer)
        goindex = functools.reduce(lambda a, b: a or referrer == url_for(b), GO_INDEX)
        if referrer == None or goindex:
            # referrer = url_for("gui_index")
            referer = HOMEPAGE
        return referrer

    def global_messages() -> str:
        if current_user.is_authenticated:
            from appli.gui.commontools import last_taxo_refresh

            last_taxo_refresh()

        cookiename = "ecotaxa_userinfo"

        import json, time

        file = app.config.get("APP_GUI_MESSAGE_FILE")
        ret = {}
        if os.path.exists(file):
            messages = None
            with open(file, "r", encoding="utf-8") as f:
                try:
                    messages = json.loads(f.read())
                except json.JSONDecodeError as e:
                    print("Invalid JSON syntax:", e)
            if isinstance(messages, dict):
                for key, message in messages.items():
                    name = key + cookiename
                    dailyinfo = request.cookies.get(name)
                    if isinstance(message, dict) and (
                        "active" in message
                        and message["active"] == 1
                        and "date" in message
                        and dailyinfo != message["date"]
                    ):
                        ret[key] = message

        if len(ret):
            return {"messages": ret, "cookiename": cookiename}
        else:
            return None

    def api_password_regexp():
        from appli.gui.users.users import api_password_regexp

        return api_password_regexp()

    def bg_scale():
        bg = str(app.config.get("BG_SCALE") or "")
        if bg != "" and os.path.exists(
            os.path.join(app.static_folder, "gui/images/montage_plankton" + bg + ".jpg")
        ):
            return bg
        else:
            return ""

    def logo_special():
        logo = str(app.config.get("LOGO_SPECIAL") or "")
        if logo != "" and os.path.exists(
            os.path.join(app.static_folder, "gui/images/logo_ecotaxa" + logo + ".png")
        ):
            return logo
        else:
            return ""

    return dict(
        message_translation=message_translation,
        unique_id=unique_id,
        breadcrumbs=gui_breadcrumbs,
        g_status=g_status,
        def_language=def_language,
        cap_words=cap_words,
        get_referrer=get_referrer,
        global_messages=global_messages,
        api_password_regexp=api_password_regexp,
        bg_scale=bg_scale,
        logo_special=logo_special,
    )
