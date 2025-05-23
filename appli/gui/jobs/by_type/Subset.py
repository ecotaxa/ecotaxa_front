# -*- coding: utf-8 -*-
import datetime
import time
from typing import ClassVar
from flask import render_template, redirect, request, flash, url_for
from appli import gvp
from appli.gui.jobs.Job import Job
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi
from to_back.ecotaxa_cli_py.models import (
    CreateProjectReq,
    SubsetReq,
    SubsetRsp,
    JobModel,
)


class SubsetJob(Job):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME = "Subset"
    STEP0_TEMPLATE: ClassVar = "/v2/jobs/subset_create.html"
    STEP1_TEMPLATE: ClassVar = "/v2/jobs/_subset_final.html"

    @classmethod
    def initial_dialog(cls):
        """In UI/flask, initial load, GET"""
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid, collid)
        if target_proj is None:
            return render_template(cls.NOOBJ_TEMPLATE, projid=projid)
        filters = cls._extract_filters_from_url()

        formdata = {
            "subsetprojecttitle": (
                target_proj["title"]
                + " - Subset created on "
                + (datetime.date.today().strftime("%Y-%m-%d"))
            )[0:255],
            "grptype": "C",
            "valtype": "P",
            "vvaleur": "",
            "pvaleur": "10",
        }

        return render_template(
            cls.STEP0_TEMPLATE,
            form=formdata,
            target_obj=target_proj,
            targetid=projid,
            filters=filters,
        )

    @classmethod
    def create_or_update(cls):
        """In UI/flask, submit/resubmit, POST"""
        projid, collid = cls.get_target_id()
        target_proj = cls.get_target_obj(projid, collid)
        subsetprojecttitle = gvp("subsetprojecttitle")
        valtype = gvp("valtype")
        vvaleur = gvp("vvaleur")
        pvaleur = gvp("pvaleur")
        grptype = gvp("grptype")
        errors = []
        valeur = ""
        # Check data validity
        if len(subsetprojecttitle) < 5:
            errors.append("Project name too short")
        if valtype == "V":
            try:
                valeur = int(vvaleur)
                if valeur <= 0:
                    errors.append("Absolute value not in range (>0)")
            except ValueError:
                errors.append("Invalid absolute value")
        elif valtype == "P":
            try:
                valeur = int(pvaleur)
                if valeur <= 0 or valeur > 100:
                    errors.append("% value not in range (]0, 100])")
            except ValueError:
                errors.append("Invalid % value")
        else:
            errors.append(
                "You must select the object selection parameter '% of values' or '# of objects'"
            )
        filters = cls._extract_filters_from_form()

        if len(errors) > 0:
            for e in errors:
                flash(e, "error")
            formdata = {
                "subsetprojecttitle": subsetprojecttitle,
                "grptype": grptype,
                "valtype": valtype,
                "vvaleur": vvaleur if valtype == "V" else "",
                "pvaleur": pvaleur if valtype == "P" else "",
            }
            return render_template(
                cls.STEP0_TEMPLATE,
                form=formdata,
                target_obj=target_proj,
                targetid=projid,
                filters=filters,
            )
        else:
            # Create the destination project
            with ApiClient(ProjectsApi, request) as api:
                req = CreateProjectReq(
                    clone_of_id=projid, title=subsetprojecttitle, access="0"
                )
                # TODO: The new project has status ANNOTATE. Is it important?
                new_prj_id: int = api.create_project(req)
            # Do the cloning
            with ApiClient(ProjectsApi, request) as api:
                req = SubsetReq(
                    filters=filters,
                    dest_prj_id=new_prj_id,
                    group_type=grptype,
                    limit_type=valtype,
                    limit_value=valeur,
                )
                rsp: SubsetRsp = api.project_subset(project_id=projid, subset_req=req)
            return redirect(url_for("gui_job_show", job_id=rsp.job_id))

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        projid = job.params["prj_id"]
        subsetprojid = job.params["req"]["dest_prj_id"]
        time.sleep(1)
        # DoTaskClean(self.task.id)
        return render_template(
            cls.STEP1_TEMPLATE, projid=projid, subsetprojid=subsetprojid
        )
