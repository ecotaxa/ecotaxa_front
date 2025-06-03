# -*- coding: utf-8 -*-
import json
from typing import ClassVar
from appli import gvp
from appli.gui.jobs.by_type.Import import ImportJob
from to_back.ecotaxa_cli_py.models import ImportReq


class UpdateImportJob(ImportJob):
    """
    Import Update, just GUI here, bulk of job subcontracted to back-end.
    """

    UI_NAME: ClassVar = "UpdateImport"
    IMPORT_TYPE: ClassVar = "update"

    @classmethod
    def job_req(cls) -> ImportReq:
        file_to_load = gvp("file_to_load")
        update_classification = cls._update_mode(gvp("updateclassif"))
        taxo_map = json.loads(gvp("taxo_mapping", "{}"))
        req = ImportReq(
            source_path=file_to_load,
            taxo_mappings=taxo_map,
            skip_existing_objects=cls._must_skip_existing_objects(),
            update_mode=update_classification,
        )
        return req

    @classmethod
    def _must_skip_existing_objects(cls) -> bool:
        """Skip existing images, forced for update"""
        # TODO: In this context, we should even check that they are present
        return True

    @classmethod
    def _update_mode(cls, ui_option: str) -> str:
        """Update something, at least objects or objects+classifications"""
        return "Cla" if ui_option == "Y" else "Yes"
