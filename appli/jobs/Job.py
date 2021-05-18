import json
from json import JSONDecodeError

import requests
from werkzeug.datastructures import FileStorage

from to_back.ecotaxa_cli_py.api import FilesApi
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
        if uploaded_file is not None and uploaded_file.filename != '':
            # Relay the file to back-end
            with ApiClient(FilesApi, request) as api:
                # Call using requests, as the generated openapi wrapper only reads the full file in memory.
                url = api.api_client.configuration.host + "/my_files/"  # endpoint is nowhere available as a const :(
                token = api.api_client.configuration.access_token
                headers = {'Authorization': 'Bearer ' + token}
                # 'requests' lib sends fine the name to back-end
                uploaded_file.name = uploaded_file.filename
                file_rsp = requests.post(url, files={"file": uploaded_file}, headers=headers)
            if file_rsp.status_code != 200:
                return None, file_rsp.text
            else:
                return file_rsp.json(), None
        else:
            return request.form.get("ServerPath", ""), None


def load_from_json(str, clazz):
    """ deserialize a json value of expected class """
    try:
        ret = json.loads(str)
    except JSONDecodeError:
        ret = clazz()
    if not isinstance(ret, clazz):
        ret = clazz()
    return ret
