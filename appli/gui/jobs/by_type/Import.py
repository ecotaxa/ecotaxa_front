# -*- coding: utf-8 -*-
import time
from pathlib import Path
from typing import ClassVar
from flask import render_template, redirect, request, url_for
from appli import gvp, app
from appli.gui.jobs.Job import Job
from appli.gui.jobs.staticlistes import py_messages
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import (
    ProjectsApi,
    UsersApi,
    JobsApi,
)
from to_back.ecotaxa_cli_py.models import (
    ImportReq,
    ImportRsp,
    JobModel,
)
from appli.gui.jobs.job_interface import import_format_options
from flask_babel import _



class ImportJob(Job):
    """
    Import, just GUI here, bulk of job subcontracted to back-end.
    Also serves as a base class for import update as pages are very similar.
    """

    UI_NAME: ClassVar = "FileImport"

    STEP0_TEMPLATE: ClassVar = "/v2/jobs/import.html"
    FINAL_TEMPLATE: ClassVar = "v2/jobs/_import_final.html"
    IMPORT_TYPE: ClassVar = None
    ACTION = "import"

    @classmethod
    def initial_dialog(cls) -> str:
        """In UI/flask, initial load, GET"""
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid)
        if target_proj is None:
            return render_template(cls.NOOBJ_TEMPLATE, projid=projid)
        # Get stored last server path value for this project, if any
        with ApiClient(UsersApi, request) as uapi:
            _unused = uapi.get_current_user_prefs(projid, "cwd")
        formdatas, formoptions, import_links = import_format_options()
        return render_template(
            cls.STEP0_TEMPLATE,
            selected_type=cls.IMPORT_TYPE,
            formdatas=formdatas,
            formoptions=formoptions,
            action_links=import_links,
            target_proj=target_proj,
            sourcedata=[
                dict(
                    {
                        "name": "myfiles",
                        "label": _("Upload or select from my files"),
                        "help": "help_import_myfiles",
                    }
                ),
                dict(
                    {
                        "name": "server",
                        "label": _("Choose a folder or zip file on the server"),
                        "help": "help_import_server",
                        "data": " data-import=commonserver data-exclude=FTP,ftp_plankton,plankton,Ecotaxa_Data_to_import,Ecotaxa_Exported_data  data-url=gui/common/ServerFolderSelectJSON data-where=import-server data-tree=commonserver data-target=unique",
                    }
                ),
            ],
            action=cls.ACTION,
        )

    @classmethod
    def job_req(cls) -> ImportReq:
        """get post params and create api request object"""
        pass

    @classmethod
    def api_job_call(cls, req: ImportReq):
        # second phase after upload to my_files - put follwing code elsewhere
        projid = int(gvp("projid"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                rsp: ImportRsp = api.import_file(projid, import_req=req)
                return rsp
            except ApiException as ae:
                if ae.status in (401, 403):
                    ae.reason = py_messages["access403"]
        return None

    @classmethod
    def create_or_update(cls):
        """In UI/flask, submit/resubmit of initial page, POST"""
        projid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid)
        # Save preferences
        server_path = gvp("ServerPath")

        if server_path != "":
            with ApiClient(UsersApi, request) as api:
                # Compute directory to open next time, we pick the parent to avoid double import of the same
                # directory or zip.
                cwd = str(Path(server_path).parent)
                api.set_current_user_prefs(projid, "cwd", cwd)
        req = cls.job_req()
        if req is not None:
            rsp = cls.api_job_call(req)
            if rsp is not None:
                return redirect(url_for("gui_job_show", job_id=rsp.job_id))
        formdatas, formoptions, import_links = import_format_options(cls.IMPORT_TYPE)
        return render_template(
            cls.STEP0_TEMPLATE,
            selected_type=cls.IMPORT_TYPE,
            formdatas=formdatas,
            formoptions=formoptions,
            action_links=import_links,
            target_proj=target_proj,
            action=cls.ACTION,
        )

    @classmethod
    def _get_file_to_load(cls):
        errors = []
        file_to_load, error = Job.get_file_from_form(request)
        if error is not None:
            errors.append((py_messages["filetoloaderror"], "error"))
            return None, errors
        return file_to_load, errors

    @classmethod
    def _taxo_mapping_from_posted(cls, mapping_str, errors):
        taxo_map = {}
        for lig in mapping_str.splitlines():
            ls = lig.split("=", 1)
            if len(ls) != 2:
                errors.append("Taxonomy Mapping : Invalid format for line %s" % lig)
            else:
                taxo_map[ls[0].strip().lower()] = ls[1].strip().lower()
        return taxo_map

    @classmethod
    def initial_question_dialog(cls, job: JobModel):
        """The back-end need some data for proceeding"""
        txt = "<h1>Text File Importation Task</h1>"
        projid = job.params["prj_id"]
        target_proj = cls.get_target_obj(projid)

        # Feed local values
        not_found_taxo = job.question["missing_taxa"]
        not_found_users = job.question["missing_users"]

        return render_template(
            "v2/jobs/_import_question.html",
            header=txt,
            taxo=not_found_taxo,
            users=not_found_users,
            job=job,
            target_proj=target_proj,
        )

    @classmethod
    def treat_question_reply(cls, job: JobModel):
        """Relay user answers (to questions) to back-end"""
        not_found_taxo = job.question["missing_taxa"]
        not_found_users = job.question["missing_users"]

        app.logger.info("Form Data = %s", request.form)
        categs = {}
        for i in range(1, 1 + len(not_found_taxo)):
            orig = gvp(
                "orig%d" % i
            )  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
            newvalue = gvp("taxolb%d" % i)
            if orig in not_found_taxo and newvalue != "":
                categs[orig] = newvalue
        users = {}
        for i in range(1, 1 + len(not_found_users)):
            orig = gvp(
                "origuser%d" % i
            )  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
            newvalue = gvp("userlb%d" % i)
            if orig in not_found_users and newvalue != "":
                users[orig] = newvalue
        answers = {"users": users, "taxa": categs}
        with ApiClient(JobsApi, request) as api:
            try:
                api.reply_job_question(job_id=job.id, body=answers)
            except ApiException as ae:
                cls.flash_any_error([str(ae)])
                return render_template(
                    "v2/jobs/_import_question.html",
                    header="",
                    taxo=not_found_taxo,
                    users=not_found_users,
                    job=job,
                )
        return redirect(url_for("gui_job_show", job_id=job.id))

    @classmethod
    def _must_skip_existing_objects(cls) -> bool:
        return False

    @classmethod
    def _update_mode(cls, ui_option: str) -> str:
        return ""  # No update for plain import

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle ou auto
        if job.state == "F":
            time.sleep(1)
            return render_template(
                cls.FINAL_TEMPLATE,
                jobid=job.id,
                source_path=job.params["req"]["source_path"],
                projid=job.params["prj_id"],
            )
        else:
            return ""