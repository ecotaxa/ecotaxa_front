# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from typing import Dict
from flask import (
    render_template,
    request,
    redirect,
    flash,
)
from markupsafe import Markup
from flask_login import current_user

from appli.utils import ApiClient
from appli.back_config import get_back_constants
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi
from to_back.ecotaxa_cli_py import ApiException
from werkzeug.exceptions import HTTPException
from to_back.ecotaxa_cli_py.models import (
    TaxonomyTreeStatus,
)


def _get_last_refresh() -> int:
    if not current_user.is_authenticated:
        return 0
    from datetime import datetime

    try:
        with ApiClient(TaxonomyTreeApi, request) as apiTaxo:
            status: TaxonomyTreeStatus = apiTaxo.taxa_tree_status()
            last_refresh = datetime.strptime(status.last_refresh, "%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError, ApiException):
        last_refresh = 0

    return last_refresh


def possible_licenses() -> list:

    licenses = get_back_constants("LICENSE")
    return licenses[0]


def possible_access() -> dict:

    consts = get_back_constants("ACCESS")
    access = {}
    sorted_access = dict(sorted(consts.items(), key=lambda x: x[1]))
    for k, v in sorted_access.items():
        access[v] = k
    return access


def possible_models():
    from to_back.ecotaxa_cli_py.api import MiscApi

    with ApiClient(MiscApi, request) as api:
        possibles = api.query_ml_models()

    scn = {a_model.name: {"name": a_model.name} for a_model in possibles}
    return scn


def jobs_summary_data() -> Dict:
    """
    Return a structure to show what is currently ongoing on jobs side.
    """
    if current_user.is_authenticated:
        # Summarize from back-end
        from appli.jobs.emul import _build_jobs_summary

        return _build_jobs_summary()
    return {}


def build_mail(emails: str, typ: str = "", text: str = "") -> str:
    """
    Build a mailto link .
    """
    return render_template("./v2/mail/_mailto.html", emails=emails, type=typ, text=text)


def last_taxo_refresh(cookiename):
    if not current_user.is_authenticated:
        return None
    from datetime import datetime

    typ = "warning"
    # cookie for messages  is type+cookiename but for warnings a suffix is needed
    dailyinfo = request.cookies.get(typ + cookiename + "_last_taxo_refresh")
    dformat = "%Y-%m-%d %H:%M:%S"
    if dailyinfo is not None:
        if (datetime.strptime(dailyinfo, dformat) - datetime.now()).days < 1:
            return None
    last_refresh = _get_last_refresh()
    if last_refresh != 0 and (datetime.now() - last_refresh).days > 7:
        py_messages = py_get_messages()
        return dict(
            {
                "type": typ,
                "content": py_messages["taxosynchro"],
                "date": last_refresh,
                "dismissible": True,
                "is_safe": True,
                "cookiename": cookiename + "_last_taxo_refresh",
            }
        )
    return None


def breadcrumbs(default=None) -> list:
    from appli.gui.staticlistes import apptree

    crumbs = request.path.split("?")
    crumbs = crumbs[0].split("/")
    if "static" in crumbs:
        return []
    if "gui" in crumbs:
        crumbs.remove("gui")
    if default is not None:
        crumbs.append(default)
    crumblist = []
    url = []
    tree = apptree
    for i, crumb in enumerate(crumbs):
        if crumb != "" or (i == 0):
            crumbvalue, childtree = breadcrumb(tree, crumb)
            url.append(crumb)
            if crumbvalue is not None:
                crumbdict = dict({"url": "/".join(url), "text": crumbvalue})
                if (
                    i + 2 == len(crumbs)
                    and isinstance(crumbs[i + 1], int)
                    or crumb.isdigit()
                ):
                    crumbdict.update(dict({"id": crumbs[i + 1]}))
                crumblist.append(crumbdict)
            if childtree is not None:
                tree = childtree

    return crumblist


def breadcrumb(tree: dict, crumb: str) -> tuple:
    if isinstance(tree, str):
        return tree, None
    if isinstance(tree, dict):
        if crumb in tree.keys():
            if isinstance(tree[crumb], str):
                return tree[crumb], None
            elif isinstance(tree[crumb], dict):
                if "children" in tree[crumb]:
                    childtree = tree[crumb]["children"]
                else:
                    childtree = None
                if "root" in tree[crumb]:
                    return tree[crumb]["root"], childtree
                elif "one" in tree[crumb]:
                    return tree[crumb]["one"], childtree
                else:
                    return None, childtree
    return None, None


def html_to_text(html: str) -> str:
    import re

    pattrns = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    return re.sub(pattrns, "", html)


# recursive to_dict
def todict(obj):
    import enum
    import collections.abc

    if isinstance(obj, str):
        return obj
    elif isinstance(obj, enum.Enum):
        return str(obj)
    elif isinstance(obj, dict):
        return dict((key, todict(val)) for key, val in obj.items())
    elif isinstance(obj, collections.abc.Iterable):
        return [todict(val) for val in obj]
    elif hasattr(obj, "__slots__"):
        return todict(
            dict((name, getattr(obj, name)) for name in getattr(obj, "__slots__"))
        )
    elif hasattr(obj, "__dict__"):
        return todict(vars(obj))
    return obj


# messages


def py_get_messages(_type=None):
    from appli.gui.staticlistes import py_messages

    if _type is None:
        return {**py_messages}
    if _type == "project":
        from appli.gui.project.staticlistes import py_messages as py_messages_type
    elif _type == "collection":
        from appli.gui.collection.staticlistes import py_messages as py_messages_type
    elif _type == "jobs":
        from appli.gui.jobs.staticlistes import py_messages as py_messages_type
    else:
        return {**py_messages}
    return {**py_messages, **py_messages_type}


# partial request - fetch - XHR
def is_partial_request():
    return request.headers.get("X-Requested-With") and (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )


def alert_box(
    _type: str,
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
        type=_type,
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
    resp_json = "application/json"
    new_ui = request.path.find("/gui/") >= 0
    description = []
    code = 500
    if is_exception or not hasattr(e, "code"):
        if trace:
            description.append(str(trace))
    else:
        code = e.code
    partial = is_partial_request()
    if isinstance(e, ApiException):
        if request.content_type == resp_json:
            return {"error": e.status, "text": e.reason, "body": e.body}, e.status
        code = e.status
        exception = format_exception(e)
        if code != 500:
            if partial:
                return {
                    "error": e.status,
                    "text": e.reason,
                    "body": e.body,
                }, e.status
            elif code not in [403, 401]:
                flash(exception[1], "error")
                if request.referrer:
                    return redirect(request.referrer)

        description.append(exception[1])
    elif isinstance(e, HTTPException):
        response = e.get_response()
        if response.content_type == resp_json:
            return e
    else:
        py_messages = py_get_messages()
        if hasattr(e, "name") and e.name is not None:
            description.append(str(e.name))
        if hasattr(e, "description") and e.description is not None:
            if e.description.find("v2/help/_") <= 0:
                description.append(str(e.description))
            else:
                description.append(py_messages["page404"])
        if hasattr(e, "response") and e.response is not None:
            description.append(str(e.response))
        if code == 403 or code == 401:
            message = py_messages["access403"]
            description.append(message)
    if not new_ui and code in [404, 403, 500]:
        return (
            render_template(
                "errors/" + str(code) + ".html",
                trace=Markup("<br>".join(description)),
                error=code,
            ),
            code,
        )
    elif request.content_type == resp_json:
        return {"error": code, "text": description}, code
    else:
        temp = render_template(
            "/v2/error.html",
            title=str(code),
            partial=partial,
            error=code,
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


def format_exception(ae) -> tuple:
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


def safe_url_redir(url: str):
    """
    remove domain from redirect
    """
    url = url.strip()
    if url == "":
        return ""
    from urllib.parse import urlparse

    redir = urlparse(url)
    url = (
        redir.path
        + str("?" + redir.query if redir.query != "" else "")
        + str("#" + redir.fragment if redir.fragment != "" else "")
    )
    return redirect(url)


def make_response(status: int, message: str) -> dict:
    return dict({"status": status, "message": message})
