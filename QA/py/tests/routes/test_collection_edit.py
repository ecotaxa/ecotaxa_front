import pytest

from fakes import api_exception, make_collection, make_min_user, model, populate
from to_back.ecotaxa_cli_py.api import CollectionsApi, GuestsApi, OrganizationsApi, UsersApi
from to_back.ecotaxa_cli_py.models import OrganizationModel

REFERER = {"Referer": "http://localhost/gui/collection/edit/1"}


@pytest.fixture
def coll_backend(backend):
    populate(backend)
    backend.on(UsersApi, "get_user", side_effect=lambda uid: make_min_user(id=uid, name=f"User {uid}"))
    backend.on(
        OrganizationsApi,
        "get_organizations",
        side_effect=lambda ids="": [model(OrganizationModel, id=int(ids or 3), name=f"Org {ids}", directories=None)],
    )
    return backend


def _form(**kw):
    data = {
        "save": "Y",
        "title": "New title",
        "short_title": "NT",
        "old_short_title": "MC",
        "license": "CC BY 4.0",
        "abstract": "abs",
        "description": "desc",
        "citation": "",
        "provider_user": "42",
        "contact_user": "42",
        "project_ids[]": ["1", "2"],
        "creator_persons[]": ["5", "org_7"],
        "associate_persons[]": [],
    }
    data.update(kw)
    return data


def _orgprefix():
    from appli.gui.collection import settings

    return settings.orgprefix


def test_collection_save(user_client, coll_backend):
    patch = coll_backend.on(CollectionsApi, "patch_collection")
    data = _form(**{"creator_persons[]": ["5", _orgprefix() + "7"]})
    rsp = user_client.post("/gui/collection/edit/1", data=data, headers=REFERER)
    assert rsp.status_code == 302, rsp.data[:500]
    assert rsp.headers["Location"] == REFERER["Referer"]
    kw = patch.call_args.kwargs
    sent = kw["collection_req"]
    assert kw["collection_id"] == 1
    assert sent.title == "New title"
    assert sent.project_ids == [1, 2]
    assert [u.id for u in sent.creator_users] == [5]
    assert [o.id for o in sent.creator_organisations] == [7]
    assert sent.associate_users == [] and sent.associate_organisations == []


def test_published_collection_keeps_its_title(user_client, coll_backend):
    published = make_collection(1)
    published.external_id = "10.1234/doi"
    coll_backend.on(CollectionsApi, "get_collection", returns=published)
    patch = coll_backend.on(CollectionsApi, "patch_collection")
    user_client.post("/gui/collection/edit/1", data=_form(), headers=REFERER)
    assert patch.call_args.kwargs["collection_req"].title == "My collection"


def test_collection_save_refused_shows_error(user_client, coll_backend):
    coll_backend.on(CollectionsApi, "patch_collection", raises=api_exception(403, "not yours"))
    rsp = user_client.post("/gui/collection/edit/1", data=_form(), headers=REFERER)
    # the form again, with the reason in an alert box, as for a project
    assert rsp.status_code == 200
    assert "not yours" in rsp.get_data(as_text=True)


def test_collection_create_refused_shows_error(user_client, coll_backend):
    coll_backend.on(CollectionsApi, "create_collection", raises=api_exception(422, "bad title"))
    rsp = user_client.post("/gui/collection/create", data={"save": "Y", "title": "T", "project_ids[]": ["1"]})
    assert rsp.status_code == 200
    assert "bad title" in rsp.get_data(as_text=True)


def test_collection_unknown_goes_to_noright(user_client, backend):
    backend.on(CollectionsApi, "get_collection", raises=api_exception(404))
    rsp = user_client.get("/gui/collection/edit/9")
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == "/gui/collection/noright/9"


def test_collection_erase_confirm_page(user_client, coll_backend):
    rsp = user_client.get("/gui/collection/erase/1")
    assert rsp.status_code == 200


def test_collection_erase(user_client, coll_backend):
    erase = coll_backend.on(CollectionsApi, "erase_collection", returns=1)
    rsp = user_client.post("/gui/collection/erase/1")
    assert rsp.status_code == 200
    erase.assert_called_once_with(1)


@pytest.mark.parametrize("status", [403, 409, 500])
def test_collection_erase_refused(user_client, coll_backend, status):
    coll_backend.on(CollectionsApi, "erase_collection", raises=api_exception(status))
    rsp = user_client.post("/gui/collection/erase/1")
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == "/gui/collection/noright/1"


def test_collection_save_without_referer(user_client, coll_backend):
    coll_backend.on(CollectionsApi, "patch_collection")
    rsp = user_client.post("/gui/collection/edit/1", data=_form())
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == "/gui/collection/edit/1"
