# -*- coding: utf-8 -*-
from typing import ClassVar

from flask import request

from appli import gvp
from appli.gui.jobs.by_type.Export import ExportJob
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ObjectsApi
from to_back.ecotaxa_cli_py.models import (
    BackupExportReq,
    ExportRsp,
)


class ExportBackupJob(ExportJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "BackupExport"
    EXPORT_TYPE: ClassVar = "backup"

    @classmethod
    def job_req(cls):
        projid, collid = cls.get_target_id()
        out_to_ftp = gvp("out_to_ftp") == "1"
        req = BackupExportReq(
            collection_id=collid,
            project_id=projid,
            out_to_ftp=out_to_ftp,
        )
        return req

    @classmethod
    def api_job_call(cls, export_req: BackupExportReq) -> ExportRsp:
        with ApiClient(ObjectsApi, request) as api:
            rsp: ExportRsp = api.export_object_set_backup(export_req)
        return rsp
