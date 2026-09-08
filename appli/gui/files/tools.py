import io
import json
import posixpath
import time
import uuid

import requests
from flask import request
from appli import gvp
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import MyFilesApi, UsersApi
from appli.utils import ApiClient
from werkzeug.datastructures import FileStorage

file_service = "/user_files/"
IMPORT_MANIFEST_LOG_NAME = "_import_original_locations.log"
IMPORT_MANIFEST_PREF_KEY = "last_import_manifest"


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


def _dedupe_nested_entries(entries: list) -> list:
    """Keep only the top-most selected entries: drop any entry that is a
    descendant of another selected entry, since moving the ancestor already
    relocates it."""
    cleaned = sorted(
        {e.strip().strip("/") for e in entries if e and e.strip().strip("/")},
        key=len,
    )
    kept: list = []
    for entry in cleaned:
        if not any(
            entry == other or entry.startswith(other + "/") for other in kept
        ):
            kept.append(entry)
    return kept


def _unique_staged_name(name: str, used: set) -> str:
    if name not in used:
        used.add(name)
        return name
    stem, ext = posixpath.splitext(name)
    i = 2
    while True:
        candidate = "%s_%d%s" % (stem, i, ext)
        if candidate not in used:
            used.add(candidate)
            return candidate
        i += 1


def stage_import_sources(projid: int, entries: list) -> dict:
    """
    Gather several files/directories, picked from anywhere in the user's My
    Files tree, into a single flat temporary staging directory so they can
    be imported as one plain-directory import:
    - each selected entry is moved directly under the staging directory,
      renamed on name collisions,
    - the real (original) location of every selected entry is written to a
      log file left in the staging directory,
    - the same mapping is remembered server-side so the import confirmation
      screen can display it once the import job completes.
    """
    entries = _dedupe_nested_entries(entries)
    if not entries:
        return {"error": "nothing_selected"}

    staging_root = "import_%s_%s" % (
        time.strftime("%Y%m%d%H%M%S"),
        uuid.uuid4().hex[:6],
    )

    mapping = []
    used_names: set = set()
    with ApiClient(MyFilesApi, request) as api:
        api.create_user_file(source_path=staging_root)
        for entry in entries:
            staged_name = _unique_staged_name(posixpath.basename(entry), used_names)
            api.move_user_file(
                source_path=entry, dest_path=staging_root + "/" + staged_name
            )
            mapping.append({"staged": staged_name, "original": entry})

    _write_staging_log(staging_root, mapping)
    _remember_manifest(projid, staging_root, mapping)
    return {"source_path": staging_root, "entries": mapping}


def _write_staging_log(staging_root: str, mapping: list) -> None:
    lines = [
        "Import staged on %s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "Real (original) location of each imported file/directory, relative to My Files:",
        "",
    ] + ["%s  <-  %s" % (item["staged"], item["original"]) for item in mapping]
    content = ("\n".join(lines) + "\n").encode("utf-8")
    with ApiClient(MyFilesApi, request) as api:
        url = api.api_client.configuration.host + file_service
        token = api.api_client.configuration.access_token
        headers = {"Authorization": "Bearer " + token}
        requests.post(
            url,
            data={"path": staging_root},
            files={
                "file": (
                    IMPORT_MANIFEST_LOG_NAME,
                    io.BytesIO(content),
                    "text/plain",
                )
            },
            headers=headers,
        )


def _remember_manifest(projid: int, staging_root: str, mapping: list) -> None:
    with ApiClient(UsersApi, request) as api:
        api.set_current_user_prefs(
            int(projid),
            IMPORT_MANIFEST_PREF_KEY,
            json.dumps({"source_path": staging_root, "entries": mapping}),
        )


def get_staged_import_manifest(projid: int, source_path: str):
    """Return the [{staged, original}, ...] mapping for a staged import
    directory, previously recorded by stage_import_sources(), or None."""
    with ApiClient(UsersApi, request) as api:
        raw = api.get_current_user_prefs(int(projid), IMPORT_MANIFEST_PREF_KEY)
    if not raw:
        return None
    try:
        manifest = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if manifest.get("source_path") != source_path:
        return None
    return manifest.get("entries")


def upload_file():
    # import json
    import requests

    dirpath = gvp("path")
    uploaded: FileStorage = request.files.get("file")
    # reqheaders = json.loads(json.dumps({k: v for k, v in request.headers.items()}))
    # Relay the file to back-end
    with ApiClient(MyFilesApi, request) as api:
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
