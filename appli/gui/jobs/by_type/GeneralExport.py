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
    GeneralExportReq,
    ExportRsp,
    ProjectModel,
    JobModel,
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
        with_internal_ids = bool(gvp("with_internal_ids"))
        with_types_row = bool(gvp("with_types_row"))
        only_annotations = bool(gvp("only_annotations"))
        taxo_mapping = gvp("taxo_mapping")
        out_to_ftp = bool(gvp("out_to_ftp"))
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
