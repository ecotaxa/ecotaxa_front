from flask import request, render_template
from appli.utils import ApiClient, DecodeEqualList
from to_back.ecotaxa_cli_py.models import ProjectSetColumnStatsModel
from to_back.ecotaxa_cli_py.api import ProjectsApi


def prj_stats(prjid: int, partial: bool, params: dict) -> str:
    if "classifsettings" in params:
        classif_settings = DecodeEqualList(params["classifsettings"])
    else:
        classif_settings = ""  # default
        # Hidden FORM summarizing the previous steps choices
    limit = params["limit"]
    names_for_stats = ""
    # Stats for about infos in table partial = True or full about page partial = False
    from appli.gui.project.projectsettings import get_target_prj

    print(prjid)
    prj = get_target_prj(prjid)
    return render_template("v2/project/_stats.html", partial=True, prj=prj)

    with ApiClient(ProjectsApi, request) as api:
        stats: ProjectSetColumnStatsModel = api.project_set_get_column_stats(
            ids=prjid,
            names="fre.area,obj.depth_min,fre.nb2",
            limit=limit,
            categories="403,2",
        )
    total = stats.total
