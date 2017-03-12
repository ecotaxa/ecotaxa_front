# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask_security.decorators import roles_accepted
from appli.database import db
import os

# Load default config and override config from an environment variable
# app.config.update(dict(
# DEBUG=True,
# SECRET_KEY='development key',
# USERNAME='admin',
# PASSWORD='default'
# ))
# definition d'un second répertoire traité en statique en plus de static
vaultBP = Blueprint('vault', __name__, static_url_path='/vault', static_folder='../vault')
app.register_blueprint(vaultBP)


@app.route('/')
def index():
    txt="""<div style='margin:5px;'><div id="homeText"'>"""
    NomFichier='appli/static/home/home.html'
    if not os.path.exists(NomFichier):
        NomFichier='appli/static/home/home-model.html'
    with open(NomFichier, 'r',encoding='utf8') as f:
        txt+=f.read()
    txt+="""
	</div>
	<div class="row" id="homeSelectors" style="margin-top: 20px; margin-bottom: 20px;">
		<div class="col-sm-6">
        <a href="/explore/" class="btn btn-primary btn-lg btn-block">Explore images</a>
        
    		<p>As a visitor, you have free access to the specimens that have been already identified by taxonomy experts.</p>

    		<p>You can explore the database by navigating along the UniEuk taxonomic tree which aims at unifying taxonomic names and tree according to reliable and curated molecular phylogenies. It encompasses the whole Eukaryotic and Prokaryotic lineages (Viruses coming soon) that have been molecularly described. Then images can be filtered according to several criteria: geographic location, depth, date and time of sampling, imaging instrument, etc.</p>
        
		</div>
		<div class="col-sm-6">
        <a href="/prj/" class="btn btn-primary btn-lg  btn-block">Contribute to a project</a>
        
        <p>As a scientist, you can contribute to the richness of this image database and to the collaborative taxonomic annotation effort. Images are organised in projects which should be consistent in terms of sampling and imaging techniques. We provide tools to support the annotation of large image datasets by supervised machine learning prediction.</p>
		</div>		
	</div>
"""
    NomFichier='appli/static/home/homebottom.html'
    if not os.path.exists(NomFichier):
        NomFichier='appli/static/home/homebottom-model.html'
    txt+="""<div class="row" id="homeLegal"><div class="col-sm-12">"""
    with open(NomFichier, 'r',encoding='utf8') as f:
        txt+=f.read()
    txt+="""</div></div></div>"""

    return PrintInCharte(txt)
    # return render_template('layout.html',bodycontent=txt)


@app.route('/test1')
def test1():
    txt = """Hello World! <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
            <font color=red><span class="glyphicon glyphicon-search" aria-hidden="true"></span></font>
            <span class="glyphicon glyphicon-user" style="color:blue"></span>
            X<br>

           """
    txt += "Name =" + getattr(current_user,'name',"???")+"<br>"
    txt += "Id ="+str(getattr(current_user,'id',-1))+"<br>"
    txt += ObjectToStr(current_user)
    txt += "<br><img src='vault/test.jpg' width=500>"
    return render_template('layout.html',bodycontent=txt)



@app.route('/testadmin')
@roles_accepted(database.AdministratorLabel)
def testadmin():
    return "Admin OK"



@app.before_request
def before_request_security():
    # time.sleep(0.1)
    # print("URL="+request.url)
    # app.logger.info("URL="+request.url)
    if "/static" in request.url:
        return
    # print(request.form)
    current_user.is_authenticated()
    g.menu = []
    g.menu.append((url_for("index"),"Home / Explore"))
    g.menu.append(("/prj/","Select Project"))
    g.useradmin=False
    g.appliadmin=False
    if current_user.has_role(database.AdministratorLabel) or current_user.has_role(database.UserAdministratorLabel) :
        g.menu.append(("","SEP"))
        g.menu.append(("/admin","Admin Screen"))
        g.useradmin=True
    if current_user.has_role(database.AdministratorLabel) :
        g.menu.append(("/Task/Create/TaskTaxoImport","Import Taxonomy"))
        g.menu.append(("/Task/Create/TaskExportDb","Export Database"))
        g.menu.append(("/Task/Create/TaskImportDB","Import Database"))
        g.appliadmin=True

    g.menu.append(("","SEP"))
    g.menu.append(("/change","Change Password"))

