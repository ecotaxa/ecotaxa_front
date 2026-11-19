import gzip
import json

import pytest
import responses

from fakes import make_project
from to_back.ecotaxa_cli_py.api import ProjectsApi

BACK = "http://backend.test"


def _project_json(projid=1, title="Test project", **kw):
    prj = {
        "projid": projid,
        "title": title,
        "status": "Annotate",
        "access": "1",
        "instrument": "Zooscan",
        "contact": None,
        "managers": [{"id": 42, "name": "Test User", "email": "user@example.org"}],
        "annotators": [],
        "viewers": [],
        "objcount": 10,
        "pctvalidated": 50.0,
        "pctclassified": 80.0,
        "cnn_network_id": None,
        "comments": "",
        "description": "",
        "visible": True,
        "license": "CC BY 4.0",
    }
    prj.update(kw)
    return prj


def _json_body(rsp):
    data = rsp.data
    if rsp.headers.get("Content-Encoding") == "gzip":
        data = gzip.decompress(data)
    return json.loads(data)


def test_projects_list_page(user_client):
    rsp = user_client.get("/gui/prj/")
    assert rsp.status_code == 200


def test_prjlist_json(user_client, backend):
    backend.requests.add(responses.GET, BACK + "/projects/search", json=[_project_json(1), _project_json(2, "Other")])
    rsp = user_client.get("/gui/prjlist/")
    assert rsp.status_code == 200
    body = _json_body(rsp)
    assert set(body) == {"columns", "data"}
    assert len(body["data"]) == 2
    # one value per column in each row
    assert all(len(row) == len(body["columns"]) for row in body["data"])
    (call,) = backend.requests.calls
    assert call.request.headers["Authorization"].startswith("Bearer ")
    assert "not_granted=False" in call.request.url


def test_prjlist_listall_asks_not_granted(user_client, backend):
    backend.requests.add(responses.GET, BACK + "/projects/search", json=[])
    rsp = user_client.get("/gui/prjlist/?listall=True")
    assert rsp.status_code == 200
    assert _json_body(rsp)["data"] == []
    assert any("not_granted=True" in c.request.url for c in backend.requests.calls)


def test_prjlist_backend_error(user_client, backend):
    backend.requests.add(responses.GET, BACK + "/projects/search", status=500)
    rsp = user_client.get("/gui/prjlist/")
    assert rsp.status_code >= 400


@pytest.mark.parametrize("status", [403, 404])
@pytest.mark.parametrize("page", ["purge", "edit", "merge", "editannot", "resettopredicted", "editdatamass", "taxofix"])
def test_project_pages_without_rights_go_to_noright(user_client, backend, page, status):
    from fakes import api_exception

    backend.on(ProjectsApi, "project_query", raises=api_exception(status))
    rsp = user_client.get(f"/gui/prj/{page}/7")
    assert rsp.status_code == 302, rsp.data[:300]
    assert rsp.headers["Location"].endswith("/gui/prj/noright/7")


@pytest.mark.parametrize("page", ["purge", "merge", "editannot", "taxofix"])
def test_explore_only_project_is_refused(user_client, backend, page):
    backend.on(ProjectsApi, "project_query", returns=make_project(7, status="ExploreOnly"))
    rsp = user_client.get(f"/gui/prj/{page}/7")
    assert rsp.status_code == 302
    assert rsp.headers["Location"].endswith("/gui/prj/noright/7")


def test_prj_manual_classification_has_image_rank_click_handler(user_client, backend):
    from fakes import populate

    populate(backend)
    rsp = user_client.get("/prj/1")
    assert rsp.status_code == 200
    html = rsp.data.decode()
    assert 'id="img_order"' in html
    assert "req['img_order']" in html
    assert "glyphicon-th" in html
    assert "!e.ctrlKey && !e.metaKey" in html
    assert "$('#img_order').val(next_order)" in html or '$("#img_order").val(next_order)' in html
    assert "next_order >= 4" in html
    for code in (97, 98, 99):
        assert f"case {code}:" not in html


@pytest.mark.parametrize(
    "posted_rank, expected_kw",
    [
        ("2", 2),
        ("3", 3),
        ("1", None),
        ("", None),
        ("0", None),
        ("abc", None),
    ],
)
def test_load_right_pane_transmits_image_position(user_client, backend, posted_rank, expected_kw):
    from fakes import model, populate
    from to_back.ecotaxa_cli_py.api import ObjectsApi, UsersApi
    from to_back.ecotaxa_cli_py.models import ObjectSetQueryRsp

    populate(backend)
    backend.on(UsersApi, "set_current_user_prefs")
    get_obj_set = backend.on(
        ObjectsApi,
        "get_object_set",
        returns=model(ObjectSetQueryRsp, object_ids=[], details=[], total_ids=0),
    )
    form = {"projid": "1", "ipp": "100", "zoom": "100", "popupenabled": "0", "dispfield": ""}
    if posted_rank:
        form["img_order"] = posted_rank
    rsp = user_client.post("/prj/LoadRightPane", data=form)
    assert rsp.status_code == 200
    get_obj_set.assert_called_once()
    if expected_kw is None:
        assert "img_order" not in get_obj_set.call_args.kwargs
    else:
        assert get_obj_set.call_args.kwargs["img_order"] == expected_kw


def test_objects_api_get_object_set_image_rank(monkeypatch):
    from to_back.ecotaxa_cli_py.api import ObjectsApi
    from to_back.ecotaxa_cli_py.api_client import ApiClient

    client = ApiClient()
    captured = {}

    def fake_call_api(resource_path, method, path_params, query_params, *args, **kwargs):
        captured["resource_path"] = resource_path
        captured["query_params"] = query_params
        return None

    monkeypatch.setattr(client, "call_api", fake_call_api)
    api = ObjectsApi(client)
    api.get_object_set(1, {}, img_order=2)
    assert captured["resource_path"] == "/object_set/{project_id}/query"
    assert ("img_order", 2) in captured["query_params"]
