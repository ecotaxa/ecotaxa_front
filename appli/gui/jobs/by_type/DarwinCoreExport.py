# -*- coding: utf-8 -*-
from typing import ClassVar, Dict, List, Union, Optional
from flask import request
from appli import gvp, gvpm
from appli.gui.jobs.by_type.Export import ExportJob
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import CollectionsApi
from to_back.ecotaxa_cli_py.models import DarwinCoreExportReq, ExportRsp, TaxoRecastRsp
from appli.gui.taxonomy.tools import posted_dwca_taxo_recast, update_taxo_recast
from appli.back_config import get_back_constants


class ExportDarwinCoreJob(ExportJob):
    """
    DarwinCore Export, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "DarwinCoreExport"
    EXPORT_TYPE: ClassVar = "darwincore"
    TARGET_TYPE: ClassVar = "collection"
    EXPORT_OPERATION: ClassVar = "dwca_export_emof"

    @classmethod
    def job_req(cls):
        import json

        projid, collection_id = cls.get_target_id()
        dry_run = gvp("dry_run") == "1"
        include_predicted = gvp("include_predicted") == "1"
        with_absent = gvp("with_types_row") == "1"
        with_computations = gvpm("with_computations" or [])
        formulae = gvp("formulae" or "")
        formulae_list = [a_line.strip().split(":") for a_line in formulae.splitlines()]
        formulae_dict = {var.strip(): val.strip() for var, val in formulae_list}
        extra_xml = gvp("extra_xml" or "")
        # taxo_recast
        recast: Dict[str, TaxoRecastRsp] = posted_dwca_taxo_recast()
        recast_operation = get_back_constants("RECAST_OPERATION")
        if len(recast["occurrence"].from_to.keys()):
            update_taxo_recast(
                target_id=collection_id,
                taxonomy_recast=recast["occurrence"],
                operation=recast_operation["dwca_export_occurrence"],
                is_collection=True,
            )
        if len(recast["emof"].from_to.keys()):
            update_taxo_recast(
                target_id=collection_id,
                taxonomy_recast=recast["emof"],
                operation=recast_operation["dwca_export_emof"],
                is_collection=True,
            )
        if extra_xml == "":
            extra_xml = []
        req = DarwinCoreExportReq(
            collection_id=collection_id,
            dry_run=dry_run,
            include_predicted=include_predicted,
            with_absent=with_absent,
            with_computations=with_computations,
            formulae=formulae_dict,
            extra_xml=extra_xml,
        )
        return req

    @classmethod
    def api_job_call(
        cls, export_req: Dict[str, Union[List, DarwinCoreExportReq]]
    ) -> str:
        with ApiClient(CollectionsApi, request) as api:
            rsp: ExportRsp = api.darwin_core_format_export(export_req["request"])
        return rsp
