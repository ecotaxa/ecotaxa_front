# -*- coding: utf-8 -*-
from typing import List

from flask import render_template, request, json

from appli import app, gvg, database, DecodeEqualList
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import SamplesApi, SampleModel, ProjectsApi, ProjectModel


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
    sql = "select DISTINCT lower(instrument) from acquisitions acq where acq.instrument is not null and acq.instrument!='' "
    if gvg("projid") != "":
        sql += " and acq.acq_sample_id in (select sampleid from samples where projid=" + str(
            int(gvg("projid"))) + ")"
    res = database.GetAll(sql + " order by 1")
    txt = "List of available Intruments : <hr><ul id=InstrumList>"
    for r in res:
        txt += "\n<li>{0}</li>".format(r[0])
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
    Prj = database.Projects.query.filter_by(projid=int(gvg("projid"))).first()
    classifsettings = DecodeEqualList(Prj.classifsettings)
    PostTaxoMapping = classifsettings.get("posttaxomapping", "")
    res = {'mapping': {}, 'taxo': {}}
    if PostTaxoMapping != '':
        res['mapping'] = {el[0].strip(): el[1].strip() for el in
                          [el.split(':') for el in PostTaxoMapping.split(',') if el != '']}
        sql = """SELECT tf.id, tf.name||case when p1.name is not null and tf.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name
                 FROM taxonomy tf
                left join taxonomy p1 on tf.parent_id=p1.id
                WHERE  tf.id = any (%s) 
                order by tf.name limit 2000"""
        res['taxo'] = {x[0]: x[1] for x in database.GetAll(sql, ([int(x) for x in res['mapping'].values()],))}

    return json.dumps(res)


@app.route("/search/annot/<int:PrjId>")
def searchannot(PrjId):
    projid = str(int(PrjId))
    res = database.GetAll("""Select id,name 
          from users
          where id in ( SELECT distinct classif_who FROM objects WHERE projid ={0} ) order by name""".format(projid))
    # if gvg("format",'J')=='J': # version JSon par defaut
    #     return json.dumps([dict(id=r[0],text=r[1]) for r in res])
    return render_template('search/annot.html', samples=res)
