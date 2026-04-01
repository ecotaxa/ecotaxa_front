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
from appli.gui.taxonomy.tools import posted_modified_recast


class ExportSummaryJob(ExportJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "SummaryExport"
    EXPORT_TYPE: ClassVar = "summary"
    RECAST_OPERATION: ClassVar = "project_export"

    @classmethod
    def job_req(cls):

        projid, collid = cls.get_target_id()
        quantity = gvp("quantity")
        summarise_by = gvp("summarise_by")
        formulae = gvp("formulae")
        out_to_ftp = gvp("out_to_ftp") == "1"
        modifiedrecast: bool = posted_modified_recast(False)
        if modifiedrecast:
            if collid > 0:
                is_collection = True
                target_id = collid
            else:
                is_collection = False
                target_id = projid
            cls.make_recast(target_id, is_collection)
        if formulae is None:
            formulae_dict = {}
        else:
            formulae_list = [
                a_line.strip().split(":") for a_line in formulae.splitlines()
            ]
            formulae_dict = {var.strip(): val.strip() for var, val in formulae_list}
        req = SummaryExportReq(
            collection_id=collid,
            project_id=projid,
            quantity=quantity,
            summarise_by=summarise_by,
            formulae=formulae_dict,
            out_to_ftp=out_to_ftp,
        )
        return req

    @classmethod
    def api_job_call(cls, export_req: SummaryExportReq) -> ExportRsp:
        with ApiClient(ObjectsApi, request) as api:
            rsp: ExportRsp = api.export_object_set_summary(export_req)
        return rsp
