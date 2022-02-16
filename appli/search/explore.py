import random
from typing import List, Dict, Any

from flask import render_template, request

import appli
from appli import app, gvg, gvp, XSSEscape
from appli.constants import DayTimeList
from appli.project.main import FilterList, MONTH_LABELS, LoadRightPaneForProj
from appli.search.leftfilters import getcommonfilters
######################################################################################################################
from appli.utils import ApiClient, get_all_visible_projects
from to_back.ecotaxa_cli_py import SamplesApi, SampleModel, ApiException, TaxonomyTreeApi, \
    TaxonModel


@app.route('/explore/')
def indexExplore() -> str:
    data: Dict[str, Any] = {}
    for k, v in FilterList.items():
        data[k] = gvg(k, v)
    data['inexplore'] = True
    data["projid"] = gvg("projid", '0')
    data["taxochild"] = gvg("taxochild", '1')

    data["projects_for_select"] = ""
    if data["projid"]:
        project_ids = set(data['projid'].split(","))
        for a_project in get_all_visible_projects():
            # TODO: Could invert the loop and query for each project id
            if str(a_project.projid) in project_ids:
                data["projects_for_select"] += "\n<option value='%s' selected>%s</option> " % (
                    a_project.projid, a_project.title)

    data["sample_for_select"] = ""
    if data["samples"]:
        PrjIds = data["projid"]
        # Sample filter was posted, select the corresponding items.
        with ApiClient(SamplesApi, request) as api:
            try:
                samples: List[SampleModel] = api.samples_search(project_ids=PrjIds,
                                                                id_pattern="")
                sample_ids = set(data['samples'].split(","))
                for a_sample in samples:
                    # TODO: Could be filtered server-side
                    if str(a_sample.sampleid) in sample_ids:
                        data["sample_for_select"] += "\n<option value='%s' selected>%s</option> " % (
                            a_sample.sampleid, a_sample.orig_id)
            except ApiException as ae:
                pass

    data["taxo_for_select"] = ""
    if gvg("taxo[]"):
        with ApiClient(TaxonomyTreeApi, request) as tapi:
            categs: List[TaxonModel] = tapi.query_taxa_set(gvg("taxo[]"))
        for a_taxon in categs:
            data["taxo_for_select"] += "\n<option value='%s' selected>%s</option> " % (a_taxon.id, a_taxon.display_name)

    data["month_for_select"] = ""
    for (a_filter, default) in enumerate(MONTH_LABELS, start=1):
        data["month_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format(
            'selected' if str(a_filter) in data.get('month', '').split(',') else '', a_filter, default)

    data["daytime_for_select"] = ""
    for (a_filter2, default) in DayTimeList.items():
        data["daytime_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format(
            'selected' if str(a_filter2) in data.get('daytime', '').split(',') else '', a_filter2, default)

    right = 'dodefault'
    classiftab = ""
    appli.AddJobsSummaryForTemplate()
    filtertab = getcommonfilters(data)
    return render_template('search/explore.html', top="", lefta=classiftab, leftb=filtertab
                           , right=right, data=data)


######################################################################################################################
@app.route('/explore/LoadRightPane', methods=['GET', 'POST'])
def ExploreLoadRightPane():
    projids = gvp("projid")

    ExtraEndScript = ""
    PageTopProjectLink = ""
    AllProjectsMap = ""
    if not projids:
        all_projects = get_all_visible_projects()
        random_project_id = random.randint(0, len(all_projects) - 1)
        random_project = all_projects[random_project_id]
        ExtraEndScript = """<script>$('#headersubtitle').html('Randomly selected project : <a href="?projid={0}">{1}</a>');</script>""". \
            format(random_project.projid, XSSEscape(random_project.title))
        projid = random_project.projid
        AllProjectsMap = render_template("search/explore_inserted_popup.html", Projid=projids)
    else:
        all_projids = [int(x) for x in gvp("projid").split(',')]
        if len(all_projids) == 1:
            PageTopProjectLink = "<p class='bg-info' style='font-size: larger;font-weight: bold;'>You can explore" \
                                 " this project in more details on its <a href='/prj/{0}'>dedicated page</a></p>". \
                format(all_projids[0])
            projid = all_projids[0]
        else:
            return "Only one project is allowed."

    ret = LoadRightPaneForProj(PrjId=projid, read_only=True, force_first_page=True)
    return PageTopProjectLink + AllProjectsMap + ret + ExtraEndScript
