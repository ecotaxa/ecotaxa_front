from flask import request, render_template
from appli.utils import ApiClient, DecodeEqualList
from to_back.ecotaxa_cli_py.models import ProjectSetColumnStatsModel
from to_back.ecotaxa_cli_py.api import ProjectsApi
from appli.constants import MappableObjectColumns, MappableParentColumns


def prj_stats(prjid: int, partial: bool, params: dict) -> str:

    limit = 5000
    if "limit" in params:
        limit = params["limit"]

    # Stats for about infos in table partial = True or full about page partial = False
    from appli.gui.project.projectsettings import get_target_prj

    prj = get_target_prj(prjid)
    used_taxa = list([])
    prjstat = dict({})
    with ApiClient(ProjectsApi, request) as api:
        taxo_stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(
            ids=str(prjid)
        )

        if len(taxo_stats):
            prjstat = taxo_stats[0]
            used_taxa.extend([str(t) for t in prjstat.used_taxa])
    from appli.gui.project.projectsettings import taxo_with_names

    usedtaxa = taxo_with_names(used_taxa)

    from appli.gui.project.projects_list_interface import render_stat_proj

    statproj = render_stat_proj(prj)
    with ApiClient(ProjectsApi, request) as api:
        stats: list = api.project_stats(prjid)

    return render_template(
        "v2/project/_stats.html",
        partial=partial,
        target_proj=statproj,
        prjstat=prjstat,
        stats=stats,
        used_taxa=usedtaxa,
    )
