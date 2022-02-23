# -*- coding: utf-8 -*-
from typing import List

from flask import render_template, g, request, json

from appli import app, gvg
from appli.utils import ApiClient, get_all_visible_projects
from to_back.ecotaxa_cli_py import SamplesApi, SampleModel, ProjectsApi, ProjectModel, ApiException


@app.route('/search/mappopup/')
def search_mappopup():
    g.filtertxt = ""
    if gvg('projid'):
        g.Projid = gvg('projid')
        projids = [int(x) for x in gvg("projid").split(',')]
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

    return render_template('search/mappopup.html')


@app.route('/search/mappopup/samples/')
def search_mappopup_samples():
    """
        AJAX call to return data for drawing samples points in the global map.
    """
    app.logger.info("Search mappopup req: %s", request.args)
    if gvg('projid'):
        projids = [int(x) for x in gvg("projid").split(',')]
    else:
        projids = [a_proj.projid for a_proj in get_all_visible_projects()]
    str_project_ids = "+".join([str(p) for p in projids])
    with ApiClient(SamplesApi, request) as api:
        samples: List[SampleModel] = api.samples_search(project_ids=str_project_ids,
                                                        id_pattern='%')

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

    ores = []
    for sam in samples:
        ores.append({'id': sam.projid, 'lat': sam.latitude, 'long': sam.longitude})
    return json.dumps(ores)


@app.route('/search/mappopup/getsamplepopover/<int:sampleid>')
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
    """.format(sampleid=sample.sampleid, orig_id=sample.orig_id,
               title=project.title, projid=project.projid,
               latitude=round(sample.latitude, 4), longitude=round(sample.longitude, 4))
    return txt


def getcommonfilters(data) -> str:
    return render_template('search/commonfilters.html', data=data)
