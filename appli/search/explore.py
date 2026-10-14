import random
from typing import List, Dict, Any, Optional

from flask import render_template, request

import appli
from appli import app, gvg, gvgm, gvp, XSSEscape
from appli.constants import DayTimeList
from appli.project.main import FilterList, MONTH_LABELS, LoadRightPaneForProj
from appli.search.leftfilters import getcommonfilters
######################################################################################################################
from appli.utils import ApiClient, can_read_visible_project
from to_back.ecotaxa_cli_py import SamplesApi, SampleModel, ApiException, TaxonomyTreeApi, \
    TaxonModel, ProjectsApi, ProjectModel


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
        # query only the selected projects, not all visible ones
        project_ids = [p for p in data['projid'].split(",") if p.strip().isdigit()]
        with ApiClient(ProjectsApi, request) as papi:
            for a_projid in project_ids:
                try:
                    a_project: ProjectModel = papi.project_query(int(a_projid), for_managing=False)
                except ApiException:
                    continue
                data["projects_for_select"] += "\n<option value='%s' selected>%s</option> " % (
                    a_project.projid, XSSEscape(a_project.title))

    data["sample_for_select"] = ""
    if data["samples"]:
        PrjIds = data["projid"].replace(",", "+")
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
                            a_sample.sampleid, XSSEscape(a_sample.orig_id))
            except ApiException as ae:
                pass

    data["taxo_for_select"] = ""
    # taxo is a comma-separated list of ids, taxo[] kept for links shared before
    taxo_ids = [t for t in gvg("taxo").split(",") + gvgm("taxo[]") if t.strip().isdigit()]
    if taxo_ids:
        with ApiClient(TaxonomyTreeApi, request) as tapi:
            try:
                categs: List[TaxonModel] = tapi.query_taxa_set("+".join(taxo_ids))
            except ApiException as ae:
                categs = []
        for a_taxon in categs:
            data["taxo_for_select"] += "\n<option value='%s' selected>%s</option> " % (
                a_taxon.id, XSSEscape(a_taxon.display_name))

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
RANDOM_PAGE_SIZE = 50
RANDOM_MAX_PAGES = 20


def _random_project() -> Optional[ProjectModel]:
    """
    Pick a random visible project having validated objects (the only ones displayed here),
    from one page of a search at a random offset, then from the first page if that one is empty.
    Projects without rights first (not_granted, public ones when anonymous), then the granted ones,
    as an app admin has no "not granted" project, like get_all_visible_projects().
    """
    fallback: List[ProjectModel] = []
    random_start = random.randint(0, RANDOM_MAX_PAGES - 1) * RANDOM_PAGE_SIZE
    with ApiClient(ProjectsApi, request) as api:
        for not_granted in (True, False):
            # random page first, then the first page (dict keeps order and drops a duplicate 0)
            for start in dict.fromkeys((random_start, 0)):
                try:
                    prjs: List[ProjectModel] = api.search_projects(not_granted=not_granted,
                                                                   fields="projid,title,access,objcount,pctvalidated",
                                                                   window_start=start,
                                                                   window_size=RANDOM_PAGE_SIZE)
                except ApiException:
                    continue
                # readable only: an anonymous user gets "Access Denied" on a public, not open, project
                visible = [p for p in prjs if can_read_visible_project(p)]
                with_validated = [p for p in visible
                                  if getattr(p, "objcount", None) and getattr(p, "pctvalidated", None)]
                if with_validated:
                    return random.choice(with_validated)
                fallback.extend(visible)
    # no project with validated objects found: any visible one
    return random.choice(fallback) if fallback else None


@app.route('/explore/LoadRightPane', methods=['GET', 'POST'])
def ExploreLoadRightPane():
    projids = gvp("projid")

    ExtraEndScript = ""
    PageTopProjectLink = ""
    AllProjectsMap = ""
    if not projids:
        random_project = _random_project()
        if random_project is None:
            return "No project to explore."
        ExtraEndScript = """<script>$('#headersubtitle').html('Randomly selected project : <a href="?projid={0}">{1}</a>');</script>""". \
            format(random_project.projid, XSSEscape(random_project.title))
        projid = random_project.projid
        AllProjectsMap = render_template("search/explore_inserted_popup.html", Projid=projids)
    else:
        try:
            all_projids = [int(x) for x in gvp("projid").split(',')]
        except ValueError:
            return "Invalid project"
        if len(all_projids) == 1:
            PageTopProjectLink = "<p class='bg-info' style='font-size: larger;font-weight: bold;'>You can explore" \
                                 " this project in more details on its <a href='/prj/{0}'>dedicated page</a></p>". \
                format(all_projids[0])
            projid = all_projids[0]
        else:
            return "Only one project is allowed."

    ret = LoadRightPaneForProj(PrjId=projid, read_only=True, force_first_page=True)
    return PageTopProjectLink + AllProjectsMap + ret + ExtraEndScript
