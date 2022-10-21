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

from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi
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
    # session["prjfilt_title"] = filt_title
    filt_instrum = gvgm("filt_instrum")  # Get instrument from posted
    # session["prjfilt_instrum"] = "|".join(filt_instrum)
    filt_subset = gvg("filt_subset", "")  # Get subset filter from posted
    # session["prjfilt_subset"] = filt_subset
    # if filt_subset == "":
    #    sess_filt_instrum = session.get("prjfilt_instrum", "")
    #    if sess_filt_instrum:
    #        filt_instrum = sess_filt_instrum.split("|")
    #    else:
    #        filt_instrum = []
    #    filt_subset = session.get("prjfilt_subset", "")
    return dict(
        {
            "title": filt_title,
            "instrum": filt_instrum,
            "subset": filt_subset,
        }
    )


def _prjs_list(listall: bool = False, filt: dict = None) -> List[ProjectModel]:
    # remove filts because of session - must be revised

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
    typeimport: str = "",
) -> str:
    from appli.project.main import _manager_mail

    # projects ids and rights for current_user
    if not current_user.is_authenticated:
        return json_dumps(
            dict(
                {
                    "error": True,
                    "status": 403,
                    "title": "403",
                    "message": py_messages["restrictedaccess"],
                }
            )
        )

    # projects list
    # action format dict {name: str = '',type: str =''}
    can_access = {}
    filt = _get_projects_filters()
    prjs = []
    has_proj = True

    # current_user is either an ApiUserWrapper or an anonymous one from flask,
    # but we're in @login_required, so
    user: UserModelWithRights = current_user.api_user
    isadmin = user and (2 in user.can_do)

    last_used_projects = list(p.projid for p in current_user.last_used_projects)
    if typeimport != "":
        listall = False
    if typeimport == "taxo":
        prjs = _prj_import_taxo()
    else:
        # get access granted projects list
        prjs = _prjs_list(False, filt)
        if len(prjs) == 0 and listall == False:
            has_proj = False
            listall = True
            # if listall add not granted projects
            if listall == True:
                prjs = prjs + _prjs_list(True, filt)
        lastprjs = list(filter(lambda p: p.projid in last_used_projects, prjs))
        # separate last_used_projects from pjs
        if len(last_used_projects):
            prjs = list(set(prjs) - set(lastprjs))
            prjs = lastprjs + prjs
        if typeimport == "":
            # reformat  current_user privileges with projects id list -usage in  main projects list
            rights = list_privileges()
            for k, v in rights.items():
                can_access.update({v: []})
                for prj in prjs:
                    for u in getattr(prj, k):
                        if current_user.id == u.id:
                            can_access[v].append(prj.projid)

    from appli.gui.project.projects_list_interface import (
        project_table_columns,
        render_for_js,
    )

    columns = project_table_columns(typeimport)
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(prjs, columns, can_access, isadmin),
            "last_used": last_used_projects,
            "has_proj": has_proj,
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
        return render_template(
            "v2/error.html", title="403", message=py_messages["restrictedaccess"]
        )

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

    if typeimport != "":
        listall = False

    if typeimport == "" and not partial:
        template = "v2/index.html"
        from appli.gui.commontools import experimental_header

        experimental = experimental_header()

    else:
        template = "v2/project/_listcontainer.html"
        experimental = ""

    return render_template(
        template,
        CanCreate=CanCreate,
        listall=listall,
        partial=partial,
        isadmin=isadmin,
        maildata=maildata,
        typeimport=typeimport,
        experimental=experimental,
    )


# new import taxo ( no more separate ids and text)
def _prj_import_taxo(prjid: int = 0) -> list:
    from markupsafe import escape

    # Query accessible projects
    with ApiClient(ProjectsApi, request) as api:
        prjs: List[ProjectModel] = api.search_projects(
            also_others=False, filter_subset=False
        )
    # And their statistics
    prj_ids = " ".join([str(a_prj.projid) for a_prj in prjs])
    with ApiClient(ProjectsApi, request) as api:
        stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(ids=prj_ids)

    # Sort for consistency
    prjs.sort(key=lambda prj: prj.title.strip().lower())
    # Collect id for each taxon to show
    taxa_ids_for_all = set()
    stats_per_project = {}
    for a_prj in prjs:
        taxa_ids_for_all.update(a_prj.init_classif_list)
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
        if a_prj.projid != prjid:
            # Inject taxon lists for display
            prj_initclassif_list = set(a_prj.init_classif_list)
            try:
                objtaxon = set(stats_per_project[a_prj.projid])
            except KeyError:
                # No stats
                objtaxon = set()
            # 'Extra' are the taxa used, but not in the classification preset
            objtaxon.difference_update(prj_initclassif_list)
            a_prj = a_prj.to_dict()  # immutable -> to_dict()
            a_prj["preset"] = dict(
                (t, escape(taxo_map.get(int(t))))
                for t in prj_initclassif_list
                if t in taxo_map
            )
            a_prj["objtaxonnotinpreset"] = dict(
                (t, escape(taxo_map.get(int(t)))) for t in objtaxon if t in taxo_map
            )
            # return only prjs with taxons
            if len(a_prj["preset"]) or len(a_prj["objtaxonnotinpreset"]):
                prjs_pojo.append(a_prj)
    return prjs_pojo
