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
    Export, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "GenExport"
    STEP0_TEMPLATE: ClassVar = "/v2/jobs/export.html"
    FINAL_TEMPLATE: ClassVar = "/v2/jobs/_final_download.html"
    EXPORT_TYPE: ClassVar = None

    @classmethod
    def initial_dialog(cls):
        """In UI/flask, initial load, GET"""
        idname = "projid"
        projid, collection_id = cls.get_target_id()
        target_obj = cls.get_target_obj(projid, collection_id)
        if collection_id != 0:
            targetid = collection_id
            cls.TARGET_TYPE = "collection"
        else:
            targetid = projid
        if target_obj == None:
            return render_template(
                cls.NOOBJ_TEMPLATE, id=targetid, target_type=cls.TARGET_TYPE
            )

        filters = cls._extract_filters_from_url()
        # always return every export possibilities
        formdatas, formoptions, export_links = export_format_options(
            target=cls.TARGET_TYPE
        )
        # if cls.EXPORT_TYPE == "summary" or cls.EXPORT_TYPE == None:
        from appli.gui.taxonomy.tools import project_used_taxa

        if cls.TARGET_TYPE == "collection":
            idname = "collection_id"
            if cls.EXPORT_TYPE in ["summary", "darwincore"]:
                taxalist = formoptions[cls.EXPORT_TYPE]["taxo_mapping"]
                if "datas" not in taxalist:
                    taxalist["datas"] = {}
                for projid in target_obj.project_ids:
                    taxalist.update(project_used_taxa(projid))
        elif cls.EXPORT_TYPE == "summary":
            formoptions[cls.EXPORT_TYPE]["taxo_mapping"]["datas"] = project_used_taxa(
                projid
            )
        # hack to have 3 types instead of one page by job export type
        return render_template(
            cls.STEP0_TEMPLATE,
            export_type=cls.EXPORT_TYPE,
            formdatas=formdatas,
            formoptions=formoptions,
            filters=filters,
            export_links=export_links,
            projid=projid,
            collection_id=collection_id,
            idname=idname,
            target_type=cls.TARGET_TYPE,
            target_obj=target_obj,
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
        projid, collid = cls.get_target_id()
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
                collection_id=collid,
                projid=projid,
            )
        else:
            export_req = {"filters": filters, "request": req}
            rsp = cls.api_job_call(export_req)
            return redirect(url_for("gui_job_show", job_id=rsp.job_id))

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        if "req" in job.params:
            req = job.params["req"]
        else:
            req = job.params
        if job.state == "F":
            if "collection_id" in req:
                collid = req["collection_id"]
            else:
                collid = 0
            if "project_id" in req:
                projid = req["project_id"]
            else:
                projid = None
            return render_template(
                cls.FINAL_TEMPLATE,
                jobid=job.id,
                outfile=job.result["out_file"],
                projid=projid,
                collection_id=collid,
                target_type=cls.TARGET_TYPE,
            )
        else:
            return ""
