import gzip
import json

import pytest

from fakes import make_user, model
from to_back.ecotaxa_cli_py.api import GuestsApi, OrganizationsApi, UsersApi
from to_back.ecotaxa_cli_py.models import GuestModel, OrganizationModel


def _body(rsp):
    data = rsp.data
    if rsp.headers.get("Content-Encoding") == "gzip":
        data = gzip.decompress(data)
    return json.loads(data)


@pytest.mark.parametrize("client_fixture", ["admin_client", "users_admin_client"])
@pytest.mark.parametrize("gz", ["", "1"])
def test_admin_users_list_json(request, backend, client_fixture, gz):
    client = request.getfixturevalue(client_fixture)
    users = [make_user(id=3, name="Ann"), make_user(id=4, name="Bob", status=0)]
    get_users = backend.on(UsersApi, "get_users", returns=users)
    rsp = client.get("/gui/admin/userslist/" + ("?gzip=1" if gz else ""))
    assert rsp.status_code == 200
    body = _body(rsp)
    assert list(body) == ["columns", "data"]
    cols = list(body["columns"])
    rows = body["data"]
    assert [r[cols.index("name")] for r in rows] == ["Ann", "Bob"]
    assert [r[cols.index("status")] for r in rows] == ["active", "inactive"]
    get_users.assert_called_once_with(ids="")


def test_guests_list_json(user_client, backend):
    guests = [model(GuestModel, id=9, name="Guest", email="g@example.org", country="France", orcid=None, organisation="Org")]
    get_guests = backend.on(GuestsApi, "get_guests", returns=guests)
    rsp = user_client.get("/gui/guestslist/?ids=9")
    assert rsp.status_code == 200
    body = _body(rsp)
    cols = list(body["columns"])
    assert body["data"][0][cols.index("name")] == "Guest"
    get_guests.assert_called_once_with(ids="9")


def test_organizations_list_json(user_client, backend):
    orgs = [model(OrganizationModel, id=1, name="IMEV", directories="edmo:1278,ror:abc")]
    backend.on(OrganizationsApi, "get_organizations", returns=orgs)
    rsp = user_client.get("/gui/organizationslist/")
    assert rsp.status_code == 200
    body = _body(rsp)
    cols = list(body["columns"])
    assert body["data"][0][cols.index("name")] == "IMEV"


def test_admin_home_for_admin(admin_client, backend):
    from fakes import make_min_user

    backend.on(UsersApi, "get_admin_users", returns=[make_min_user(id=1, name="App Admin")])
    rsp = admin_client.get("/gui/admin/")
    assert rsp.status_code == 200
    assert b"App Admin" in rsp.data


def test_site_message_page(admin_client):
    rsp = admin_client.get("/gui/admin/messages/")
    assert rsp.status_code == 200
