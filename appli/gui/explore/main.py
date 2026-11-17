# -*- coding: utf-8 -*-
# Explore page, v2: public map of the samples, with the selected samples below it
import json
import math
from typing import List, Dict, Any, Optional, Tuple, Mapping

from flask import Response, render_template, request
from flask_babel import _
from flask_login import current_user

from appli import app, gvg, gvp
from appli.gui.commontools import alert_box
from appli.gui.project.projects_list import projects_access
from appli.gui.project.projects_list_interface_json import (
    project_table_columns,
    render_for_js,
    render_samples_stats,
)
from appli.utils import ApiClient, can_read_visible_project
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


def _visible_projects(
    instrument_filter: str = "", fields: str = "projid,title,access"
) -> List[ProjectModel]:
    """The visible projects, granted or not, with only the given fields."""
    with ApiClient(ProjectsApi, request) as api:
        try:
            filters = {}
            if instrument_filter:
                # the back-end matches a part of the instrument code, callers can compare the whole one
                fields += ",instrument"
                filters["instrument_filter"] = instrument_filter
            projects: List[ProjectModel] = api.search_projects(
                title_filter="%", fields=fields, **filters
            )
            otherprojects: List[ProjectModel] = api.search_projects(
                title_filter="%", not_granted=True, fields=fields, **filters
            )
        except ApiException:
            return []
    return [prj for prj in projects + otherprojects if prj.access != "0"]


def _map_bounds(args: Mapping[str, str]) -> Dict[str, float]:
    """
    The usable bounds among MapN, MapS, MapW and MapE: a missing or invalid one doesn't filter.
    """
    bounds = {}
    for name in ("MapN", "MapS", "MapW", "MapE"):
        try:
            value = float(args.get(name, ""))
        except ValueError:
            continue
        if math.isfinite(value):
            bounds[name] = value
    return bounds


def _in_map_bounds(lat: float, lon: float, bounds: Dict[str, float]) -> bool:
    """
    Is the point inside the bounds? West greater than East is a box across the antimeridian.
    """
    north, south = bounds.get("MapN"), bounds.get("MapS")
    west, east = bounds.get("MapW"), bounds.get("MapE")
    if north is not None and lat > north:
        return False
    if south is not None and lat < south:
        return False
    if west is not None and east is not None and west > east:
        return lon >= west or lon <= east
    if west is not None and lon < west:
        return False
    if east is not None and lon > east:
        return False
    return True


@app.route("/gui/explore/map/samples/")
def gui_explore_map_samples():
    """
    The points of the map: readable samples with coordinates, filtered on projects, instrument and lat/lon box.
    """
    instrum = gvg("instrum")
    projids = None
    if gvg("projid"):
        projids = [int(x) for x in gvg("projid").split(",") if x.strip().isdigit()]
    if projids is None or instrum:
        # anonymous users can only read samples of open projects, a public one refuses the whole search
        visible = [
            a_proj.projid
            for a_proj in _visible_projects(instrument_filter=instrum)
            if can_read_visible_project(a_proj)
            and (not instrum or a_proj.instrument == instrum)
        ]
        projids = visible if projids is None else [p for p in projids if p in visible]
    if not projids:
        return Response("[]", mimetype="application/json")
    with ApiClient(SamplesApi, request) as api:
        try:
            samples: List[SampleModel] = api.samples_search(
                project_ids="+".join([str(p) for p in projids]), id_pattern="%"
            )
        except ApiException as ae:
            app.logger.error("Explore map samples error: %s", ae.status)
            return Response("[]", mimetype="application/json")
    bounds = _map_bounds(request.args)
    points = [
        {"id": sam.sampleid, "projid": sam.projid, "lat": sam.latitude, "long": sam.longitude}
        for sam in samples
        # no point on the map without coordinates
        if sam.latitude is not None
        and sam.longitude is not None
        and _in_map_bounds(sam.latitude, sam.longitude, bounds)
    ]
    return Response(json.dumps(points), mimetype="application/json")


def vignette_size(
    origwidth: Optional[int],
    origheight: Optional[int],
    zoom: int,
    page_width: int,
    window_height: int,
) -> Tuple[int, int]:
    """
    Displayed size of an object image: zoomed, at least 75px, at most the page width and window height.
    Same rules as the images of the legacy classification page.
    """
    if origwidth is None or origheight is None:
        # no image, happens for subsets without images
        origwidth = width = 80
        origheight = height = 40
    else:
        width = origwidth * zoom // 100
        height = origheight * zoom // 100
    if max(width, height) < 75:  # under 75px, no scaling
        if max(origwidth, origheight) < 75:
            width = origwidth  # a small image is displayed as is
            height = origheight
        elif max(origwidth, origheight) == origwidth:
            width = 75
            height = max(origheight * 75 // origwidth, 1)
        else:
            height = 75
            width = max(origwidth * 75 // origheight, 1)
    # the image always fits in the screen
    if width > page_width:
        width = page_width
        height = max(math.trunc(origheight * width / origwidth), 1)
    if height > window_height:
        height = window_height
        width = max(math.trunc(origwidth * height / origheight), 1)
    return width, height


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
        for prj in _visible_projects(fields="*default")
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
