# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os
from typing import Optional, List, Tuple, Union
from flask import g, request, url_for, send_from_directory, session
from flask.typing import ResponseReturnValue
from flask_login import current_user
from appli import app, PrintInCharte, ecopart_url
from appli.api_proxy import proxy_request
from appli.constants import (
    AdministratorLabel,
    UserAdministratorLabel,
    is_static_unprotected,
    APP_MANAGER_MESSAGE_FILE,
    CUSTOM_HOME_TOP,
    CUSTOM_HOME_BOTTOM,
)


@app.route("/")
def index():
    txt = """<div style='margin:5px;'><div id="homeText"'>"""
    # lecture du message de l'application manager
    NomFichier = APP_MANAGER_MESSAGE_FILE
    if os.path.exists(NomFichier):
        with open(NomFichier, "r", encoding="utf8") as f:
            message = f.read()
            if len(message) > 5:
                txt += """
                    <div class="alert alert-warning alert-dismissable" role="alert">
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                        <p><strong>Message from the application manager</strong></p>{0}
                    </div>
                """.format(
                    message
                )
    # Lecture de la partie Haute
    NomFichier = CUSTOM_HOME_TOP
    if not os.path.exists(NomFichier):
        NomFichier = "appli/static/home/home-model.html"
    with open(NomFichier, "r", encoding="utf8") as f:
        txt += f.read()
    txt += (
        """
    </div>
    <div class="row" id="homeSelectors" style="margin-top: 20px; margin-bottom: 20px;">
        <div class="col-sm-4">
        <a href="/explore/" class="btn btn-primary btn-lg btn-block">Explore images</a>
        </div>
        <div class="col-sm-4">
        <a href="/gui/prj/" class="btn btn-primary btn-lg  btn-block">Contribute to a project</a>
        </div>
        <div class="col-sm-4">
        <a href="%s" class="btn btn-primary btn-lg  btn-block">Particle module</a>
        </div>
    </div>
    """
        % ecopart_url
    )
    NomFichier = CUSTOM_HOME_BOTTOM
    if not os.path.exists(NomFichier):
        NomFichier = "appli/static/home/homebottom-model.html"
    with open(NomFichier, "r", encoding="utf8") as f:
        txt += f.read()
    return PrintInCharte(txt)


@app.route("/vault/<path:filename>")
def get_from_vault(filename):
    # Serve an image, if e.g. apache or nginx did not intercept the query
    return proxy_request("api/vault/" + filename)


@app.before_request
def before_request_security() -> Optional[ResponseReturnValue]:
    # time.sleep(0.1)
    # print("URL="+request.url)
    # app.logger.info("URL="+request.url)
    if is_static_unprotected(request.path):
        return None
    mru_projects = []
    # current_user is either an ApiUserWrapper or an anonymous one from flask
    g.cookieGAOK = request.cookies.get("GAOK", "")
    if not current_user.is_authenticated:
        return None
    mru_projects = current_user.last_used_projects
    # TODO: A bit useless as unlogged users have no menu to use
    menu: List[Union[Tuple[str, str], Tuple[str, str, str]]] = []
    menu.append((url_for("index"), "Home"))
    menu.append(("/explore/", "Explore"))
    if len(mru_projects) > 0:
        menu.append(("/prj/", "Contribute to a project", "SUB"))
        for a_prj in mru_projects:
            menu.append(
                ("/prj/%d" % a_prj.projid, "[%d] %s" % (a_prj.projid, a_prj.title))
            )
        menu.append(("", "NOSUB"))
    else:
        menu.append(("/prj/", "Contribute to a project"))
    menu.append((ecopart_url, "Go to EcoPart"))
    menu.append(("", "SEP"))
    if request.endpoint == "indexPrj" and request.view_args is not None:
        from_prj = request.view_args.get("PrjId")
        menu.append(
            (
                "javascript:PostDynForm('/taxo/browse/?fromprj=%s');" % from_prj,
                "Browse Taxonomy",
            )
        )
    else:
        menu.append(("javascript:PostDynForm('/taxo/browse/');", "Browse Taxonomy"))
    if current_user.is_admin == True:
        menu.append(("", "SEP"))
        menu.append(("/gui/admin/", "Admin Screen"))
        if current_user.is_app_admin == True:
            menu.append(("/gui/jobs/listall", "Task Manager"))

    menu.append(("", "SEP"))
    menu.append(("/gui/me/profile", "Profile"))
    g.menu = menu
    from appli.gui.commontools import experimental_header

    g.experimental = experimental_header()
    return None


@app.after_request
def after_request(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data: "
        "cdnjs.cloudflare.com server.arcgisonline.com www.google.com *.googletagmanager.com *.google-analytics.com *.analytics.google.com"
        " www.gstatic.com cdn.ckeditor.com  "
        "cdn.jsdelivr.net unpkg.com fonts.googleapis.com fonts.gstatic.com;"
        "frame-ancestors 'self';form-action 'self';  "
    )
    return response
