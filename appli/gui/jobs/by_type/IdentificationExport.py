# -*- coding: utf-8 -*-
from typing import ClassVar

from flask import request

from appli import gvp
from appli.gui.jobs.by_type.GeneralExport import ExportGeneralJob
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ObjectsApi
from to_back.ecotaxa_cli_py.models import (
    GeneralExportReq,
    ExportRsp,
)


class ExportIdentificationJob(ExportGeneralJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "IdentificationExport"
    EXPORT_TYPE: ClassVar = "identification"

    @classmethod
    def job_req(cls):
        projid, collid = cls.get_target_id()
        only_annotations = True
        out_to_ftp = gvp("out_to_ftp") == "1"
        req = GeneralExportReq(
            collection_id=collid,
            project_id=projid,
            only_annotations=True,
            out_to_ftp=out_to_ftp,
        )
        return req

    @classmethod
    def api_job_call(cls, export_req: GeneralExportReq) -> str:
        with ApiClient(ObjectsApi, request) as api:
            rsp: ExportRsp = api.export_object_set_general(export_req)
        return rsp
