from flask import flash, request
from appli import gvg, gvp
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import FilesApi

from appli.utils import ApiClient
from appli.gui.jobs.staticlistes import py_messages


def dir_list(subdir):
    with ApiClient(FilesApi, request) as api:
        try:
            #: DirectoryModel
            dirlist = api.list_user_files(subdir)
        except ApiException as ae:
            if ae.status in (401, 403):
                ae.reason = py_messages["dirlist"]["nopermission"]
            elif ae.status == 404:
                dirlist = dict({"path": ""})
            else:
                return None, ae
    return dirlist, None


def upload_file(subdir):
    import json
    import requests

    # body = request.get_data()
    # print(body)
    # uploaded = gvp("file")
    dirpath = gvp("path")
    tag = gvp("tag")
    uploaded: FileStorage = request.files.get("file")
    reqheaders = json.loads(json.dumps({k: v for k, v in request.headers.items()}))
    # Relay the file to back-end
    with ApiClient(FilesApi, request) as api:
        # Call using requests, as the generated openapi wrapper only reads the full file in memory.
        url = api.api_client.configuration.host + "/my_files/"
        token = api.api_client.configuration.access_token
        # reqheaders["Authorization"] = "Bearer " + token
        headers = {
            "Authorization": "Bearer " + token,
            # "Content-Range": reqheaders["Content-Range"],
            # "Transfer-Encoding": reqheaders["Transfer-Encoding"],
        }
        # headers = reqheaders
        # 'requests' lib sends fine the name to back-end
        uploaded.name = uploaded.filename
        rsp = requests.post(
            url,
            data={"tag": tag, "path": dirpath},
            files={"file": uploaded},
            headers=headers,
        )
        if rsp.status_code != 200:
            return rsp.text
        else:
            return rsp.json()


def get_file_from_request():
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


def read_in_chunks(file_object, CHUNK_SIZE):
    while True:
        data = file_object.read(CHUNK_SIZE)
        if not data:
            break
        yield data
    # END GENERATOR
