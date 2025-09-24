import json
from json import JSONDecodeError
from typing import Optional, Dict

import requests
from flask import g, flash
from werkzeug.datastructures import FileStorage

from appli import gvg, XSSEscape, gvp
from appli.project import sharedfilter
from to_back.ecotaxa_cli_py.api import MyfilesApi
from to_back.ecotaxa_cli_py.models import JobModel
from appli.utils import ApiClient


class Job(object):
    """
    UI for long-running process on back-end side.
    """

    JOB_ID_POST_PARAM = "job_id"

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
    def final_download_action(cls, job_id, prj_id, out_file: Optional[str]) -> str:
        if out_file is None:
            return "Error, final file not available"

        ret = (
            "<a href='/api/jobs/%d/file' class='btn btn-primary btn-sm ' "
            "role='button'>Get file %s</a>" % (job_id, out_file)
        )
        if prj_id is not None:
            ret += (
                " <a href='/Job/Clean/%d?thengotoproject=Y' "
                "class='btn btn-primary btn-sm ' "
                "role='button'>FORCE Delete of %s and back to project "
                "(no danger for the original database) </a>" % (job_id, out_file)
            )
        else:
            ret += (
                " <a href='/Job/Clean/%d' class='btn btn-primary btn-sm ' "
                "role='button'>FORCE Delete of %s (no danger for the "
                "original database) </a>" % (job_id, out_file)
            )
        ret += (
            "<br>Local users can also retrieve the file in the "
            "EcoTaxa folder temptask/task%06d (useful for huge files)" % job_id
        )
        return ret

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
            with ApiClient(MyfilesApi, request) as api:
                # Call using requests, as the generated openapi wrapper only reads the full file in memory.
                url = (
                    api.api_client.configuration.host + "/user_files/"
                )  # endpoint is nowhere available as a const :(
                token = api.api_client.configuration.access_token
                headers = {"Authorization": "Bearer " + token}
                # 'requests' lib sends fine the name to back-end
                uploaded_file.name = uploaded_file.filename
                file_rsp = requests.post(
                    url,
                    files={"file": uploaded_file},
                    data={"path": uploaded_file.name},
                    headers=headers,
                )
            if file_rsp.status_code != 200:
                return None, file_rsp.text
            else:
                return file_rsp.json(), None
        else:
            return request.form.get("ServerPath", ""), None

    @classmethod
    def _extract_filters_from_url(cls, filters: Dict[str, str], target_prj) -> str:
        # Extract filter values, they are in the URL (GET)
        for k in sharedfilter.FilterList:
            if gvg(k, "") != "":
                filters[k] = gvg(k, "")
        return cls._remind_filters(filters, target_prj)

    @classmethod
    def _remind_filters(cls, filters, target_prj):
        # Remind filters in the page
        filtertxt = ""
        if len(filters) > 0:
            filtertxt += ",".join([k + "=" + v for k, v in filters.items() if v != ""])
            g.headcenter = "<h4><a href='/prj/{0}?{2}'>{1}</a></h4>".format(
                target_prj.projid,
                XSSEscape(target_prj.title),
                "&".join([k + "=" + v for k, v in filters.items() if v != ""]),
            )
        return filtertxt

    @classmethod
    def _extract_filters_from_form(cls, filters, target_prj):
        # Extract filter values, they are in the submitted values (POST)
        for k in sharedfilter.FilterList:
            if gvp(k, "") != "":
                filters[k] = gvp(k, "")
        return cls._remind_filters(filters, target_prj)

    @classmethod
    def flash_any_error(cls, errors):
        if len(errors) > 0:
            for e in errors:
                flash(e, "error")
            return True
        else:
            return False


def load_from_json(str, clazz):
    """deserialize a json value of expected class"""
    try:
        ret = json.loads(str)
    except JSONDecodeError:
        ret = clazz()
    if not isinstance(ret, clazz):
        ret = clazz()
    return ret
