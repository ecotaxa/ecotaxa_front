# -*- coding: utf-8 -*-
import json
from typing import ClassVar
from appli import gvp
from appli.gui.jobs.by_type.Import import ImportJob
from to_back.ecotaxa_cli_py.models import ImportReq


class ImportGeneralJob(ImportJob):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME: ClassVar = "GeneralImport"
    IMPORT_TYPE: ClassVar = "general"

    @classmethod
    def job_req(cls) -> ImportReq:
        file_to_load = gvp("file_to_load")
        # Decode posted variables & load defaults from class
        skip_already_loaded_file = gvp("skiploaded") == "Y"
        skip_object_duplicate = (
            gvp("skipobjectduplicate") == "Y" or cls._must_skip_existing_objects()
        )

        # Categories/taxonomy mapping
        taxo_map = json.loads(gvp("taxo_mapping", "{}"))
        req = ImportReq(
            source_path=file_to_load,
            taxo_mappings=taxo_map,
            skip_loaded_files=skip_already_loaded_file,
            skip_existing_objects=skip_object_duplicate,
            update_mode="",
        )
        return req
