# -*- coding: utf-8 -*-
import logging
import time
from typing import List, Any

from flask import render_template, g, flash, request

from appli import db, PrintInCharte, gvp, gvg, EncodeEqualList, DecodeEqualList, app, XSSEscape
from appli.database import CSVIntStringToInClause
from appli.project import sharedfilter
from appli.tasks.taskmanager import AsyncTask
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ObjectsApi, ObjectSetQueryRsp, ProjectsApi, ProjectModel, \
    ApiException, ProjectTaxoStatsModel, TaxonomyTreeApi, TaxonModel, ProjectSetColumnStatsModel, PredictionReq, \
    PredictionRsp, JobsApi, JobModel


# noinspection PyPep8Naming,PyUnboundLocalVariable
class TaskClassifAuto2(AsyncTask):
    # noinspection PyPep8Naming
    class Params(AsyncTask.Params):
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr is None:  # Valeurs par defaut ou vide pour init
                self.Methode = 'randomforest'
                self.ProjectId = None
                self.BaseProject = ""
                self.CritVar = None
                self.Taxo = ""
                self.learninglimit = ""
                self.CustSettings = {}
                self.PostTaxoMapping = ""
                self.filtres = {}
                self.usescn = ""

    def __init__(self, task=None):
        super().__init__(task)
        self.pgcur = db.engine.raw_connection().cursor()
        if task is None:
            self.param = self.Params()
        else:
            self.param = self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon for Automatic Classification V2 Task %d" % self.task.id)

    OBJECT_VARS = {"depth_max", "depth_min"}

    def SPStep1(self):
        logging.info("Input Param = %s" % (self.param.__dict__,))

        # Extract params into properly formatted vars
        prj_id = self.param.ProjectId
        src_prj_ids = [int(prj_id) for prj_id in self.param.BaseProject.split(",")]
        use_scn = self.param.usescn == 'Y'
        #
        learning_limit = None
        if self.param.learninglimit:
            learning_limit = int(self.param.learninglimit)
        # Chosen vars need to be prefixed
        chosen_vars = self.param.CritVar.split(",")
        obj_vars = ["obj." + a_var if a_var in self.OBJECT_VARS else "fre." + a_var
                    for a_var in chosen_vars]
        categories = [int(classif_id) for classif_id in self.param.Taxo.split(",")]
        filters = self.param.filtres

        # TRANSITORY: Still use Linux executable for generating deep features
        if self.param.usescn == 'Y':
            # Fetch the target project for the SCN settings
            with ApiClient(ProjectsApi, self.cookie) as api:
                target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            # Late import due to circular dependency
            from .prediction_deep_features import ComputeSCNFeatures
            self.UpdateProgress(5, "Generating missing deep features")
            if not ComputeSCNFeatures(self, target_prj):
                self.task.taskstate = "Error"
                self.UpdateProgress(5, "Deep features generation failed. See logs.")
                return

        # logging.info("Start Step 1")
        # TInit = time.time()

        # Prepare back-end call
        req = PredictionReq(project_id=prj_id,
                            source_project_ids=src_prj_ids,
                            learning_limit=learning_limit,
                            categories=categories,
                            features=obj_vars,
                            use_scn=use_scn)
        with ApiClient(ObjectsApi, self.cookie) as api:
            rsp: PredictionRsp = api.predict_object_set_object_set_predict_post({'filters': filters,
                                                                                 'request': req})

        # Wait for the back-end job to complete, copying its messages
        pct = self.task.progresspct
        msg = self.task.progressmsg
        job_id = rsp.job_id
        while True:
            with ApiClient(JobsApi, self.cookie) as api:
                job: JobModel = api.get_job_jobs_job_id_get(job_id=job_id)
            if job.progress_pct != pct or job.progress_msg != msg:
                pct = job.progress_pct
                msg = job.progress_msg
                self.UpdateProgress(pct, msg)
            if job.state in ('E', 'F'):
                break
            time.sleep(5)

        # Copy Job status into task
        self.task.taskstate = "Done"
        if job.state == 'E':
            self.task.taskstate = 'Error'
            self.UpdateProgress(100, "See Prediction Job which failed")
        else:
            self.UpdateProgress(100, job.progress_msg)

        # TODO: This is indeed a Post-prediction mapping, but the UI in a pre-training One
        # for i, v in enumerate(SqlParam):
        #     if v['cat'] in PostTaxoMapping:
        #         SqlParam[i]['cat'] = PostTaxoMapping[v['cat']]

    def QuestionProcessScreenSelectSource(self, target_prj: ProjectModel):
        # First configuration page, choose base projects
        # The page reloads itself when using the "Search" button
        try:
            # In case the filter box was used, validate it.
            if gvp("filt_featurenbr"):
                filt_featurenbr = int(gvp("filt_featurenbr"))
            else:
                filt_featurenbr = 10
        except ValueError:
            flash("Common features must be an integer", category="error")
            return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
        title_filter = gvp('filt_title', '')
        instrument_filter = gvp('filt_instrum', '')
        filters_info = self.GetFilterText()
        src_projs_str = gvp('srcs', '').split(",")
        src_projs = [int(prj_str) for prj_str in src_projs_str if prj_str.isdigit()]

        # Get previous choices AKA settings which are stored at project level
        settings = DecodeEqualList(target_prj.classifsettings)
        target_features = set(target_prj.obj_free_cols.keys())

        previous_ls = settings.get("baseproject", "")  # a coma-separated list of project IDs
        if previous_ls != "":
            # We can have one or several base projects, which are reminded here
            settings_prj_ids = [int(prj_id) for prj_id in previous_ls.split(",") if prj_id.isdigit()]
        else:
            settings_prj_ids = []

        # Collect information for out-of-table projects as well
        no_tbl_projs = {}  # key: project ID, value: ProjectModel

        # Collect all projects matching the conditions
        usable_proj_list = self.api_read_accessible_projects(instrument_filter, title_filter)

        # Enrich the list with useful calculations
        filtered_projs = []
        matching_per_proj = {}
        validated_per_proj = {}
        for a_maybe_src_prj in usable_proj_list:
            matching_features = len(set(a_maybe_src_prj.obj_free_cols.keys()) & target_features)
            if matching_features < filt_featurenbr:
                no_tbl_projs[a_maybe_src_prj.projid] = a_maybe_src_prj
                continue
            matching_per_proj[a_maybe_src_prj.projid] = matching_features
            validated = (a_maybe_src_prj.objcount if a_maybe_src_prj.objcount else 0) * \
                        (a_maybe_src_prj.pctvalidated if a_maybe_src_prj.pctvalidated else 0) / 100
            validated_per_proj[a_maybe_src_prj.projid] = validated
            filtered_projs.append(a_maybe_src_prj)

        # Sort to have the most interesting ones in first
        filtered_projs.sort(key=lambda r: (-matching_per_proj[r.projid], -validated_per_proj[r.projid]))
        table_lines = []
        for a_maybe_src_prj in filtered_projs:
            matching = matching_per_proj[a_maybe_src_prj.projid]
            validated = validated_per_proj[a_maybe_src_prj.projid]
            cnn_network_id = a_maybe_src_prj.cnn_network_id if a_maybe_src_prj.cnn_network_id else ""
            if a_maybe_src_prj.projid in src_projs:
                checked = True
                src_projs.remove(a_maybe_src_prj.projid)
            elif a_maybe_src_prj.projid in settings_prj_ids:
                checked = True
            else:
                checked = False
            line = {"checked": checked, "projid": a_maybe_src_prj.projid, "title": a_maybe_src_prj.title,
                    "validated_nb": int(validated), "matching_nb": matching, "deep_model": cnn_network_id}
            if not checked:
                table_lines.append(line)
            else:
                table_lines.insert(0, line)

        # Collect project info for missing IDs. We need remaining ALL selected source projects and settings ones
        base_prj_infos = []
        not_found_msg = "(ignored, not found)"
        for a_base_prj_id in settings_prj_ids + src_projs:
            if a_base_prj_id in no_tbl_projs:
                continue
            with ApiClient(ProjectsApi, request) as api:
                try:
                    proj: ProjectModel = api.project_query_projects_project_id_get(a_base_prj_id,
                                                                                   for_managing=False)
                    no_tbl_projs[a_base_prj_id] = proj
                except ApiException as _ae:
                    # The base project might be gone or not visible to current user
                    base_prj_infos.append((a_base_prj_id, not_found_msg))

        if len(src_projs) > 0:
            # Remaining source projects are filtered by display, but still valid in selection
            inp = "<input type='checkbox' checked='true' class='selproj' data-prjid='{projid}'>#{projid}&nbsp;-&nbsp;{title} "
            filtered_by_search = "".join([inp.format(projid=prj_id, title=no_tbl_projs[prj_id].title)
                                          for prj_id in src_projs])
            table_lines.insert(0, "Not in table due to filter:&nbsp;" + filtered_by_search)

        return render_template('task/classifauto2_create_lstproj.html',
                               url=request.query_string.decode('utf-8'),
                               prj_table=table_lines,
                               deep_features=target_prj.cnn_network_id,
                               filters_info=filters_info)

    @staticmethod
    def api_read_accessible_projects(instrument_filter, title_filter):
        bef = time.time()
        with ApiClient(ProjectsApi, request) as api:
            ret: List[ProjectModel] = api.search_projects_projects_search_get(not_granted=False,
                                                                              title_filter=title_filter,
                                                                              instrument_filter=instrument_filter,
                                                                              filter_subset=False)
        with ApiClient(ProjectsApi, request) as api:
            ret.extend(api.search_projects_projects_search_get(not_granted=True,
                                                               title_filter=title_filter,
                                                               instrument_filter=instrument_filter,
                                                               filter_subset=False))
        app.logger.info('Get Projects API call duration: %0.3f s', time.time() - bef)
        return ret

    @classmethod
    def api_read_projects(cls, auth: Any, src_prj_ids: List[int], revobjmapbaseByProj, common_features):
        """ Read project's free columns and add them to the common set """
        ret = []
        for src_prj_id in src_prj_ids:
            with ApiClient(ProjectsApi, auth) as api:
                proj: ProjectModel = api.project_query_projects_project_id_get(src_prj_id,
                                                                               for_managing=False)
            revobjmapbaseByProj[src_prj_id] = cls.GetAugmentedReverseObjectMap(proj)
            common_features.intersection_update(set(revobjmapbaseByProj[src_prj_id].keys()))
            ret.append(proj)
        return ret

    def QuestionProcessScreenSelectSourceTaxo(self, target_prj: ProjectModel):
        # Second écran de configuration, choix des taxa utilisés dans la source

        # Get via API all implied projects
        posted_srcs = gvp('src', gvg('src'))
        src_prj_ids = [int(x) for x in posted_srcs.split(',') if x.isdigit()]
        src_projs = []
        for a_prij_id in src_prj_ids:
            with ApiClient(ProjectsApi, request) as api:
                src_proj: ProjectModel = api.project_query_projects_project_id_get(a_prij_id,
                                                                                   for_managing=False)
            src_projs.append("#%s - %s" % (src_proj.projid, src_proj.title))
        src_prj_ids_sql = ",".join([str(x) for x in src_prj_ids])  # By chance it's an OK format for the API as well

        # Get the number of validated objects of each category in all source projects
        with ApiClient(ProjectsApi, request) as api:
            stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats_project_set_taxo_stats_get(
                ids=src_prj_ids_sql,
                taxa_ids="all")
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
            taxa: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=taxa_ids)
        taxa_per_id = {taxon.id: taxon for taxon in taxa}

        # Get the number of validated objects of each category in each source project
        total_validated = sum(validated_categ_count.values())
        taxo_table = [[taxon_id, taxa_per_id[taxon_id].display_name, nbr_v]
                      for taxon_id, nbr_v in validated_categ_count.items()]
        taxo_table.sort(key=lambda r: r[2], reverse=True)
        # There are < in display names which make them unbreakable during resize
        for a_row in taxo_table:
            if "<" in a_row[1]:
                a_row[1] = a_row[1].replace("<", " < ")

        # Get previous settings which influence how to display the categories (pre-checked or not)
        d = DecodeEqualList(target_prj.classifsettings)
        categories_in_settings = d.get('seltaxo')
        if categories_in_settings:
            settings_taxo_set = {int(x) for x in categories_in_settings.split(',')}
        else:
            settings_taxo_set = {}
        g.TaxoList = [[r[0], r[1], r[2],
                       round(100 * r[2] / total_validated, 1),
                       'checked' if len(settings_taxo_set) == 0 or r[0] in settings_taxo_set else '']
                      for r in taxo_table]  # Add object % and 'checked' or not

        filters_text = self.GetFilterText()

        src_prjs_str = ",&nbsp;".join(src_projs)
        return render_template('task/classifauto2_create_lsttaxo.html'
                               , url=request.query_string.decode('utf-8')
                               , filters_info=filters_text, src_prj_ids=src_prj_ids_sql,
                               src_prjs=src_prjs_str, prj=target_prj)

    def GetFilterText(self):
        TxtFiltres = sharedfilter.GetTextFilter(self.param.filtres)
        if TxtFiltres:
            return "<p><span style='color:red;font-weight:bold;font-size:large;'>USING Active Project Filters</span><BR>Filters : " + TxtFiltres + "</p>"
        else:
            return ""

    def QuestionProcess(self):
        prj_id = int(gvg("projid"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")
        g.prjtitle = target_prj.title
        for k in sharedfilter.FilterList:
            self.param.filtres[k] = gvg(k, "")
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_prj.projid, XSSEscape(target_prj.title))
        txt = ""
        errors = []
        # Le projet de base est choisi second écran ou validation du second ecran
        if gvp('starttask') == "Y":
            # validation du second ecran
            self.param.ProjectId = gvg("projid")
            if gvg("src", gvp("src", "")) != "":
                self.param.BaseProject = CSVIntStringToInClause(gvg("src", gvp("src", "")))
            self.param.CritVar = gvp("CritVar")
            if gvp('ReadPostTaxoMappingFromLB') == "Y":
                self.param.PostTaxoMapping = ",".join(
                    (x[6:] + ":" + gvp(x) for x in request.form if x[0:6] == "taxolb"))
            else:
                self.param.PostTaxoMapping = gvp("PostTaxoMapping")
            self.param.learninglimit = gvp("learninglimit")
            self.param.usescn = gvp("usescn", "")
            # self.param.Taxo=",".join( (x[4:] for x in request.form if x[0:4]=="taxo") )
            self.param.Taxo = gvp('Taxo')
            self.param.CustSettings = DecodeEqualList(gvp("TxtCustSettings"))
            g.TxtCustSettings = gvp("TxtCustSettings")
            # Verifier la coherence des données
            if self.param.CritVar == '' and self.param.usescn == "":
                errors.append("You must select some variable")
            if self.param.Taxo == '': errors.append("You must select some category")

            # Use the API entry point for querying the impacted objects. At these point we just need
            # to know if it's != 0
            with ApiClient(ObjectsApi, self.cookie) as api:
                filters = dict(self.param.filtres)
                filters["statusfilter"] = "UP"
                res: ObjectSetQueryRsp = api.get_object_set_object_set_project_id_query_post(
                    project_id=self.param.ProjectId,
                    project_filters=filters,
                    window_size=100)

            if len(res.object_ids) == 0:
                msg = self.cook_no_object_message()
                errors.append(msg)

            if len(errors) > 0:
                for e in errors:
                    flash(e, "error")
            else:
                # Pas d'erreur, on memorise les parametres dans le projet et on lance la tache
                # On ajoute les valeurs dans CustSettings pour les sauver dans le ClassifSettings du projet
                PrjCS = DecodeEqualList(target_prj.classifsettings)
                d = self.param.CustSettings.copy()
                if gvg("src", gvp("src", "")) != "":
                    # on n'écrase que si les données sont saisies, sinon on prend dans le projet
                    d['critvar'] = self.param.CritVar
                    d['baseproject'] = self.param.BaseProject
                    d['seltaxo'] = self.param.Taxo
                else:
                    if "critvar" in PrjCS: d["critvar"] = PrjCS["critvar"]
                    if "baseproject" in PrjCS: d["baseproject"] = PrjCS["baseproject"]
                    if "seltaxo" in PrjCS: d["seltaxo"] = PrjCS["seltaxo"]
                d['posttaxomapping'] = self.param.PostTaxoMapping
                # Update project classification settings
                with ApiClient(ProjectsApi, request) as api:
                    api. \
                        set_project_predict_settings_projects_project_id_prediction_settings_put(project_id=prj_id,
                                                                                                 settings=EncodeEqualList(
                                                                                                     d))
                return self.StartTask(self.param)
        else:  # valeurs par default
            if gvp('src', gvg('src')) == "":
                return self.QuestionProcessScreenSelectSource(target_prj)
            elif gvp('seltaxo', gvg('seltaxo')) == "":
                return self.QuestionProcessScreenSelectSourceTaxo(target_prj)

            # OK, third page of the wizard, proceed
            d = DecodeEqualList(target_prj.classifsettings)
            # Certaines variable on leur propre zone d'edition, les autres sont dans la zone texte custom settings
            self.param.CritVar = d.get("critvar", "")
            self.param.Taxo = d.get("seltaxo", "")
            # Référence for the 5000: Ricour Florian & al 2022
            self.param.learninglimit = int(gvp("learninglimit", "5000"))
            if "critvar" in d:
                del d["critvar"]
            if "methode" in d:
                del d["methode"]
            if "learninglimit" in d:
                del d["learninglimit"]
            if "seltaxo" in d:
                del d["seltaxo"]
            if "PostTaxoMapping" in d:
                del d["PostTaxoMapping"]
            if "baseproject" in d:
                del d["baseproject"]
            g.TxtCustSettings = EncodeEqualList(d)
            self.param.Taxo = ",".join((x[4:] for x in request.form if x[0:4] == "taxo" and x[0:6] != "taxolb"))
            self.param.PostTaxoMapping = ",".join((x[6:] + ":" + gvp(x) for x in request.form if x[0:6] == "taxolb"))

        # Determination des criteres/variables utilisées par l'algo de learning
        revobjmap = self.GetAugmentedReverseObjectMap(target_prj)  # Dict NomVariable=>N° colonne ex Area:n42
        common_features = set(revobjmap.keys())

        # Loop over source projects, get their keys and determine a set of common keys (for dest + all srcs)
        # Note: given the harcoded values in @see GetAugmentedReverseObjectMap, the common keys comprise
        # at least depth_min and depth_max
        src_prj_lst = gvp("src", gvg("src"))
        revobjmapbaseByProj = {}
        src_prj_ids = [int(prj_id) for prj_id in src_prj_lst.split(",") if prj_id.isdigit()]

        src_projs = self.api_read_projects(request, src_prj_ids, revobjmapbaseByProj, common_features)

        # critlist[feature] 0:feature , 1:% validated , 2:distinct
        critlist = {k: [k, -1, -1] for k in common_features}

        # Prepare names for the API call
        names_for_stats = ",".join(["fre.%s" % col for col in common_features if col not in self.OBJECT_VARS])
        names_for_stats += ("," if names_for_stats else "") + ",".join(["obj.%s" % col for col in self.OBJECT_VARS])
        # Stats on training set, i.e. projects+categories+limit
        with ApiClient(ProjectsApi, request) as api:
            stats: ProjectSetColumnStatsModel = \
                api.project_set_get_column_stats_project_set_column_stats_get(ids=src_prj_lst,
                                                                              names=names_for_stats,
                                                                              limit=self.param.learninglimit,
                                                                              categories=self.param.Taxo)
        g.LsSize = stats.total
        for col, count, variance in zip(stats.columns, stats.counts, stats.variances):
            prfx, name = col.split(".", 1)
            critlist[name][1] = round(100 * (1 - count / stats.total))  # % Missing in source projects
            critlist[name][2] = ' ' if variance is None else ('Y' if variance != 0 else 'N')

        g.SCN = None
        if app.config.get("SCN_ENABLED", False):
            cnn_networks = set([target_prj.cnn_network_id]+[a_prj.cnn_network_id for a_prj in src_projs])
            g.SCN = target_prj.cnn_network_id is not None and len(cnn_networks) == 1

        g.critlist = list(critlist.values())
        g.critlist.sort(key=lambda t: t[0])
        # app.logger.info(revobjmap)
        data = self.param
        data.src = src_prj_lst
        return render_template('task/classifauto2_create_settings.html', header=txt, data=data,
                               filters_info=self.GetFilterText())

    def cook_no_object_message(self):
        msg = "No object to classify, perhaps all objects were already classified."
        if len(self.param.filtres) > 0:
            msg += " Note that you have active filters, which reduces potential target objects."
        return msg

    @classmethod
    def GetAugmentedReverseObjectMap(cls, prj: ProjectModel):
        """ Return numerical free columns for a project + 2 hard-coded ones """
        ret = {k: v for k, v in prj.obj_free_cols.items() if v[0] == 'n'}
        for an_obj_var in cls.OBJECT_VARS:
            ret[an_obj_var] = an_obj_var
        return ret

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId = self.param.ProjectId
        time.sleep(1)
        # DoTaskClean(self.task.id)
        return """<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a> """.format(
            PrjId)
