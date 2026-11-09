# -*- coding: utf-8 -*-
import math
from typing import Dict, List, Mapping

from flask import render_template, g, request, json

from appli import app, gvg, XSSEscape
from appli.utils import ApiClient, get_all_visible_projects, can_read_visible_project
from to_back.ecotaxa_cli_py import (
    SamplesApi,
    SampleModel,
    ProjectsApi,
    ProjectModel,
    ApiException,
)


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


@app.route("/search/mappopup/")
def search_mappopup():
    g.filtertxt = ""
    if gvg("projid"):
        g.Projid = gvg("projid")
        projids = [int(x) for x in gvg("projid").split(",")]
        titles = []
        with ApiClient(ProjectsApi, request) as api:
            for a_proj in projids:
                project: ProjectModel = api.project_query(project_id=a_proj)
                titles.append(project.title)
        g.filtertxt += "Project = " + ",".join(titles)

    # TODO: It's a bit useless to have this, as all other filters are not taken into account.
    # Either the map reflects the selection, with all criteria, or not.
    # if gvg('taxoid'):
    #     g.taxoid = gvg('taxoid')
    #     taxa_names = []
    #     with ApiClient(TaxonomyTreeApi, request) as api:
    #         categs: List[TaxonModel] = api.query_taxa_set(gvg('taxoid'))
    #     for a_taxon in categs:
    #         taxa_names.append(a_taxon.display_name)
    #     g.filtertxt += " ,Taxonomy = " + ",".join(taxa_names)
    #     if gvg('taxochild'):
    #         g.taxochild = gvg('taxochild')
    #         g.filtertxt += "(with child)"

    return render_template("search/mappopup.html")


@app.route("/search/mappopup/samples/")
def search_mappopup_samples():
    """
    AJAX call to return data for drawing samples points in the global map.
    """
    app.logger.info("Search mappopup req: %s", request.args)
    instrum = gvg("instrum")
    projids = None
    if gvg("projid"):
        projids = [int(x) for x in gvg("projid").split(",") if x.strip().isdigit()]
    if projids is None or instrum:
        # anonymous users can only read samples of open projects, a public one refuses the whole search
        visible = [
            a_proj.projid
            for a_proj in get_all_visible_projects(instrument_filter=instrum)
            if can_read_visible_project(a_proj)
            and (not instrum or a_proj.instrument == instrum)
        ]
        projids = visible if projids is None else [p for p in projids if p in visible]
    if not projids:
        return json.dumps([])
    str_project_ids = "+".join([str(p) for p in projids])
    with ApiClient(SamplesApi, request) as api:
        try:
            samples: List[SampleModel] = api.samples_search(
                project_ids=str_project_ids, id_pattern="%"
            )
        except ApiException as ae:
            app.logger.error("Search mappopup samples error: %s", ae.status)
            return json.dumps([])

    # TODO: Put into API one day
    #     if gvg('taxoid'):
    #         sql += " and sampleid in (select sampleid from objects where classif_id=any (%(taxoid)s) "
    #         sqlparam['taxoid'] = [int(x) for x in gvg("taxoid").split(',')];
    #         if gvg("taxochild") == "1":
    #             sqlparam['taxoid'] = [int(x[0]) for x in GetAll("""WITH RECURSIVE rq(id) as ( select id FROM taxonomy where id =any (%(taxoid)s)
    #                                     union
    #                                     SELECT t.id FROM rq JOIN taxonomy t ON rq.id = t.parent_id
    #                                     ) select id from rq """, {"taxoid": sqlparam['taxoid']})]
    #
    #         if gvg('projid'): sql += " and projid=any (%(projid)s) "
    #         sql += " ) "  # optimisation qui provoque de faux résultats : and (t.nbrobjcum>0 or t.nbrobj>0)
    #
    #     res = GetAll(sql, sqlparam)

    bounds = _map_bounds(request.args)
    ores = []
    for sam in samples:
        # no point on the map without coordinates
        if sam.latitude is None or sam.longitude is None:
            continue
        if not _in_map_bounds(sam.latitude, sam.longitude, bounds):
            continue
        ores.append(
            {
                "id": sam.sampleid,
                "projid": sam.projid,
                "lat": sam.latitude,
                "long": sam.longitude,
            }
        )
    return json.dumps(ores)


@app.route("/search/mappopup/getsamplepopover/<int:sampleid>")
def search_mappopup_samplepopover(sampleid: int):
    """
    AJAX call for getting a sample information.
    """
    try:
        with ApiClient(SamplesApi, request) as sapi:
            sample: SampleModel = sapi.sample_query(sample_id=sampleid)
        with ApiClient(ProjectsApi, request) as papi:
            project: ProjectModel = papi.project_query(project_id=sample.projid)
    except ApiException as ae:
        return str(ae)
    txt = """ID : {sampleid}<br>
    Original ID : {orig_id}<br>
    Project : {title} ({projid})<br>
    Lat/Lon : {latitude}/{longitude}
    """.format(
        sampleid=sample.sampleid,
        orig_id=XSSEscape(sample.orig_id),
        title=XSSEscape(project.title),
        projid=project.projid,
        latitude=round(sample.latitude, 4),
        longitude=round(sample.longitude, 4),
    )
    return txt


def getcommonfilters(data) -> str:
    return render_template("search/commonfilters.html", data=data)
