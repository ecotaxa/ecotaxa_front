# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
#
# V2 new font interface projects list
#

from typing import List


from flask import session, request, render_template, flash
from flask_login import current_user
from appli.utils import ApiClient

from to_back.ecotaxa_cli_py.api import ProjectsApi
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    UserModelWithRights,
)

# list of project privileges
def list_privileges() -> dict:
    return dict({"viewers": "View", "annotators": "Annotate", "managers": "Manage"})


def _get_mailto_manager(request, type: str = "") -> str:
    from to_back.ecotaxa_cli_py import MiscApi, Constants

    with ApiClient(MiscApi, request) as api:
        consts: Constants = api.used_constants()
        mgr_coords = consts.app_manager
        from appli.gui.commontools import build_mail

        return build_mail(emails=mgr_coords[1], type=type, text=mgr_coords[0])


def _get_mailto_instrument() -> str:
    # Construct a mailto: link, in case the instrument is not found
    from appli.gui.commontools import build_mail
    from appli.utils import get_managers

    admin_users = get_managers()
    emails = ";".join([usr.email for usr in admin_users])
    return build_mail(emails=emails, type="instrument_not_in_the_list")


def _get_projects_filters() -> dict:
    from appli import gvg, gvgm

    filt_title = gvg("filt_title", session.get("prjfilt_title", ""))
    session["prjfilt_title"] = filt_title
    filt_instrum = gvgm("filt_instrum")  # Get instrument from posted
    session["prjfilt_instrum"] = "|".join(filt_instrum)
    filt_subset = gvg("filt_subset")  # Get subset filter from posted
    session["prjfilt_subset"] = filt_subset
    if filt_subset == "":
        sess_filt_instrum = session.get("prjfilt_instrum", "")
        if sess_filt_instrum:
            filt_instrum = sess_filt_instrum.split("|")
        else:
            filt_instrum = []
        filt_subset = session.get("prjfilt_subset", "")
    return dict(
        {
            "title": filt_title,
            "instrum": filt_instrum,
            "subset": filt_subset,
        }
    )


def _prjs_list(listall: bool = False, filt: dict = None) -> List[ProjectModel]:
    prjs: List[ProjectModel] = []
    qry_filt_instrum = [""] if len(filt["instrum"]) == 0 else filt["instrum"]
    for an_instrument in qry_filt_instrum:
        with ApiClient(ProjectsApi, request) as apiProj:
            prjs.extend(
                apiProj.search_projects(
                    not_granted=listall,
                    title_filter=filt["title"],
                    instrument_filter=an_instrument,
                    filter_subset=(filt["subset"] == "Y"),
                )
            )
    # Sort for consistency - removed to test
    prjs.sort(key=lambda prj: prj.title.strip().lower())
    return prjs


def projects_list(
    listall: bool = False,
    partial: bool = False,
    action: str = "",
    typeimport: str = None,
) -> str:
    from appli.project.main import _manager_mail

    # projects ids and rights for current_user
    if not current_user.is_authenticated:
        render_template("v2/error.html", title="403", message=_("Restricted access"))
    # projects list
    # action format dict {name: str = '',type: str =''}
    can_access = {}
    filt = _get_projects_filters()
    prjs = []
    has_proj = True
    # get access granted projects list

    if action != "":
        listall = False
        partial = True
    prjs = _prjs_list(False, filt)
    if len(prjs) == 0 and listall == False:
        has_proj = False
        listall = True
    # if listall add not granted projects
    if listall == True:
        prjs = prjs + _prjs_list(True, filt)
    # prjs = prjs + prjs + prjs + prjs + prjs + prjs + prjs
    # reformat  current_user privileges
    rights = list_privileges()
    for k, v in rights.items():
        can_access.update({v: []})
        for prj in prjs:
            for u in getattr(prj, k):
                if current_user.id == u.id:
                    can_access[v].append(prj.projid)
    # current_user is either an ApiUserWrapper or an anonymous one from flask,
    # but we're in @login_required, so
    user: UserModelWithRights = current_user.api_user
    CanCreate = user and (1 in user.can_do)
    isadmin = user and (2 in user.can_do)

    maildata = dict(
        {
            # mail_instrument not in use
            #        "mail_instrument": _get_mailto_instrument(),
            "mailto_create_right": _get_mailto_manager(
                request, type="ask_for_creation_right"
            ),
            "_manager_mail": _manager_mail,
        }
    )
    # separate last_used_projects from pjs
    last_used_projects = list(p.projid for p in current_user.last_used_projects)
    from appli.gui.project.projects_list_interface import (
        project_table_columns,
        render_for_js,
    )

    columns = project_table_columns(action, typeimport)
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(prjs, columns, can_access, isadmin),
            "last_used": last_used_projects,
        }
    )
    if action == "" and not partial:
        template = "v2/index.html"
        from appli.gui.commontools import experimental_header

        experimental = experimental_header()

    else:
        template = "v2/project/_listcontainer.html"
        experimental = ""

    return render_template(
        template,
        tabledef=tabledef,
        CanCreate=CanCreate,
        filters=filt,
        can_access=can_access,
        listall=listall,
        partial=partial,
        isadmin=isadmin,
        maildata=maildata,
        has_proj=has_proj,
        typeimport=typeimport,
        experimental=experimental,
    )
