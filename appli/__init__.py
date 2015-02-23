# -*- coding: utf-8 -*-
from flask import Flask,render_template,request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security #, SQLAlchemyUserDatastore
import inspect,html
import appli.securitycachedstore

app = Flask("appli")
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

import appli.database
# Setup Flask-Security
user_datastore = appli.securitycachedstore.SQLAlchemyUserDatastoreCACHED(db, database.users, database.roles)
security = Security(app, user_datastore)


def ObjectToStr(o):
    return str([(n, v) for n, v in inspect.getmembers(o) if((not inspect.ismethod(v))and  (not inspect.isfunction(v))and  (n!='__module__')and  (n!='__doc__') )])

def PrintInCharte(txt):
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    return render_template('layout.html',bodycontent=txt)
def gvg(varname,defvalue=''):
    """
    Permet de récuperer une variable dans la Chaine GET ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par default si elle n'existe pas
    """
    return request.args.get(varname, defvalue)
def gvp(varname,defvalue=''):
    """
    Permet de récuperer une variable dans la Chaine POST ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par default si elle n'existe pas
    """
    return request.form.get(varname, defvalue)

# Ici les imports des modules qui definissent des routes
import appli.main
import appli.adminusers
import appli.tasks.view
import appli.search.view

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.exception(e)
    return render_template("errors/500.html"), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    # Ceci est imperatif si on veux pouvoir avoir des messages d'erreurs à l'écran sous apache
    app.logger.exception(e)
    import traceback,sys
    # Ajout des informations d'exception dans le template custom
    tb_list = traceback.format_tb(e.__traceback__)
    s = "<b>Error:</b> %s <br><b>Description: </b>%s \n<b>Traceback:</b>" % (html.escape(str(e.__class__)), html.escape(str(e)))
    for i in tb_list[::-1]:
        s += "\n" + html.escape(i)
    return render_template('errors/500.html' ,trace=s), 500

