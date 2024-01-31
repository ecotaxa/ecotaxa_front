# -*- coding: utf-8 -*-
from typing import ClassVar

from flask import request

from appli import gvp
from appli.gui.jobs.by_type.Export import ExportJob
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ObjectsApi
from to_back.ecotaxa_cli_py.models import (
    GeneralExportReq,
    ExportRsp,
)


class ExportBackupJob(ExportJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "GeneralExport"
    EXPORT_TYPE: ClassVar = "general"

    @classmethod
    def job_req(cls):
        projid = int(gvp("projid"))
        split_by = gvp("split_by")
        with_images = gvp("with_images")
        with_internal_ids = gvp("with_internal_ids") == '1'
        with_types_row = gvp("with_types_row") == '1'
        only_annotations = gvp("only_annotations") == '1'
        taxo_mapping = gvp("taxo_mapping")
        out_to_ftp = gvp("out_to_ftp") == '1'
        req = GeneralExportReq(
            project_id=projid,
            split_by=split_by,
            with_images=with_images,
            with_internal_ids=with_internal_ids,
            only_annotations=only_annotations,
            with_types_row=with_types_row,
            # taxo_mapping=taxo_mapping,
            out_to_ftp=out_to_ftp,
        )
        return req

    @classmethod
    def api_job_call(cls, export_req: GeneralExportReq) -> str:
        with ApiClient(ObjectsApi, request) as api:
            rsp: ExportRsp = api.export_object_set_general(export_req)
        return rsp
