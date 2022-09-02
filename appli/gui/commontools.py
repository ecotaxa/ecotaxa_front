# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from typing import List, Dict, Optional
from flask import render_template, request, flash, Markup, session
from flask_login import current_user
from appli.constants import GUI_PATH

from gettext import NullTranslations
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    UserModelWithRights,
    TaxonomyTreeStatus,
)


def _get_last_refresh() -> str:
    import datetime

    with ApiClient(TaxonomyTreeApi, request) as apiTaxo:
        status: TaxonomyTreeStatus = apiTaxo.taxa_tree_status()
        try:
            last_refresh = datetime.datetime.strptime(
                status.last_refresh, "%Y-%m-%dT%H:%M:%S"
            )
        except (ValueError, TypeError):
            last_refresh = None
    return last_refresh


def experimental_header(filename: str = "") -> str:
    # Add experimental URL for vips
    from appli.gui.staticlistes import vip_list, newpath

    path = request.path

    if not current_user.is_authenticated or current_user.id not in vip_list:
        return ""
    if path.find(GUI_PATH) < 0:
        keypath = path.split("/")
        del keypath[0]
        checkpath = keypath[0]
        if len(keypath) > 1:
            checkpath = checkpath + "/" + keypath[1]
        print("path =" + path)
        if checkpath not in newpath:
            return ""
        hint = "A new version of this page is available."
        session["oldpath"] = path
        experimental = (
            "<a class="
            + '"inline-block py-2 px-3 text-center whitespace-nowrap align-baseline" style="margin-top:0;margin-right:175px;z-index:100;color:#d6544b;font-weight:bold;font-size:0.925rempadding:.25rem .5rem;text-shadow:2px 2px 6px #FFaa00;" href="'
            + GUI_PATH
            + path
            + '" title="'
            + hint
            + '">'
            + "New!</a>"
        )

    else:
        hint = "Back to current version."
        oldpath = session.get("oldpath", path.replace(GUI_PATH, ""))
        experimental = (
            '<a  class="experimental" href="'
            + oldpath
            + '"  title="'
            + hint
            + '">Back</a>'
        )
    return experimental


def _jobs_summary_data() -> Dict:
    """
    Return a structure to show what is currently ongoing on jobs side.
    """
    if current_user.is_authenticated:
        # Summarize from back-end
        from appli.jobs.emul import _build_jobs_summary

        return _build_jobs_summary()
    return ""


def webstats(app) -> str:
    return app.config.get("GOOGLE_ANALYTICS_ID", "")


# temporary while 2 interfaces live together
def RenderTemplate(
    filename="index", templates="v2/", title="EcoTaxa 2.6", webstats="", bg=False
) -> str:
    import os

    jobs_summary = _jobs_summary_data()
    experimental = experimental_header()
    if filename[-1] == "/":
        filename = filename[:-1]
    if os.path.exists("appli/templates/" + templates + filename + ".html"):
        return render_template(
            templates + filename + ".html",
            jobs_summary=jobs_summary,
            webstats=webstats,
            experimental=experimental,
            current_user=current_user,
            title=title,
            bg=bg,
            gui=GUI_PATH + "/",
        )


def build_mail(emails: str, link_text: str, subject: str = "", body: str = ""):
    import urllib.parse

    """
    Build a mailto link to all app managers.
    """

    params = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body
    if params:
        txt_params = "?" + urllib.parse.urlencode(params).replace("+", "%20")
    else:
        txt_params = ""
    return "<a href='mailto:{0}{1}'>{2}</a>".format(emails, txt_params, link_text)


def find_language() -> NullTranslations:

    # Get the browser current language
    import gettext
    from appli.constants import KNOWN_LANGUAGES, TRANSLATION_PATH, DEFAULT_LOCALE

    # see https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1 to get all the 2 digits country codes
    # TODO put this constant in ecotaxa_dev/appli/project/__init__.py ?
    curLang: str = ""
    prefLangs = request.accept_languages
    if prefLangs is not None:
        # Here, there is at least one language
        # First one is the prefered language in the list of handled languages
        for l in prefLangs:
            curLang = l[0][
                :2
            ]  # first 2 letters show the country, and translations tables folders are organised this way
            if curLang in KNOWN_LANGAGES:
                try:  # N.B. [curLang] and not curLang in the following line
                    lang = gettext.translation(
                        "ecotaxa", "messages", [curLang]
                    )  # curLang == 'fr' or 'en' or 'zh' or 'pt' ...
                    okCurLang = True
                except:  # language corrupted or not existing
                    okCurLang = False
                if okCurLang:
                    lang.install()
                    return lang
            # try the next language
    # Tried all the languages without success, or there is no supported langage
    curLang = "en"  # desperate, so take english as last solution
    lang = gettext.translation("ecotaxa", "messages", [curLang])
    lang.install()
    return lang


def get_error_message(message: str) -> str:
    list_errors = dict(
        {
            "nomanager": "A manager person needs to be designated among the current project persons",
            "nobody": "One person, at least, needs to be related to the project",
            "nocontact": "A contact person needs to be designated among the current project managers.",
            "emptyname": "A privilege is incomplete. Please select a member name or delete the privilege row",
            "oneatleast": "One member at least is required with Manage privilege and contact property  ",
            "uhasnopriv": "privilege is missing",
        }
    )
    if message in list_errors.keys():
        return list_errors[message]
    else:
        return message
        return False


def last_taxo_refresh(partial: bool = False):
    import datetime

    if partial == True:
        return
    last_refresh = _get_last_refresh()
    if last_refresh is None or (datetime.datetime.now() - last_refresh).days > 7:
        flashtxt = (
            "Taxonomy synchronization and Ecotaxa version check wasn’t done during the last 7 days, "
            "Ask application administrator to do it."
        )  # +str(PDT.lastserverversioncheck_datetime)
        flashtxt += "  <a href='/taxo/browse/' class='btn btn-primary btn-xs'>Synchronize to check Ecotaxa version</a>"
        flash(Markup(flashtxt), "warning")


def breadcrumbs(filename: str) -> list:
    crumbs = pathloc.split("/")
    apptree = dict(
        {
            "": "Home",
            "prj": "Project",
            "help": "Help",
            "listall": "All",
            "create": "create",
            "edit": "edit",
        }
    )
    breadcrumb = []
    for crumb in crumbs:
        if crumb in apptree.keys():
            breadcrumb.append(dict({"link": "/".join(link), "text": apptree[crumb]}))
    return breadcrumb
