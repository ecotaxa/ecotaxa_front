# -*- coding: utf-8 -*-
import time
from typing import Dict

from flask import render_template
from flask_login import current_user

from appli import database, PrintInCharte, gvg
from appli.tasks.importcommon import *
from appli.tasks.taskmanager import AsyncTask
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import SimpleImportReq, SimpleImportRsp, ProjectsApi


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
        prj_id = gvg("p")
        prj = database.Projects.query.filter_by(projid=prj_id).first()
        if not prj.CheckRight(1):
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
            FileToSave, FileToSaveFileName = get_file_from_form(self, errors)
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
            with ApiClient(ProjectsApi, self.cookie) as api:
                rsp: SimpleImportRsp = api.simple_import_simple_import_project_id_post(self.param.ProjectId, req)
            errors.extend(rsp.errors)
            # Check for errors. If any, stay in current state.
            if not flash_any_error(errors):
                # start Step1, in a subprocess as we're in UI process, reusing log files
                return self.StartTask(self.param, step=1, FileToSave=FileToSave, FileToSaveFileName=FileToSaveFileName)

        # Display the form, enrich it first
        # Example: preset = {"imgdate": "20150327", "imgtime": "1447",
        #                    "latitude": "-12.06398", "longitude": "-135.05325","depthmin": "50",
        #                    "depthmax": "70","userlb":8, "status":'V', "taxolb":25827}
        if 'userlb' in preset and preset['userlb'] is not None:
            usr = database.users.query.filter_by(id=preset['userlb']).first()
            if usr:
                preset["annot_name"] = usr.name
        if 'taxolb' in preset and preset['taxolb'] is not None:
            taxo = database.Taxonomy.query.filter_by(id=preset['taxolb']).first()
            if taxo:
                preset["taxo_name"] = taxo.name
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
