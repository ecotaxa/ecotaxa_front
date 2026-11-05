import json

import pytest

from fakes import make_min_user, make_project, populate
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi


@pytest.fixture
def edit_backend(backend):
    populate(backend)
    backend.on(
        UsersApi,
        "search_user",
        returns=[make_min_user(id=42, name="Test User"), make_min_user(id=43, name="Other", email="o@example.org")],
    )
    return backend


def _form(**kw):
    data = {
        "save": "Y",
        "title": "Renamed project",
        "members[member]": ["42", "43"],
        "members[privilege]": ["Manage", "Annotate"],
        "contact_user_id": "42",
        "subsample_coef": "1/subsample.sub_part",
        "total_water_volume": "",
        "individual_volume": "",
    }
    data.update(kw)
    return data


def test_edit_saves_project(user_client, edit_backend):
    update = edit_backend.on(ProjectsApi, "update_project")
    rsp = user_client.post("/gui/prj/edit/1", data=_form())
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == "/gui/prj/edit/1"
    update.assert_called_once()
    sent = update.call_args.kwargs["project_model"]
    assert update.call_args.kwargs["project_id"] == 1
    assert sent.title == "Renamed project"
    assert [u.id for u in sent.managers] == [42]
    assert [u.id for u in sent.annotators] == [43]
    assert sent.viewers == []
    assert sent.contact.id == 42
    # formulae sent as JSON, with back-end prefixes
    assert json.loads(sent.formulae) == {"subsample_coef": "1/ssm.sub_part"}


def test_edit_without_formulae_sends_empty_json(user_client, edit_backend):
    update = edit_backend.on(ProjectsApi, "update_project")
    user_client.post("/gui/prj/edit/1", data=_form(subsample_coef=""))
    assert update.call_args.kwargs["project_model"].formulae == "{}"


@pytest.mark.parametrize(
    "change",
    [
        {"contact_user_id": "43"},  # contact is not a manager
        {"members[member]": ["43"], "members[privilege]": ["Annotate"], "contact_user_id": "43"},  # no manager
        {"members[member]": ["42", "99"], "members[privilege]": ["Manage", "View"]},  # 99 unknown
        {"members[member]": [], "members[privilege]": []},  # no member
    ],
)
def test_edit_refused_without_valid_members(user_client, edit_backend, change):
    update = edit_backend.on(ProjectsApi, "update_project")
    rsp = user_client.post("/gui/prj/edit/1", data=_form(**change))
    assert rsp.status_code == 200
    update.assert_not_called()


@pytest.mark.parametrize(
    "change, key",
    [
        ({"contact_user_id": "43"}, "getcontactuserinmanagers"),
        ({"members[member]": ["43"], "members[privilege]": ["Annotate"], "contact_user_id": "43"}, "managerrequired"),
    ],
)
def test_edit_member_errors_are_readable(user_client, edit_backend, change, key):
    from markupsafe import escape
    from appli.gui.staticlistes import py_messages

    edit_backend.on(ProjectsApi, "update_project")
    rsp = user_client.post("/gui/prj/edit/1", data=_form(**change))
    page = rsp.get_data(as_text=True)
    assert key not in page
    assert str(escape(str(py_messages[key]))) in page


def test_edit_backend_refusal_keeps_page(user_client, edit_backend):
    from fakes import api_exception

    edit_backend.on(ProjectsApi, "update_project", raises=api_exception(422, "bad formulae"))
    rsp = user_client.post("/gui/prj/edit/1", data=_form())
    assert rsp.status_code == 200
