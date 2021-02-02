# -*- coding: utf-8 -*-
from typing import List

from flask import render_template, request, json

from appli import app, gvg, DecodeEqualList
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import SamplesApi, SampleModel, ProjectsApi, ProjectModel, InstrumentApi, TaxonomyTreeApi, \
    TaxonModel, ProjectUserStatsModel


@app.route("/search/samples")
def searchsamples():
    # Entry point for searching in samples for one or several project
    # Get request params
    if gvg("projid") != "":
        project_ids = [int(gvg("projid"))]
    elif gvg("projid[]") != "":
        project_ids = [int(x) for x in request.args.getlist("projid[]")]
    else:
        project_ids = []
    project_ids = "+".join([str(p) for p in project_ids])
    pattern = gvg("q")
    # Do back-end call
    with ApiClient(SamplesApi, request) as api:
        samples: List[SampleModel] = api.samples_search_samples_search_get(project_ids=project_ids,
                                                                           id_pattern=gvg("q"))
    if gvg("format", 'J') == 'J':  # version JSon par defaut
        return json.dumps([dict(id=s.sampleid, text=s.orig_id) for s in samples])
    else:
        # Render HTML
        for_disp = [(s.sampleid, s.orig_id) for s in samples]
        return render_template('search/samples.html', samples=for_disp)


@app.route("/search/exploreproject")
def searchexploreproject():
    # Public page
    with ApiClient(ProjectsApi, request) as api:
        prjs: List[ProjectModel] = api.search_projects_projects_search_get(title_filter=gvg("q"))
    for_disp = [dict(id=p.projid, text=p.title) for p in prjs]
    return json.dumps(for_disp)


@app.route("/search/instrumlist")
def searchinstrumlist():
    project_ids = ""
    if gvg("projid") != "":
        project_ids = gvg("projid")
    with ApiClient(InstrumentApi, request) as api:
        instrums: List[str] = api.instrument_query_instruments_get(project_ids=project_ids)
    txt = "List of available Intruments : <hr><ul id=InstrumList>"
    for r in instrums:
        txt += "\n<li>{0}</li>".format(r)
    txt += """</ul>
    <hr>
    &nbsp;<button type="button" class="btn btn-default btn-"  onclick="$('#PopupDetails').modal('hide');">Close</button>
    <br><br>
    <script>
    $('#InstrumList li').click(function(){
        $('#filt_instrum').val($(this).text());
        $('#PopupDetails').modal('hide');
    }).css('cursor','pointer');
    </script>
    """
    return txt


@app.route("/search/gettaxomapping")
def searchgettaxomapping():
    # Very specific call during Automatic Classification, to decode the mapping b/w
    # taxa from classif and target taxa.
    proj_id = int(gvg("projid"))
    with ApiClient(ProjectsApi, request) as api:
        proj: ProjectModel = api.project_query_projects_project_id_get(proj_id, for_managing=False)
    # Example proj.classifsetting
    #     baseproject=1850,1578,1581
    #     critvar=%area,angle,area,area_exc,bx,by,cdexc,centroids,circ.,circex,convarea,convperim,cv,elongation,esd,fcons,feret,feretareaexc,fractal,height,histcum1,histcum2,histcum3,intden,kurt,major,max,mean,meanpos,median,min,minor,mode,nb1,nb2,perim.,perimareaexc,perimferet,perimmajor,range,skelarea,skew,slope,sr,stddev,symetrieh,symetriehc,symetriev,symetrievc,thickr,width,x,xm,xstart,y,ym,ystart
    #     posttaxomapping=45067:25828,45041:78383
    #     seltaxo=25828,84963,85061,85076,85044,11514,85116,85123,12908,51958,11518,81935,12838,45036,85078,12846,30815,45052,45054,56693,11512
    #     usemodel_foldername=testln1
    classifsettings = DecodeEqualList(proj.classifsettings)
    PostTaxoMapping = classifsettings.get("posttaxomapping", "")
    res = {'mapping': {}, 'taxo': {}}
    if PostTaxoMapping != '':
        res['mapping'] = {el[0].strip(): el[1].strip() for el in
                          [el.split(':') for el in PostTaxoMapping.split(',') if el != '']}
        # Collect name for each needed id
        lst = "+".join(res['mapping'].values())
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxo_info: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=lst)
        # Fill in result list
        res['taxo'] = {taxon_rec.id: taxon_rec.display_name for taxon_rec in taxo_info}

    return json.dumps(res)


@app.route("/search/annotators/<int:PrjId>")
def searchannot(PrjId):
    # Return all annotators for a project
    with ApiClient(ProjectsApi, request) as api:
        stats: List[ProjectUserStatsModel] = api.project_set_get_user_stats_project_set_user_stats_get(ids=str(PrjId))
    res = [(r.id, r.name) for r in stats[0].annotators]
    return render_template('search/annot.html', samples=res)
