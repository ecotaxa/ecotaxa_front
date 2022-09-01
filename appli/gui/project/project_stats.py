from flask import request, render_template, flash
from appli.utils import ApiClient, DecodeEqualList
from appli import gvg
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
    # Stats for about
    return render_template("v2/project/_stats.html", partial=partial)
    with ApiClient(ProjectsApi, request) as api:
        stats: ProjectSetColumnStatsModel = api.project_set_get_column_stats(
            ids=prjid,
            names="fre.area,obj.depth_min,fre.nb2",
            limit=limit,
            categories="403,2",
        )
    total = stats.total
    for col, count, variance in zip(stats.columns, stats.counts, stats.variances):
        prfx, name = col.split(".", 1)
        critlist[name][1] = round(
            100 * (1 - count / stats.total)
        )  # % Missing in source projects
        critlist[name][2] = " " if variance is None else ("Y" if variance != 0 else "N")
