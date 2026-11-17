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
                                       ("/gui/files/rename", {"entry": "", "dest": "b"})])
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

