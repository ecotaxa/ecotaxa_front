# -*- coding: utf-8 -*-
from typing import ClassVar
from flask import render_template, redirect, request, flash
from appli import gvg, gvp
from appli.gui.jobs.staticlistes import py_messages
from appli.gui.jobs.by_type.Export import ExportJob
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi, UsersApi
from to_back.ecotaxa_cli_py.models import (
    SummaryExportReq,
    ExportRsp,
    ProjectModel,
    JobModel,
)

from appli.back_config import get_app_manager_mail


class ExportSummaryJob(ExportJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "SummaryExport"
    EXPORT_TYPE: ClassVar = "summary"

    @classmethod
    def job_req(cls):
        projid = int(gvp("projid"))
        quantity = gvp("quantity")
        summarise_by = gvp("summarise_by")
        taxo_mapping = gvp("taxo_mapping")
        formulae = gvp("formulae")
        out_to_ftp = bool(gvp("out_to_ftp"))
        req = SummaryExportReq(
            project_id=projid,
            quantity=quantity,
            summarise_by=summarise_by,
            taxo_mapping=taxo_mapping,
            formulae=formulae,
        )
        return req

    @classmethod
    def api_job_call(cls, export_req: SummaryExportReq) -> str:
        with ApiClient(ObjectsApi, request) as api:
            rsp: ExportRsp = api.export_object_set_summary(export_req)
        return rsp
