# -*- coding: utf-8 -*-

from appli.jobs.by_type.Import import ImportJob


class ImportUpdateJob(ImportJob):
    """
        Import Update, just GUI here, bulk of job subcontracted to back-end.
    """
    UI_NAME = "ImportUpdate"

    # Variations over base class
    STEP0_TEMPLATE = "jobs/importupdate_create.html"

    @classmethod
    def _must_skip_existing_objects(cls) -> bool:
        """ Skip existing images, forced for update """
        # TODO: In this context, we should even check that they are present
        return True

    @classmethod
    def _update_mode(cls, ui_option: str) -> str:
        """ Update something, at least objects or objects+classifications """
        return "Cla" if ui_option == "Y" else "Yes"
