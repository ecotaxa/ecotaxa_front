import json

from typing import Optional, Dict, ClassVar, Union, Tuple

import requests
from flask import flash, request
from werkzeug.datastructures import FileStorage

from appli import gvg, gvp
from appli.project import sharedfilter
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import FilesApi, JobsApi
from to_back.ecotaxa_cli_py.models import JobModel
from appli.utils import ApiClient


class Job(object):
    """
    UI for long-running process on back-end side.
    """

    JOB_ID_POST_PARAM: ClassVar = "job_id"
    NOOBJ_TEMPLATE: ClassVar = "/v2/project/noright.html"
    FINAL_TEMPLATE: ClassVar = None
    TARGET_TYPE: ClassVar = None
    # for loop in collection projects
    DONE: ClassVar = []

    def __init__(self):
        pass

    @staticmethod
    def find_job_class_by_name(clazz, name: str):
        """
        Find a subclass with given UI name.
        """
        for job_sub_class in clazz.__subclasses__():
            if job_sub_class.UI_NAME == name:
                return job_sub_class
            else:
                for_subclass = Job.find_job_class_by_name(job_sub_class, name)
                if for_subclass:
                    return for_subclass

    @staticmethod
    def initial_dialog() -> str:
        """
        Return HTML for displaying the initial Job dialog. To override.
        """
        return ""

    @staticmethod
    def final_action(job: JobModel) -> str:
        """
        Return HTML for specific stuff to do where the job is finished.
        """
        return ""

    @classmethod
    def get_project_id(cls, collection_id: int = 0) -> Union[int, str]:
        if collection_id != 0:
            coll = cls.get_target_obj(0, collection_id)
            if coll is not None:
                projs = [str(prj) for prj in coll.project_ids]
                return ",".join(projs)
            else:
                raise
        else:
            if request.method == "GET":
                prjid = gvg("projid" or 0)
            else:
                prjid = gvp("projid" or 0)
            if prjid != 0:
                projid = int(prjid)
            return projid

    @classmethod
    def get_target_id(cls) -> Tuple[Union[int, str], int]:
        if request.method == "GET":
            collid = gvg("collection_id" or "")
        else:
            collid = gvp("collection_id" or "")
        if collid != "":
            cls.TARGET_TYPE == "collection"
            collection_id = int(collid)
        else:
            collection_id = 0
        projid = cls.get_project_id(collection_id)
        return projid, collection_id

    @classmethod
    def get_target_obj(cls, projid: int, collection_id: Optional[int] = 0):
        if collection_id != 0:
            from appli.gui.collection.settings import get_collection

            return get_collection(collection_id)
        else:
            from appli.gui.project.projectsettings import get_target_prj

            return get_target_prj(projid, full=False)

    @classmethod
    def get_file_from_form(cls, request):
        """
        Common treatment of "file" fields in several tasks.
        We have either:
            - ServerPath posted variable, a string with a path on server, relative to
                SERVERLOADAREA configuration entry.
            or
            - request.files posted, with the full file content inside.
        """
        uploaded_file: FileStorage = request.files.get("uploadfile")
        if uploaded_file is not None and uploaded_file.filename != "":
            # Relay the file to back-end
            with ApiClient(FilesApi, request) as api:
                # Call using requests, as the generated openapi wrapper only reads the full file in memory.
                url = (
                    api.api_client.configuration.host + "/my_files/"
                )  # endpoint is nowhere available as a const :(
                token = api.api_client.configuration.access_token
                headers = {"Authorization": "Bearer " + token}
                # 'requests' lib sends fine the name to back-end
                uploaded_file.name = uploaded_file.filename
                file_rsp = requests.post(
                    url, files={"file": uploaded_file}, headers=headers
                )
                if file_rsp.status_code != 200:
                    return None, file_rsp.text
                else:
                    return file_rsp.json(), None
        else:
            return request.form.get("ServerPath", ""), None

    @classmethod
    def _extract_filters_from_url(cls) -> list:
        # Extract filter values, they are in the URL (GET)
        return list(
            filter(
                lambda f: f[1] != "",
                [(k, gvg(k, "")) for k in sharedfilter.FilterList],
            )
        )

    @classmethod
    def _extract_filters_from_form(cls) -> list:
        # Extract filter values, they are in the POST
        return list(
            filter(
                lambda f: f[1] != "", [(k, gvp(k, "")) for k in sharedfilter.FilterList]
            )
        )

    @classmethod
    def flash_any_error(cls, errors):
        if len(errors) > 0:
            for e in errors:
                flash(e, "error")
            return True
        else:
            return False

    @classmethod
    def get_job(cls) -> Optional[JobModel]:
        try:
            with ApiClient(JobsApi, request) as api:
                job: JobModel = api.get_job(job_id=cls.JOB_ID_POST_PARAM)
        except ApiException as ae:
            if ae.status in (401, 403):
                flash(py_messages["notauthorized"], "error")
            elif ae.status == 404:
                flash(py_messages["notfound"], "error")


def load_from_json(str, clazz):
    """deserialize a json value of expected class"""
    from json import JSONDecodeError

    try:
        ret = json.loads(str)
    except JSONDecodeError:
        ret = clazz()
    if not isinstance(ret, clazz):
        ret = clazz()
    return ret
