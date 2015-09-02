# -*- coding: utf-8 -*-

import os,sys
# Permet de traiter le probleme de l'execution dans un virtualenv sous windows de mathplotlib qui requiert TCL
if sys.platform.startswith('win32'):
    virtualprefix = sys.base_prefix
    sys.base_prefix = sys.real_prefix
    from tkinter import _fix
    if "TCL_LIBRARY" not in os.environ:
        # reload module, so that sys.real_prefix be used
        from imp import reload
        reload(_fix)
    sys.base_prefix = virtualprefix

from flask import Flask,render_template,request,g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security #, SQLAlchemyUserDatastore
import inspect,html,sys,math
import appli.securitycachedstore

app = Flask("appli")
app.config.from_pyfile('config.cfg')

PythonExecutable="TEST"

db = SQLAlchemy(app,session_options={'expire_on_commit':True}) # expire_on_commit évite d'avoir des select quand on manipule les objets aprés un commit.

import appli.database
# Setup Flask-Security
user_datastore = appli.securitycachedstore.SQLAlchemyUserDatastoreCACHED(db, database.users, database.roles)
security = Security(app, user_datastore)


def ObjectToStr(o):
#    return str([(n, v) for n, v in inspect.getmembers(o) if((not inspect.ismethod(v))and  (not inspect.isfunction(v))and  (n!='__module__')and  (n!='__doc__') and  (n!='__dict__') and  (n!='__dir__')and  (n!='__delattr__')and  (n!='__dir__')and  (n!='__dir__') )])
    return str([(n, v) for n, v in inspect.getmembers(o) if(('method' not in str(v))and  (not inspect.isfunction(v))and  (n!='__module__')and  (n!='__doc__') and  (n!='__dict__') and  (n!='__dir__') and  (n!='__weakref__') )])

def PrintInCharte(txt):
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    AddTaskSummaryForTemplate()
    return render_template('layout.html',bodycontent=txt)


def AddTaskSummaryForTemplate():
    from flask.ext.login import current_user
    if getattr(current_user, 'id', -1) > 0:
        g.tasksummary = appli.database.GetAssoc2Col(
            "SELECT taskstate,count(*) from temp_tasks WHERE owner_id=%(owner_id)s group by taskstate"
            , {'owner_id': current_user.id})


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

def ntcv(v):
    """
    Permet de récuperer une chaine que la source soit une chaine ou un None issue d'une DB
    :param v: Chaine potentiellement None
    :return: V ou chaine vide
    """
    if v is None:
        return ""
    return v

def DecodeEqualList(txt):
    res={}
    for l in str(txt).splitlines():
        ls=l.split('=',1)
        if len(ls)==2:
            res[ls[0].strip().lower()]=ls[1].strip().lower()
    return res
def EncodeEqualList(map):
    l=["%s=%s"%(k,v) for k,v in map.items()]
    l.sort()
    return "\n".join(l)

def ScaleForDisplay(v):
    """
    Permet de supprimer les decimales supplementaires des flottant en fonctions de la valeur et de ne rien faire au reste
    :param v: valeur à ajuste
    :return: Texte formaté
    """
    if isinstance(v, (float)):
        if(abs(v)<100):
            return "%0.2f"%(v)
        else: return "%0.f"%(v)
    elif v is None:
        return ""
    else:
        return v

def ComputeLimitForImage(imgwidth,imgheight,LimitWidth,LimitHeight):
    width=imgwidth
    height=imgheight
    if width>LimitWidth:
        width=LimitWidth
        height=math.trunc(imgheight*width/imgwidth)
        if height==0: height=1
    if height>LimitHeight:
        height=LimitHeight
        width=math.trunc(imgwidth*height/imgheight)
        if width==0: width=1
    return width,height


# Ici les imports des modules qui definissent des routes
import appli.main
import appli.adminusers
import appli.tasks.taskmanager
import appli.search.view
import appli.project.view

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
    db.session.rollback()
    return render_template('errors/500.html' ,trace=s), 500

def JinjaFormatDateTime(d,format='%Y-%m-%d %H:%M:%S'):
    if d is None:
        return ""
    return d.strftime(format)

app.jinja_env.filters['datetime'] = JinjaFormatDateTime