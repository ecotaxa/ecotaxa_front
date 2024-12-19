from flask import request, render_template, flash, redirect, url_for
from appli.utils import ApiClient, DecodeEqualList
from to_back.ecotaxa_cli_py.api import ProjectsApi
from to_back.ecotaxa_cli_py import ApiException
from appli.constants import MappableObjectColumns, MappableParentColumns
from appli.gui.staticlistes import py_messages
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    ProjectTaxoStatsModel,
    MinimalCollectionBO,
)


def prj_stats(prjid: int, partial: bool, params: dict) -> str:

    from collections.abc import Iterable

    limit = 5000
    if "limit" in params:
        limit = params["limit"]
    # Stats for about infos in table partial = True or full about page partial = False
    from appli.gui.project.projectsettings import get_target_prj

    prj = get_target_prj(prjid)
    if prj is None:
        if partial:
            return render_template(
                "v2/partials/_error.html",
                error=403,
                message=py_messages["accessonly"]["manage"],
                partial=True,
                is_safe=True,
            )
        else:
            flash(py_messages["selectotherproject"], "info")
            return redirect(url_for("gui_prj"))
    used_taxa = list([])
    taxastats = list(dict({}))
    annotators = None
    samples = None
    initclassiflist = None
    collections = list([])
    if partial == True:
        req_taxa = ""
    else:
        req_taxa = "all"
    from appli.gui.project.projects_list_interface_json import render_stat_proj

    statproj = render_stat_proj(prj, partial)
    with ApiClient(ProjectsApi, request) as api:
        taxo_stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(
            ids=str(prjid), taxa_ids=req_taxa
        )
        # easier format to display stats by taxon id
        if len(taxo_stats):
            if not partial:
                taxastats.extend(map(lambda x: x.to_dict(), taxo_stats))
                used_taxa.extend([str(t.used_taxa[0]) for t in taxo_stats])
            else:
                taxastats = taxo_stats[0]
                used_taxa.extend([str(t) for t in taxastats.used_taxa])
                taxastats = [taxastats.to_dict()]
        collections: List[MinimalCollectionBO] = api.project_collections(prjid)

        from appli.gui.taxonomy.tools import taxo_with_names, taxo_with_lineage
        from markupsafe import escape

        usedtaxa = taxo_with_lineage(used_taxa)
    if not partial:
        annotators = list()
        if isinstance(initclassiflist, Iterable):
            initclassiflist = taxo_with_names(prj.init_classif_list)
        # format list for template
        for i, taxastat in enumerate(taxastats):
            n = list(filter(lambda x: (x[0] == taxastat["used_taxa"][0]), usedtaxa))
            if len(n) and len(n[0]):
                name = n[0][1]
                taxastats[i]["name"] = name
                taxastats[i]["lineage"] = n[0][2]

        from to_back.ecotaxa_cli_py.models import ProjectUserStatsModel

        with ApiClient(ProjectsApi, request) as api:
            try:
                annotators_stats: List[
                    ProjectUserStatsModel
                ] = api.project_set_get_user_stats(ids=str(prjid))
            except ApiException as ae:
                annotators_stats = None
                flash("error in getting user stats " + str(ae.status), "error")
        if isinstance(annotators_stats, Iterable) and len(annotators_stats) > 0:
            for r in annotators_stats[0].annotators:
                f = list(
                    filter(
                        lambda a: (a.id == r.id),
                        annotators_stats[0].activities,
                    )
                )
                if len(f):
                    nb_actions = f[0].nb_actions
                    last_annot = f[0].last_annot
                else:
                    nb_actions = 0
                    last_annot = None
                annotators.append(
                    dict(
                        {
                            "id": r.id,
                            "name": r.name,
                            "nb_actions": nb_actions,
                            "last_annot": last_annot,
                        }
                    )
                )
        # to have a full list of users
        for right, members in statproj["privileges"].items():
            for member in members:
                f = list(filter(lambda a: (a["id"] == member["id"]), annotators))
                if len(f) == 0:
                    annotators.append(
                        dict(
                            {
                                "id": member["id"],
                                "name": member["name"],
                                "nb_actions": 0,
                                "last_annot": None,
                            }
                        )
                    )
    # translations
    from appli.gui.staticlistes import (
        py_project_status,
        py_project_rights,
        py_user_roles,
    )

    return render_template(
        "v2/project/_stats.html",
        partial=partial,
        target_proj=statproj,
        taxastats=taxastats,
        initclassiflist=initclassiflist,
        annotators=annotators,
        used_taxa=usedtaxa,
        collections=collections,
        translations=dict(
            {
                "roles": py_user_roles,
                "status": py_project_status,
                "rights": py_project_rights,
            }
        ),
    )


def prj_samples_stats(project_ids: str, partial: bool, format: str = "json") -> str:
    from to_back.ecotaxa_cli_py.api import SamplesApi

    with ApiClient(SamplesApi, request) as api:
        samples: List[SampleModel] = api.samples_search(
            project_ids=project_ids, id_pattern=""
        )
    sample_ids = ",".join(list([str(sample.sampleid) for sample in samples]))
    with ApiClient(SamplesApi, request) as api:
        samplestats: List[SampleModel] = api.sample_set_get_stats(sample_ids=sample_ids)
    from appli.gui.project.projects_list_interface_json import (
        project_table_columns,
        render_samples_stats,
    )

    columns = {
        **project_table_columns("", "samples"),
        **project_table_columns("", "validations"),
    }
    tabledef = dict(
        {
            "columns": columns,
            "data": render_samples_stats(samples, samplestats, partial, format),
            "type": "json",
        }
    )
    if format == "json":
        return tabledef
    else:
        return render_template(
            "./v2/project/_samplestats.html",
            partial=partial,
            tabledef=tabledef,
        )
