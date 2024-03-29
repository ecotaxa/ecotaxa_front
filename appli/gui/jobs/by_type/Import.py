# -*- coding: utf-8 -*-
import time
from pathlib import Path
from typing import List, ClassVar

from flask import render_template, redirect, request, flash, url_for

from appli import PrintInCharte, gvg, gvp, app
from appli.back_config import get_app_manager_mail
from appli.gui.jobs.Job import Job
from appli.gui.jobs.staticlistes import py_messages
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import (
    FilesApi,
    ProjectsApi,
    UsersApi,
    TaxonomyTreeApi,
    JobsApi,
)
from to_back.ecotaxa_cli_py.models import (
    ImportReq,
    ImportRsp,
    TaxonModel,
    ProjectModel,
    JobModel,
    DirectoryModel,
)


class ImportJob(Job):
    """
    Import, just GUI here, bulk of job subcontracted to back-end.
    Also serves as a base class for import update as pages are very similar.
    """

    UI_NAME: ClassVar = "FileImport"

    STEP0_TEMPLATE: ClassVar = "/v2/jobs/import.html"
    FINAL_TEMPLATE: ClassVar = "v2/jobs/_import_final.html"

    @classmethod
    def initial_dialog(cls) -> str:
        """In UI/flask, initial load, GET"""
        prj_id = int(gvg("p"))
        target_proj = cls.get_target_prj(prj_id, full=True)
        if target_proj == None:
            return render_template(cls.NOPROJ_TEMPLATE, projid=prj_id)
        # Get stored last server path value for this project, if any
        with ApiClient(UsersApi, request) as uapi:
            server_path = uapi.get_current_user_prefs(prj_id, "cwd")
        return render_template(
            cls.STEP0_TEMPLATE,
            ServerPath=server_path,
            TxtTaxoMap="",
            target_proj=dict(
                {"title": target_proj.title, "projid": target_proj.projid}
            ),
            prjmanagermail=target_proj.managers[0].email,
            appmanagermailto=get_app_manager_mail(request),
        )

    # TODO - add a class to receive a stream - big files upload - request.stream
    @classmethod
    def create_or_update(cls):
        """In UI/flask, submit/resubmit of initial page"""
        prj_id = int(gvg("p"))
        target_proj = cls.get_target_prj(prj_id)

        # Form Submit -> check and store values to use
        errors = []
        file_to_load = gvp("file_to_load", "")
        # Decode posted variables & load defaults from class
        skip_already_loaded_file = gvp("skiploaded") == "Y"
        skip_object_duplicate = (
            gvp("skipobjectduplicate") == "Y" or cls._must_skip_existing_objects()
        )
        # Import update parameter
        update_classification = cls._update_mode(gvp("updateclassif"))
        # Categories/taxonomy mapping
        str_taxo_mapping = gvp("TxtTaxoMap")
        taxo_map = cls._taxo_mapping_from_posted(str_taxo_mapping, errors)

        # Validate/store import file parameter
        # file_to_load, error = Job.get_file_from_stream(request)

        if file_to_load == "":
            file_to_load, error = Job.get_file_from_form(request)
            if error is not None:
                flash(py_messages["filetoloaderror"], "error")
                return error
        # Save preferences
        server_path = gvp("ServerPath")
        if server_path != "":
            with ApiClient(UsersApi, request) as api:
                # Compute directory to open next time, we pick the parent to avoid double import of the same
                # directory or zip.
                cwd = str(Path(server_path).parent)
                api.set_current_user_prefs(prj_id, "cwd", cwd)

        req = ImportReq(
            source_path=file_to_load,
            taxo_mappings=taxo_map,
            skip_loaded_files=skip_already_loaded_file,
            skip_existing_objects=skip_object_duplicate,
            update_mode=update_classification,
        )

        # second phase after upload to my_files - put follwing code elsewhere
        with ApiClient(ProjectsApi, request) as api:
            try:
                rsp: ImportRsp = api.import_file(prj_id, req)
            except ApiException as ae:
                if ae.status in (401, 403):
                    ae.reason = py_messages["access403"]

        if len(rsp.errors) > 0:
            for e in errors:
                flash(e, "error")
        else:
            # The task should be running
            job_id = rsp.job_id
            return redirect(url_for("gui_job_show", job_id=job_id))

        if server_path == "":
            # Get stored last value for this project
            with ApiClient(UsersApi, request) as api:
                server_path = api.get_current_user_prefs(prj_id, "cwd")
        return render_template(
            cls.STEP0_TEMPLATE,
            header="",
            data=req,
            ServerPath=server_path,
            TxtTaxoMap=str_taxo_mapping,
            target_proj=target_proj,
        )

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
        prj_id = job.params["prj_id"]
        target_proj = cls.get_target_prj(prj_id)

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

    #################################################################################################

    def ShowCustomDetails(self):
        # e.g. http://localhost:5001/Task/Show/40202?CustomDetails=Y
        # param.TaxoFound is rsp.found_taxa, so key=taxon name (seen in TSV), value=resolved ID
        node_ids = "+".join([str(x) for x in set(self.param.TaxoFound.values())])
        with ApiClient(TaxonomyTreeApi, request) as api:
            nodes: List[TaxonModel] = api.query_taxa_set(ids=node_ids)
        nodes_dict = {a_node.id: a_node.name for a_node in nodes}
        # issue a line per resolved name
        txt = "<p><u>Used mapping, usable for next import</u></p>"
        for seen_name, resolved_id in self.param.TaxoFound.items():
            if resolved_id in nodes_dict:
                txt += "{0}={1}<br>".format(seen_name, nodes_dict[resolved_id])
        return PrintInCharte(txt)

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
