#
# Several My Files entries imported together: the front job gathers them into one
# folder, and puts them back in their place if the import fails or is abandoned.
#
import json

import pytest

from fakes import api_exception, model
from to_back.ecotaxa_cli_py.api import JobsApi, MyFilesApi, ProjectsApi, UsersApi
from to_back.ecotaxa_cli_py.models import (
    DirectoryEntryModel,
    DirectoryModel,
    ImportRsp,
    JobModel,
)

STAGED = "import_20261117103000_abcdef"
MAPPING = [
    {"staged": "x.zip", "original": "a/x.zip"},
    {"staged": "x_2.zip", "original": "b/x.zip"},
]
PREF_KEY = "import_staged:" + STAGED


def _job(state):
    return model(
        JobModel,
        id=5,
        owner_id=42,
        type="GeneralImport",
        state=state,
        step=1,
        progress_pct=100,
        progress_msg="",
        params={"prj_id": 3, "req": {"source_path": STAGED}},
        result={},
        errors=[],
        question={},
        reply={},
        inside={},
        creation_date="2026-11-17T10:00:00",
        updated_on="2026-11-17T10:05:00",
    )


def _listing(path, names=()):
    entries = [model(DirectoryEntryModel, name=n, type="F") for n in names]
    return model(DirectoryModel, path=path, entries=entries)


def _staged_backend(backend, taken=()):
    """The mapping remembered, the original places free unless in taken"""
    backend.on(UsersApi, "get_current_user_prefs", returns=json.dumps(MAPPING))
    prefs = backend.on(UsersApi, "set_current_user_prefs")

    def listing(path):
        names = [p.split("/")[-1] for p in taken if p.rsplit("/", 1)[0] == path]
        return _listing(path, names)

    backend.on(MyFilesApi, "list_user_files", side_effect=listing)
    move = backend.on(MyFilesApi, "move_user_file", returns="ok")
    remove = backend.on(MyFilesApi, "remove_user_file", returns=1)
    return prefs, move, remove


def test_failed_import_puts_back(user_client, backend):
    backend.on(JobsApi, "get_job", returns=_job("E"))
    prefs, move, remove = _staged_backend(backend)
    body = user_client.get("/gui/job/status/5").get_json()
    assert "back in their place" in body["finalaction"]
    assert [c.kwargs for c in move.call_args_list] == [
        {"source_path": STAGED + "/x.zip", "dest_path": "a/x.zip"},
        {"source_path": STAGED + "/x_2.zip", "dest_path": "b/x.zip"},
    ]
    # The folder, with only the log left, and the mapping are gone
    remove.assert_called_once_with(source_path=STAGED)
    prefs.assert_called_once_with(3, PREF_KEY, "")


def test_failed_import_original_place_taken(user_client, backend):
    backend.on(JobsApi, "get_job", returns=_job("E"))
    prefs, move, remove = _staged_backend(backend, taken=["b/x.zip"])
    body = user_client.get("/gui/job/status/5").get_json()
    assert "kept in " + STAGED in body["finalaction"] and "b/x.zip" in body["finalaction"]
    assert move.call_count == 1
    remove.assert_not_called()
    # Kept for a retry
    assert json.loads(prefs.call_args.args[2]) == [MAPPING[1]]


def test_done_import_left_alone(user_client, backend):
    backend.on(JobsApi, "get_job", returns=_job("F"))
    backend.on(UsersApi, "get_current_user_prefs", returns=json.dumps(MAPPING))
    body = user_client.get("/gui/job/status/5").get_json()
    assert "a/x.zip" in body["finalaction"]  # The original locations, displayed


@pytest.mark.parametrize("state", ["A", "E"])
def test_erased_import_puts_back(user_client, backend, state):
    backend.on(JobsApi, "get_job", returns=_job(state))
    erase = backend.on(JobsApi, "erase_job")
    prefs, move, remove = _staged_backend(backend)
    user_client.get("/gui/job/clean/5")
    assert move.call_count == 2
    erase.assert_called_once_with(job_id=5)


def test_job_creation_stages_entries(user_client, backend):
    from fakes import make_project

    backend.on(ProjectsApi, "project_query", returns=make_project(3))
    create = backend.on(MyFilesApi, "create_user_file", returns="ok")
    move = backend.on(MyFilesApi, "move_user_file", returns="ok")
    prefs = backend.on(UsersApi, "set_current_user_prefs")
    imp = backend.on(ProjectsApi, "import_file", returns=model(ImportRsp, job_id=7, errors=[]))
    import responses

    backend.requests.add(responses.POST, "http://backend.test/user_files/", json={})
    rsp = user_client.post(
        "/gui/job/create/GeneralImport",
        data={"projid": "3", "entries": ["a/x.zip", "b/x.zip", "a/x.zip/inner"]},
    )
    assert rsp.status_code == 302 and rsp.headers["Location"].endswith("/gui/job/show/7")
    staged = create.call_args.kwargs["source_path"]
    assert staged.startswith("import_")
    assert move.call_count == 2
    assert imp.call_args.kwargs["import_req"].source_path == staged
    assert prefs.call_args.args[1] == "import_staged:" + staged


def test_job_refused_puts_back(user_client, backend):
    from fakes import make_project

    backend.on(MyFilesApi, "create_user_file", returns="ok")
    backend.on(ProjectsApi, "project_query", returns=make_project(3))
    backend.on(ProjectsApi, "import_file", raises=api_exception(403))
    import responses

    backend.requests.add(responses.POST, "http://backend.test/user_files/", json={})
    _prefs, move, remove = _staged_backend(backend)
    rsp = user_client.post(
        "/gui/job/create/GeneralImport", data={"projid": "3", "entries": ["a/x.zip", "b/x.zip"]}
    )
    assert rsp.status_code == 200  # Back to the form
    # 2 moves in, 2 moves back
    assert move.call_count == 4
    assert remove.call_count == 1


def test_staging_failure_puts_back(user_client, backend):
    from fakes import make_project

    backend.on(MyFilesApi, "create_user_file", returns="ok")
    backend.on(ProjectsApi, "project_query", returns=make_project(3))
    backend.on(UsersApi, "get_current_user_prefs", returns="")
    backend.on(MyFilesApi, "list_user_files", returns=_listing("a"))
    calls = []

    def move(source_path, dest_path):
        calls.append((source_path, dest_path))
        if len(calls) == 2:
            raise api_exception(422, "Archive extraction in progress, retry later")
        return "ok"

    backend.on(MyFilesApi, "move_user_file", side_effect=move)
    remove = backend.on(MyFilesApi, "remove_user_file", returns=1)
    rsp = user_client.post(
        "/gui/job/create/GeneralImport", data={"projid": "3", "entries": ["a/x.zip", "b/y.zip"]}
    )
    assert rsp.status_code == 200
    # a/x.zip moved in, b/y.zip refused, a/x.zip moved back, the empty folder removed
    assert calls[2][1] == "a/x.zip" and len(calls) == 3
    remove.assert_called_once()
