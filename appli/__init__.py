# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import html
import inspect
import math
import sys
import traceback
import urllib.parse
from typing import List, Optional
from flask import Flask, render_template, Markup, request, g
from flask_login import current_user, LoginManager
from appli.utils import ApiClient, ntcv
from to_back.ecotaxa_cli_py import UsersApi, MinUserModel
from appli.security_on_backend import user_from_api
from to_back.ecotaxa_cli_py import ApiException

app = Flask("appli")
app.config.from_pyfile("../config/config.cfg")
app.logger.setLevel(10)

# Read more config
backend_url = app.config["BACKEND_URL"]
assert backend_url.startswith("http://")
assert not backend_url.endswith("/")

ecopart_url = app.config["ECOPART_URL"]

# config and setup babel
from appli.constants import KNOWN_LANGUAGES, TRANSLATION_PATH
from flask_babel import Babel
from appli.ecotaxa_version import ecotaxa_version
app.config["BABEL_TRANSLATION_DIRECTORIES"] = TRANSLATION_PATH
app.config["PREFERRED_URL_SCHEME"] = "https"
babel = Babel(app)
# set up login manager
login_manager = LoginManager()
login_manager.login_view = "gui_login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return user_from_api(user_id)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(KNOWN_LANGUAGES)


def XSSEscape(txt):
    return html.escape(txt)


def PrintInCharte(txt: str, title: Optional[str] = None):
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    AddJobsSummaryForTemplate()
    if not title:
        title = "EcoTaxa"
    return render_template("layout.html", bodycontent=txt, title=title)


def ErrorFormat(txt: str) -> str:
    return (
        """
<div class='cell panel ' style='background-color: #f2dede; margin: 15px;'><div class='body' >
				<table style='background-color: #f2dede'><tr><td width='50px' style='color: red;font-size: larger'> <span class='glyphicon glyphicon-exclamation-sign'></span></td>
				<td style='color: red;font-size: larger;vertical-align: middle;'><B>%s</B></td>
				</tr></table></div></div>
    """
        % txt
    )


def AddJobsSummaryForTemplate() -> None:
    """
    Set in global 'g' a structure to show what is currently ongoing on jobs side.
    @see appli/templates/layout.html
    """
    if current_user.is_authenticated:
        # Summarize from back-end
        from appli.jobs.emul import _build_jobs_summary

        g.jobs_summary = _build_jobs_summary()
        g.google_analytics_id = app.config.get("GOOGLE_ANALYTICS_ID", "")


def gvg(varname: str, defvalue: str = "") -> str:
    """
    Permet de récuperer une variable dans la Chaine GET ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par defaut si elle n'existe pas
    """
    ret = request.args.get(varname, defvalue)
    return ret


def gvgm(varname: str) -> List[str]:
    """
    Permet de récuperer, pour une variable, toutes les valeurs dans la Chaine GET
    :param varname: Variable à récuperer
    :return: Liste des valeurs ou liste vide si la variable n'est pas présente
    """
    lst = request.args.getlist(varname)
    # filter empty values
    # return [a_val for a_val in lst if a_val]

    return [a_val for a_val in lst if a_val]


def gvp(varname: str, defvalue: str = "") -> str:
    """
    Permet de récuperer une variable dans la Chaine POST ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par defaut si elle n'existe pas
    """
    ret = request.form.get(varname, defvalue)
    # TODO: form is ImmutableMultiDict, meaning that .get can (and does) return list
    # -> the signature is wrong in flask/werkzeug source.
    return ret


def gvpm(varname: str) -> List[str]:
    """
    Permet de récuperer, pour une variable, toutes les valeurs dans la Chaine POST
    :param varname: Variable à récuperer
    :return: Liste des valeurs ou liste vide si la variable n'est pas présente
    """
    lst = request.form.getlist(varname)
    # filter empty values
    # return [a_val for a_val in lst if a_val]
    return [a_val for a_val in lst if a_val]


def nonetoformat(v, fmt: str):
    """
    Permet de faire un formatage qui n'aura lieu que si la donnée n'est pas nulle et permet récuperer une chaine que la source soit une données ou un None issue d'une DB
    :param v: Chaine potentiellement None
    :param fmt: clause de formatage qui va etre générée par {0:fmt}
    :return: V ou chaine vide
    """
    if v is None:
        return ""
    return ("{0:" + fmt + "}").format(v)


def XSSUnEscape(txt):
    return html.unescape(txt)


def TaxoNameAddSpaces(name):
    Parts = [XSSEscape(x) for x in ntcv(name).split("<")]
    return " &lt;&nbsp;".join(Parts)  # premier espace secable, second non


def FormatError(Msg, *args, DoNotEscape=False, **kwargs):
    caller_frameinfo = inspect.getframeinfo(sys._getframe(1))
    txt = Msg.format(*args, **kwargs)
    app.logger.error("FormatError from {} : {}".format(caller_frameinfo.function, txt))
    if not DoNotEscape:
        Msg = Msg.replace("\n", "__BR__")
    txt = Msg.format(*args, **kwargs)
    if not DoNotEscape:
        txt = XSSEscape(txt)
    txt = txt.replace("__BR__", "<br>")
    return "<div class='alert alert-danger' role='alert'>{}</div>".format(txt)


def FAIcon(classname, styleclass="fas"):
    return "<span class='{} fa-{}'></span> ".format(styleclass, classname)


def FormatSuccess(Msg, *args, DoNotEscape=False, **kwargs):
    txt = Msg.format(*args, **kwargs)
    if not DoNotEscape:
        txt = XSSEscape(txt)
    if not DoNotEscape:
        Msg = Msg.replace("\n", "__BR__")
    txt = Msg.format(*args, **kwargs)
    if not DoNotEscape:
        txt = XSSEscape(txt)
    txt = txt.replace("__BR__", "<br>")
    return "<div class='alert alert-success' role='alert'>{}</div>".format(txt)


def ComputeLimitForImage(imgwidth, imgheight, LimitWidth, LimitHeight):
    width = imgwidth
    height = imgheight
    if width > LimitWidth:
        width = LimitWidth
        height = math.trunc(imgheight * width / imgwidth)
        if height == 0:
            height = 1
    if height > LimitHeight:
        height = LimitHeight
        width = math.trunc(imgwidth * height / imgheight)
        if width == 0:
            width = 1
    return width, height


_utf_warn = "HINT: Did you use utf-8 while transferring?"

import unicodedata


def _suspicious_str(path: str):
    if not isinstance(path, str):
        return False
    try:
        t = repr(path)
        for c in path:
            # Below throws an exception and that's all we need
            unicodedata.name(c)
            if 0xFFF0 <= ord(c) <= 0xFFFF:
                # Replacement chars
                return True
        return False
    except ValueError:
        return True


def UtfDiag(errors, path: str):
    if _suspicious_str(path):
        errors.append(_utf_warn)


def UtfDiag2(fn, path1: str, path2: str):
    if _suspicious_str(path1) or _suspicious_str(path2):
        fn(_utf_warn)


def UtfDiag3(path: str):
    if _suspicious_str(path):
        return ". " + _utf_warn
    return ""


# import routes && functions for the new interface
import appli.gui.main

# Ici les imports des modules qui definissent des routes
import appli.main
import appli.search.view
import appli.project.view
import appli.taxonomy.taxomain
import appli.usermgmnt
import appli.api_proxy
import appli.project.emodnet
import appli.jobs.views
from appli.gui.commontools import new_ui_error


# error handlers
@app.errorhandler(404)
def not_found(e):
    return new_ui_error(e)


@app.errorhandler(401)
def unauthorized(e):
    return new_ui_error(e)


@app.errorhandler(403)
def forbidden(e):
    return new_ui_error(e)


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.exception(e)
    return new_ui_error(e)


# @app.errorhandler(ApiException)
# def handle_apiexception(e):
#    app.logger.exception(e)
#    return new_ui_error(e)


@app.errorhandler(Exception)
def unhandled_exception(e):
    # Ceci est imperatif si on veut pouvoir avoir des messages d'erreurs à l'écran sous apache
    app.logger.exception(e)
    # Ajout des informations d'exception dans le template custom
    tb_list = traceback.format_tb(e.__traceback__)
    s = "<b>Error:</b> %s <br><b>Description: </b>%s \n<b>Traceback:</b>" % (
        html.escape(str(e.__class__)),
        html.escape(str(e)),
    )
    for i in tb_list[::-1]:
        s += "\n" + html.escape(i)
    return new_ui_error(e, True, trace=s)
    # return render_template("errors/500.html", trace=s), 500


def JinjaFormatDateTime(d, format="%Y-%m-%d %H:%M:%S"):
    if d is None:
        return ""
    return d.strftime(format)


def JinjaNl2BR(t):
    return t.replace("\n", "<br>\n")


def JinjaGetUsersManagerList(sujet=""):
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


def JinjaGetEcotaxaVersionText():
    return ecotaxa_version["version"] + "." + ecotaxa_version["date"]


app.jinja_env.filters["datetime"] = JinjaFormatDateTime
app.jinja_env.filters["nl2br"] = JinjaNl2BR
app.jinja_env.globals.update(
    GetManagerList=JinjaGetUsersManagerList,
    GetEcotaxaVersionText=JinjaGetEcotaxaVersionText,
)
