# -*- coding: utf-8 -*-
from typing import ClassVar
from flask import render_template, redirect, request, flash, url_for
from appli import gvg, gvp
from appli.gui.jobs.staticlistes import py_messages
from appli.gui.jobs.Job import Job
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi
from to_back.ecotaxa_cli_py.models import (
    GeneralExportReq,
    ExportRsp,
    ProjectModel,
    JobModel,
)
from appli.gui.jobs.job_interface import export_format_options


class ExportJob(Job):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "GenExport"
    STEP0_TEMPLATE: ClassVar = "/v2/jobs/export.html"
    STEP1_TEMPLATE: ClassVar = "/v2/jobs/_final_download.html"
    EXPORT_TYPE: ClassVar = None

    @classmethod
    def initial_dialog(cls):
        """In UI/flask, initial load, GET"""
        projid = int(gvg("projid"))
        target_proj = cls.get_target_prj(projid)
        if target_proj == None:
            return render_template(cls.NOPROJ_TEMPLATE, projid=projid)

        filters = cls._extract_filters_from_url()
        formdatas, formoptions, export_links = export_format_options(cls.EXPORT_TYPE)
        if cls.EXPORT_TYPE == "summary" or cls.EXPORT_TYPE == None:
            from appli.gui.taxonomy.tools import project_used_taxa

            formoptions["summary"]["taxo_mapping"]["datas"] = project_used_taxa(projid)
        return render_template(
            cls.STEP0_TEMPLATE,
            export_type=cls.EXPORT_TYPE,
            formdatas=formdatas,
            formoptions=formoptions,
            filters=filters,
            export_links=export_links,
            target_proj=target_proj,
        )

    @classmethod
    def job_req(cls):
        """get post params and create api request object"""
        return None

    @classmethod
    def api_job_call(cls, export_req) -> str:
        """call api method depending on export type"""
        return ""

    @classmethod
    def create_or_update(cls):
        """In UI/flask, submit/resubmit of initial page, POST"""
        projid = int(gvp("projid"))
        target_proj = cls.get_target_prj(projid)
        errors = []
        filters = cls._extract_filters_from_form()
        req = cls.job_req()
        if len(errors) > 0 or cls.EXPORT_TYPE == None:
            for e in errors:
                flash(e, "error")

            formdatas, formoptions, export_links = export_format_options(
                cls.EXPORT_TYPE
            )
            formdatas[cls.EXPORT_TYPE].datas.options = req.__to_dict__
            return render_template(
                cls.STEP0_TEMPLATE,
                export_type=cls.EXPORT_TYPE,
                formdatas=formdatas,
                formoptions=formoptions,
                filters=filters,
                export_links=export_links,
                target_proj=target_proj,
            )
        else:
            export_req = {"filters": filters, "request": req}
            rsp = cls.api_job_call(export_req)
            return redirect(url_for("gui_job_show", job_id=rsp.job_id))

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        if job.state == "F":
            projid = job.params["req"]["project_id"]
            target_proj = cls.get_target_prj(projid)
            return render_template(
                cls.STEP1_TEMPLATE,
                jobid=job.id,
                projid=projid,
                outfile=job.result["out_file"],
                target_proj=target_proj,
            )
        else:
            return ""
