from datetime import datetime

import pytest

from fakes import make_min_user


@pytest.fixture
def users_json(req_ctx):
    from appli.gui.admin import users_list_interface_json as m

    return m


def test_user_table_columns_have_labels(users_json):
    for fn in (users_json.user_table_columns, users_json.guest_table_columns, users_json.organization_table_columns):
        cols = fn()
        assert "select" in cols
        for key, col in cols.items():
            assert key == "select" or "label" in col, (fn.__name__, key)


def test_users_render_for_js(users_json):
    cols = {
        "select": {"field": "id"},
        "id": {},
        "name": {},
        "status": {},
        "usercreationdate": {},
    }
    users = [
        {"id": 3, "name": "A", "status": 1, "usercreationdate": datetime(2024, 1, 2, 3, 4, 5)},
        {"id": 4, "name": "B", "status": -1, "usercreationdate": None},
    ]
    rows = users_json.render_for_js(users, cols)
    assert rows == [
        [3, 3, "A", "active", "2024-01-02T03:04:05"],
        [4, 4, "B", "blocked", None],
    ]


@pytest.fixture
def prj_json(req_ctx):
    from appli.gui.project import projects_list_interface_json as m

    return m


def test_project_table_columns_selections(prj_json):
    lst = prj_json.project_table_columns("", selection="list")
    assert lst["select"] == {"select": "controls", "field": "projid"}
    merge = prj_json.project_table_columns("", selection="merge")
    assert merge["select"]["select"] == "select"
    assert set(lst) - {"select"} == set(merge) - {"select"}


def test_render_prj_summary(prj_json):
    from fakes import model
    from to_back.ecotaxa_cli_py.models import ProjectModel

    prj = model(ProjectModel, projid=5, title="  My project ", contact=None)
    assert prj_json.render_prj_summary(prj) == {"projid": 5, "title": "My project", "contact": None}
    assert prj_json.render_prj_summary_json({"projid": 5, "title": " t ", "contact": "c", "x": 1}) == {
        "projid": 5,
        "title": "t",
        "contact": "c",
    }


def test_render_stat_proj_json_partial(prj_json):
    prj = {
        "projid": 1,
        "title": " T ",
        "comments": "",
        "cnn_network_id": None,
        "instrument": "UVP5",
        "status": "Annotate",
        "access": "1",
        "managers": [1],
        "annotators": [],
        "viewers": [],
    }
    out = prj_json.render_stat_proj_json(dict(prj), partial=True)
    assert out["title"] == "T"
    assert out["privileges"] == {"managers": [1], "annotators": [], "viewers": []}
    assert "access" not in out
    full = prj_json.render_stat_proj_json(dict(prj, sample_free_cols={}), partial=False)
    assert full["access"] == "1" and full["sample_free_cols"] == {}


def test_render_stat_proj_privileges(prj_json):
    from fakes import model
    from to_back.ecotaxa_cli_py.models import ProjectModel

    mgr = make_min_user(id=7, name="Mgr")
    prj = model(
        ProjectModel,
        projid=1,
        title="P ",
        status="Annotate",
        comments=None,
        cnn_network_id=None,
        instrument="Zooscan",
        managers=[mgr],
        annotators=[],
        viewers=[],
    )
    out = prj_json.render_stat_proj(prj)
    assert out["title"] == "P"
    assert out["privileges"]["managers"][0]["id"] == 7
    assert out["privileges"]["annotators"] == []


@pytest.fixture
def coll_json(req_ctx):
    from appli.gui.collection import collections_list_interface_json as m

    return m


def test_collection_columns_and_summary(coll_json):
    cols = coll_json.collection_table_columns("")
    assert cols
    summ = coll_json.render_coll_summary_json({"id": 1, "title": "C", "other": 0})
    assert summ.get("id") == 1 and "other" not in summ
