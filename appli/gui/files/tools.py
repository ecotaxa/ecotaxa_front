import requests
from flask import request
from appli import gvp
from to_back.ecotaxa_cli_py.api import MyFilesApi
from appli.utils import ApiClient
from werkzeug.datastructures import FileStorage

file_service = "/user_files/"


def dir_list(sub_path=None):
    if sub_path is None:
        sub_path = "/"

    with ApiClient(MyFilesApi, request) as api:
        dirlist = api.list_user_files(sub_path)
    return dirlist, None


def create_dir_file(source_path: str) -> str:
    if source_path == "" or source_path == "/":
        return ""

    with ApiClient(MyFilesApi, request) as api:
        ret = api.create_user_file(source_path=source_path)
    return ret


def remove_dir_file(source_path: str) -> int:
    if source_path == "" or source_path == "/":
        source_path = "*"

    with ApiClient(MyFilesApi, request) as api:
        ret = api.remove_user_file(source_path=source_path)

    return ret


def move_dir_file(source_path: str, dest_path: str) -> str:
    if source_path == "" or dest_path == "" or source_path == dest_path:
        return ""
    with ApiClient(MyFilesApi, request) as api:
        ret = api.move_user_file(source_path=source_path, dest_path=dest_path)
    return ret


def upload_file():
    from tusclient import client

    dirpath = gvp("path")
    uploaded: FileStorage = request.files.get("file")

    # Relay the file to back-end
    with ApiClient(MyFilesApi, request) as api:
        url = api.api_client.configuration.host + "/big_files/upload"
        token = api.api_client.configuration.access_token
        headers = {"Authorization": "Bearer " + token}

        my_client = client.TusClient(url, headers=headers)
        uploader = my_client.uploader(
            file_stream=uploaded.stream,
            metadata={"filename": uploaded.filename, "path": dirpath},
            chunk_size=10_000_000,
        )
        uploader.upload()
    # Tus doesn't return the same thing as the original POST
    return {}, None
