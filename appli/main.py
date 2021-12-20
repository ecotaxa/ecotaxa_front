# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os

from flask import Blueprint, g, request, url_for, send_from_directory

from appli import app, PrintInCharte
from part_app.urls import PART_URL
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import UsersApi
from to_back.ecotaxa_cli_py.models import UserModelWithRights

# VUE_PATH == "/gui"

vaultBP = Blueprint('vault', __name__,
                    static_url_path='/vault', static_folder='../vault')
app.register_blueprint(vaultBP)

@app.route('/')
def index():
    from appli.project.__init__ import connectPythonToPrime
    if connectPythonToPrime:    
        def find_language():
            # Get the browser current language
            import gettext
            # see https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1 to get all the 2 digits country codes           
            KNOWN_LANGAGES = ['en','pt','zh','fr'] # TODO put this constant in ecotaxa_dev/appli/project/__init__.py ?
            curLang:str = ''
            prefLangs = request.accept_languages
            if prefLangs is not None:
                # Here, there is at least one language            
                # First one is the prefered language in the list of handled languages
                for l in prefLangs:
                    curLang:str = l[0][:2] # first 2 letters show the country, and translations tables folders are organised this way
                    if curLang in KNOWN_LANGAGES:
                        try: # N.B. [curLang] and not curLang in the following line
                            lang = gettext.translation ('ecotaxa', 'messages', [curLang] ) # curLang == 'fr' or 'en' or 'zh' or 'pt' ...
                            okCurLang = True
                        except: # language corrupted or not existing
                            okCurLang = False
                        if okCurLang:
                            lang.install()
                            return lang
                    # try the next language
            # Tried all the languages without success, or there is no supported langage
            curLang = 'en' # desperate, so take english as last solution
            lang = gettext.translation ('ecotaxa', 'messages', [curLang] )
            lang.install()
            return lang

        from appli import PrintInCharte_bs5    
        from flask import render_template, request
        language = find_language()
        return PrintInCharte_bs5(
            # EcoTaxa_about_page and Welcome_to_EcoTaxa not yet used here
            render_template(    "project/about_ecotaxa.html",
                                EcoTaxa_is_a_web_application = language.gettext("EcoTaxa_is_a_web_application"),
                                If_you_use_EcoTaxa = language.gettext("If_you_use_EcoTaxa"),
                                The_development_of_EcoTaxa = language.gettext("The_development_of_EcoTaxa"),
                                Sorbonne_Universite_and_CNRS = language.gettext("Sorbonne_Universite_and_CNRS"),
                                The_Programme_Investissements_d_Avenir = language.gettext("The_Programme_Investissements_d_Avenir"),
                                The_Partner_University_Fund = language.gettext("The_Partner_University_Fund"),
                                The_CNRS_LEFE_program = language.gettext("The_CNRS_LEFE_program"),
                                The_Belmont_Forum = language.gettext("The_Belmont_Forum"),
                                The_Watertools_company = language.gettext("The_Watertools_company"),
                                The_maintenance_of_the_software = language.gettext("The_maintenance_of_the_software"),
                                The_persons_who_made_EcoTaxa = language.gettext("The_persons_who_made_EcoTaxa"),
                                Marc_Picheral_and = language.gettext("Marc_Picheral_and"),
                                Sebastien_Colin = language.gettext("Sebastien_Colin"),
                                Developers = language.gettext("Developers"),
                                Deep_learning = language.gettext("Deep_learning"),
                                testing_and_feedback = language.gettext("testing_and_feedback"),
                                Disclaimer = language.gettext("Disclaimer")
            )
        )
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
            <a href="/part/" class="btn btn-primary btn-lg  btn-block">Particle module</a>
            </div>		
        </div>
    """
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


@app.before_request
def before_request_security():
    # time.sleep(0.1)
    # print("URL="+request.url)
    # app.logger.info("URL="+request.url)
    g.db = None
    if "/static" in request.url:
        return
    if "/vault/" in request.url:
        return
    if "/api/" in request.url:
        return
    # print(request.form)
    user_is_logged = False
    user_can_create = False
    user_can_administrate = False
    user_can_administrate_users = False
    mru_projects = []
    with ApiClient(UsersApi, request) as api:
        try:
            user: UserModelWithRights = api.show_current_user()
            user_is_logged = True
            user_can_create = 1 in user.can_do
            user_can_administrate = 2 in user.can_do
            user_can_administrate_users = 3 in user.can_do
            mru_projects = user.last_used_projects
        except ApiException as ae:
            if ae.status in (401, 403):
                pass
    # current_user.is_authenticated
    g.cookieGAOK = request.cookies.get('GAOK', '')
    g.menu = []
    g.menu.append((url_for("index"), "Home"))
    g.menu.append(("/explore/", "Explore"))
    if len(mru_projects) > 0:
        g.menu.append(("/prj/", "Contribute to a project", "SUB"))
        for a_prj in mru_projects:
            g.menu.append(("/prj/%d" % a_prj.projid,
                           "[%d] %s" % (a_prj.projid, a_prj.title)))
        g.menu.append(("", "NOSUB"))
    else:
        # TODO: I can't see the menu _at all_ for unlogged users?
        g.menu.append(("/prj/", "Select Project"))
    g.menu.append((PART_URL, "Particle Module"))
    if user_is_logged:
        g.menu.append((PART_URL+"prj/", "Particle projects management"))
    g.menu.append(("", "SEP"))
    if request.endpoint == 'indexPrj':
        g.menu.append(("javascript:PostDynForm('/taxo/browse/?fromprj=%d');" % (
            request.view_args.get('PrjId'),), "Browse Taxonomy"))
    else:
        g.menu.append(
            ("javascript:PostDynForm('/taxo/browse/');", "Browse Taxonomy"))
    if user_can_administrate or user_can_administrate_users:
        g.menu.append(("", "SEP"))
        g.menu.append(("/admin/", "Admin Screen"))
        g.menu.append(("/Jobs/listall", "Task Manager"))

    g.useradmin = user_can_administrate_users
    g.appliadmin = user_can_administrate
    g.menu.append(("", "SEP"))
    g.menu.append(("/change", "Change Password"))


@app.teardown_appcontext
def before_teardown_commitdb(error):
    try:
        if g.db:
            try:
                g.db.commit()
            except:
                g.db.rollback()
    except Exception as e:  # si probleme d'accés à g.db ou d'operation sur la transaction on passe silencieusement
        app.logger.error(
            "before_teardown_commitdb : Unhandled exception (can be safely ignored) : {0} ".format(e))


@app.after_request
def after_request(response):
    response.headers[
        'Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data: cdnjs.cloudflare.com server.arcgisonline.com www.google.com www.gstatic.com www.google-analytics.com cdn.ckeditor.com cdn.jsdelivr.net unpkg.com fonts.googleapis.com fonts.gstatic.com ecotaxa.obs-vlfr.fr;frame-ancestors 'self';form-action 'self';"
    return response
