# -*- coding: utf-8 -*-
import time
from typing import List

from flask import render_template, g, redirect

from appli import PrintInCharte, gvg
from appli.constants import get_app_manager_mail
from appli.jobs.Job import Job
from appli.tasks.importcommon import *
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ImportReq, ImportRsp, ProjectsApi, UsersApi, ApiException, \
    TaxonomyTreeApi, TaxonModel, ProjectModel, JobModel, JobsApi


class ImportJob(Job):
    """
        Import, just GUI here, bulk of job subcontracted to back-end.
        Also serves as a base class for import update as pages are very similar.
    """
    UI_NAME = "FileImport"

    STEP0_TEMPLATE = "jobs/import_create.html"

    @classmethod
    def initial_dialog(cls):
        """ In UI/flask, initial load, GET """
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
        g.appmanagermailto = get_app_manager_mail(request)
        # Get stored last server path value for this project, if any
        with ApiClient(UsersApi, request) as api:
            server_path = api.get_current_user_prefs_users_my_preferences_project_id_get(prj_id,
                                                                                         "cwd")
        return render_template(cls.STEP0_TEMPLATE, header="",
                               ServerPath=server_path,
                               TxtTaxoMap="")

    @classmethod
    def create_or_update(cls):
        """ In UI/flask, submit/resubmit of initial page """
        prj_id = int(gvg("p"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")
                else:
                    raise
        # Feed global template values
        g.prjtitle = target_prj.title
        g.prjprojid = target_prj.projid
        g.prjmanagermailto = target_prj.managers[0].email
        g.appmanagermailto = get_app_manager_mail(request)

        # Form Submit -> check and store values to use
        errors = []

        # Decode posted variables & load defaults from class
        skip_already_loaded_file = gvp("skiploaded") == "Y"
        skip_object_duplicate = gvp("skipobjectduplicate") == 'Y' or cls._must_skip_existing_objects()
        # Import update parameter
        update_classification = cls._update_mode(gvp("updateclassif"))
        # Categories/taxonomy mapping
        str_taxo_mapping = gvp('TxtTaxoMap')
        taxo_map = cls._taxo_mapping_from_posted(str_taxo_mapping, errors)

        # Validate/store import file parameter
        file_to_load, error = Job.get_file_from_form(request)
        if error is not None:
            return error
        # Save preferences
        server_path = gvp("ServerPath")
        if server_path != "":
            with ApiClient(UsersApi, request) as api:
                # Compute directory to open next time, we pick the parent to avoid double import of the same
                # directory or zip.
                cwd = str(Path(server_path).parent)
                api.set_current_user_prefs_users_my_preferences_project_id_put(prj_id, "cwd", cwd)

        req = ImportReq(source_path=file_to_load,
                        taxo_mappings=taxo_map,
                        skip_loaded_files=skip_already_loaded_file,
                        skip_existing_objects=skip_object_duplicate,
                        update_mode=update_classification)

        with ApiClient(ProjectsApi, request) as api:
            try:
                rsp: ImportRsp = api.import_file_file_import_project_id_post(prj_id, req)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("Not enough permission for importing into this project")
                else:
                    raise

        if len(rsp.errors) > 0:
            for e in errors:
                flash(e, "error")
        else:
            # The task should be running
            job_id = rsp.job_id
            return redirect("/Job/Monitor/%d" % job_id)

        if server_path == "":
            # Get stored last value for this project
            with ApiClient(UsersApi, request) as api:
                server_path = api.get_current_user_prefs_users_my_preferences_project_id_get(prj_id,
                                                                                             "cwd")
        return render_template(cls.STEP0_TEMPLATE, header="",
                               data=req, ServerPath=server_path,
                               TxtTaxoMap=str_taxo_mapping)

    @classmethod
    def _taxo_mapping_from_posted(cls, mapping_str, errors):
        taxo_map = {}
        for lig in mapping_str.splitlines():
            ls = lig.split('=', 1)
            if len(ls) != 2:
                errors.append("Taxonomy Mapping : Invalid format for line %s" % lig)
            else:
                taxo_map[ls[0].strip().lower()] = ls[1].strip().lower()
        return taxo_map

    @classmethod
    def initial_question_dialog(cls, job: JobModel):
        """ The back-end need some data for proceeding """
        txt = "<h1>Text File Importation Task</h1>"
        prj_id = job.params["prj_id"]
        with ApiClient(ProjectsApi, request) as api:
            target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
        # Feed global template values
        g.prjtitle = target_prj.title
        g.prjprojid = target_prj.projid
        # Feed local values
        not_found_taxo = job.question["missing_taxa"]
        not_found_users = job.question["missing_users"]
        return render_template('jobs/import_question1.html',
                               header=txt, taxo=not_found_taxo, users=not_found_users,
                               job=job)

    @classmethod
    def treat_question_reply(cls, job: JobModel):
        """ Relay user answers (to questions) to back-end """
        not_found_taxo = job.question["missing_taxa"]
        not_found_users = job.question["missing_users"]

        app.logger.info("Form Data = %s", request.form)
        categs = {}
        for i in range(1, 1 + len(not_found_taxo)):
            orig = gvp("orig%d" % i)  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
            newvalue = gvp("taxolb%d" % i)
            if orig in not_found_taxo and newvalue != "":
                categs[orig] = newvalue
        users = {}
        for i in range(1, 1 + len(not_found_users)):
            orig = gvp("origuser%d" % i)  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
            newvalue = gvp("userlb%d" % i)
            if orig in not_found_users and newvalue != "":
                users[orig] = newvalue
        answers = {"users": users,
                   "taxa": categs}
        with ApiClient(JobsApi, request) as api:
            try:
                api.reply_job_question_jobs_job_id_answer_post(job_id=job.id, body=answers)
            except ApiException as ae:
                flash_any_error([str(ae)])
                return render_template('jobs/import_question1.html',
                                       header="", taxo=not_found_taxo, users=not_found_users,
                                       job=job)
        return redirect("/Job/Monitor/%d" % job.id)

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
            nodes: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=node_ids)
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
        prj_id = job.params["prj_id"]
        time.sleep(1)
        # TODO: Remove the commented, but for now we have trace information inside
        # DoTaskClean(self.task.id)
        return "<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>" \
               "<a href='/Task/Create/TaskClassifAuto2?projid={0}' class='btn btn-primary btn-sm'" \
               "role=button>Go to Automatic Classification Screen</a> ".format(prj_id)
