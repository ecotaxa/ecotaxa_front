# -*- coding: utf-8 -*-

from .taskimport2back import TaskImportToBack


class TaskImportUpdateToBack(TaskImportToBack):
    """
        Import Update, just GUI here, bulk of job subcontracted to back-end.
    """
    # Variations over base class
    STEP0_TEMPLATE = "task/importupdate_create.html"

    def __init__(self, task=None):
        super().__init__(task)

    def _must_skip_existing_objects(self) -> bool:
        # Skip existing images
        # TODO: In this context, we should even check that they are present
        return True

    def _update_mode(self) -> str:
        return "Cla" if self.param.UpdateClassif == "Y" else "Yes"
