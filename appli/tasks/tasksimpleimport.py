# -*- coding: utf-8 -*-
import time
from typing import Dict, List

from flask import render_template
from flask_login import current_user

from appli import PrintInCharte, gvg
from appli.tasks.importcommon import *
from appli.tasks.taskmanager import AsyncTask
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import SimpleImportReq, SimpleImportRsp, ProjectsApi, ProjectModel, ApiException, \
    UsersApi, UserModel, TaxonomyTreeApi, TaxonModel


# noinspection DuplicatedCode
class TaskSimpleImport(AsyncTask):
    """
        Simple Import, just GUI here, bulk of job subcontracted to back-end.
    """
    SimpleImportPreset: Dict[str, Dict] = {}

    class Params(AsyncTask.Params):
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr is None:
                self.InData = 'My In Data'
                self.ProjectId = None
                # Common values for all images
                self.values = []
                # Errors displayed to user
                self.steperrors = []
                # Final result
                self.ObjectCount = ""

    def __init__(self, task=None):
        super().__init__(task)
        if task is None:
            self.param = self.Params()
        else:
            self.param = self.Params(task.inputparam)

    def _CreateDialogStep0(self):
        """ In UI/flask, task.taskstep = 0 AKA initial dialog """
        prj_id = int(gvg("p"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                _target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status == 403:
                    return PrintInCharte("ACCESS DENIED for this project")
        self.param.ProjectId = prj_id
        preset = self.SimpleImportPreset.setdefault(current_user.id, {})

        if gvp('starttask') != "Y":
            # First display
            pass
        else:
            # Form Submit -> check and store values to use
            errors = []
            # Validate/store import file parameter
            file_to_save, file_to_save_file_name = get_file_from_form(self, errors)
            # Use backend to validate the form
            values = {}
            self.param.values = values
            req = SimpleImportReq(task_id=0,
                                  source_path=self.param.InData,
                                  values=self.param.values)
            # fields have same id as in the API call
            for fld in req.possible_values:
                values[fld] = gvp(fld)
                if values[fld] == "":
                    values[fld] = None
                preset[fld] = values[fld]
            with ApiClient(ProjectsApi, request) as api:
                rsp: SimpleImportRsp = api.simple_import_simple_import_project_id_post(self.param.ProjectId, req)
            errors.extend(rsp.errors)
            # Check for errors. If any, stay in current state.
            if not flash_any_error(errors):
                # start Step1, in a subprocess as we're in UI process, reusing log files
                return self.StartTask(self.param, step=1,
                                      FileToSave=file_to_save,
                                      FileToSaveFileName=file_to_save_file_name)

        # Display the form, enrich it first
        # Example: preset = {"imgdate": "20150327", "imgtime": "1447",
        #                    "latitude": "-12.06398", "longitude": "-135.05325","depthmin": "50",
        #                    "depthmax": "70","userlb":8, "status":'V', "taxolb":25827}
        if 'userlb' in preset and preset['userlb'] is not None:
            with ApiClient(UsersApi, request) as api:
                user: UserModel = api.get_user_users_user_id_get(user_id=int(preset['userlb']))
            if user:
                preset["annot_name"] = user.name
        if 'taxolb' in preset and preset['taxolb'] is not None:
            with ApiClient(TaxonomyTreeApi, request) as api:
                nodes: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=preset['taxolb'])
            if nodes:
                preset["taxo_name"] = nodes[0].name
        return PrintInCharte(render_template("project/simpleimport.html", preset=preset))

    # noinspection PyPep8Naming
    def SPStep1(self):
        """ In subprocess, task.taskstep = 1 """
        self.UpdateProgress(0, "Waiting for backend")
        logging.info("Input Param = %s" % self.param.__dict__)
        # Back-end call
        req = SimpleImportReq(task_id=self.task.id,
                              source_path=self.param.InData,
                              values=self.param.values)
        with ApiClient(ProjectsApi, self.cookie) as api:
            rsp: SimpleImportRsp = api.simple_import_simple_import_project_id_post(self.param.ProjectId, req)

        if len(rsp.errors) != 0:
            msg = "Some errors were found during import"
            logging.error(msg + ":")
            for an_err in rsp.errors:
                logging.error(an_err)
            self.task.taskstate = "Error"
            self.task.progressmsg = msg
            self.param.steperrors = rsp.errors[:1000]
            self.UpdateParam()
        else:
            # Done
            self.param.ObjectCount = rsp.nb_images
            self.task.taskstate = "Done"
            self.UpdateProgress(100, "Import done")

    # noinspection PyPep8Naming
    def QuestionProcess(self):
        """ Called from tasking framework """
        txt = "<h1>Simple Import Task</h1>"
        if self.task.taskstep == 0:
            return self._CreateDialogStep0()
        return PrintInCharte(txt)

    # noinspection PyPep8Naming
    def GetDoneExtraAction(self):
        """ Called when done """
        prj_id = self.param.ProjectId
        obj_count = self.param.ObjectCount
        time.sleep(1)
        # DoTaskClean(self.task.id)
        return "Imported %s images successfully<br><a href='/prj/%s' class='btn btn-primary'>Go to project</a>" \
               % (obj_count, prj_id)
