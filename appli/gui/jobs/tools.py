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
                raise ApiException(
                    status=ae.status,
                    reason=py_messages["dirlist"]["nopermission"],
                )
            elif ae.status == 404:
                dirlist = dict({"path": ""})
            else:
                return None, ae

    return dirlist, None


async def upload_file(subdir, request):
    import json

    uploaded = request.files.get("file")
    final = True
    reqheaders = json.loads(json.dumps({k: v for k, v in request.headers.items()}))
    # final = gvp("final")
    # uploadedchunk: FileStorage = request.files.get("file")
    # print(reqheaders["Content-Range"])
    body = b""
    async for chunk in request.stream():
        body += chunk

    print(body)
    await response(scope, receive, send)

    if final:
        if uploaded is not None and uploaded.filename != "":
            # Relay the file to back-end
            with ApiClient(FilesApi, request) as api:
                # Call using requests, as the generated openapi wrapper only reads the full file in memory.
                url = (
                    api.api_client.configuration.host + "/my_files/"
                )  # endpoint is nowhere available as a const :(
                token = api.api_client.configuration.access_token
                headers = {
                    "Authorization": "Bearer " + token,
                    # "Content-Range": reqheaders["Content-Range"],
                }
                # 'requests' lib sends fine the name to back-end
                uploaded.name = uploaded.filename
                import requests

                uploaded.tag = subdir
                rsp = requests.post(url, files={"file": uploaded}, headers=headers)
            if rsp.status_code != 200:
                return None, rsp.text
            else:
                return rsp.json(), None

        else:
            return None, dict({"err": 422, "message": py_messages["upload"]["nofile"]})
