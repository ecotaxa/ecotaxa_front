import pytest
from itsdangerous import URLSafeTimedSerializer, TimestampSigner

from fakes import api_exception, model, populate
from to_back.ecotaxa_cli_py.api import GuestsApi, OrganizationsApi
from to_back.ecotaxa_cli_py.models import OrganizationModel


def _token(app, payload):
    return URLSafeTimedSerializer(
        app.config["MAILSERVICE_SECRET_KEY"], salt=app.config["MAILSERVICE_SALT"].encode(), signer=TimestampSigner
    ).dumps(payload)


def test_create_organization_with_edmo(user_client, backend):
    populate(backend)
    create = backend.on(OrganizationsApi, "create_organization", returns=12)
    rsp = user_client.post("/gui/persons/create?type=organization", data={"name": "New Org", "edmo": "1278"})
    body = rsp.get_json()
    assert body["success"] is True and body["organization"] == {"id": 12, "name": "New Org"}
    kw = create.call_args.kwargs
    assert kw["organization_model"].directories == "edmo:1278"
    assert kw["token"] is None


def test_create_organization_from_registration(app, anon_client, backend):
    populate(backend)
    create = backend.on(OrganizationsApi, "create_organization", returns=13)
    tok = _token(app, {"id": "-1", "email": "new@example.org"})
    rsp = anon_client.post(f"/gui/persons/create?type=organization&token={tok}", data={"name": "Org", "edmo": ""})
    assert rsp.get_json()["success"] is True
    assert create.call_args.kwargs["token"] == tok
    assert create.call_args.kwargs["organization_model"].directories is None


def test_anonymous_without_token_cannot_create(anon_client):
    rsp = anon_client.post("/gui/persons/create?type=organization", data={"name": "Org"})
    assert rsp.status_code == 302
    assert "/gui/login" in rsp.headers["Location"]


def test_anonymous_cannot_create_guest_even_with_token(app, anon_client):
    tok = _token(app, {"id": "-1"})
    rsp = anon_client.post(f"/gui/persons/create?type=guest&token={tok}", data={"name": "G"})
    assert rsp.status_code == 302


def test_create_organization_http_status(user_client, backend):
    populate(backend)
    backend.on(OrganizationsApi, "create_organization", returns=12)
    rsp = user_client.post("/gui/persons/create?type=organization", data={"name": "New Org", "edmo": ""})
    assert rsp.status_code == 200


def test_create_organization_bad_edmo(user_client, backend):
    populate(backend)
    rsp = user_client.post("/gui/persons/create?type=organization", data={"name": "Org", "edmo": "12ab"})
    assert rsp.status_code == 422
    assert rsp.get_json()["error"] == 1


@pytest.mark.parametrize("back_status, status", [(401, 403), (403, 403), (404, 422), (409, 422), (500, 422)])
def test_create_organization_refused(user_client, backend, back_status, status):
    populate(backend)
    backend.on(OrganizationsApi, "create_organization", raises=api_exception(back_status, "refused"))
    rsp = user_client.post("/gui/persons/create?type=organization", data={"name": "Org", "edmo": ""})
    assert rsp.status_code == status
    assert rsp.get_json()["error"] == 1


def test_admin_edits_organization_keeps_other_directories(admin_client, backend):
    populate(backend)
    backend.on(
        OrganizationsApi, "get_organizations", returns=[model(OrganizationModel, id=3, name="IMEV", directories="edmo:1,ror:abc")]
    )
    update = backend.on(OrganizationsApi, "update_organization", returns=3)
    rsp = admin_client.post("/gui/admin/organizations/edit/3", data={"name": "IMEV2", "edmo": "2"})
    assert rsp.status_code == 302
    sent = update.call_args.kwargs["organization_model"]
    assert sent["name"] == "IMEV2" and sent["directories"] == "edmo:2,ror:abc"


def _guest_form(**kw):
    data = {"firstname": "Gus", "lastname": "Guest", "email": "gus@example.org", "organisation": "IMEV", "country": "France", "orcid": ""}
    data.update(kw)
    return data


def test_create_guest(user_client, backend):
    populate(backend)
    create = backend.on(GuestsApi, "create_guest", returns=21)
    rsp = user_client.post("/gui/admin/guests/create", data=_guest_form())
    assert rsp.status_code in (200, 302)
    sent = create.call_args.kwargs["guest_model"]
    assert sent.email == "gus@example.org"
    assert sent.name.strip() == "Gus Guest"


def test_create_guest_refused(user_client, backend):
    populate(backend)
    backend.on(GuestsApi, "create_guest", raises=api_exception(422, "exists"))
    rsp = user_client.post("/gui/admin/guests/create", data=_guest_form())
    assert rsp.status_code == 302
    assert rsp.headers["Location"].rstrip("/").endswith("/gui/admin/guests")


def test_admin_creates_user(users_admin_client, backend):
    from to_back.ecotaxa_cli_py.api import UsersApi

    populate(backend)
    create = backend.on(UsersApi, "create_user", returns=88)
    data = {
        "firstname": "New",
        "lastname": "User",
        "email": "nu@example.org",
        "password": "Secret#1234",
        "organisation": "IMEV",
        "country": "France",
        "orcid": "",
        "usercreationreason": "",
        "status": "1",
        "can_do": ["1"],
    }
    rsp = users_admin_client.post("/gui/admin/users/create", data=data)
    assert rsp.status_code == 200
    sent = create.call_args.kwargs["user_model_with_rights"]
    assert sent.name == "New User" and sent.email == "nu@example.org"
