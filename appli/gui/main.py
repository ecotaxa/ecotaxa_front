# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os
import json
import urllib
from typing import List
from flask import request, url_for, render_template, redirect, flash
from flask_login import current_user, login_required
from appli import app, gvg, gvp
from appli.gui.commontools import is_partial_request
from appli.gui.staticlistes import py_messages, py_user
from appli.back_config import get_back_constants, bytes_to_human_readable
from flask import make_response
from to_back.ecotaxa_cli_py.models import DirectoryModel, DirectoryEntryModel

login_required.login_view = "gui/login"

HOMEPAGE = "/gui/"


@app.route("/")
@app.route("/gui")
@app.route("/gui/")
@app.route("/gui/home")
@app.route("/gui/index")
def gui_index():
    return render_template("v2/index.html")


@app.route("/gui/logout", methods=["GET", "POST"])
@app.route("/gui/logout/", methods=["GET", "POST"])
@login_required
def gui_logout():
    from flask_login import logout_user

    logout_user()
    return redirect(url_for("gui_login"))


@app.route("/gui/login", methods=["GET", "POST"])
@app.route("/gui/login/", methods=["GET", "POST"])
def gui_login():
    if current_user.is_authenticated:
        return redirect(HOMEPAGE)
    referer = request.referrer
    if request.method == "POST":
        from appli.security_on_backend import login_validate
        from appli.gui.commontools import safe_url_redir

        email = gvp("email", "")
        password = gvp("password", "")
        remember = gvp("remember", "")
        if email == "" or password == "":
            flash(py_user["invaliddata"], "error")
        else:
            resp, userdata = login_validate(email, password, (remember == "y"))
            if resp:
                _next = gvp("next", "")
                _next = _next.strip()
                if _next != "":
                    return safe_url_redir(_next)
                return redirect(HOMEPAGE)
            elif isinstance(userdata, dict):
                redir = url_for("gui_me_activate", token="no")
                return redirect(redir)
            else:
                return redirect(url_for("gui_login"))
    else:
        referer = gvg("next", "")

    if referer in [url_for("gui_login"), url_for("gui_index")]:
        referer = ""
    return render_template("v2/login.html", next=referer, bg=True)


@app.route("/gui/register", defaults={"token": None}, methods=["GET", "POST"])
@app.route("/gui/register/", defaults={"token": None}, methods=["GET", "POST"])
@app.route("/gui/register/<token>", methods=["GET", "POST"])
def gui_register(token=None):

    if token is None and current_user.is_authenticated:
        return redirect(url_for("index"))
    partial = is_partial_request()
    from appli.gui.users.users import user_register

    return user_register(token, partial=partial)


@app.route("/gui/about/")
def gui_about():
    from appli.gui.sponsorslist import sponsors

    return render_template("v2/about.html", sponsors=sponsors, bg=True)


@app.route("/gui/checkcaptcha")
def gui_check_captcha():
    from appli.gui.users.users import check_homecaptcha

    token = gvg("r", "")
    return check_homecaptcha(token)


@app.route("/gui/privacy")
@app.route("/gui/privacy/")
def gui_privacy():

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
def gui_prjlist():
    # gzip not really necessary - jsonifiy with separators

    from appli.gui.project.projects_list import projects_list

    listall = gvg("listall", "False")
    managing = gvg("for_managing", "False")
    if listall == "False":
        _all = False
    else:
        _all = True
    if managing == "False":
        for_managing = False
    else:
        for_managing = True
    typeimport = gvg("typeimport")
    gz = True
    encoding = "utf-8"
    content = json.dumps(
        projects_list(listall=_all, for_managing=for_managing, typeimport=typeimport),
        separators=(",", ":"),
    ).encode(encoding)

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
def gui_importsettings():
    typeimport = gvg("typeimport")
    from appli.gui.project.projects_list import projects_list_page

    partial = is_partial_request()
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

    # TODO limit stats
    # params = dict({"limit": "5000"})
    partial = is_partial_request()

    return prj_stats(projid, partial=partial)  # , params=params)


@app.route("/gui/prjsamplestats/<int:projid>")
@login_required
def gui_prj_aboutsamples(projid):
    from appli.gui.project.project_stats import prj_samples_stats

    partial = is_partial_request()
    _format = gvg("format", "json")
    content = prj_samples_stats(str(projid), partial=partial, _format=_format)
    if _format == "json":
        encoding = "utf-8"
        content = json.dumps(content, separators=(",", ":")).encode(encoding)
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
    return render_template(".v2/help/_help_user_profile.html")


@app.route("/gui/help/<path:filename>")
@login_required
def gui_help(filename):
    from os.path import exists
    from markupsafe import escape

    partial = is_partial_request()
    filename = escape(filename)
    title = gvg("title", "")
    args = {}
    if filename.find("_collection_settings") >= 0:
        from appli.gui.commontools import possible_licenses

        args.update({"licenses": possible_licenses()})
    if filename[0:1] != "_":
        return render_template(
            "/v2/help/index.html",
            filename=filename,
            partial=partial,
            title=title,
            notfound=None,
            args=args,
        )
    filename = "/v2/help/" + filename + ".html"
    if not exists("appli/templates" + filename):
        return render_template(
            "/v2/help/index.html", notfound=filename, partial=partial
        )
    return render_template(filename, partial=partial, title=title, args=args)


# alert boxes xhr
@app.route("/gui/alertbox", methods=["GET", "POST"])
def gui_alert():
    inverse = gvp("inverse", "False")
    dismissible = gvp("dismissible", "False")
    codemessage = gvp("codemessage", "")
    is_safe = gvp("is_safe", "False")
    is_safe = bool(is_safe)
    inverse = bool(inverse)
    dismissible = bool(dismissible)
    message = gvp("message")
    _type = gvp("type")
    title = gvp("title")
    from appli.gui.commontools import alert_box

    return alert_box(
        _type=_type,
        title=title,
        inverse=inverse,
        dismissible=dismissible,
        codemessage=codemessage,
        is_safe=is_safe,
        message=message,
    )


@app.route("/gui/<path:filename>")
@login_required
def gui_other(filename):
    from markupsafe import escape
    from os.path import exists

    partial = is_partial_request()
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


# import from server - list
@app.route("/gui/common/ServerFolderSelectJSON")
def gui_server_folder_select_json():
    # Get posted vars
    parent = gvg("id")
    zip_only = gvg("ZipOnly") == "Y"
    # The explored part
    if parent == "#":
        current_path = ""  # root
    else:
        current_path = parent
    # Call back-end for directory content
    from appli.utils import ApiClient
    from to_back.ecotaxa_cli_py.api import FilesApi

    with ApiClient(FilesApi, request) as api:
        # List files remotely
        dir_desc: DirectoryModel = api.list_common_files(path=current_path)
        entries_in_dir: List[DirectoryEntryModel] = dir_desc.entries
    res = []
    for entry in entries_in_dir:
        path_to_root = (current_path + "/" if current_path else "") + entry.name
        entry_name = entry.name
        if entry.type == "D":
            if zip_only:
                res.append(
                    dict(
                        id=path_to_root,
                        name=entry_name,
                        parent=parent,
                        children=True,
                    )
                )
            else:
                res.append(
                    dict(
                        id=path_to_root,
                        name=entry_name,
                        parent=parent,
                        children=True,
                    )
                )
        if entry.name.lower().endswith(".zip"):
            # For zip files we have details, the date is a bit too precise however
            fmt = (entry_name, entry.size / 1048576, entry.mtime[:-7])
            res.append(
                dict(
                    id=path_to_root,
                    name=entry_name,
                    size="%s (%.1f Mb : %s)" % fmt,
                    parent=parent,
                    children=False,
                )
            )
    res.sort(key=lambda val: str.upper(val["id"]), reverse=False)
    return json.dumps(res)


# cookie for sitemessaging
@app.route("/gui/setmsgcookie", methods=["POST"])
def gui_setmsgcookie():
    cookiename = gvp("name")
    cookievalue = gvp("value")
    response = make_response("")
    if cookiename != "" and cookievalue != "":
        response.set_cookie(cookiename, cookievalue)
    return response, 302


# erros messages for js messaging && notifications modules
@app.route("/gui/i18n", methods=["GET"])
def gui_i18n():
    encoding = "utf-8"
    from appli.gui.staticlistes import py_messages_titles, py_user

    content = json.dumps(dict(py_messages, **py_user, **py_messages_titles)).encode(
        encoding
    )
    response = make_response(content)
    response.headers["Content-length"] = len(content)
    response.headers["Content-Encoding"] = encoding
    response.headers["Content-Type"] = "application/json"
    return response


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
import appli.gui.collection.main
import appli.gui.guests.main


# utility display functions for jinja template
@app.template_filter("urlencode")
def urlencode_filter(s):
    from markupsafe import Markup

    if type(s) == "Markup":
        s = s.unescape()
    s = s.encode("utf8")
    s = urllib.parse.quote_plus(s)
    return Markup(s)


@app.context_processor
def utility_processor():
    def message_translation(message: str, _type: str, is_safe: bool = False) -> str:
        from appli.gui.staticlistes import py_messages

        if message in py_messages:
            return py_messages[message]
        else:
            from appli.gui.jobs.staticlistes import py_messages

            if message in py_messages["messages"]:
                return py_messages["messages"][message]
        return message

    def unique_id():
        import uuid

        return str(uuid.uuid1())

    def cap_words(text: str):
        return text.title()

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

        if key is not None:
            if key in g_data:
                return g_data[key]
            else:
                return {}
        return g_data

    def gui_breadcrumbs() -> list:
        from appli.gui.commontools import breadcrumbs

        return breadcrumbs()

    def get_referrer() -> str:
        referrer = gvg("next", request.referrer)
        if referrer is None or referrer in [
            url_for("gui_login"),
            url_for("gui_me_forgotten"),
            url_for("gui_register"),
        ]:
            referrer = HOMEPAGE
        return referrer

    def get_manager_list(sujet=""):
        from appli.utils import ApiClient
        from to_back.ecotaxa_cli_py import (
            UsersApi,
            MinUserModel,
        )

        admin_users: List[MinUserModel]
        if current_user.is_authenticated:
            # With a connected user, return administrators
            with ApiClient(UsersApi, request) as api:
                admin_users = api.get_admin_users()
        else:
            # With an anonymous user, return user administrators (for account issues)
            with ApiClient(UsersApi, request) as api:
                admin_users = api.get_users_admins()
        if sujet:
            sujet = "?" + urllib.parse.urlencode({"subject": sujet}).replace("+", "%20")

        return " ".join(
            [
                "<li><a href='mailto:{1}{0}'>{2} ({1})</a></li> ".format(
                    sujet, r.email, r.name
                )
                for r in admin_users
            ]
        )

    def global_messages() -> list:
        listmessages = []
        cookiename = app.config.get("APP_GUI_MESSAGE_COOKIE_NAME")
        from flask import get_flashed_messages

        # get flashed messages and display in left box
        flashed = get_flashed_messages(True)
        if len(flashed):
            for f in flashed:
                message = dict(
                    {
                        "type": f[0],
                        "content": f[1],
                    }
                )
                if f[0] == "success":
                    message["duration"] = 4000
                else:
                    message["dismissible"] = True
                listmessages.append(message)
        # get maintenance and info messages from admin and display in left box
        import json
        from datetime import datetime

        file = app.config.get("APP_GUI_MESSAGE_FILE")
        if os.path.exists(file):
            messages = None
            with open(file, "r", encoding="utf-8") as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError as e:
                    print("Invalid JSON syntax:", e)

            if isinstance(messages, dict):
                # build messages param for template {"type":,"content":,"date":,"dismissible":, duration:}
                for key, message in messages.items():
                    name = key + cookiename
                    # homepage active message stays
                    delta = 10
                    if key != "homepage":
                        dailyinfo = request.cookies.get(name)
                        if dailyinfo is not None:
                            dformat = "%Y-%m-%d %H:%M:%S.%f"
                            delta = (
                                datetime.strptime(message["date"], dformat)
                                - datetime.strptime(dailyinfo, dformat)
                            ).days
                    if isinstance(message, dict) and (
                        "active" in message
                        and message["active"] == 1
                        and "date" in message
                        and delta > 1
                    ):

                        if "content" in message:
                            message["content"] = "<br>".join(
                                str(message["content"]).split("\r\n")
                            )
                            message["is_safe"] = True
                        message["type"] = key
                        message["cookiename"] = cookiename
                        message["dismissible"] = True
                        # for white bg
                        message["inverse"] = True
                        listmessages.append(message)
            # get taxomessage and display in left box
            if current_user.is_authenticated:
                from appli.gui.commontools import last_taxo_refresh

                taxomessage = last_taxo_refresh(cookiename)
                if isinstance(taxomessage, dict):
                    listmessages.append(taxomessage)

        return listmessages

    def ecopart_url():
        return app.config.get("ECOPART_URL", "")

    def api_password_regexp():
        from appli.gui.users.users import api_password_regexp

        return api_password_regexp()

    def license_texts() -> dict:
        from appli.gui.commontools import possible_licenses

        licenses = possible_licenses()
        return licenses

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

    def max_upload_size(human=True):
        ttl = get_back_constants("MAX_UPLOAD_SIZE")
        if human:
            return bytes_to_human_readable(ttl)
        return ttl

    def days_to_live():
        return get_back_constants("TIME_TO_LIVE")

    return dict(
        message_translation=message_translation,
        unique_id=unique_id,
        gui_breadcrumbs=gui_breadcrumbs,
        g_status=g_status,
        def_language=def_language,
        cap_words=cap_words,
        get_referrer=get_referrer,
        global_messages=global_messages,
        api_password_regexp=api_password_regexp,
        license_texts=license_texts,
        bg_scale=bg_scale,
        logo_special=logo_special,
        get_manager_list=get_manager_list,
        ecopart_url=ecopart_url,
        max_upload_size=max_upload_size,
        days_to_live=days_to_live,
    )
