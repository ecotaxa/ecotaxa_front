# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)

import os,sys,pathlib,urllib.parse
# Permet de traiter le probleme de l'execution dans un virtualenv sous windows de mathplotlib qui requiert TCL
if sys.platform.startswith('win32'):
    virtualprefix = sys.base_prefix
    if hasattr(sys, 'real_prefix'):
        sys.base_prefix = sys.real_prefix
    if float(sys.winver.replace('-32','')) < 3.5:
        from tkinter import _fix
        if "TCL_LIBRARY" not in os.environ:
            # reload module, so that sys.real_prefix be used
            from imp import reload
            reload(_fix)
    sys.base_prefix = virtualprefix

VaultRootDir=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..","vault")
if not os.path.exists(VaultRootDir):
    os.mkdir(VaultRootDir)
TempTaskDir=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..","temptask")
if not os.path.exists(TempTaskDir):
    os.mkdir(TempTaskDir)

from flask import Flask,render_template,request,g
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security
import inspect,html,math,threading,time,traceback
import appli.securitycachedstore
import matplotlib
matplotlib.use('Agg')

app = Flask("appli")
app.config.from_pyfile('config.cfg')
app.config['SECURITY_MSG_DISABLED_ACCOUNT']=('Your account is disabled. Email to the User manager (list on the left) to re-activate.','error')
app.logger.setLevel(10)

if 'PYTHONEXECUTABLE' in app.config:
    app.PythonExecutable=app.config['PYTHONEXECUTABLE']
else:
    app.PythonExecutable="TBD"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app,session_options={'expire_on_commit':True}) # expire_on_commit évite d'avoir des select quand on manipule les objets aprés un commit.

def XSSEscape(txt):
    return html.escape(txt)

import appli.database
# Setup Flask-Security
user_datastore = appli.securitycachedstore.SQLAlchemyUserDatastoreCACHED(db, database.users, database.roles)
security = Security(app, user_datastore)

app.MRUClassif = {} # Dictionnaire des valeurs recement utilisé par les classifications
app.MRUClassif_lock = threading.Lock()

def ObjectToStr(o):
#    return str([(n, v) for n, v in inspect.getmembers(o) if((not inspect.ismethod(v))and  (not inspect.isfunction(v))and  (n!='__module__')and  (n!='__doc__') and  (n!='__dict__') and  (n!='__dir__')and  (n!='__delattr__')and  (n!='__dir__')and  (n!='__dir__') )])
    return str([(n, v) for n, v in inspect.getmembers(o) if(('method' not in str(v))and  (not inspect.isfunction(v))and  (n!='__module__')and  (n!='__doc__') and  (n!='__dict__') and  (n!='__dir__') and  (n!='__weakref__') )])

def PrintInCharte(txt,title=None):
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    AddTaskSummaryForTemplate()
    module='' # Par defaut c'est Ecotaxa
    if request.path.find('/part')>=0:
        module = 'part'
    if not title:
        if module == 'part':
            title='EcoPart'
        else:
            title = 'EcoTaxa'
    return render_template('layout.html',bodycontent=txt,module=module,title=title)

def ErrorFormat(txt):
    return """
<div class='cell panel ' style='background-color: #f2dede; margin: 15px;'><div class='body' >
				<table style='background-color: #f2dede'><tr><td width='50px' style='color: red;font-size: larger'> <span class='glyphicon glyphicon-exclamation-sign'></span></td>
				<td style='color: red;font-size: larger;vertical-align: middle;'><B>%s</B></td>
				</tr></table></div></div>
    """%(txt)

def AddTaskSummaryForTemplate():
    from flask_login import current_user
    if getattr(current_user, 'id', -1) > 0:
        g.tasksummary = appli.database.GetAssoc2Col(
            "SELECT taskstate,count(*) from temp_tasks WHERE owner_id=%(owner_id)s group by taskstate"
            , {'owner_id': current_user.id})
    g.google_analytics_id = app.config.get('GOOGLE_ANALYTICS_ID', '')


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

def nonetoformat(v,fmt :str):
    """
    Permet de faire un formatage qui n'aura lieu que si la donnée n'est pas nulle et permet récuperer une chaine que la source soit une données ou un None issue d'une DB
    :param v: Chaine potentiellement None
    :param fmt: clause de formatage qui va etre générée par {0:fmt}
    :return: V ou chaine vide
    """
    if v is None:
        return ""
    return ("{0:"+fmt+"}").format(v)

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

def XSSUnEscape(txt):
    return html.unescape(txt)

def TaxoNameAddSpaces(name):
    Parts=[XSSEscape(x) for x in ntcv(name).split('<')]
    return ' &lt;&nbsp;'.join(Parts) # premier espace secable, second non

def FormatError(Msg,*args,DoNotEscape=False,**kwargs):
    caller_frameinfo=inspect.getframeinfo(sys._getframe(1))
    txt = Msg.format(*args, **kwargs)
    app.logger.error("FormatError from {} : {}".format(caller_frameinfo.function,txt))
    if not DoNotEscape:
        Msg=Msg.replace('\n','__BR__')
    txt=Msg.format(*args,**kwargs)
    if not DoNotEscape:
        txt=XSSEscape(txt)
    txt=txt.replace('__BR__','<br>')
    return "<div class='alert alert-danger' role='alert'>{}</div>".format(txt)

def FAIcon(classname,styleclass='fas'):
    return "<span class='{} fa-{}'></span> ".format(styleclass,classname)

def FormatSuccess(Msg,*args,DoNotEscape=False,**kwargs):
    txt=Msg.format(*args,**kwargs)
    if not DoNotEscape:
        txt=XSSEscape(txt)
    if not DoNotEscape:
        Msg=Msg.replace('\n','__BR__')
    txt=Msg.format(*args,**kwargs)
    if not DoNotEscape:
        txt=XSSEscape(txt)
    txt=txt.replace('__BR__','<br>')
    return "<div class='alert alert-success' role='alert'>{}</div>".format(txt)

def CreateDirConcurrentlyIfNeeded(DirPath:pathlib.Path):
    """
    Permets de créer le répertoire passé en paramètre s'il n'existe pas et le crée si nécessaire.
    Si la création échoue, il teste s'il n'a pas été créé par un autre processus, et dans ce cas ne remonte pas d'erreur.
    :param DirPath: répertoire à créer sous forme de path
    """
    try:
        if not DirPath.exists():
            DirPath.mkdir()
    except Exception as e:
        if not DirPath.exists():
            raise e


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

def GetAppManagerMailto():
    if 'APPMANAGER_EMAIL' in app.config and 'APPMANAGER_NAME' in app.config:
        return "<a href='mailto:{APPMANAGER_EMAIL}'>{APPMANAGER_NAME} ({APPMANAGER_EMAIL})</a>".format(**app.config)
    return ""

def CalcAstralDayTime(Date,Time,Latitude,Longitude):
    """
    Calcule la position du soleil pour l'heure donnée.
    :param Date: Date UTC
    :param Time:  Heure UTC
    :param Latitude: Latitude
    :param Longitude: Longitude
    :return: D pour Day, U pour Dusk/crépuscule, N pour Night/Nuit, A pour Aube/Dawn
    """
    from astral import Location
    l = Location()
    l.solar_depression= 'nautical'
    l.latitude = Latitude
    l.longitude = Longitude
    s = l.sun(date=Date, local=False)
    # print(Date,Time,Latitude,Longitude,s,)
    Result = '?'
    Inter=( {'d': 'sunrise', 'f': 'sunset' , 'r': 'D'}
          , {'d': 'sunset' , 'f': 'dusk'   , 'r': 'U'}
          , {'d': 'dusk'   , 'f': 'dawn'   , 'r': 'N'}
          , {'d': 'dawn'   , 'f': 'sunrise', 'r': 'A'}
           )
    for I in Inter:
        if s[I['d']].time()<s[I['f']].time() and (Time>=s[I['d']].time() and Time<=s[I['f']].time() ) :
            Result=I['r']
        elif s[I['d']].time() > s[I['f']].time() and (Time >= s[I['d']].time() or Time <= s[I['f']].time()):
            Result = I['r'] # Changement de jour entre les 2 parties de l'intervalle
    return Result

# Ici les imports des modules qui definissent des routes
import appli.main
import appli.adminusers
import appli.tasks.taskmanager
import appli.search.view
import appli.project.view
import appli.part.view
import appli.taxonomy.taxomain
import appli.usermgmnt

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

def JinjaNl2BR(t):
    return t.replace('\n', '<br>\n');

def JinjaGetManagerList(sujet=""):
    LstUsers=database.GetAll("""select distinct u.email,u.name,Lower(u.name)
FROM users_roles ur join users u on ur.user_id=u.id
where ur.role_id=2
and u.active=TRUE and email like '%@%'
order by Lower(u.name)""")
    if sujet:
        sujet="?"+urllib.parse.urlencode({"subject":sujet}).replace('+','%20')
    return " ".join(["<li><a href='mailto:{1}{0}'>{2} ({1})</a></li> ".format(sujet,*r) for r in LstUsers ])

ecotaxa_version="2.2.6"
def JinjaGetEcotaxaVersionText():
    return ecotaxa_version+" 2020-04-27"

app.jinja_env.filters['datetime'] = JinjaFormatDateTime
app.jinja_env.filters['nl2br'] = JinjaNl2BR
app.jinja_env.globals.update(GetManagerList=JinjaGetManagerList,GetEcotaxaVersionText=JinjaGetEcotaxaVersionText)


"""Changelog
2020-04-27 : V 2.2.6
    Bugfix #364 #366: Import de fichiers encodés latin_1 sous Linux.
    Bugfix #351: Exception python lors de l'import si la 2eme ligne du TSV n'est pas conforme.
2020-04-23 : V 2.2.5
    Amélioration du texte d'information sur le serveur FTP lors des exports.
2020-04-20 : V 2.2.4
    Bugfix/Regression #340 les imports d'objets sont en notation degrée decimaux et non pas degree.minutes
    Réduction du nombre de décimales lors des conversions des latitudes et longitudes exprimées en minutes
    Suppression de warning de dépraciation sur WTForm validators.required 
2020-02-07 : V 2.2.3
    Ajout de normpath sur certaines resolution de chemin suite à problème avec des lien sympboliques
2020-01-29 : V 2.2.2
    Part : Modification comportement default_depthoffset now override
    Part import : uvp6 sample use Pressure_offset
    Part export : Divers bugfix 
    Part view : Ajustement groupe de classes 
2020-01-14 : V 2.2.1
    Generation vignette : Largeur minimale pour voir au moins l'echelle
    Gestion UVP6 Remote : Format LOV TSV
    Fix python 3.7
    Améliorations performances import
    Part : Gestion graphique temporel temps absolu
    Part : Gestion graphique 1 couleur par sample + legende si un seul projet
    Part export : gestion aggregation des TSV sur détaillé et réduit + nom projet dans les summary
    Part import : ajustement format LOV TSV
    Part import : ignore les samples sans depth si profil vertical sinon si depth invalide mise à 0
      
2019-08-18 : V 2.2.0
    Intégration of UVPApp Data Format
2019-04-18 : V 2.1.0
    Fix #304,#316,#317
2019-04-03 : V 2.1.0
    Fix #111,#277,#304,#305,#306,#307,#311,#312,#314
2019.02.01 : V 2.0.1
    Fix implementation minor bug
2019.01.25 : V 2.0.0
    Integration with EcotaxoServer
    Handling new display_name child<parent #87,#172
    Python Packages upgrade (flask, numpy, scikit, .... ), Bootstrap Upgrade
    fix/improve #216,#274,#284,#280 
2018.11.22 : V 1.6.1
    Minor fix
2018.11.14 : V 1.6
    RandomForestClassifier modified from balanced to auto
    Export redesigned
    Import #224,#243,#248: Robustified issues with Sun Position computation, lat/lon of sample always recomputed
    ReImport : Added sun position computation, lat/lon of sample always recomputed
    Subset #255 : Added duplication of CNN features
    Admin Project : Enhanced user management
    Manual classif #169,#164 : Refresh counter at each save, use separated badges
    Manual classif #163,#162,#260 : autoremove autoadded by sort displayed fields, Validation,ObjDate,Lat,Long date available on list and added on popup
    Manual classif #161,#159,#158 : autorefresh on top filter value change, added Ctrl+L for Validate selection, Keep vertical position on save
    Manual classif #211,#210,#209,#207,#205,#183 : Help for TaxoFilter,Improved validator filter, Added filter on validation date, added save dubious
    Manual classif #212,#217: duplicated saving status, Annotator can import
    Maps : #208 added informations on the sample
    EcoPart Fix : computation of Plankton abondance include only Validated Now (then Reduced & Détailled export too)
    EcoPart Fix #201 : Export of raw now handle not-living exclusion
    EcoPart Fix #196: computation of Plankton abondance use the Deepth offset now, also substracted
    EcoPart Fix #184 : When ecotaxa project are merged, associated PartProject are now associated to the target project
    Also #214,#220,#186,#179,#178,#176,#175,#152,#107
    User Management : Handle Self creation and Country
    Privacy : Added privacy page and Google Analytics Opt-out
2018.08.16 : V 1.5.2
              Added hability to work on database without trust connection configured on pg_hba
              Added CSRF Token on AdminForms most sensibles screens
              Added CSRF protection on console screen
              Added CSP policies to reduce impact of XSS attack
              Fixed several SQL Inject vulnerabilities
              Fixed no more errors if folder SCN_networks is missing
              Removed dead code
2018.03.14 : V 1.5.1b
              Moved Daily task in external launch using cron.py
              fixed computation on particle
              modified handling of ftp export copy due to issue on LOV FTP is on NFS volume
2018.01.16 : V 1.5.1
              Bugfix on privilèges on part module causing performance issues
2017.12.23 : V 1.5
              Minor adjustements
2017.11.08 : V 1.4
              Deep machine learning Integration
              Optimization of classification update query
              Added a table for Statistics by taxo/project to optimize displays on classification
              Bugfix on Particle module
2017.11.03 : V 1.3.2
              On manual classification splitted menu on 2 menu : Project wide and filtered
              Implementing Automatic classification V2
              - Filtered prediction
              - Can save/and predict from model
              - New Screen for PostPredictionMapping
              - Multiple project for Learning Set
              - Handling Nan,+/- Inf as empty value
2017.09.16 : V 1.3.1
              Evolution of Confusion matrix for sklearn,numpy,matplotlib upgrade
              Evolution of RandomForest parameters
2017.07.05 : V 1.3.0
              Introduction of Particle module
2017.03.28 : V 1.2.3
              Bugfix in display annotator on image Popup
              Bugfix is Manage.py where using global db routine.
2017.03.22 : V 1.2.2
              Added composite taxon Taxon(parent) in metadata update screen
2017.03.12 : V 1.2.1
              Improved database transaction management to avoid long transaction
2017.01.30 : V 1.2
              Explore : Improved no result, improved taxo filter
              Explore : Public user can go on manual classification of any visible project
              Explore : Map on home of explore
              Map : Filter by project and Taxo
              Details page : MailTo to notify classif error, display on map,
              Details page : edit data by manager
              Import : Wizard to premapping, added taxo (parent) format allowed at import
              Import : Image import only with form to fill metadata
              Export BD at project level.
              Prediction : Limit count for statistics, predict only filtered taxon on target set
              Conf Matrix : Export TSV
              Topper : Progress bar, improved button clic, improved clear filter
              Contribute : Display selection count, change line selection behavior
              Contribute : Show taxo children
              Task : New menu for app admin + can see all task of all users


2016.12.07 : V 1.1 Several changes on annotation page, filters
              Select project : filter on name, instrument, subset
              Select project : display email
              Manual Classif : Several minor changes
              Manual Classif : Propose last 5 classification
              New Filters : Instrument, Annotator, Free Field, Month, Day period
              Import : New feature to update matadata from file
              Import : Bugfix on uppercase column name
              Project : New status to block prediction
              Filter on feature : Purge, subset, Export
              TSV Export : split in multiple file, predefined check, separate internalID, add 2nd line for reimport
              AutoClean empty sample
              Zoom : 200%
              Admin : All manager can create a project
              Home Page : Custom message by App manager
              Prediction : added PostClassifMapping
2016.06.10 : Removed X before Object name
             if file home.html or homebottom.html is missing use home-model.html and homebottom-model.html
             Theses file are read as UTF-8 Format instead of target platform settings.
             Integration of licenses files as md format before integration to GitHub
2016.03.15 : Added CreateDirConcurrentlyIfNeeded to avoid conflinct in creation of images directory by concurrent task
2016.01.17 : Added parameter PYTHONEXECUTABLE in Config.cfg
             Added objects view creation in Manage CreateDB
             Added a Matplotlib uses to execute correctly on GraphicLess server.
             Added Cascade delete on DB Definition to create them during CreateDB (obj_field & Histo)
             During ImportDb compare Taxon Name and Parent Taxon Name to process correctly Name duplicate
2015.12.14 : Bugfix in import task, use only ecotaxa prefixed files
2015.12.11 : Improved CSV export to include Direct Taxonomy parent name and Taxonomy hierarchy
             Included license.txt File

"""