# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os
from typing import Optional, List, Tuple, Union

from flask import g, request, url_for, send_from_directory
from flask.typing import ResponseReturnValue
from flask_login import current_user

from appli import app, PrintInCharte, ecopart_url
from appli.api_proxy import proxy_request
from appli.constants import is_static_unprotected
from appli.main_vue import index_vue


# VUE_PATH == "/gui"

@app.route('/')
def index():
    from appli.project.__init__ import connectPythonToPrime
    if connectPythonToPrime:
        return index_vue()
    else:
        txt = """<div style='margin:5px;'><div id="homeText"'>"""
        # lecture du message de l'application manager
        NomFichier = 'appli/static/home/appmanagermsg.html'
        if os.path.exists(NomFichier):
            with open(NomFichier, 'r', encoding='utf8') as f:
                message = f.read()
                if len(message) > 5:
                    txt += """
                        <div class="alert alert-warning alert-dismissable" role="alert">
                            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                            <p><strong>Message from the application manager</strong></p>{0}
                        </div>
                    """.format(message)
        # Link to new EcoTaxa about page : see https://github.com/ecotaxa/ecotaxa_dev/issues/701
        # We have to do something like : txt += '<a href="https://ecotaxa.obs-vlfr.fr/gui/ecotaxa_about>About EcoTaxa...</a>'    
        # txt +="<div>\n"
        # txt += '<a href="' + VUE_PATH + '/ecotaxa_about' + '">About EcoTaxa...</a>\n'
        # txt +="</div>\n"

        # Lecture de la partie Haute
        NomFichier = 'appli/static/home/home.html'
        if not os.path.exists(NomFichier):
            NomFichier = 'appli/static/home/home-model.html'
        with open(NomFichier, 'r', encoding='utf8') as f:
            txt += f.read()
        txt += """
        </div>
        <div class="row" id="homeSelectors" style="margin-top: 20px; margin-bottom: 20px;">
            <div class="col-sm-4">
            <a href="/explore/" class="btn btn-primary btn-lg btn-block">Explore images</a>
            </div>
            <div class="col-sm-4">
            <a href="/prj/" class="btn btn-primary btn-lg  btn-block">Contribute to a project</a>
            </div>		
            <div class="col-sm-4">
            <a href="%s" class="btn btn-primary btn-lg  btn-block">Particle module</a>
            </div>		
        </div>
    """ % ecopart_url
        NomFichier = 'appli/static/home/homebottom.html'
        if not os.path.exists(NomFichier):
            NomFichier = 'appli/static/home/homebottom-model.html'
        txt += """<div class="row" id="homeLegal"><div class="col-sm-12">"""
        with open(NomFichier, 'r', encoding='utf8') as f:
            txt += f.read()
        txt += """<br><a href='/privacy'>Privacy</a></div></div></div>"""
        return PrintInCharte(txt)


# Where we serve the Vue front-end
GUI_PATH = app.root_path + "/gui/"  # TODO ? replace /gui by VUE_PATH ?


# Everything there should be pre-processed e.g.:
# ecotaxa_front/proto/ecotaxa-cli$ for f in `grep -rwl "/front/" dist/ `; do sed -e "s/\/front\//\/gui\//g" $f > $f.2; mv $f.2 $f; done

@app.route('/gui')  # TODO ? replace /gui by VUE_PATH ?
def gui_index():
    return send_from_directory(GUI_PATH, 'index.html')


@app.route('/gui/<path:filename>')  # TODO ? replace /gui by VUE_PATH ?
def gui_any(filename):
    try:
        return send_from_directory(GUI_PATH, filename)
    except:
        return gui_index()


@app.route('/vault/<path:filename>')
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
    user_can_administrate = False
    user_can_administrate_users = False
    mru_projects = []
    # current_user is either an ApiUserWrapper or an anonymous one from flask
    if current_user.is_authenticated:
        user_can_administrate = 2 in current_user.can_do
        user_can_administrate_users = 3 in current_user.can_do
        mru_projects = current_user.last_used_projects
    g.cookieGAOK = request.cookies.get('GAOK', '')
    g.useradmin = user_can_administrate_users
    g.appliadmin = user_can_administrate
    # TODO: A bit useless as unlogged users have no menu to use
    menu: List[Union[Tuple[str, str], Tuple[str, str, str]]] = []
    menu.append((url_for("index"), "Home"))
    menu.append(("/explore/", "Explore"))
    if len(mru_projects) > 0:
        menu.append(("/prj/", "Contribute to a project", "SUB"))
        for a_prj in mru_projects:
            menu.append(("/prj/%d" % a_prj.projid,
                         "[%d] %s" % (a_prj.projid, a_prj.title)))
        menu.append(("", "NOSUB"))
    else:
        menu.append(("/prj/", "Contribute to a project"))
    menu.append((ecopart_url, "Go to EcoPart"))
    menu.append(("", "SEP"))
    if request.endpoint == 'indexPrj' and request.view_args is not None:
        from_prj = request.view_args.get('PrjId')
        menu.append(("javascript:PostDynForm('/taxo/browse/?fromprj=%s');" % from_prj, "Browse Taxonomy"))
    else:
        menu.append(("javascript:PostDynForm('/taxo/browse/');", "Browse Taxonomy"))
    if user_can_administrate or user_can_administrate_users:
        menu.append(("", "SEP"))
        menu.append(("/admin/", "Admin Screen"))
        menu.append(("/Jobs/listall", "Task Manager"))

    menu.append(("", "SEP"))
    menu.append(("/change", "Change Password"))
    g.menu = menu
    return None


@app.after_request
def after_request(response):
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data: " \
                                                  "cdnjs.cloudflare.com server.arcgisonline.com www.google.com " \
                                                  "www.gstatic.com www.google-analytics.com cdn.ckeditor.com " \
                                                  "cdn.jsdelivr.net unpkg.com fonts.googleapis.com fonts.gstatic.com;" \
                                                  "frame-ancestors 'self';form-action 'self';"
    return response
