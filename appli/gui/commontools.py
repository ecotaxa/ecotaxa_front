# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from typing import List, Dict, Optional
from flask import render_template, request, flash, session
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


def jobs_summary_data() -> Dict:
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

    jobs_summary = jobs_summary_data()
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


def build_mail(emails: str, type: str = "", text: str = "") -> str:
    """
    Build a mailto link .
    """
    return render_template("./v2/mail/_mailto.html", emails=emails, type=type)


def last_taxo_refresh(partial: bool = False):
    import datetime
    from appli.gui.staticlistes import py_messages

    if partial == True:
        return
    last_refresh = _get_last_refresh()
    if last_refresh is None or (datetime.datetime.now() - last_refresh).days > 7:

        flash(py_messages["taxosynchro"], "warning")


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
