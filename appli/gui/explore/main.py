# -*- coding: utf-8 -*-
# Explore page, v2: public map of the samples, with the selected samples below it
import json
from typing import List, Dict, Any, Optional, Tuple

from flask import Response, render_template, request
from flask_babel import _
from flask_login import current_user

from appli import app, gvp
from appli.gui.commontools import alert_box
from appli.project.main import vignette_size
from appli.gui.project.projects_list import projects_access
from appli.gui.project.projects_list_interface_json import (
    project_table_columns,
    render_for_js,
    render_samples_stats,
)
from appli.utils import ApiClient, can_read_visible_project, get_all_visible_projects
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi, SamplesApi
from to_back.ecotaxa_cli_py.models import (
    ObjectSetQueryRsp,
    ProjectModel,
    SampleModel,
    SampleTaxoStatsModel,
)

IMAGE_FIELDS = [
    "obj.objid",
    "obj.imgcount",
    "img.file_name",
    "img.width",
    "img.height",
    "img.thumb_file_name",
    "img.thumb_width",
    "txo.display_name",
]


@app.route("/gui/explore/")
def gui_explore():
    # Map of the samples, the selected samples are displayed below it
    return render_template("v2/explore/index.html")


def _object_images(
    prj_id: int, filters: Dict[str, str], ipp: int, zoom: int
) -> Tuple[List[Dict[str, Any]], int]:
    """The images of the first ipp objects of the project matching the filters, sized for the posted
    page width, and the total number of matching objects."""
    page_width = max(int(gvp("resultwidth")) - 40, 200) if gvp("resultwidth").isdigit() else 800
    window_height = max(int(gvp("windowheight")) - 100, 200) if gvp("windowheight").isdigit() else 600
    with ApiClient(ObjectsApi, request) as api:
        objs: ObjectSetQueryRsp = api.get_object_set(
            project_id=prj_id,
            project_filters=filters,
            fields=",".join(IMAGE_FIELDS),
            window_size=ipp,
            window_start=0,
        )
    images: List[Dict[str, Any]] = []
    for obj_dtl in objs.details:
        dtl = dict(zip(IMAGE_FIELDS, obj_dtl))
        width, height = vignette_size(
            dtl["img.width"], dtl["img.height"], zoom, page_width, window_height
        )
        # the thumbnail when it is big enough, else the image itself
        thumb = dtl["img.thumb_file_name"]
        if thumb is None or dtl["img.thumb_width"] is None or dtl["img.thumb_width"] < width:
            thumb = dtl["img.file_name"]
        images.append(
            {
                "objid": dtl["obj.objid"],
                "src": thumb,
                "width": width,
                "height": height,
                "taxon": dtl["txo.display_name"],
                "imgcount": dtl["obj.imgcount"],
            }
        )
    return images, objs.total_ids


EXTENT_FIELDS = ["obj.objdate", "obj.objtime", "obj.depth_min", "obj.depth_max"]


def _sample_extreme(
    api: ObjectsApi, sample: SampleModel, order_field: str, filters: Dict[str, str]
) -> Optional[Dict[str, Any]]:
    """The first object of the sample in the given order, nulls are last in ascending order only,
    so the descending orders come with a filter excluding them."""
    filters = dict(filters, samples=str(sample.sampleid))
    objs: ObjectSetQueryRsp = api.get_object_set(
        project_id=sample.projid,
        project_filters=filters,
        fields=",".join(EXTENT_FIELDS),
        order_field=order_field,
        window_size=1,
        window_start=0,
    )
    if not objs.details:
        return None
    return dict(zip(EXTENT_FIELDS, objs.details[0]))


def _sample_extent(api: ObjectsApi, sample: SampleModel) -> Dict[str, Any]:
    first = _sample_extreme(api, sample, "obj.objdate", {})
    last = _sample_extreme(api, sample, "-obj.objdate", {"fromdate": "0001-01-01"})
    shallow = _sample_extreme(api, sample, "obj.depth_min", {})
    deep = _sample_extreme(api, sample, "-obj.depth_max", {"depthmin": "-999999", "depthmax": "999999"})

    def _datetime(row):
        if row is None or row["obj.objdate"] is None:
            return None
        return " ".join(str(v) for v in (row["obj.objdate"], row["obj.objtime"]) if v is not None)

    return {
        "sample": sample,
        "fromdate": _datetime(first),
        "todate": _datetime(last),
        "depthmin": shallow["obj.depth_min"] if shallow else None,
        "depthmax": deep["obj.depth_max"] if deep else None,
    }


def _sample_taxo_stats(sample: SampleModel) -> Optional[Dict[str, Any]]:
    """Classification totals and used taxa of the sample. Without stats, the sample is still displayed."""
    try:
        with ApiClient(SamplesApi, request) as api:
            rows: List[SampleTaxoStatsModel] = api.sample_set_get_stats(
                sample_ids=str(sample.sampleid)
            )
        if not rows:
            return None
        stats = render_samples_stats([sample], rows)[0]
    except ApiException:
        return None
    # (id, (name, status)), or (id, "notfound") for the -1 of unclassified objects
    stats["taxa"] = [
        named for _id, named in stats["used_taxa"] if named != "notfound"
    ]
    return stats


@app.route("/gui/explore/map/projects", methods=["POST"])
def gui_explore_map_projects():
    """The selected samples of the map: for several ones the usual table of their projects, loaded
    apart, for a single one its project, taxonomy stats and validated objects."""
    sampleids = [int(s) for s in gvp("samples").split(",") if s.strip().isdigit()]
    if len(sampleids) != 1:
        projids = sorted({int(p) for p in gvp("projects").split(",") if p.strip().isdigit()})
        return render_template(
            "v2/explore/_map_projects_table.html",
            projids=",".join(str(p) for p in projids),
            partial=True,
        )
    try:
        with ApiClient(SamplesApi, request) as sapi:
            sample: SampleModel = sapi.sample_query(sample_id=sampleids[0])
        with ApiClient(ProjectsApi, request) as papi:
            project = papi.project_query(sample.projid, for_managing=False)
        with ApiClient(ObjectsApi, request) as oapi:
            extent = _sample_extent(oapi, sample)
    except ApiException as ae:
        if ae.status in (401, 403):
            return alert_box("warning", "", "accessdenied", _("Access denied"))
        return alert_box("error", "", "explore", _("Error loading the projects"))
    try:
        images, total = _object_images(
            sample.projid, {"samples": str(sample.sampleid), "statusfilter": "V"}, 100, 100
        )
    except ApiException:
        images, total = [], 0
    return render_template(
        "v2/explore/_map_sample.html",
        project=project,
        row=extent,
        stats=_sample_taxo_stats(sample),
        images=images,
        total=total,
        partial=True,
    )


def _project_row(prj: ProjectModel) -> Dict[str, Any]:
    """A project as the usual projects table reads it. Field by field: a boosted API model has no
    attribute for what the back-end didn't send, as members to anonymous users, and to_dict() is shallow."""

    def person(user) -> Optional[Dict[str, Any]]:
        if user is None:
            return None
        return {key: getattr(user, key, None) for key in ("id", "name", "email")}

    row = {
        key: getattr(prj, key, None)
        for key in ("projid", "title", "instrument", "status", "access", "objcount", "pctvalidated")
    }
    row["contact"] = person(getattr(prj, "contact", None))
    for key in ("managers", "annotators", "viewers"):
        row[key] = [person(user) for user in getattr(prj, key, None) or []]
    return row


@app.route("/gui/explore/projects/<ids>")
def gui_explore_projects(ids: str):
    """The usual projects table, public, for the given projects among the readable ones."""
    wanted = {int(p) for p in ids.split(",") if p.strip().isdigit()}
    # an anonymous user gets the same projects from both searches
    prjs = {
        prj.projid: _project_row(prj)
        for prj in get_all_visible_projects(fields="*default")
        if prj.projid in wanted and can_read_visible_project(prj)
    }
    rows = sorted(prjs.values(), key=lambda prj: prj["projid"])
    columns = project_table_columns("", listall=True)
    if not current_user.is_authenticated:
        del columns["status"]
    # not the json of flask, which sorts the keys: the cells of a row are in the order of the columns
    content = json.dumps(
        {"columns": columns, "data": render_for_js(rows, columns, projects_access(rows))},
        separators=(",", ":"),
    )
    return Response(content, mimetype="application/json")
