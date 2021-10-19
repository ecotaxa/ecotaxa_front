# -*- coding: utf-8 -*-
import json
import logging
import os
import sys
import time
from pathlib import Path
from subprocess import Popen, TimeoutExpired, DEVNULL, PIPE
from typing import List, Any

import numpy as np
from flask import render_template, g, flash, request
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

from appli import db, database, PrintInCharte, gvp, gvg, EncodeEqualList, DecodeEqualList, app, TempTaskDir, \
    XSSEscape
from appli.database import GetAll, CSVIntStringToInClause
from appli.project import sharedfilter
from appli.project.stats import UpdateProjectStat
from appli.tasks.taskmanager import AsyncTask
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ObjectsApi, ObjectSetQueryRsp, ClassifyAutoReq, ProjectsApi, ProjectModel, \
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
                self.keeplog = "no"
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

    def ComputeSCNFeatures(self, Prj: ProjectModel):
        logging.info("Start SCN features Computation ")
        # Minimal sanity check
        if Prj.cnn_network_id is None or len(Prj.cnn_network_id) == 0:
            logging.error("No SCN Network set for this project. See settings.")
            self.task.taskstate = "Error"
            return False
        if self.param.BaseProject != '':
            PrjListInClause = CSVIntStringToInClause(self.param.BaseProject + ',' + str(self.param.ProjectId))
        else:
            PrjListInClause = str(self.param.ProjectId)
        # Find the _potentially_ useful for SCN rows and update their cnn_feature lines
        sql = """select objid,file_name from (
                select obj.objid,  images.file_name,rank() over(partition by obj.objid order by images.imgid) rang
                    from objects obj
                    join images on images.objid=obj.objid
                    left join obj_cnn_features cnn on obj.objid=cnn.objcnnid                    
                    where obj.projid in({0}) and cnn.objcnnid is NULL
                    ) Q 
                    where rang=1
                    """.format(PrjListInClause)
        self.pgcur.execute(sql)
        WorkDir = Path(self.GetWorkingDir())
        scn_input = WorkDir / "scn_input.csv"
        output_dir = WorkDir / "scn_output"
        if not output_dir.exists(): output_dir.mkdir()
        vaultdir = (Path(TempTaskDir) / "../vault/").resolve().as_posix() + "/"
        # Configure the execution
        scn_model_dir = Path(os.path.normpath((Path(TempTaskDir) / "../SCN_networks" / Prj.cnn_network_id).as_posix())). \
            resolve()
        meta = json.load((scn_model_dir / "meta.json").open('r'))
        TStep = time.time()
        NbrLig = 0
        with scn_input.open('w') as finput:
            while True:
                # recupère les images des objets à calculer
                DBRes = self.pgcur.fetchmany(1000)
                if len(DBRes) == 0:
                    break
                NbrLig += len(DBRes)
                finput.writelines(("%s,%s%s\n" % (r[0], vaultdir, r[1]) for r in DBRes))
        if NbrLig == 0:
            logging.info("No Missing SCN Features")
            return True
        TStep = time.time()
        env = {
            "MODEL_DIR": scn_model_dir.as_posix(),
            "OUTPUT_DIR": output_dir.resolve().as_posix(),
            # input data
            "UNLABELED_DATA_FN": scn_input.as_posix(),
            # start at the last epoch (NB: this is the previous STOP_EPOCH - 1 because of 0-based indexing)
            "EPOCH": str(meta['epoch']),
            # stop early = do not train
            "STOP_EPOCH": "0",
            # whether to compute features on the input file
            "DUMP_FEATURES": "1"
        }
        # display the current environment
        for k, v in env.items():
            logging.info("{}: {}".format(k, v))

        # time out for the communication with the binary
        # beware, this is for the full execution event while execution can be long for training
        timeout_in_s = 1200

        scn_binary = app.config['SCN_BINARY']
        # recopie toutes les variables d'environnement utile pour l'environnement simulé
        for k, v in os.environ.items():
            env[k] = v
        # TEST sur le PC de laurent avec script de simulation
        if scn_binary == 'TEST_PC_LAURENT':
            # for extra in ['PATH','SYSTEMROOT']:
            #     env[extra]= os.environ[extra]
            scn_binary = sys.executable + " " + (
                    Path(TempTaskDir) / "../appli/tasks/simulateur_SCN.py").resolve().as_posix()

        shelloption = scn_binary.endswith('.sh')

        logging.info("scn_binary=" + scn_binary)
        # bufsize=1: Line buffering
        with Popen(scn_binary, shell=shelloption, stdin=DEVNULL, stdout=PIPE, stderr=PIPE, env=env,
                   universal_newlines=True, bufsize=1) as p:
            try:
                outs, errs = p.communicate(timeout=timeout_in_s)
            except TimeoutExpired:
                p.kill()
                outs, errs = p.communicate()
        logging.info("Return code: {}".format(p.returncode))
        logging.info("Output: \n%s", outs)
        logging.info("Errors: %s", errs)

        upcur = db.engine.raw_connection().cursor()
        InsSQL = """insert into obj_cnn_features(objcnnid, cnn01, cnn02, cnn03, cnn04, cnn05, cnn06, cnn07, cnn08, cnn09, cnn10, cnn11, cnn12, cnn13, cnn14, cnn15, cnn16, cnn17, cnn18, cnn19, cnn20, cnn21, cnn22, cnn23, cnn24, cnn25, cnn26, cnn27, cnn28, cnn29, cnn30, cnn31, cnn32, cnn33, cnn34, cnn35, cnn36, cnn37, cnn38, cnn39, cnn40, cnn41, cnn42, cnn43, cnn44, cnn45, cnn46, cnn47, cnn48, cnn49, cnn50) 
                    values(%(objcnnid)s,%(cnn01)s,%(cnn02)s,%(cnn03)s,%(cnn04)s,%(cnn05)s,%(cnn06)s,%(cnn07)s,%(cnn08)s,%(cnn09)s,%(cnn10)s,%(cnn11)s,%(cnn12)s,%(cnn13)s,%(cnn14)s,%(cnn15)s,%(cnn16)s,%(cnn17)s,%(cnn18)s,%(cnn19)s,%(cnn20)s,%(cnn21)s,%(cnn22)s,%(cnn23)s,%(cnn24)s,%(cnn25)s,%(cnn26)s,%(cnn27)s,%(cnn28)s,%(cnn29)s,%(cnn30)s,%(cnn31)s,%(cnn32)s,%(cnn33)s,%(cnn34)s,%(cnn35)s,%(cnn36)s,%(cnn37)s,%(cnn38)s,%(cnn39)s,%(cnn40)s,%(cnn41)s,%(cnn42)s,%(cnn43)s,%(cnn44)s,%(cnn45)s,%(cnn46)s,%(cnn47)s,%(cnn48)s,%(cnn49)s,%(cnn50)s )"""

        pca = joblib.load(scn_model_dir / "feature_pca.jbl")

        def ProcessLig():
            nonlocal LigData, InsSQL, upcur, LigID, pca
            # pour générer un fichier de test
            # pca = PCA(n_components=50)
            # pca.fit(np.array(LigData))
            # pca_fn = model_dir/"feature_pca.jbl"
            # joblib.dump(pca, pca_fn)

            pcares = pca.transform(np.array(LigData))
            SQLParam = [{"cnn%02d" % (i + 1): float(x) for i, x in enumerate(feat)} for feat in pcares]
            for i in range(len(SQLParam)):
                SQLParam[i]['objcnnid'] = LigID[i]
            database.ExecSQL("delete from obj_cnn_features where objcnnid= any(%s)", (LigID,))
            upcur.executemany(InsSQL, SQLParam)
            upcur.connection.commit()
            LigData = []
            LigID = []

        with (output_dir / 'unlabeled_features.csv').open('r') as fout:
            LigID = []
            LigData = []
            for l in fout:
                Lig = l.split(',')
                LigID.append(int(Lig[0]))
                LigData.append([float(x) for x in Lig[2:]])
                if len(LigData) > 100:
                    ProcessLig()
        if len(LigData) > 0:
            ProcessLig()
        return True

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

        logging.info("Start Step 1")
        TInit = time.time()

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

        # Wait for the back-end job to complete
        job_id = rsp.job_id
        while True:
            with ApiClient(JobsApi, self.cookie) as api:
                job: JobModel = api.get_job_jobs_job_id_get(job_id=job_id)
            if job.state in ('E', 'F'):
                break
            logging.info("Job: %s", job)
            time.sleep(5)

        self.task.taskstate = "Done"
        self.UpdateProgress(100, "Job completed on back-end")

        return

        with ApiClient(ProjectsApi, self.cookie) as api:
            target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)

        MapPrj = self.GetAugmentedReverseObjectMap(target_prj)  # Dict NomVariable=>N° colonne ex Area:n42
        CommonKeys = set(MapPrj.keys())

        # PostTaxoMapping décodé sous la forme source:target
        PostTaxoMapping = {int(el[0].strip()): int(el[1].strip()) for el in
                           [el.split(':') for el in self.param.PostTaxoMapping.split(',') if el != '']}
        logging.info("PostTaxoMapping = %s ", PostTaxoMapping)

        CNNCols = ""
        if self.param.usescn == 'Y':
            if not self.ComputeSCNFeatures(target_prj):
                return
            CNNCols = "".join([",cnn%02d" % (i + 1) for i in range(50)])

        # Calcul du modèle à partir de projets sources
        self.UpdateProgress(1, "Retrieve Data from Learning Set")

        revobjmapbaseByProj = {}
        base_projects = self.param.BaseProject
        src_prj_ids = [int(prj_id) for prj_id in base_projects.split(",")]

        self.api_read_projects(self.cookie, src_prj_ids, revobjmapbaseByProj, CommonKeys)

        if self.param.learninglimit:
            self.param.learninglimit = int(self.param.learninglimit)  # convert
        logging.info("MapPrj %s", MapPrj)
        logging.info("MapPrjBase %s", revobjmapbaseByProj)
        CritVar = self.param.CritVar.split(",")

        # ne garde que les colonnes communes qui sont aussi selectionnées.
        CommonKeys.intersection_update(set(CritVar))

        # Online help says "Missing values are replaced by the median value for this feature from the learning set."
        sql = ""
        for bprojid in src_prj_ids:
            if sql != "":
                sql += " union all "
            sql += "select 1"
            for c in CommonKeys:
                sql += ",coalesce(percentile_cont(0.5) WITHIN GROUP (ORDER BY {0}),-9999) as {1}". \
                    format(revobjmapbaseByProj[bprojid][c], MapPrj[c])
            sql += " from objects "
            sql += " where projid={0} and classif_id is not null and classif_qual='V'".format(bprojid)

        if self.param.learninglimit:
            # random() instead?
            LimitHead = """ with objlist as ( select objid from (
                        select obj.objid,row_number() over(PARTITION BY classif_id order by random_value) rang
                        from objects obj
                        where obj.projid in ({0}) and obj.classif_id is not null and classif_qual='V' ) q 
                        where rang <={1} ) """. \
                format(base_projects, self.param.learninglimit)
            LimitFoot = """ and objid in ( select objid from objlist ) """
            sql = LimitHead + sql + LimitFoot
        else:
            LimitHead = LimitFoot = ""
        DefVal = GetAll(sql)[0]

        # Extrait les données du learning set
        sql = ""
        for bprojid in src_prj_ids:
            if sql != "":
                sql += " \nunion all "
            sql = "select classif_id"
            for c in CommonKeys:
                sql += ",coalesce(case when {0} not in ('Infinity','-Infinity','NaN') then {0} end,{1}) as {2}".format(
                    revobjmapbaseByProj[bprojid][c], DefVal[MapPrj[c]], MapPrj[c])
            sql += CNNCols + " from objects "
            if self.param.usescn == 'Y':
                sql += " join obj_cnn_features on obj_cnn_features.objcnnid=objects.objid "
            sql += """ where classif_id is not null and classif_qual='V'
                        and projid in({0})
                        and classif_id in ({1}) """.format(base_projects, self.param.Taxo)
        if self.param.learninglimit:
            sql = LimitHead + sql + LimitFoot
        # Convertie le LS en tableau NumPy
        DBRes = np.array(GetAll(sql))
        LSSize = DBRes.shape[0]
        learn_cat = DBRes[:, 0]  # Que la classif
        learn_var = DBRes[:, 1:]  # exclu l'objid & la classif
        DBRes = None  # libere la mémoire
        logging.info('DB Conversion to NP : %0.3f s', time.time() - TInit)
        logging.info("Variable shape %d Row, %d Col", *learn_var.shape)
        # Note : La multiplication des jobs n'est pas forcement plus performante, en tous cas sur un petit ensemble.
        Classifier = RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=1, class_weight="balanced")

        # TStep = time.time()
        # cette solution ne convient pas, car lorsqu'on l'applique par bloc de 100 parfois il n'y a pas de valeur dans
        # toute la colonne et du coup la colonne est supprimé car on ne peut pas calculer la moyenne.
        # learn_var = Imputer().fit_transform(learn_var)
        # learn_var[learn_var==np.nan] = -99999 Les Nan sont des NULL dans la base traités parle coalesce
        # logging.info('Clean input variables :  %0.3f s', time.time() - TStep)
        TStep = time.time()
        Classifier.fit(learn_var, learn_cat)
        logging.info('Model fit duration :  %0.3f s', time.time() - TStep)
        # ------ Fin de la partie apprentissage ou chargement du modèle

        # Use the API entry point for filtering
        with ApiClient(ObjectsApi, self.cookie) as api:
            res: ObjectSetQueryRsp = api.get_object_set_object_set_project_id_query_post(self.param.ProjectId,
                                                                                         self.param.filtres)
            affected_where = " and ( classif_qual='P' or classif_qual is null) and o.objid = any (%(objids)s) "
            sqlparam = {"objids": sorted(res.object_ids)}

        NbrItem = \
            GetAll("select count(*) from objects o where projid={0} {1} ".format(target_prj.projid, affected_where),
                   sqlparam)[
                0][
                0]

        if NbrItem == 0:
            msg = self.cook_no_object_message()
            raise Exception(msg)  # Inside the task, so cannot display anything for the user

        sql = "select objid"
        for c in CommonKeys:
            sql += ",coalesce(case when {0} not in ('Infinity','-Infinity','NaN') then {0} end,{1}) as {0}".format(
                MapPrj[c], DefVal[MapPrj[c]])
        sql += CNNCols + " from objects o "
        if self.param.usescn == 'Y':
            sql += " join obj_cnn_features on obj_cnn_features.objcnnid=o.objid "
        sql += """ where projid={0} {1}
                    order by objid""".format(target_prj.projid, affected_where)
        self.pgcur.execute(sql, sqlparam)
        # logging.info("SQL=%s",sql)
        ProcessedRows = 0
        while True:
            self.UpdateProgress(15 + 85 * (ProcessedRows / NbrItem), "Processed %d/%d" % (ProcessedRows, NbrItem))
            TStep = time.time()
            # recupère les variables des objets à classifier
            DBRes = np.array(self.pgcur.fetchmany(100))
            if len(DBRes) == 0:
                break
            ProcessedRows += len(DBRes)
            Tget_Ids = DBRes[:, 0]  # Que l'objid
            Tget_var = DBRes[:, 1:]  # exclu l'objid
            TStep2 = time.time()
            # Tget_var= Imputer().fit_transform(Tget_var) # voir commentaire sur learn_var
            # Tget_var[Tget_var==np.nan] = -99999
            Result = Classifier.predict_proba(Tget_var)
            ResultMaxCol = np.argmax(Result, axis=1)
            # Typage important pour les perf postgresql
            SqlParam = [{'cat': int(Classifier.classes_[mc]), 'p': r[mc], 'id': int(i)} for i, mc, r in
                        zip(Tget_Ids, ResultMaxCol, Result)]
            # TODO: This is indeed a Post-prediction mapping, but the UI in a pre-training One
            # for i, v in enumerate(SqlParam):
            #     if v['cat'] in PostTaxoMapping:
            #         SqlParam[i]['cat'] = PostTaxoMapping[v['cat']]
            TStep3 = time.time()
            # Call auto classification storage primitive on back-end
            with ApiClient(ObjectsApi, self.cookie) as api:
                req = ClassifyAutoReq(target_ids=[a_classif['id'] for a_classif in SqlParam],
                                      classifications=[a_classif['cat'] for a_classif in SqlParam],
                                      scores=[a_classif['p'] for a_classif in SqlParam],
                                      keep_log=self.param.keeplog == 'Yes')
                api.classify_auto_object_set_object_set_classify_auto_post(classify_auto_req=req)
            logging.info('Chunk Db Extract %d/%d, Classification and Db Save :  %0.3f s %0.3f+%0.3f+%0.3f'
                         , ProcessedRows, NbrItem
                         , time.time() - TStep, TStep2 - TStep, TStep3 - TStep2, time.time() - TStep3)

        UpdateProjectStat(target_prj.projid)
        self.task.taskstate = "Done"
        self.UpdateProgress(100, "Classified %d objects" % ProcessedRows)

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
                checked = 'checked="true"'
                src_projs.remove(a_maybe_src_prj.projid)
            elif a_maybe_src_prj.projid in settings_prj_ids:
                checked = 'checked="true"'
            else:
                checked = ""
            line = """<tr><td><input type='checkbox' {checked} class='selproj' data-prjid='{projid}'></td>
                      <td>#{projid} - {title}</td><td>{objvalid:0.0f}</td><td>{MatchingFeatures}</td><td>{cnn_network_id}</td>
                      </tr>""".format(MatchingFeatures=matching, checked=checked, projid=a_maybe_src_prj.projid,
                                      title=a_maybe_src_prj.title, objvalid=validated,
                                      cnn_network_id=cnn_network_id)
            if checked == "":
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

        return render_template('task/classifauto2_create_lstproj.html'
                               , url=request.query_string.decode('utf-8')
                               , TblBody="".join(table_lines)
                               , filters_info=filters_info)

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
    def api_read_projects(cls, auth: Any, src_prj_ids: List[int], revobjmapbaseByProj, CommonKeys):
        """ Read project's free columns and add them to the common set """
        for src_prj_id in src_prj_ids:
            with ApiClient(ProjectsApi, auth) as api:
                proj: ProjectModel = api.project_query_projects_project_id_get(src_prj_id,
                                                                               for_managing=False)
            revobjmapbaseByProj[src_prj_id] = cls.GetAugmentedReverseObjectMap(proj)
            CommonKeys.intersection_update(set(revobjmapbaseByProj[src_prj_id].keys()))

    def QuestionProcessScreenSelectSourceTaxo(self, target_prj: ProjectModel):
        # Second écran de configuration, choix des taxon utilisés dans la source

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
            self.param.keeplog = gvp("keeplog")
            self.param.usescn = gvp("usescn", "")
            # self.param.Taxo=",".join( (x[4:] for x in request.form if x[0:4]=="taxo") )
            self.param.Taxo = gvp('Taxo')
            self.param.CustSettings = DecodeEqualList(gvp("TxtCustSettings"))
            g.TxtCustSettings = gvp("TxtCustSettings")
            # Verifier la coherence des données
            if self.param.CritVar == '' and self.param.usescn == "":
                errors.append("You must select some variable")
            if self.param.Taxo == '': errors.append("You must select some category")

            # Use the API entry point for filtering
            with ApiClient(ObjectsApi, self.cookie) as api:
                res: ObjectSetQueryRsp = api.get_object_set_object_set_project_id_query_post(self.param.ProjectId,
                                                                                             self.param.filtres)
                affected_where = " and ( classif_qual='P' or classif_qual is null) and o.objid = any (%(objids)s) "
                sqlparam = {"objids": sorted(res.object_ids)}

            NbrItem = \
                GetAll("select count(*) from objects o where projid={0} {1} ".format(target_prj.projid, affected_where),
                       sqlparam)[
                    0][0]
            if NbrItem == 0:
                msg = self.cook_no_object_message()
                errors.append(msg)

            if len(errors) > 0:
                for e in errors:
                    flash(e, "error")
            else:  # Pas d'erreur, on memorize les parametres dans le projet et on lance la tache
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
        CommonKeys = set(revobjmap.keys())

        # Loop over source projects, get their keys and determine a set of common keys (for dest + all srcs)
        # Note: given the harcoded values in @see GetAugmentedReverseObjectMap, the common keys comprise
        # at least depth_min and depth_max
        src_prj_lst = gvp("src", gvg("src"))
        revobjmapbaseByProj = {}
        src_prj_ids = [int(prj_id) for prj_id in src_prj_lst.split(",") if prj_id.isdigit()]

        self.api_read_projects(request, src_prj_ids, revobjmapbaseByProj, CommonKeys)

        # critlist[NomCol] 0:NomCol , 1:LS % validé rempli , 2:LS Nbr distincte ,3:Cible % rempli ,4:Cible % NV Rempli Inutile ?
        critlist = {k: [k, -1, -1, -1, -1] for k in CommonKeys}

        # Prepare names for the API call
        names_for_stats = ",".join(["fre.%s" % col for col in CommonKeys])
        names_for_stats = names_for_stats \
            .replace("fre.depth_min", "obj.depth_min") \
            .replace("fre.depth_max", "obj.depth_max")
        # Stats on training set
        with ApiClient(ProjectsApi, request) as api:
            stats: ProjectSetColumnStatsModel = \
                api.project_set_get_column_stats_project_set_column_stats_get(ids=src_prj_lst,
                                                                              names=names_for_stats)
        g.LsSize = stats.total
        for col, count, variance in zip(stats.columns, stats.counts, stats.variances):
            prfx, name = col.split(".")
            critlist[name][1] = round(100 * (1 - count / stats.total))  # % Missing dans Learning Set
            critlist[name][2] = ' ' if variance is None else (
                'Y' if variance != 0 else 'N')  # Distinct values N si une seule ou pas de valeur

        # Calcul des stats du projet cible
        with ApiClient(ProjectsApi, request) as api:
            stats: ProjectSetColumnStatsModel = \
                api.project_set_get_column_stats_project_set_column_stats_get(ids=str(target_prj.projid),
                                                                              names=names_for_stats)
        for col, count, variance in zip(stats.columns, stats.counts, stats.variances):
            prfx, name = col.split(".")
            critlist[name][3] = round(100 * (1 - count / stats.total))  # % Missing dans cible
            critlist[name][4] = ' ' if variance is None else (
                'Y' if variance != 0 else 'N')  # Distinct values N si une seule ou pas de valeur

        # Calcul des stats de la dispo des données SCN
        g.SCN = None
        if app.config.get("SCN_ENABLED", False):
            sql = """
              select p.projid,p.title,n.nbr,n.nbr-nbrscn miss_scn,cnn_network_id scnmodel
              from projects p
              join (select obj.projid,count(*) nbr,count(cnn.objcnnid) nbrscn  
                    from objects obj
                    left join obj_cnn_features cnn on obj.objid=cnn.objcnnid  
                    where obj.projid in({0}) group by projid) N on n.projid=p.projid
              order by p.projid
              """.format(src_prj_lst + (",%d" % target_prj.projid))
            g.SCN = GetAll(sql)
            g.SCNImpossible = None
            DistinctSCN = {r['scnmodel'] for r in g.SCN}
            if None in DistinctSCN:
                g.SCNImpossible = "Some project are not configured for Deep Learning"
            elif len(DistinctSCN) > 1:
                g.SCNImpossible = "All projects must use the same Network"

        g.critlist = list(critlist.values())
        g.critlist.sort(key=lambda t: t[0])
        # app.logger.info(revobjmap)
        data = self.param
        data.src = src_prj_lst
        return render_template('task/classifauto2_create_settings.html', header=txt, data=data,
                               PreviousTxt=self.GetFilterText())

    def cook_no_object_message(self):
        msg = "No object to classify, perhaps all objects were already classified."
        if len(self.param.filtres) > 0:
            msg += " Note that you have active filters, which reduces potential target objects."
        return msg

    @classmethod
    def GetAugmentedReverseObjectMap(cls, prj: ProjectModel):
        """ Return numerical free columns for a project + 2 hard-coded ones """
        ret = {k: v for k, v in prj.obj_free_cols.items() if k[0] == 'n'}
        ret['depth_min'] = 'depth_min'
        ret['depth_max'] = 'depth_max'
        return ret

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId = self.param.ProjectId
        time.sleep(1)
        # DoTaskClean(self.task.id)
        return """<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a> """.format(
            PrjId)
