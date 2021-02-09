# -*- coding: utf-8 -*-
import time
from typing import List

from flask import render_template, g

from appli import PrintInCharte, gvg, db
from appli.constants import get_app_manager_mail
from appli.tasks.importcommon import *
from appli.tasks.taskmanager import AsyncTask
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ImportPrepReq, ImportPrepRsp, ImportRealReq, ProjectsApi, UsersApi, ApiException, \
    TaxonomyTreeApi, TaxonModel, ProjectModel, UserModel


# noinspection DuplicatedCode
class TaskImportToBack(AsyncTask):
    """
        Import, just GUI here, bulk of job subcontracted to back-end.
        Also serves as a base class for import update as pages are very similar.
    """
    STEP0_TEMPLATE = "task/import_create.html"

    class Params(AsyncTask.Params):
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr is None:  # Valeurs par defaut ou vide pour init
                self.InData = 'My In Data'
                self.ProjectId = None
                self.SkipAlreadyLoadedFile = "N"  # permet de dire si on
                self.SkipObjectDuplicate = "N"
                # For import update
                self.UpdateClassif = "N"
                # mapping, stored at project level
                self.Mapping = {}
                self.TaxoMap = {}
                # Extra params added during steps
                self.TotalRowCount = 0
                self.TaxoFound = {}
                self.UserFound = {}
                # Errors displayed to user
                self.steperrors = []

    def __init__(self, task=None):
        super().__init__(task)
        if task is None:
            self.param = self.Params()
        else:
            self.param = self.Params(task.inputparam)

    # noinspection PyMethodMayBeStatic
    def SPCommon(self):
        """ Executed before each step, i.e. in subprocess """
        logging.info("Execute SPCommon")

    def _CreateDialogStep0(self):
        """ In UI/flask, task.taskstep = 0 AKA initial dialog """
        prj_id = int(gvg("p"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")
        g.prjtitle = target_prj.title
        g.prjprojid = target_prj.projid
        g.prjmanagermailto = target_prj.managers[0].email
        txt = ""
        g.appmanagermailto = get_app_manager_mail(request)

        server_path = gvp("ServerPath")
        if gvp('starttask') == "Y":
            # Form Submit -> check and store values to use
            errors = []
            self.param.ProjectId = gvg("p")
            self.param.SkipAlreadyLoadedFile = gvp("skiploaded")
            self.param.SkipObjectDuplicate = gvp("skipobjectduplicate")
            # Import update parameter
            self.param.UpdateClassif = gvp("updateclassif")
            taxo_map = {}
            for lig in gvp('TxtTaxoMap').splitlines():
                ls = lig.split('=', 1)
                if len(ls) != 2:
                    errors.append("Taxonomy Mapping : Invalid format for line %s" % lig)
                else:
                    taxo_map[ls[0].strip().lower()] = ls[1].strip().lower()
            # Import file parameter
            file_to_save, file_to_save_file_name = get_file_from_form(self, errors)
            # Save preferences
            if server_path != "":
                with ApiClient(UsersApi, request) as api:
                    # Compute directory to open next time, we pick the parent to avoid double import of the same
                    # directory or zip.
                    cwd = str(Path(server_path).parent)
                    api.set_current_user_prefs_users_my_preferences_project_id_put(self.param.ProjectId, "cwd", cwd)

            if len(errors) > 0:
                for e in errors:
                    flash(e, "error")
            else:
                self.param.TaxoMap = taxo_map  # on stocke le dictionnaire et pas la chaine
                # start Step1, in a subprocess as we're in UI process, reusing log files
                return self.StartTask(self.param, step=1, FileToSave=file_to_save,
                                      FileToSaveFileName=file_to_save_file_name)
        else:  # valeurs par default
            self.param.ProjectId = gvg("p")
        if server_path == "":
            with ApiClient(UsersApi, request) as api:
                server_path = api.get_current_user_prefs_users_my_preferences_project_id_get(self.param.ProjectId,
                                                                                             "cwd")
        return render_template(self.STEP0_TEMPLATE, header=txt, data=self.param, ServerPath=server_path,
                               TxtTaxoMap=gvp("TxtTaxoMap"))

    def SPStep1(self):
        """ In subprocess, task.taskstep = 1 """
        self.UpdateProgress(0, "Waiting for backend")
        logging.info("Input Param = %s" % self.param.__dict__)
        logging.info("Start Step 1 : Data validation and preparation")
        req = ImportPrepReq(task_id=self.task.id,
                            source_path=self.param.InData,
                            taxo_mappings=self.param.TaxoMap,
                            skip_loaded_files=(self.param.SkipAlreadyLoadedFile == "Y"),
                            skip_existing_objects=self._must_skip_existing_objects(),
                            update_mode=self._update_mode())
        with ApiClient(ProjectsApi, self.cookie) as api:
            try:
                rsp: ImportPrepRsp = api.import_preparation_import_prep_project_id_post(self.param.ProjectId, req)
            except ApiException as ae:
                if ae.status in (401, 403):
                    self.task.taskstate = "Error"
                    self.task.progressmsg = "You don't have enough permission on this project"
                    self.UpdateParam()
                    return
                else:
                    raise
        # Copy back into params the eventually amended fields in response
        self.param.InData = rsp.source_path
        self.param.TaxoFound = rsp.found_taxa
        self.param.UserFound = rsp.found_users
        self.param.Mapping = rsp.mappings
        self.param.TotalRowCount = rsp.rowcount
        self.UpdateParam()
        if len(rsp.errors) != 0:
            msg = "Some errors were found during file parsing"
            logging.error(msg + ":")
            for an_err in rsp.errors:
                logging.error(an_err)
            self.task.taskstate = "Error"
            self.task.progressmsg = msg
            self.param.steperrors = rsp.errors[:1000]
            self.UpdateParam()
        elif len(self._notFoundTaxoInParam()) > 0 or len(self._notFoundUsersInParam()) > 0:
            self.task.taskstate = "Question"
            db.session.commit()
        else:
            # We're still in spawned subprocess so we can import right away
            self.SPStep2()

    def _MappingDialogStep1(self):
        """ In UI/flask, task.taskstep = 1 AKA mapping of not found entities """
        txt = "<h1>Text File Importation Task</h1>"
        errors = []
        prj_id = self.param.ProjectId
        with ApiClient(ProjectsApi, request) as api:
            target_project: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
        g.prjtitle = target_project.title
        g.prjprojid = target_project.projid
        not_found_taxo = self._notFoundTaxoInParam()
        not_found_users = self._notFoundUsersInParam()
        app.logger.info("Pending Taxo Not Found = %s", not_found_taxo)
        app.logger.info("Pending Users Not Found = %s", not_found_users)
        if gvp('starttask') == "Y":
            # Submit -> check and store values to use
            app.logger.info("Form Data = %s", request.form)
            for i in range(1, 1 + len(not_found_taxo)):
                orig = gvp("orig%d" % i)  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
                newvalue = gvp("taxolb%d" % i)
                if orig in not_found_taxo and newvalue != "":
                    # OK it could be a bit more efficient by grouping calls
                    with ApiClient(TaxonomyTreeApi, request) as api:
                        nodes: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=newvalue)
                    taxon = nodes[0]
                    app.logger.info(orig + " associated to " + taxon.name)
                    self.param.TaxoFound[orig] = taxon.id
                else:
                    errors.append("Taxonomy Manual Mapping : Invalid value '%s' for '%s'" % (newvalue, orig))
            for i in range(1, 1 + len(not_found_users)):
                orig = gvp("origuser%d" % i)  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
                newvalue = gvp("userlb%d" % i)
                if orig in not_found_users and newvalue != "":
                    with ApiClient(UsersApi, request) as api:
                        user: UserModel = api.get_user_users_user_id_get(user_id=int(newvalue))
                    app.logger.info("User " + orig + " associated to " + user.name)
                    self.param.UserFound[orig]['id'] = user.id
                else:
                    errors.append("User Manual Mapping : Invalid value '%s' for '%s'" % (newvalue, orig))
            app.logger.info("Final Taxofound = %s", self.param.TaxoFound)
            self.UpdateParam()  # On met à jour ce qui à été accepté
            # Verifier la coherence des données
            if len(errors) == 0:
                # start Step2, subprocess as we're in UI process
                return self.StartTask(self.param, step=2)
            for e in errors:
                flash(e, "error")
            not_found_taxo = [k for k, v in self.param.TaxoFound.items() if v is None]
            not_found_users = [k for k, v in self.param.UserFound.items() if v.get('id') is None]
        return render_template('task/import_question1.html', header=txt, taxo=not_found_taxo, users=not_found_users,
                               task=self.task)

    def _must_skip_existing_objects(self) -> bool:
        return self.param.SkipObjectDuplicate == "Y"

    def _update_mode(self) -> str:
        return ""  # No update for plain import

    def SPStep2(self):
        """ In subprocess, task.taskstep = 2 """
        self.UpdateProgress(0, "Waiting for backend")
        logging.info("Input Param = %s" % self.param.__dict__)
        logging.info("Start Step 2 : Effective data import")
        req = ImportRealReq(task_id=self.task.id,
                            taxo_mappings=self.param.TaxoMap,
                            update_mode=self._update_mode(),  # from class
                            skip_loaded_files=(self.param.SkipAlreadyLoadedFile == "Y"),
                            skip_existing_objects=self._must_skip_existing_objects(),
                            source_path=self.param.InData,  # from prep
                            mappings=self.param.Mapping,  # from prep
                            rowcount=self.param.TotalRowCount,  # from prep
                            found_users=self.param.UserFound,  # from prep & UI
                            found_taxa=self.param.TaxoFound  # from prep & UI
                            )
        with ApiClient(ProjectsApi, self.cookie) as api:
            api.real_import_import_real_project_id_post(self.param.ProjectId, req)
        self.task.taskstate = "Done"
        self.UpdateProgress(100, "Processing done")

    def QuestionProcess(self):
        """ Called from tasking framework """
        txt = "<h1>Text File Importation Task</h1>"
        if self.task.taskstep == 0:
            return self._CreateDialogStep0()
        if self.task.taskstep == 1:
            return self._MappingDialogStep1()
        return PrintInCharte(txt)

    def ShowCustomDetails(self):
        # e.g. http://localhost:5001/Task/Show/40202?CustomDetails=Y
        # param.TaxoFound is rsp.found_taxa, so key=taxon name (seen in TSV), value=resolved ID
        node_ids = "+".join([str(x) for x in set(self.param.TaxoFound.values())])
        with ApiClient(TaxonomyTreeApi, request) as api:
            nodes: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=node_ids)
        nodes_dict = {a_node.id: a_node.name for a_node in nodes}
        # issue a line per resolved name
        txt = "<p><u>Used mapping, usable for next import</u></p>"
        for seen_name, resolved_id in self.param.TaxoFound.items():
            if resolved_id in nodes_dict:
                txt += "{0}={1}<br>".format(seen_name, nodes_dict[resolved_id])
        return PrintInCharte(txt)

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle ou auto
        prj_id = self.param.ProjectId
        time.sleep(1)
        # TODO: Remove the commented, but for now we have trace information inside
        # DoTaskClean(self.task.id)
        return "<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>" \
               "<a href='/Task/Create/TaskClassifAuto2?projid={0}' class='btn btn-primary btn-sm'" \
               "role=button>Go to Automatic Classification Screen</a> ".format(prj_id)

    def _notFoundTaxoInParam(self):
        return [k for k, v in self.param.TaxoFound.items() if v is None]

    def _notFoundUsersInParam(self):
        return [k for k, v in self.param.UserFound.items() if v.get('id') is None]
