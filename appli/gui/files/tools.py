import requests
from flask import request
from appli import gvp
from to_back.ecotaxa_cli_py.api import MyfilesApi
from appli.utils import ApiClient
from werkzeug.datastructures import FileStorage

file_service = "/user_files/"


def dir_list(sub_path=None):
    if sub_path is None:
        sub_path = "/"

    with ApiClient(MyfilesApi, request) as api:
        dirlist = api.list_my_files(sub_path)
    return dirlist, None


def create_dir_file(source_path: str) -> str:
    if source_path == "" or source_path == "/":
        return ""

    with ApiClient(MyfilesApi, request) as api:
        ret = api.create_my_file(source_path=source_path)
    return ret


def remove_dir_file(source_path: str) -> int:
    if source_path == "" or source_path == "/":
        return 0

    with ApiClient(MyfilesApi, request) as api:
        ret = api.remove_my_file(source_path=source_path)

    return ret


def move_dir_file(source_path: str, dest_path: str) -> str:
    if source_path == "" or dest_path == "" or source_path == dest_path:
        return ""
    with ApiClient(MyfilesApi, request) as api:
        ret = api.move_my_file(source_path=source_path, dest_path=dest_path)
    return ret


def upload_file():
    # import json
    import requests

    dirpath = gvp("path")
    uploaded: FileStorage = request.files.get("file")
    # reqheaders = json.loads(json.dumps({k: v for k, v in request.headers.items()}))
    # Relay the file to back-end
    with ApiClient(MyfilesApi, request) as api:
        # Call using requests, as the generated openapi wrapper only reads the full file in memory.
        url = api.api_client.configuration.host + file_service
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
            data={"path": dirpath},
            files={"file": uploaded},
            headers=headers,
        )
    return rsp.json()
