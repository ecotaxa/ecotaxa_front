# -*- coding: utf-8 -*-
import time
from typing import List, Any, Final, ClassVar

from flask import render_template, g, redirect, flash, request
from appli import PrintInCharte, gvg, gvp
from appli.gui.jobs.Job import Job
from appli.utils import ApiClient, DecodeEqualList, EncodeEqualList
from to_back.ecotaxa_cli_py import (
    ObjectsApi,
    ObjectSetQueryRsp,
    ProjectSetColumnStatsModel,
    ProjectTaxoStatsModel,
    PredictionReq,
    PredictionRsp,
)
from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import TaxonModel, ProjectModel, JobModel


class PredictionJob(Job):
    """
    Prediction, just GUI here, bulk of work subcontracted to back-end.
    """

    UI_NAME: Final = "Prediction"
    STEP0_TEMPLATE: ClassVar = "v2/jobs/prediction_create_lstproj.html"
    STEP1_TEMPLATE: ClassVar = ("v2/jobs/prediction_create_lsttaxo.html",)
    STEP2_TEMPLATE: ClassVar = "v2/jobs/prediction_create_settings.html"
    FINAL_TEMPLATE: ClassVar = "v2/jobs/_prediction_final.html"
    OBJECT_VARS: Final = {"depth_max", "depth_min"}

    @classmethod
    def initial_dialog(cls):
        """In UI/flask, initial load, GET"""
        return cls.base_projects_select_page()

    @classmethod
    def create_or_update(cls):
        """In UI/flask, submit/resubmit of pages"""
        if gvp("src", gvg("src")) == "":
            # Source not chosen yet
            return cls.base_projects_select_page()
        elif gvp("learninglimit", gvg("learninglimit")) == "":
            # Source chosen but not categories
            return cls.categories_config_page()
        elif gvp("starttask") != "Y":
            # Source chosen and categories but not features
            return cls.features_config_page()
        else:
            errs = cls.validate_task()
            if len(errs) > 0:
                for e in errs:
                    flash(e, "error")
                return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
            # All OK
            return cls.start_task()

    @classmethod
    def get_target_filters(cls) -> str:

        return target_proj, filters_html

    @classmethod
    def base_projects_select_page(cls):
        # First configuration page, choose base projects
        # This page is called from initial GET or POSTs to iself when project filters are used
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid, collid)
        filters_html = cls.GetFilterText(cls._extract_filters_from_url())
        if target_proj is None:
            return PrintInCharte(filters_html)
        # The page reloads itself (POST) when using the "Search" button
        try:
            # In case the filter box was used, validate it.
            if gvp("filt_featurenbr"):
                filt_featurenbr = int(gvp("filt_featurenbr"))
            else:
                filt_featurenbr = 10
        except ValueError:
            flash("Common features must be an integer", category="error")
            return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
        title_filter = gvp("filt_title", "")
        if request.method == "GET":
            instrument_filter = target_proj.instrument
        else:
            instrument_filter = gvp("filt_instrum", "")

        src_projs_str = gvp("srcs", "").split(",")
        src_projs = [int(prj_str) for prj_str in src_projs_str if prj_str.isdigit()]

        # Get previous choices AKA settings which are stored at project level
        settings = DecodeEqualList(target_proj.classifsettings)
        target_features = set(target_proj.obj_free_cols.keys())

        previous_ls = settings.get(
            "baseproject", ""
        )  # a coma-separated list of project IDs

        return render_template(
            cls.STEP0_TEMPLATE,
            url=request.query_string.decode("utf-8"),
            deep_features=target_proj.cnn_network_id,
            filters_info=filters_html,
            filt_title=title_filter,
            filt_features_nbr=filt_featurenbr,
            filt_instrum=instrument_filter,
            target_proj=target_proj,
        )

    #################################################################################################

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        projid = job.params["req"]["project_id"]
        if job.state == "F":
            projid = job.params["req"]["project_id"]
            time.sleep(1)
            # TODO: Remove the commented, but for now we have trace information inside
            # DoTaskClean(self.task.id)
        return render_template(cls.FINAL_TEMPLATE, projid=projid, result=job.result)

    #################################################################################################

    @classmethod
    def validate_task(cls):
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid, collid)
        filters_html = cls.GetFilterText(cls._extract_filters_from_url())

        (
            src_prj_ids,
            categories,
            learning_limit,
            pre_mapping,
            obj_vars,
            use_scn,
        ) = cls.get_posted_task_params()

        # Check a bit
        errors = []
        if len(obj_vars) == 0 and use_scn is False:
            errors.append("You must select some variable")
        if len(categories) == 0:
            errors.append("You must select some category")

        # Use the API entry point for querying the impacted objects. At this point we just need
        # to know if it's != 0
        with ApiClient(ObjectsApi, request) as api:
            filters = cls._extract_filters_from_url()
            filters["statusfilter"] = "UP"
            res: ObjectSetQueryRsp = api.get_object_set(
                project_id=target_proj.projid, project_filters=filters, window_size=100
            )

        if len(res.object_ids) == 0:
            msg = cls.cook_no_object_message(filters)
            errors.append(msg)

        if len(errors) == 0:
            # Save parameters
            sav = {
                "critvar": gvp("CritVar"),
                "baseproject": gvp("src"),
                "seltaxo": gvp("Taxo"),
                "posttaxomapping": gvp("PostTaxoMapping"),
            }
            # Update project classification settings
            with ApiClient(ProjectsApi, request) as api:
                api.set_project_predict_settings(
                    project_id=target_proj.projid, settings=EncodeEqualList(sav)
                )
        return errors

    @classmethod
    def start_task(cls):
        # Launch Job on back-end
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid, collid)
        filters_html = cls.GetFilterText(cls._extract_filters_from_url())
        if target_proj is None:
            return PrintInCharte(filters_html)
        filters = cls._extract_filters_from_url()

        (
            src_prj_ids,
            categories,
            learning_limit,
            pre_mapping,
            obj_vars,
            use_scn,
        ) = cls.get_posted_task_params()

        # Prepare back-end call
        req = PredictionReq(
            project_id=target_proj.projid,
            source_project_ids=src_prj_ids,
            learning_limit=learning_limit,
            categories=categories,
            features=obj_vars,
            use_scn=use_scn,
            pre_mapping=pre_mapping,
        )
        # Call and redirect
        with ApiClient(ObjectsApi, request) as api:
            rsp: PredictionRsp = api.predict_object_set(
                {"filters": filters, "request": req}
            )
        return redirect("/Job/Monitor/%d" % rsp.job_id)

    @classmethod
    def get_posted_task_params(cls):
        # Extract params into properly formatted vars
        src_prj_ids = [int(prj_id) for prj_id in gvp("src").split(",")]
        use_scn = gvp("usescn") == "Y"
        learning_limit = int(gvp("learninglimit"))
        # Chosen vars need to be prefixed
        chosen_vars = gvp("CritVar").split(",")
        obj_vars = [
            "obj." + a_var if a_var in cls.OBJECT_VARS else "fre." + a_var
            for a_var in chosen_vars
        ]
        if obj_vars == ["fre."]:
            # Tricky case with 0 var
            obj_vars.clear()
        chosen_taxo = gvp("Taxo").split(",")
        categories = [int(classif_id) for classif_id in chosen_taxo]
        pre_taxo_mapping = gvp("PostTaxoMapping")
        if len(pre_taxo_mapping) > 0:
            pre_map_txt = [mpg.split(":") for mpg in pre_taxo_mapping.split(",")]
        else:
            pre_map_txt = []
        pre_mapping = {int(from_): int(to) for from_, to in pre_map_txt}
        return src_prj_ids, categories, learning_limit, pre_mapping, obj_vars, use_scn

    @classmethod
    def api_read_projects(
        cls, auth: Any, src_prj_ids: List[int], revobjmapbaseByProj, common_features
    ):
        """Read project's free columns and add them to the common set"""
        ret = []
        for src_prj_id in src_prj_ids:
            with ApiClient(ProjectsApi, auth) as api:
                proj: ProjectModel = api.project_query(src_prj_id, for_managing=False)
            revobjmapbaseByProj[src_prj_id] = cls.GetAugmentedReverseObjectMap(proj)
            common_features.intersection_update(
                set(revobjmapbaseByProj[src_prj_id].keys())
            )
            ret.append(proj)
        return ret

    @classmethod
    def categories_config_page(cls):
        # Configuration of categories for the prediction.
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid, collid)
        filters_html = cls.GetFilterText(cls._extract_filters_from_url())
        if target_proj is None:
            return PrintInCharte(filters_html)

        # Get via API all implied projects
        posted_srcs = gvp("src", gvg("src"))
        src_prj_ids = [int(x) for x in posted_srcs.split(",") if x.isdigit()]
        src_projs = []
        for a_prij_id in src_prj_ids:
            with ApiClient(ProjectsApi, request) as api:
                src_proj: ProjectModel = api.project_query(
                    a_prij_id, for_managing=False
                )
            src_projs.append("#%s - %s" % (src_proj.projid, src_proj.title))
        src_prj_ids_sql = ",".join(
            [str(x) for x in src_prj_ids]
        )  # By chance it's an OK format for the API as well

        # Get the number of validated objects of each category in all source projects
        with ApiClient(ProjectsApi, request) as api:
            stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(
                ids=src_prj_ids_sql, taxa_ids="all"
            )
        validated_categ_count = dict()
        for a_stat in stats:
            categ = a_stat.used_taxa[0]  # In this mode, a single taxa in the list
            if a_stat.nb_validated == 0:
                continue
            if categ in validated_categ_count:
                validated_categ_count[categ] += a_stat.nb_validated
            else:
                validated_categ_count[categ] = a_stat.nb_validated

        # Get info on them
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join([str(x) for x in validated_categ_count.keys()])
            taxa: List[TaxonModel] = api.query_taxa_set(ids=taxa_ids)
        taxa_per_id = {taxon.id: taxon for taxon in taxa}

        # Get the number of validated objects of each category in each source project
        total_validated = sum(validated_categ_count.values())
        taxo_table = [
            [taxon_id, taxa_per_id[taxon_id].display_name, nbr_v]
            for taxon_id, nbr_v in validated_categ_count.items()
        ]
        taxo_table.sort(key=lambda r: r[2], reverse=True)
        # There are < in display names which make them unbreakable during resize
        for a_row in taxo_table:
            if "<" in a_row[1]:
                a_row[1] = a_row[1].replace("<", " < ")

        # Get previous settings which influence how to display the categories (pre-checked or not)
        d = DecodeEqualList(target_proj.classifsettings)
        categories_in_settings = d.get("seltaxo")
        if categories_in_settings:
            settings_taxo_set = {int(x) for x in categories_in_settings.split(",")}
        else:
            settings_taxo_set = {}
        g.TaxoList = [
            [
                r[0],
                r[1],
                r[2],
                round(100 * r[2] / total_validated, 1),
                (
                    "checked"
                    if len(settings_taxo_set) == 0 or r[0] in settings_taxo_set
                    else ""
                ),
            ]
            for r in taxo_table
        ]  # Add object % and 'checked' or not

        src_prjs_str = ",&nbsp;".join(src_projs)
        return render_template(
            cls.STEP1_TEMPLATE,
            url=request.query_string.decode("utf-8"),
            filters_info=filters_html,
            src_prj_ids=src_prj_ids_sql,
            src_prjs=src_prjs_str,
            target_proj=target_proj,
        )

    @classmethod
    def GetFilterText(cls, filters_text) -> str:
        if filters_text:
            return (
                "<p><span style='color:red;font-weight:bold;font-size:large;'"
                ">USING Active Project Filters</span><BR>Filters : "
                + filters_text
                + "</p>"
            )
        else:
            return ""

    @classmethod
    def cook_no_object_message(cls, filters):
        msg = "No object to classify, perhaps all objects were already classified."
        if len(filters) > 0:
            msg += " Note that you have active filters, which reduces potential target objects."
        return msg

    @classmethod
    def GetAugmentedReverseObjectMap(cls, prj: ProjectModel):
        """Return numerical free columns for a project + 2 hard-coded ones"""
        ret = {k: v for k, v in prj.obj_free_cols.items() if v[0] == "n"}
        for an_obj_var in cls.OBJECT_VARS:
            ret[an_obj_var] = an_obj_var
        return ret

    @classmethod
    def features_config_page(cls):
        # Third page of the wizard, proceed
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid, collid)
        filters_html = cls.GetFilterText(cls._extract_filters_from_url())
        if target_proj is None:
            return PrintInCharte(filters_html)

        src_prj_lst = gvp("src", gvg("src"))

        prev_settings = DecodeEqualList(target_proj.classifsettings)
        # Hidden FORM summarizing the previous steps choices
        hidden = {
            "src": src_prj_lst,
            "learninglimit": int(gvp("learninglimit", "5000")),
            # Reference for the 5000: Ricour Florian & al 2022
            "features": prev_settings.get("critvar", ""),  # Chosen variables last time
            "taxo": ",".join(
                (x[4:] for x in request.form if x[0:4] == "taxo" and x[0:6] != "taxolb")
            ),
            "pre_mapping": ",".join(
                (x[6:] + ":" + gvp(x) for x in request.form if x[0:6] == "taxolb")
            ),
        }

        # Determination des criteres/variables utilisées par l'algo de learning
        revobjmap = cls.GetAugmentedReverseObjectMap(
            target_proj
        )  # Dict NomVariable=>N° colonne ex Area:n42
        common_features = set(revobjmap.keys())

        # Loop over source projects, get their keys and determine a set of common keys (for dest + all srcs)
        # Note: given the hardcoded values in @see GetAugmentedReverseObjectMap, the common keys comprise
        # at least depth_min and depth_max
        revobjmapbaseByProj = {}
        src_prj_ids = [
            int(prj_id) for prj_id in src_prj_lst.split(",") if prj_id.isdigit()
        ]

        src_projs = cls.api_read_projects(
            request, src_prj_ids, revobjmapbaseByProj, common_features
        )

        # critlist[feature] 0:feature , 1:% validated , 2:distinct
        critlist = {k: [k, -1, -1] for k in common_features}

        # Prepare names for the API call
        names_for_stats = ",".join(
            ["fre.%s" % col for col in common_features if col not in cls.OBJECT_VARS]
        )
        names_for_stats += ("," if names_for_stats else "") + ",".join(
            ["obj.%s" % col for col in cls.OBJECT_VARS]
        )
        # Stats on training set, i.e. projects+categories+limit
        with ApiClient(ProjectsApi, request) as api:
            stats: ProjectSetColumnStatsModel = api.project_set_get_column_stats(
                ids=src_prj_lst,
                names=names_for_stats,
                limit=hidden["learninglimit"],
                categories=hidden["taxo"],
            )
        g.LsSize = stats.total
        for col, count, variance in zip(stats.columns, stats.counts, stats.variances):
            prfx, name = col.split(".", 1)
            critlist[name][1] = round(
                100 * (1 - count / stats.total)
            )  # % Missing in source projects
            critlist[name][2] = (
                " " if variance is None else ("Y" if variance != 0 else "N")
            )

        cnn_networks = set(
            [target_proj.cnn_network_id] + [a_prj.cnn_network_id for a_prj in src_projs]
        )
        g.SCN = target_proj.cnn_network_id is not None and len(cnn_networks) == 1

        g.critlist = list(critlist.values())
        g.critlist.sort(key=lambda t: t[0])
        return render_template(
            cls.STEP2_TEMPLATE,
            header="",
            data=hidden,
            filters_info=filters_html,
            target_proj=target_proj,
        )
