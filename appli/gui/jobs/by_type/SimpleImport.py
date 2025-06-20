# -*- coding: utf-8 -*-
import json
from typing import Dict, List, Final, ClassVar

from flask import request, flash
from appli import gvp
from appli.gui.jobs.by_type.Import import ImportJob
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi, TaxonomyTreeApi
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.models import (
    SimpleImportReq,
    SimpleImportRsp,
    MinUserModel,
    TaxonModel,
)


class SimpleImportJob(ImportJob):
    """
    Simple Import, just GUI here, bulk of job subcontracted to back-end.
    """

    UI_NAME: ClassVar = "SimpleImport"
    IMPORT_TYPE: ClassVar = "simple"
    PREFS_KEY: Final = "img_import"

    @classmethod
    def job_req(cls) -> SimpleImportReq:
        file_to_load = gvp("file_to_load")
        # update_classification = cls._update_mode(gvp("updateclassif"))
        # taxo_map = json.loads(gvp("taxo_mapping", "{}"))
        req = SimpleImportReq(source_path=file_to_load, values={})
        for fld in req.possible_values:
            a_val = gvp(fld)
            if a_val == "":
                continue
            req.values[fld] = a_val

        # dry run call for checking input
        projid = int(gvp("projid"))
        with ApiClient(ProjectsApi, request) as api:
            rsp: SimpleImportRsp = api.simple_import(
                project_id=projid, simple_import_req=req, dry_run=True
            )
        errors = rsp.errors
        # Check for errors. If any, stay in current state.
        if not cls.flash_any_error(errors):
            # Save preferences
            with ApiClient(UsersApi, request) as api:
                val_to_write = json.dumps(req.values)
                api.set_current_user_prefs(projid, cls.PREFS_KEY, val_to_write)
        return req

    @classmethod
    def api_job_call(cls, import_req: SimpleImportReq) -> SimpleImportRsp:
        projid = int(gvp("projid"))
        with ApiClient(ProjectsApi, request) as api:
            rsp: SimpleImportRsp = api.simple_import(
                project_id=projid, simple_import_req=import_req, dry_run=False
            )
        return rsp

    @classmethod
    def _lookup_names(cls, form: Dict):
        """Set the names for the form fields which take numerical IDs"""
        if form.get("userlb") is not None:
            with ApiClient(UsersApi, request) as api:
                user: MinUserModel = api.get_user(user_id=int(form["userlb"]))
            if user:
                form["annot_name"] = user.name
        if form.get("taxolb") is not None:
            with ApiClient(TaxonomyTreeApi, request) as tapi:
                nodes: List[TaxonModel] = tapi.query_taxa_set(ids=form["taxolb"])
            if nodes:
                form["taxo_name"] = nodes[0].name
