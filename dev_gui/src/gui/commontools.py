# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from typing import List, Dict, Optional
from flask import render_template, request, redirect, flash, session, url_for, Markup
from flask_login import current_user
from appli.constants import GUI_PATH

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    UserModelWithRights,
    TaxonomyTreeStatus,
)
from appli.constants import (
    AdministratorLabel,
    UserAdministratorLabel,
)


def _get_last_refresh() -> str:
    if not current_user.is_authenticated:
        return None
    import datetime

    with ApiClient(TaxonomyTreeApi, request) as apiTaxo:
        status: TaxonomyTreeStatus = apiTaxo.taxa_tree_status()
        try:
            last_refresh = datetime.datetime.strptime(
                status.last_refresh, "%Y-%m-%dT%H:%M:%S"
            )
        except (ValueError, TypeError, ApiException):
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


def breadcrumbs(default=None) -> list:
    from appli.gui.staticlistes import apptree

    crumbs = request.path.split("/")
    if "gui" in crumbs:
        crumbs.remove("gui")
    if default != None:
        crumbs.append(default)
    crumblist = []
    parent = ""
    url = []
    for i, crumb in enumerate(crumbs):
        if crumb != "":
            crumbvalue = breadcrumb(apptree, crumb, parent)
            url.append(crumb)
            if crumbvalue != None:
                crumbdict = dict({"url": "/gui/" + "/".join(url), "text": crumbvalue})
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


def py_get_messages(type=None):
    from appli.gui.staticlistes import py_messages

    if type == None:
        return {**py_messages}
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


def alert_box(
    type: str,
    title: str,
    codemessage: str,
    message: str,
    dismissible: bool = False,
    inverse: bool = False,
    is_safe: bool = False,
    extra: str = None,
):
    return render_template(
        "v2/partials/_alertbox.html",
        type=type,
        title=title,
        message=message,
        codemessage=codemessage,
        inverse=inverse,
        dismissible=dismissible,
        is_safe=is_safe,
        extra=extra,
        partial=True,
    )


# new_ui_error
def new_ui_error(e, is_exception: bool = False, trace: str = None):
    new_ui = request.path.find("/gui/") >= 0
    description = []
    code = 500

    if is_exception or not hasattr(e, "code"):
        if trace:
            description.append(str(trace))
    else:
        code = e.code
    partial = is_partial_request(request)
    if isinstance(e, ApiException):
        code = e.status
        exception = format_exception(e)
        if code != 500:
            if partial:
                return alert_box(
                    type="error",
                    title="error",
                    dismissible=True,
                    codemessage=str(code),
                    message=exception[1],
                )
            elif code not in [403, 401]:
                flash(exception[1], "error")
                return redirect(request.referrer)
        description.append(exception[1])

    else:
        py_messages = py_get_messages()
        if hasattr(e, "name") and e.name != None:
            description.append(str(e.name))
        if hasattr(e, "description") and e.description != None:
            if e.description.find("v2/help/_") <= 0:
                description.append(str(e.description))
            else:
                description.append(py_messages["page404"])
        if hasattr(e, "response") and e.response != None:
            description.append(str(e.response))
        if code == 403 or code == 401:
            message = py_messages["access403"]
            description.append(message)
    if not new_ui and code in [404, 403, 500]:
        return (
            render_template(
                "errors/" + str(code) + ".html", trace=Markup("<br>".join(description))
            ),
            code,
        )
    else:
        temp = render_template(
            "/v2/error.html",
            title=str(code),
            partial=partial,
            message=Markup("<br>".join(description)),
            is_safe=True,
        )
        return (
            temp,
            code,
        )


#
# crsf_token


def crsf_token():
    import string
    import secrets

    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(45))


def format_exception(ae, partial=True) -> tuple:
    if hasattr(ae, "status"):
        msg = str(ae.status)
    else:
        msg = ""
    if hasattr(ae, "body"):
        import json

        detail = ""
        if isinstance(ae.body, str):
            if ae.status == 500:
                detail = ae.body
            else:
                body = json.loads(ae.body)
                if "detail" in body:
                    detail = str(body["detail"])
        elif isinstance(ae.body, object):
            detail = json.dumps(ae.body)
        msg = msg + " - " + detail
        return ae.status, msg


def safe_url_redir(url: str) -> str:
    """
    remove domain from redirect
    """
    if url is not None:
        url = url.strip()
    if not url:
        return False
    from urllib.parse import urlparse

    redir = urlparse(url)
    url = (
        redir.path
        + str("?" + redir.query if redir.query != "" else "")
        + str("#" + redir.fragment if redir.fragment != "" else "")
    )
    return url
