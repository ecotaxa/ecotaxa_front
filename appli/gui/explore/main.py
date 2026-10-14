# -*- coding: utf-8 -*-
# Explore page, v2: public map of the samples, with the projects of the selected samples
from typing import List, Dict, Any, Optional, Tuple

from flask import render_template, request
from flask_babel import _

from appli import app, gvp
from appli.gui.commontools import alert_box
from appli.project.main import vignette_size
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi, SamplesApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import (
    ObjectSetQueryRsp,
    SampleModel,
    ProjectTaxoStatsModel,
    TaxonModel,
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
    # Map of the samples, the projects of the selected samples are displayed below it
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


# Above, the selection is truncated: each sample costs a few queries
MAX_MAP_SAMPLES = 50
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


TOP_TAXA = 5


def _projects_taxo_stats(projids: List[int]) -> Dict[int, Dict[str, Any]]:
    """Classification totals and most validated taxa per project, from the precomputed
    projects stats (cheap, unlike the samples ones). Without stats, the boxes are still displayed."""
    try:
        with ApiClient(ProjectsApi, request) as api:
            rows: List[ProjectTaxoStatsModel] = api.project_set_get_stats(
                ids="+".join(str(p) for p in projids), taxa_ids="all"
            )
        # one row per taxon present in the project
        stats: Dict[int, Dict[str, Any]] = {}
        for row in rows:
            stat = stats.setdefault(
                row.projid,
                {"validated": 0, "predicted": 0, "dubious": 0, "unclassified": 0, "taxa": []},
            )
            stat["validated"] += row.nb_validated
            stat["predicted"] += row.nb_predicted
            stat["dubious"] += row.nb_dubious
            stat["unclassified"] += row.nb_unclassified
            if row.used_taxa[0] != -1 and row.nb_validated > 0:
                stat["taxa"].append((row.used_taxa[0], row.nb_validated))
        for stat in stats.values():
            stat["nbtaxa"] = len(stat["taxa"])
            stat["taxa"] = sorted(stat["taxa"], key=lambda t: -t[1])[:TOP_TAXA]
        taxa_ids = {tid for stat in stats.values() for tid, _nb in stat["taxa"]}
        names: Dict[int, str] = {}
        if taxa_ids:
            with ApiClient(TaxonomyTreeApi, request) as api:
                taxa: List[TaxonModel] = api.query_taxa_set(
                    ids="+".join(str(t) for t in taxa_ids)
                )
            names = {taxon.id: taxon.display_name for taxon in taxa}
        for stat in stats.values():
            stat["taxa"] = [(names.get(tid, str(tid)), nb) for tid, nb in stat["taxa"]]
        return stats
    except ApiException:
        return {}


@app.route("/gui/explore/map/projects", methods=["POST"])
def gui_explore_map_projects():
    """Projects of the samples selected on the map, with the samples information."""
    sampleids = [int(s) for s in gvp("samples").split(",") if s.strip().isdigit()]
    truncated = len(sampleids) > MAX_MAP_SAMPLES
    sampleids = sampleids[:MAX_MAP_SAMPLES]
    projects: Dict[int, Dict[str, Any]] = {}
    try:
        with ApiClient(SamplesApi, request) as sapi:
            samples: List[SampleModel] = [
                sapi.sample_query(sample_id=sampleid) for sampleid in sampleids
            ]
        with ApiClient(ProjectsApi, request) as papi, ApiClient(
            ObjectsApi, request
        ) as oapi:
            for sample in samples:
                if sample.projid not in projects:
                    projects[sample.projid] = {
                        "project": papi.project_query(
                            sample.projid, for_managing=False
                        ),
                        "samples": [],
                    }
                projects[sample.projid]["samples"].append(_sample_extent(oapi, sample))
    except ApiException as ae:
        if ae.status in (401, 403):
            return alert_box("warning", "", "accessdenied", _("Access denied"))
        return alert_box("error", "", "explore", _("Error loading the projects"))
    single = len(samples) == 1
    if single:
        # only one sample: its validated objects are displayed in its project box
        sample = samples[0]
        prj = projects[sample.projid]
        try:
            prj["images"], prj["total"] = _object_images(
                sample.projid, {"samples": str(sample.sampleid), "statusfilter": "V"}, 100, 100
            )
        except ApiException:
            prj["images"], prj["total"] = [], 0
    stats = _projects_taxo_stats(list(projects.keys()))
    for projid, prj in projects.items():
        prj["stats"] = stats.get(projid)
    return render_template(
        "v2/explore/_map_projects.html",
        projects=list(projects.values()),
        single=single,
        truncated=truncated,
        max_samples=MAX_MAP_SAMPLES,
        partial=True,
    )
