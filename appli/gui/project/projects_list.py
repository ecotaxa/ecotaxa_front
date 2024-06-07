# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
#
# V2 new font interface projects list
#

from typing import List

from flask import session, request, render_template
from flask_login import current_user

from appli.utils import ApiClient
from werkzeug.exceptions import Forbidden
from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi, AuthentificationApi
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    UserModelWithRights,
)

# flash and errors messages translated
from appli.gui.staticlistes import py_messages

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

    filt_title = gvg("filt_title", "")
    filt_instrum = gvgm("filt_instrum")
    filt_subset = gvg("filt_subset", "")

    return dict(
        {
            "title": filt_title,
            "instrum": filt_instrum,
            "subset": filt_subset,
        }
    )


def _prjs_list_api(
    listall: bool = False,
    filt: dict = {},
    for_managing: bool = False,
    summary: bool = False,
) -> list:
    import requests

    prjs = list([])
    qry_filt_instrum = (
        [""]
        if ("instrum" not in filt or len(filt["instrum"]) == 0)
        else filt["instrum"]
    )
    for an_instrument in qry_filt_instrum:
        payload = dict(
            {
                "not_granted": listall,
                "title_filter": filt["title"],
                "instrument_filter": an_instrument,
                "filter_subset": (filt["subset"] == "Y"),
                "for_managing": for_managing,
            }
        )
        if summary == True:
            payload.update({"summary": True})
        with ApiClient(ProjectsApi, request) as apiproj:
            url = (
                apiproj.api_client.configuration.host + "/projects/search"
            )  # endpoint is nowhere available as a const :(
            token = apiproj.api_client.configuration.access_token
            headers = {
                "Authorization": "Bearer " + token,
            }
        r = requests.get(url, headers=headers, params=payload)
        if r.status_code == 200:
            prjs.extend(r.json())
        else:
            r.raise_for_status()
    return prjs


def projects_list(
    listall: bool = False,
    partial: bool = False,
    for_managing: bool = False,
    selection="list",
    filt=None,
    typeimport: str = "",
) -> str:
    # TODO review usage of listall - currently is used for not_granted
    import datetime
    from appli.project.main import _manager_mail

    # projects ids and rights for current_user
    if not current_user.is_authenticated:
        return dict(
            {
                "error": True,
                "status": 403,
                "title": "403",
                "message": py_messages["access403"],
            }
        )

    can_access = {}
    if filt == None:
        filt = _get_projects_filters()
    prjs = []
    # current_user is either an ApiUserWrapper or an anonymous one from flask,
    # but we're in @login_required, so
    user: UserModelWithRights = current_user.api_user
    isadmin = current_user.is_app_admin == True
    if typeimport != "":
        # full list avalaible to import - 2 calls when not app admin
        listall = False
    if typeimport == "taxo":
        prjs = _prj_import_taxo_api(0, filt)
        if current_user.is_app_admin == False:
            prjs = prjs + _prj_import_taxo_api(0, filt, not_granted=True)
    else:
        prjs = _prjs_list_api(listall, filt, for_managing=for_managing, summary=True)
        if typeimport != "" and current_user.is_app_admin == False:
            prjs = prjs + _prjs_list_api(True, filt, for_managing=for_managing)
        now = datetime.datetime.now()
        # last_used_projects are put on top of list in the interface
        last_used_projects = list(p.projid for p in current_user.last_used_projects)
        if len(last_used_projects):
            lastprjs = list(filter(lambda p: p["projid"] in last_used_projects, prjs))
            # separate last_used_projects from pjs
            prjs = list(filter(lambda p: p["projid"] not in last_used_projects, prjs))
            prjs = lastprjs + prjs
        if typeimport == "":
            # reformat  current_user privileges with projects id list -usage in  main projects list
            rights = list_privileges()
            for k, v in rights.items():
                can_access.update({v: []})
                for prj in prjs:
                    for u in prj[k]:
                        if current_user.id == u["id"]:
                            can_access[v].append(prj["projid"])

    from appli.gui.project.projects_list_interface_json import (
        project_table_columns,
        render_for_js,
    )

    columns = project_table_columns(typeimport, selection=selection)
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(prjs, columns, can_access),
        }
    )
    return tabledef


# project list page without projects list data


def projects_list_page(
    listall: bool = False,
    partial: bool = False,
    typeimport: str = "",
) -> str:
    from appli.project.main import _manager_mail

    # projects ids and rights for current_user
    if not current_user.is_authenticated:
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    # current_user is either an ApiUserWrapper or an anonymous one from flask,
    # but we're in @login_required, so
    user: UserModelWithRights = current_user.api_user
    # no more project creator
    if user.id:
        CanCreate = True
    else:
        CanCreate = False
    isadmin = current_user.is_app_admin == True

    from appli.gui.project.projects_list_interface_json import project_table_columns

    if typeimport == "" and not partial:
        template = "v2/project/index.html"
    else:
        template = "v2/project/_listcontainer.html"

    lastprjs = [p.projid for p in user.last_used_projects]
    return render_template(
        template,
        CanCreate=CanCreate,
        listall=listall,
        partial=partial,
        isadmin=isadmin,
        # columns=json.dumps(columns),
        last_used_projects=lastprjs,
        typeimport=typeimport,
    )


# new import taxo ( no more separate ids and text)
def _prj_import_taxo_api(
    prjid: int = 0, filt: dict = None, not_granted: bool = False
) -> list:
    import requests

    prjs = list([])
    qry_filt_instrum = (
        [""] if (filt == None or len(filt["instrum"]) == 0) else filt["instrum"]
    )
    for_managing = False
    for an_instrument in qry_filt_instrum:
        with ApiClient(ProjectsApi, request) as apiproj:
            url = (
                apiproj.api_client.configuration.host + "/projects/search/"
            )  # endpoint is nowhere available as a const :(
            token = apiproj.api_client.configuration.access_token
            headers = {
                "Authorization": "Bearer " + token,
                # "Content-Range": reqheaders["Content-Range"],
            }
            payload = dict(
                {
                    "for_managing": for_managing,
                    "not_granted": not_granted,
                    "instrument_filter": an_instrument,
                    "filter_subset": False,
                }
            )
            r = requests.get(url, headers=headers, params=payload)
            if r.status_code == 200:
                prjs.extend(r.json())
            else:
                r.raise_for_status()
    prj_ids = " ".join([str(a_prj["projid"]) for a_prj in prjs])
    with ApiClient(ProjectsApi, request) as api:
        stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(ids=prj_ids)
    # Sort for consistency
    prjs.sort(key=lambda prj: prj["title"].strip().lower())
    # Collect id for each taxon to show
    taxa_ids_for_all = set()
    stats_per_project = {}
    for a_prj in prjs:
        taxa_ids_for_all.update(a_prj["init_classif_list"])
    for a_stat in stats:
        taxa_ids_for_all.update(a_stat.used_taxa)
        stats_per_project[a_stat.projid] = a_stat.used_taxa
    # Collect name for each existing id
    lst = [str(tid) for tid in taxa_ids_for_all if tid != -1]
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(lst))
    taxo_map = {taxon_rec.id: taxon_rec.display_name for taxon_rec in res}
    txt = ""
    prjs_pojo = []
    for a_prj in prjs:
        # exclude current prj
        if a_prj["projid"] != prjid:
            # Inject taxon lists for display
            prj_initclassif_list = set(a_prj["init_classif_list"])
            try:
                objtaxon = set(stats_per_project[a_prj["projid"]])
            except KeyError:
                # No stats
                objtaxon = set()
            # 'Extra' are the taxa used, but not in the classification preset
            objtaxon.difference_update(prj_initclassif_list)
            a_prj["preset"] = dict(
                (t, taxo_map.get(int(t))) for t in prj_initclassif_list if t in taxo_map
            )
            a_prj["objtaxonnotinpreset"] = dict(
                (t, taxo_map.get(int(t))) for t in objtaxon if t in taxo_map
            )
            # return only prjs with taxons
            if len(a_prj["preset"]) or len(a_prj["objtaxonnotinpreset"]):
                prjs_pojo.append(a_prj)
    return prjs_pojo
