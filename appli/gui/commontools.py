# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from typing import List, Dict, Optional
from flask import render_template, request, redirect, flash, session, url_for
from flask_login import current_user
from appli.constants import GUI_PATH

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

    if partial == True:
        return
    last_refresh = _get_last_refresh()
    if last_refresh is None or (datetime.datetime.now() - last_refresh).days > 7:

        flash("taxosynchro", "warning")


def breadcrumbs() -> list:
    from appli.gui.staticlistes import apptree

    crumbs = request.path.split("/")
    if "gui" in crumbs:
        crumbs.remove("gui")
    crumblist = []
    parent = ""
    url = []
    for i, crumb in enumerate(crumbs):
        if crumb != "":
            crumbvalue = breadcrumb(apptree, crumb, parent)
            url.append(crumb)
            if crumbvalue != None:
                crumbdict = dict({"url": "/".join(url), "id": next, "text": crumbvalue})
                if len(crumbs) == i + 2:
                    if isinstance(crumbs[i + 1], int) or crumbs[i + 1].isdigit():
                        crumbdict.update(dict({"id": crumbs[i + 1]}))
                    else:
                        crumbdict.update(dict({"action": crumbs[i + 1]}))
                crumblist.append(crumbdict)
                parent = crumb
    return crumblist


def breadcrumb(tree: dict, crumb: str, parent: str = "") -> str:

    if isinstance(tree, str):
        return tree
    if parent != "" and parent in tree.keys():
        tree = tree[parent]
        if isinstance(tree, dict) and "children" in tree.keys():
            tree = tree["children"]
    if isinstance(tree, dict) and crumb in tree.keys():
        if isinstance(tree[crumb], str):
            return tree[crumb]
        elif isinstance(tree[crumb], dict):
            if "root" in tree[crumb]:
                return tree[crumb]["root"]
            else:
                return breadcrumb(tree[crumb])
    else:
        return None


def html_to_text(html: str) -> str:
    import re

    pattrns = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    return re.sub(pattrns, "", html)


# recursive to_dict
def todict(obj):
    import enum, collections

    if isinstance(obj, str):
        return obj
    elif isinstance(obj, enum.Enum):
        return str(obj)
    elif isinstance(obj, dict):
        return dict((key, todict(val)) for key, val in obj.items())
    elif isinstance(obj, collections.Iterable):
        return [todict(val) for val in obj]
    elif hasattr(obj, "__slots__"):
        return todict(
            dict((name, getattr(obj, name)) for name in getattr(obj, "__slots__"))
        )
    elif hasattr(obj, "__dict__"):
        return todict(vars(obj))
    return obj


# messages


def py_get_messages(type):
    from appli.gui.staticlistes import py_messages

    if type == "project":
        from appli.gui.project.staticlistes import py_messages as py_messages_type
    elif type == "jobs":
        from appli.gui.jobs.staticlistes import py_messages as py_messages_type

    return {**py_messages, **py_messages_type}


# partial request - fetch - XHR
def is_partial_request(request):
    return request.headers.get("X-Requested-With") and (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )


#
# crsf_token


def crsf_token():
    import string
    import secrets

    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(45))
