# -*- coding: utf-8 -*-
import time
from pathlib import Path
from typing import List, ClassVar
import requests
from flask import render_template, redirect, request, flash

from appli import gvg, gvp, app
from appli.gui.jobs.Job import Job
from appli.gui.jobs.staticlistes import py_messages
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import (
    FilesApi,
    ProjectsApi,
    UsersApi,
    JobsApi,
)
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    JobModel,
    DirectoryModel,
)


class UploadJob(Job):
    """
    Import, just GUI here, bulk of job subcontracted to back-end.
    Also serves as a base class for import update as pages are very similar.
    """

    UI_NAME: ClassVar = "FileUpload"

    STEP0_TEMPLATE: ClassVar = "/v2/jobs/import.html"
    STEP1_TEMPLATE: ClassVar = "/v2/jobs/_import_directives.html"

    @classmethod
    def initial_dialog(cls) -> str:
        """In UI/flask, initial load, GET"""
        prj_id = int(gvg("p"))
        target_proj = cls.get_target_prj(prj_id)

        # Get stored last server path value for this project, if any
        with ApiClient(UsersApi, request) as uapi:
            server_path = uapi.get_current_user_prefs(prj_id, "cwd")
        return render_template(
            cls.STEP0_TEMPLATE,
            header="",
            ServerPath=server_path,
            TxtTaxoMap="",
            target_proj=target_proj,
            prjmanagermail=target_prj.managers[0].email,
        )

    @classmethod
    def create_or_update(cls):
        """In UI/flask, submit/resubmit of initial page"""
        prj_id = int(gvg("p"))
        target_proj = cls.get_target_prj(prj_id)
        errors = []
        # file_to_load, error = Job.get_file_from_stream(request)

        with ApiClient(FilesApi, request) as api:
            try:
                #: DirectoryModel
                dirlist = api.list_user_files("ecotaxa_import")
            except ApiException as ae:
                if ae.status in (401, 403):
                    ae.reason = py_messages["dirlist"]["nopermission"]

        from appli.gui.commontools import todict

        dirlist = todict(dirlist)
        return dict({"file_to_load": file_to_load})
        return render_template(
            cls.STEP1_TEMPLATE,
            header="",
            file_to_load=file_to_load,
            dirlist=dirlist,
            ServerPath=server_path,
            target_proj=rtarget_proj,
        )

    @classmethod
    def get_request_stream(cls, request):
        import tempfile

        file = tempfile.TemporaryFile("wb+")
        for chunk in iter(lambda: request.stream.read(16384), bytes()):
            file.write(chunk)
        return file

    @classmethod
    def get_file_from_stream(cls, request):
        # Relay the file to back-end streaming

        with ApiClient(FilesApi, request) as api:
            # Call using requests, as the generated openapi wrapper only reads the full file in memory.
            url = (
                api.api_client.configuration.host + "/my_files/"
            )  # endpoint is nowhere available as a const :(
            token = api.api_client.configuration.access_token
            headers = {"Authorization": "Bearer " + token}
            # 'requests' lib sends fine the name to back-end
            uploaded_file = cls.get_request_stream(request)
            # uploaded_file.name = "testimport.zip"
            # uploaded_file.type = "application/zip"
            file_rsp = requests.post(
                url, headers=headers, files={"file": uploaded_file}
            )

            if file_rsp.status_code != 200:
                return None, file_rsp.text
            else:
                return file_rsp.json(), None

    @classmethod
    def _update_mode(cls, ui_option: str) -> str:
        return ""  # No update for plain import
