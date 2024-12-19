# -*- coding: utf-8 -*-
from typing import ClassVar

from flask import request

from appli import gvp
from appli.gui.jobs.by_type.Export import ExportJob
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ObjectsApi
from to_back.ecotaxa_cli_py.models import (
    SummaryExportReq,
    ExportRsp,
)


class ExportSummaryJob(ExportJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "SummaryExport"
    EXPORT_TYPE: ClassVar = "summary"

    @classmethod
    def job_req(cls):
        import json

        projid, collid = cls.get_target_id()
        quantity = gvp("quantity")
        summarise_by = gvp("summarise_by")
        taxo_mapping = json.loads(gvp("taxo_mapping", "{}"))
        formulae = gvp("formulae")
        out_to_ftp = gvp("out_to_ftp") == "1"
        formulae_list = [a_line.strip().split(":") for a_line in formulae.splitlines()]
        formulae_dict = {var.strip(): val.strip() for var, val in formulae_list}
        req = SummaryExportReq(
            collection_id=collid,
            project_id=projid,
            quantity=quantity,
            summarise_by=summarise_by,
            taxo_mapping=taxo_mapping,
            formulae=formulae_dict,
            out_to_ftp=out_to_ftp,
        )
        return req

    @classmethod
    def api_job_call(cls, export_req: SummaryExportReq) -> str:
        with ApiClient(ObjectsApi, request) as api:
            rsp: ExportRsp = api.export_object_set_summary(export_req)
        return rsp
