# -*- coding: utf-8 -*-
from typing import ClassVar
from flask import render_template, redirect, request, flash, url_for
from appli import gvg, gvp
from appli.gui.jobs.staticlistes import py_messages
from appli.gui.jobs.by_type.Export import ExportJob
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi
from to_back.ecotaxa_cli_py.models import (
    BackupExportReq,
    ExportRsp,
    ProjectModel,
    JobModel,
)


class ExportBackupJob(ExportJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "BackupExport"
    EXPORT_TYPE: ClassVar = "backup"

    @classmethod
    def job_req(cls):
        projid = int(gvp("projid"))
        out_to_ftp = bool(gvp("out_to_ftp"))
        req = BackupExportReq(
            project_id=projid,
            out_to_ftp=out_to_ftp,
        )
        return req

    @classmethod
    def api_job_call(cls, export_req: BackupExportReq) -> str:
        with ApiClient(ObjectsApi, request) as api:
            rsp: ExportRsp = api.export_object_set_backup(export_req)
        return rsp
