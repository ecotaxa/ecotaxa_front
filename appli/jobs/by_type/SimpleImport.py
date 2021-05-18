# -*- coding: utf-8 -*-
import json
import time
from typing import Dict, List

from flask import render_template, redirect

from appli import PrintInCharte, gvg
from appli.jobs.Job import Job, load_from_json
from appli.tasks.importcommon import *
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import SimpleImportReq, SimpleImportRsp, ProjectModel, UserModel, TaxonModel, \
    JobModel


class SimpleImportJob(Job):
    """
        Simple Import, just GUI here, bulk of job subcontracted to back-end.
    """
    UI_NAME = "SimpleImport"

    PREFS_KEY = "img_import"

    @classmethod
    def initial_dialog(cls):
        """ In UI/flask, initial load, GET """
        prj_id = int(gvg("p"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                _target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")

        # Load previous values from user preferences
        with ApiClient(UsersApi, request) as api:
            preset_str = api.get_current_user_prefs_users_my_preferences_project_id_get(prj_id, cls.PREFS_KEY)
            preset = load_from_json(preset_str, dict)

        # Display the form, enrich it first
        # Example: preset = {"imgdate": "20150327", "imgtime": "1447",
        #                    "latitude": "-12.06398", "longitude": "-135.05325","depthmin": "50",
        #                    "depthmax": "70","userlb":8, "status":'V', "taxolb":25827}
        cls._lookup_names(preset)

        return PrintInCharte(render_template("jobs/simpleimport.html", preset=preset))

    @classmethod
    def create_or_update(cls):
        """ In UI/flask, submit/resubmit of initial page """
        prj_id = int(gvg("p"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                _target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")

        # Form Submit -> check and store values to use
        errors = []
        # Validate/store import file parameter
        file_to_load, file_error = Job.get_file_from_form(request)
        if file_error is not None:
            return file_error
        # Use backend to validate the form
        values = {}
        # fields have same names as in the API call...
        req = SimpleImportReq(source_path=file_to_load,
                              values=values)
        for fld in req.possible_values:
            a_val = gvp(fld)
            if a_val == "":
                continue
            values[fld] = a_val
        # dry run call for checking input
        with ApiClient(ProjectsApi, request) as api:
            rsp: SimpleImportRsp = api.simple_import_simple_import_project_id_post(project_id=prj_id,
                                                                                   simple_import_req=req,
                                                                                   dry_run=True)
        errors.extend(rsp.errors)
        # Check for errors. If any, stay in current state.
        if not flash_any_error(errors):
            # Save preferences
            with ApiClient(UsersApi, request) as api:
                val_to_write = json.dumps(values)
                api.set_current_user_prefs_users_my_preferences_project_id_put(prj_id, cls.PREFS_KEY, val_to_write)

            # Run for real
            with ApiClient(ProjectsApi, request) as api:
                rsp: SimpleImportRsp = api.simple_import_simple_import_project_id_post(project_id=prj_id,
                                                                                       simple_import_req=req,
                                                                                       dry_run=False)
                job_id = rsp.job_id
                return redirect("/Job/Monitor/%d" % job_id)

        # Display the form, enrich it first
        # Example preset: {"imgdate": "20150327", "imgtime": "1447",
        #                  "latitude": "-12.06398", "longitude": "-135.05325","depthmin": "50",
        #                  "depthmax": "70","userlb":8, "status":'V', "taxolb":25827}
        cls._lookup_names(values)

        return PrintInCharte(render_template("jobs/simpleimport.html",
                                             preset=values))

    @classmethod
    def _lookup_names(cls, form: Dict):
        """ Set the names for the form fields which take numerical IDs """
        if form.get('userlb') is not None:
            with ApiClient(UsersApi, request) as api:
                user: UserModel = api.get_user_users_user_id_get(user_id=int(form['userlb']))
            if user:
                form["annot_name"] = user.name
        if form.get('taxolb') is not None:
            with ApiClient(TaxonomyTreeApi, request) as api:
                nodes: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=form['taxolb'])
            if nodes:
                form["taxo_name"] = nodes[0].name

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        """ Called when finished """
        prj_id = job.params["prj_id"]
        obj_count = job.result["nb_images"]
        time.sleep(1)
        # DoTaskClean(self.task.id)
        return "Imported %s images successfully<br><a href='/prj/%s' class='btn btn-primary'>Go to project</a>" \
               % (obj_count, prj_id)
