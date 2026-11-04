import pytest

from to_back.ecotaxa_cli_py.api import MyFilesApi


def test_list_root(user_client, backend):
    lst = backend.on(MyFilesApi, "list_user_files", returns={"path": "/", "entries": [{"name": "a.zip", "type": "F"}]})
    rsp = user_client.get("/gui/files/list")
    assert rsp.status_code == 200
    assert rsp.get_json() == {"path": "/", "entries": [{"name": "a.zip", "type": "F"}]}
    lst.assert_called_once_with("/")


def test_list_subpath(user_client, backend):
    lst = backend.on(MyFilesApi, "list_user_files", returns={"path": "d/e", "entries": []})
    rsp = user_client.get("/gui/files/list/d/e")
    assert rsp.status_code == 200
    lst.assert_called_once_with("d/e")


@pytest.mark.parametrize("url, data", [("/gui/files/create", {"entry": " "}), ("/gui/files/move", {"entry": "a", "dest": ""}),
                                       ("/gui/files/rename", {"entry": "", "dest": "b"}), ("/gui/files/import/stage", {"projid": ""})])
def test_missing_params_answer_422_without_backend_call(user_client, url, data):
    rsp = user_client.post(url, data=data)
    assert rsp.status_code == 200
    assert rsp.get_json()["status"] == 422


def test_create(user_client, backend):
    create = backend.on(MyFilesApi, "create_user_file", returns="newdir")
    rsp = user_client.post("/gui/files/create", data={"entry": " newdir "})
    assert rsp.get_json() == {"status": 200, "message": "newdir"}
    create.assert_called_once_with(source_path="newdir")


def test_move(user_client, backend):
    move = backend.on(MyFilesApi, "move_user_file", returns="b/a")
    rsp = user_client.post("/gui/files/move", data={"entry": "a", "dest": "b/a"})
    assert rsp.get_json() == {"status": 200, "message": "b/a"}
    move.assert_called_once_with(source_path="a", dest_path="b/a")


@pytest.mark.parametrize("entry, sent", [("dir/f.zip", "dir/f.zip"), ("", "*"), ("/", "*")])
def test_remove(user_client, backend, entry, sent):
    # empty entry (trash) means everything: the back-end understands '*'
    rm = backend.on(MyFilesApi, "remove_user_file", returns=1)
    rsp = user_client.post("/gui/files/remove", data={"entry": entry})
    assert rsp.get_json() == {"status": 200, "message": "1"}
    rm.assert_called_once_with(source_path=sent)


def test_import_stage(user_client, backend):
    import responses

    create = backend.on(MyFilesApi, "create_user_file", returns="ok")
    move = backend.on(MyFilesApi, "move_user_file", returns="ok")
    from to_back.ecotaxa_cli_py.api import UsersApi

    prefs = backend.on(UsersApi, "set_current_user_prefs")
    backend.requests.add(responses.POST, "http://backend.test/user_files/", json={})
    rsp = user_client.post(
        "/gui/files/import/stage", data={"projid": "3", "entries": ["a/x.zip", "b/x.zip", "a/x.zip/inner"]}
    )
    body = rsp.get_json()
    assert body["status"] == 200, body
    staging = body["message"]["source_path"]
    assert staging.startswith("import_")
    entries = body["message"]["entries"]
    # nested a/x.zip/inner is dropped, same names get a suffix
    assert sorted(e["staged"] for e in entries) == ["x.zip", "x_2.zip"]
    assert sorted(e["original"] for e in entries) == ["a/x.zip", "b/x.zip"]
    create.assert_called_once_with(source_path=staging)
    assert move.call_count == 2
    # the staging log is uploaded next to the files
    assert len(backend.requests.calls) == 1
    # and the mapping remembered for the import confirmation screen
    assert prefs.call_args.args[:2] == (3, "last_import_manifest")
