# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from flask import Blueprint, render_template, g, request, url_for
from flask_login import current_user
from appli import app, ObjectToStr, PrintInCharte, database, db
from flask_security.decorators import roles_accepted
import appli.part
import os

# definition d'un second répertoire traité en statique en plus de static
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UsersApi, UserModelWithRights, ApiException

vaultBP = Blueprint('vault', __name__, static_url_path='/vault', static_folder='../vault')
app.register_blueprint(vaultBP)


@app.route('/')
def index():
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


@app.route('/test1')
def test1():
    txt = """Hello World! <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
            <font color=red><span class="glyphicon glyphicon-search" aria-hidden="true"></span></font>
            <span class="glyphicon glyphicon-user" style="color:blue"></span>
            X<br>

           """
    txt += "Name =" + getattr(current_user, 'name', "???") + "<br>"
    txt += "Id =" + str(getattr(current_user, 'id', -1)) + "<br>"
    txt += ObjectToStr(current_user)
    txt += "<br><img src='vault/test.jpg' width=500>"
    return render_template('layout.html', bodycontent=txt)


@app.route('/testadmin')
@roles_accepted(database.AdministratorLabel)
def testadmin():
    return "Admin OK"


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
    # print(request.form)
    user_is_logged = False
    user_can_create = False
    user_can_administrate = False
    user_can_administrate_users = False
    mru_projects = []
    with ApiClient(UsersApi, request) as api:
        try:
            user: UserModelWithRights = api.show_current_user_users_me_get()
            user_is_logged = True
            user_can_create = 1 in user.can_do
            user_can_administrate = 2 in user.can_do
            user_can_administrate_users = 3 in user.can_do
            mru_projects = user.last_used_projects
        except ApiException as ae:
            if ae.status == 403:
                pass
    # current_user.is_authenticated
    g.cookieGAOK = request.cookies.get('GAOK', '')
    g.menu = []
    g.menu.append((url_for("index"), "Home / Explore"))
    if len(mru_projects) > 0:
        g.menu.append(("/prj/", "Select Project", "SUB"))
        for a_prj in mru_projects:
            g.menu.append(("/prj/%d" % a_prj.projid, "[%d] %s" % (a_prj.projid, a_prj.title)))
        g.menu.append(("", "NOSUB"))
    else:
        # TODO: I can't see the menu _at all_ for unlogged users?
        g.menu.append(("/prj/", "Select Project"))
    g.menu.append(("/part/", "Particle Module"))
    if user_is_logged:
        g.menu.append(("/part/prj/", "Particle projects management"))
    if user_can_create or user_can_administrate:
        g.menu.append(("", "SEP"))
        # g.menu.append(("/taxo/browse/","Manage Taxonomy"))
        if request.endpoint == 'indexPrj':
            g.menu.append(("javascript:PostDynForm('/taxo/browse/?fromprj=%d',{updatestat:'Y'});" % (
                request.view_args.get('PrjId'),), "Manage Taxonomy"))
        else:
            g.menu.append(("javascript:PostDynForm('/taxo/browse/',{updatestat:'Y'});", "Manage Taxonomy"))
    #     ?fromprj={{ g.Projid }}
    if user_can_administrate or user_can_administrate_users:
        g.menu.append(("", "SEP"))
        g.menu.append(("/admin/", "Admin Screen"))
        g.menu.append(("/Task/listall", "Task Manager"))

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
        app.logger.error("before_teardown_commitdb : Unhandled exception (can be safely ignored) : {0} ".format(e))


@app.after_request
def after_request(response):
    response.headers[
        'Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data: cdnjs.cloudflare.com server.arcgisonline.com www.google.com www.gstatic.com www.google-analytics.com cdn.ckeditor.com cdn.jsdelivr.net;frame-ancestors 'self';form-action 'self';"
    return response
