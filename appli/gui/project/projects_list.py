# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
#
# V2 new font interface projects list
#

from typing import List

from appli import gvg, gvgm
from flask import session, request, render_template, flash
from flask_login import current_user
from flask_security import login_required
from appli.project.main import _manager_mail
from appli.back_config import get_app_manager_mail
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    UserModelWithRights,
    TaxonomyTreeStatus,
)

# list of project privileges
def list_privileges() -> dict:
    return dict({"viewers": "View", "annotators": "Annotate", "managers": "Manage"})


def _get_mailto_instrument() -> str:
    # Construct a mailto: link, in case the instrument is not found
    from appli.gui.commontools import build_mail
    from appli.utils import get_managers

    admin_users = get_managers()
    emails = ";".join([usr.email for usr in admin_users])
    return build_mail(
        emails=emails,
        link_text="Not in the list",
        subject="Request for adding an instrument to EcoTaxa",
        body="""**Information for creation**

    Instrument name:
    URL of the description in the BODC L22 vocabulary http://vocab.nerc.ac.uk/collection/L22/current/ :

    **Reason for creation**
    Explain how widely the instrument is distributed and why it should be added to the standard list.
    """,
    )


def _get_projects_filters() -> dict:

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
    # prjs.sort(key=lambda prj: prj.title.strip().lower())
    return prjs


def projects_list(
    listall: bool = False,
    partial: bool = False,
    action: str = "",
    typeimport: str = "all",
    type: str = "json",
):

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
    prjs = _prjs_list(False, filt)
    if len(prjs) == 0 and listall == False:
        has_proj = False
        listall = True
    # if listall add not granted projects
    if listall == True:
        prjs = prjs + _prjs_list(True, filt)

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
    mailto_instrument = _get_mailto_instrument()
    # App manager mail for granting right to create
    mailto_create_right = get_app_manager_mail(
        request, "EcoTaxa : Please provide me the Project creation right"
    )
    # separate last_used_projects from pjs
    last_used_projects = list(p.projid for p in current_user.last_used_projects)
    last_used_projects = list(filter(lambda p: p.projid in last_used_projects, prjs))
    if len(last_used_projects):
        prjs = list(set(prjs) - set(last_used_projects))
    if action == "" and partial == False:

        from appli.gui.commontools import experimental_header

        return render_template(
            "v2/index.html",
            prjlist=prjs,
            last_used_projects=last_used_projects,
            CanCreate=CanCreate,
            filters=filt,
            can_access=can_access,
            listall=listall,
            isadmin=2 in user.can_do,
            mailto_instrument=mailto_instrument,
            mailto_create_right=mailto_create_right,
            _manager_mail=_manager_mail,
            has_proj=has_proj,
            experimental=experimental_header(),
        )
    elif action != "":
        # imports - partial= True and listall= false
        if action == "importsettings":
            # if type == "json" get data in json format
            return render_template(
                "v2/project/_listimport.html",
                prjlist=prjs,
                last_used_projects=last_used_projects,
                filters=filt,
                listall=False,
                typeimport=typeimport,
                isadmin=2 in user.can_do,
            )

    else:
        # partial == True : send header from template and rows from other template / separated and dispatched  in js - do better one day  -  action 'request' key "projects" in js
        response = render_template(
            "v2/project/_list.html",
            prjlist=prjs,
            last_used_projects=last_used_projects,
            filters=filt,
            listall=listall,
            partial=partial,
            can_access=can_access,
            mailto_instrument=mailto_instrument,
            mailto_create_right=mailto_create_right,
            _manager_mail=_manager_mail,
            isadmin=2 in user.can_do,
        )

        if response != "":
            response = (
                response
                + "<--- header --->"
                + render_template("v2/project/_headerlist.html", listall=listall)
            )
        return response
