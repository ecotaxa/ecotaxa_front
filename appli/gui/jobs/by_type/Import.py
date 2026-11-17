# -*- coding: utf-8 -*-
import time
from pathlib import Path
from typing import ClassVar, Optional, Union, Any
from flask import render_template, redirect, request, url_for, g, flash
from appli import gvp, gvpm, app
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
    TaxoRecastRsp,
    SimpleImportReq,
)
from appli.gui.jobs.job_interface import import_format_options
from appli.back_config import get_back_constants
from appli.gui.taxonomy.tools import update_taxo_recast, get_taxo_recast
from flask_babel import _
from markupsafe import escape


class ImportJob(Job):
    """
    Import, just GUI here, bulk of job subcontracted to back-end.
    Also serves as a base class for import update as pages are very similar.
    """

    UI_NAME: ClassVar = "FileImport"

    STEP0_TEMPLATE: ClassVar = "/v2/jobs/import.html"
    FINAL_TEMPLATE: ClassVar = "/v2/jobs/_import_final.html"
    TAXO_TEMPLATE: ClassVar = "/v2/jobs/_import_question.html"
    IMPORT_TYPE: ClassVar[Optional[str]] = None
    ACTION = "import"

    @classmethod
    def initial_dialog(cls) -> str:
        """In UI/flask, initial load, GET"""
        projid, _collid = cls.get_target_id()
        target_proj = cls.get_target_obj(int(projid))
        if target_proj is None:
            return render_template(cls.NOOBJ_TEMPLATE, projid=projid)
        # Get stored last server path value for this project, if any
        with ApiClient(UsersApi, request) as uapi:
            _unused = uapi.get_current_user_prefs(int(projid), "cwd")
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
                        "label": _("Import from my files"),
                        "help": "help_import_myfiles",
                        "open":True
                    }
                ),
                dict(
                    {
                        "name": "server",
                        "label": _("Import from a folder or zip file on the server"),
                        "help": "help_import_server",
                        "data": " data-import=commonserver data-selectunder=Ecotaxa_Data_to_import  data-url=gui/common/ServerFolderSelectJSON data-where=import-server data-tree=commonserver data-target=unique",
                    }
                ),
            ],
            action=cls.ACTION,
        )

    @classmethod
    def job_req(cls) -> Optional[Union[ImportReq, SimpleImportReq]]:
        """get post params and create api request object"""
        return None

    @classmethod
    def api_job_call(cls, req: Any):
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
        projid, _collid = cls.get_target_id()
        target_proj = cls.get_target_obj(int(projid))
        # Save preferences
        server_path = gvp("ServerPath")

        if server_path != "":
            with ApiClient(UsersApi, request) as api:
                # Compute directory to open next time, we pick the parent to avoid double import of the same
                # directory or zip.
                cwd = str(Path(server_path).parent)
                api.set_current_user_prefs(int(projid), "cwd", cwd)
        # Several entries picked in My Files: gathered into one folder for the job
        staged = None
        entries = gvpm("entries")
        if entries:
            from appli.gui.files.tools import stage_import_sources

            ret = stage_import_sources(int(projid), entries)
            if "error" in ret:
                flash(_("Unable to prepare the selected files/directories for import."), "error")
            else:
                staged = g.import_staged = ret["source_path"]
        if staged is not None or not entries:
            rsp = None
            try:
                req = cls.job_req()
                if req is not None:
                    rsp = cls.api_job_call(req)
            finally:
                if rsp is None and staged is not None:
                    cls._restore(int(projid), staged)
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
    def _source_path(cls) -> str:
        """The folder the selected entries were staged into, else the posted one"""
        return g.get("import_staged") or gvp("file_to_load")

    @staticmethod
    def _restore(projid: int, source_path: str) -> str:
        """Put back staged entries. Return HTML telling it, or '' if nothing to do."""
        from appli.gui.files.tools import restore_import_sources

        kept = restore_import_sources(projid, source_path)
        if kept is None:
            return ""
        if not kept:
            msg = _("The selected files/directories are back in their place in My Files.")
            return '<div class="alert is-info">%s</div>' % msg
        msg = _("Could not put back in their place, kept in %s:") % escape(source_path)
        items = "".join("<li>%s</li>" % escape(an_item["original"]) for an_item in kept)
        return '<div class="alert warning">%s<ul>%s</ul></div>' % (msg, items)

    @classmethod
    def on_failure(cls, job: JobModel) -> str:
        if job.state != "E":
            return ""
        return cls._restore(job.params["prj_id"], job.params["req"]["source_path"])

    @classmethod
    def on_erase(cls, job: JobModel) -> None:
        from appli.gui.files.tools import forget_staged_import

        projid, source_path = job.params["prj_id"], job.params["req"]["source_path"]
        if job.state in ("E", "A"):  # Failed or abandoned at the question
            cls._restore(projid, source_path)
        forget_staged_import(projid, source_path)

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
        params: dict = job.params
        projid = params["prj_id"]
        target_proj = cls.get_target_obj(int(projid))

        # Feed local values
        question: dict = job.question
        if "missing_taxa" in question.keys():
            not_found_taxo = question["missing_taxa"]
            recast_operation = get_back_constants("RECAST_OPERATION")
            operation = recast_operation["project_import"]
            recast = get_taxo_recast(
                target_id=projid, operation=operation, is_collection=False
            )
        else:
            recast = None
            not_found_taxo = []
        if "missing_users" in question.keys():
            not_found_users = question["missing_users"]
        else:
            not_found_users = []
        return render_template(
            cls.TAXO_TEMPLATE,
            taxo=not_found_taxo,
            recast=recast,
            users=not_found_users,
            job=job,
            target_proj=target_proj,
        )

    @classmethod
    def treat_question_reply(cls, job: JobModel):
        """Relay user answers (to questions) to back-end"""
        question: dict = job.question
        params: dict = job.params
        if "missing_taxa" in question.keys():
            not_found_taxo = question["missing_taxa"]
        else:
            not_found_taxo = []
        if "missisng_users" in question.keys():
            not_found_users = question["missing_users"]
        else:
            not_found_users = []
        app.logger.info("Form Data = %s", request.form)
        categs = {}
        for i in range(1, 1 + len(not_found_taxo)):
            orig = gvp(
                "item-taxo-%d" % i
            )  # Le nom original est dans item-taxo-XX et la nouvelle valeur dans item-replace-XX
            newvalue = gvp("item-replace-%d" % i)
            if orig in not_found_taxo and newvalue != "":
                categs[orig] = newvalue
        users = {}
        for i in range(1, 1 + len(not_found_users)):
            orig = gvp(
                "origuser%d" % i
            )  # Le nom original est dans origXX et la nouvelle valeur dans user-replace-XX
            newvalue = gvp("user-replace-%d" % i)
            if orig in not_found_users and newvalue != "":
                users[orig] = newvalue
        answers = {"users": users, "taxa": categs}
        if len(answers["taxa"].values()):
            cls.make_recast(params["prj_id"], answers["taxa"])
        with ApiClient(JobsApi, request) as api:
            try:
                api.reply_job_question(job_id=job.id, body=answers)
            except ApiException as ae:
                cls.flash_any_error([str(ae)])
                return render_template(
                    cls.TAXO_TEMPLATE,
                    header="",
                    taxo=not_found_taxo,
                    users=not_found_users,
                    replace=answers,
                    job=job,
                )
        return redirect(url_for("gui_job_show", job_id=job.id))

    @classmethod
    def make_recast(cls, target_id: int, values: dict):
        newrecast = TaxoRecastRsp(from_to=values, doc={})
        recast_operation = get_back_constants("RECAST_OPERATION")
        operation = recast_operation["project_import"]
        recast = get_taxo_recast(
            target_id=target_id, operation=operation, is_collection=False
        )
        if recast is None:
            recast=newrecast
        else:
            recast.from_to.update(newrecast.from_to)
            recast.doc.update(newrecast.doc)
        recasts = {operation: recast}
        for operation, recast in recasts.items():
            update_taxo_recast(
                target_id=target_id,
                taxonomy_recast=recast,
                operation=operation,
                is_collection=False,
            )

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
            projid = job.params["prj_id"]
            source_path = job.params["req"]["source_path"]
            from appli.gui.files.tools import get_staged_import_manifest

            return render_template(
                cls.FINAL_TEMPLATE,
                jobid=job.id,
                source_path=source_path,
                original_sources=get_staged_import_manifest(projid, source_path),
                projid=projid,
            )
        else:
            return ""
