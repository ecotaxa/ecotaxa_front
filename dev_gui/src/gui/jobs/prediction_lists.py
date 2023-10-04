import time
from typing import List, Any, Final, Tuple, Optional, Dict

from flask import render_template, g, redirect, flash, request

from appli import PrintInCharte, gvg, XSSEscape, gvp, app
from appli.gui.jobs.Job import Job
from appli.utils import ApiClient, DecodeEqualList, EncodeEqualList
from to_back.ecotaxa_cli_py import (
    ApiException,
    ObjectsApi,
    ObjectSetQueryRsp,
    ProjectSetColumnStatsModel,
    ProjectTaxoStatsModel,
    PredictionReq,
    PredictionRsp,
)
from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import TaxonModel, ProjectModel


def api_read_accessible_projects(instrument_filter, title_filter):
    bef = time.time()
    with ApiClient(ProjectsApi, request) as api:
        ret: List[ProjectModel] = api.search_projects(
            not_granted=False,
            title_filter=title_filter,
            instrument_filter=instrument_filter,
            filter_subset=False,
        )
    with ApiClient(ProjectsApi, request) as api:
        ret.extend(
            api.search_projects(
                not_granted=True,
                title_filter=title_filter,
                instrument_filter=instrument_filter,
                filter_subset=False,
            )
        )
    app.logger.info("Get Projects API call duration: %0.3f s", time.time() - bef)
    return ret


def projects_for_prediction_list(projid):
    # First configuration page, choose base projects
    # This page is called from initial GET or POSTs to iself when project filters are used
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(projid, for_managing=False)
        except ApiException as ae:
            if ae.status in (401, 403):
                ae.reason = py_messages["access403"]
    if target_proj is None:
        return PrintInCharte(filters_html)
    # The page reloads itself (POST) when using the "Search" button
    try:
        # In case the filter box was used, validate it.
        if gvp("filt_featurenbr"):
            filt_featurenbr = int(gvp("filt_featurenbr"))
        else:
            filt_featurenbr = 10
    except ValueError:
        flash("Common features must be an integer", category="error")
        return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
    title_filter = gvp("filt_title", "")
    if request.method == "GET":
        instrument_filter = target_proj.instrument
    else:
        instrument_filter = gvp("filt_instrum", "")

    src_projs_str = gvp("srcs", "").split(",")
    src_projs = [int(prj_str) for prj_str in src_projs_str if prj_str.isdigit()]

    # Get previous choices AKA settings which are stored at project level
    settings = DecodeEqualList(target_proj.classifsettings)
    target_features = set(target_proj.obj_free_cols.keys())

    previous_ls = settings.get(
        "baseproject", ""
    )  # a coma-separated list of project IDs
    if previous_ls != "":
        # We can have one or several base projects, which are reminded here
        settings_prj_ids = [
            int(prj_id) for prj_id in previous_ls.split(",") if prj_id.isdigit()
        ]
    else:
        settings_prj_ids = []

    # Collect information for out-of-table projects as well
    no_tbl_projs = {}  # key: project ID, value: ProjectModel

    # Collect all projects matching the conditions
    usable_proj_list = api_read_accessible_projects(instrument_filter, title_filter)

    # Enrich the list with useful calculations
    filtered_projs = []
    matching_per_proj = {}
    validated_per_proj = {}
    for a_maybe_src_prj in usable_proj_list:
        matching_features = len(
            set(a_maybe_src_prj.obj_free_cols.keys()) & target_features
        )
        if matching_features < filt_featurenbr:
            no_tbl_projs[a_maybe_src_prj.projid] = a_maybe_src_prj
            continue
        matching_per_proj[a_maybe_src_prj.projid] = matching_features
        validated = (
            (a_maybe_src_prj.objcount if a_maybe_src_prj.objcount else 0)
            * (a_maybe_src_prj.pctvalidated if a_maybe_src_prj.pctvalidated else 0)
            / 100
        )
        validated_per_proj[a_maybe_src_prj.projid] = validated
        filtered_projs.append(a_maybe_src_prj)

    # Sort to have the most interesting ones in first
    filtered_projs.sort(
        key=lambda r: (-matching_per_proj[r.projid], -validated_per_proj[r.projid])
    )
    table_lines = []
    for a_maybe_src_prj in filtered_projs:
        matching = matching_per_proj[a_maybe_src_prj.projid]
        validated = validated_per_proj[a_maybe_src_prj.projid]
        cnn_network_id = (
            a_maybe_src_prj.cnn_network_id if a_maybe_src_prj.cnn_network_id else ""
        )
        if a_maybe_src_prj.projid in src_projs:
            checked = True
            src_projs.remove(a_maybe_src_prj.projid)
        elif a_maybe_src_prj.projid in settings_prj_ids:
            checked = True
        else:
            checked = False
        line = dict(
            {
                "projid": a_maybe_src_prj.projid,
                "title": a_maybe_src_prj.title,
                "validated_nb": int(validated),
                "matching_nb": matching,
                "deep_model": cnn_network_id,
                "instrument": a_maybe_src_prj.instrument,
            }
        )
        if not checked:
            table_lines.append(line)
        else:
            table_lines.insert(0, line)

    # Collect project info for missing IDs. We need remaining ALL selected source projects and settings ones
    base_prj_infos = []
    not_found_msg = "(ignored, not found)"
    for a_base_prj_id in settings_prj_ids + src_projs:
        if a_base_prj_id in no_tbl_projs:
            continue
        with ApiClient(ProjectsApi, request) as api:
            try:
                proj: ProjectModel = api.project_query(
                    a_base_prj_id, for_managing=False
                )
                no_tbl_projs[a_base_prj_id] = proj
            except ApiException as _ae:
                # The base project might be gone or not visible to current user
                base_prj_infos.append((a_base_prj_id, not_found_msg))

    for prj_id in src_projs:
        # Remaining source projects are filtered by display, but still valid in selection
        line = {
            "projid": prj_id,
            "title": "⚠️ Filtered ⚠️" + no_tbl_projs[prj_id].title,
            "validated_nb": "",
            "matching_nb": "",
            "deep_model": "",
        }
        table_lines.insert(0, line)
    return table_lines
