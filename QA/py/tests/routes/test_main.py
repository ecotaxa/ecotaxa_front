import json

import pytest

from fakes import api_exception, make_user, model
from to_back.ecotaxa_cli_py.api import AuthentificationApi, UsersApi
from to_back.ecotaxa_cli_py.models import TokenRsp


@pytest.mark.parametrize("url", ["/", "/gui", "/gui/", "/gui/home", "/gui/index"])
def test_index_anonymous(anon_client, url):
    rsp = anon_client.get(url)
    assert rsp.status_code == 200
    assert b"<html" in rsp.data.lower()


def test_index_logged_in(user_client):
    rsp = user_client.get("/gui/")
    assert rsp.status_code == 200
    assert user_client.user.name.encode() in rsp.data


def test_login_page(anon_client):
    rsp = anon_client.get("/gui/login")
    assert rsp.status_code == 200
    assert b'name="email"' in rsp.data and b'name="password"' in rsp.data


def test_login_page_redirects_logged_user(user_client):
    rsp = user_client.get("/gui/login")
    assert rsp.status_code == 302


def test_login_missing_fields(anon_client):
    rsp = anon_client.post("/gui/login", data={"email": "", "password": ""})
    assert rsp.status_code == 200


def test_login_success_sets_session(anon_client, backend):
    user = make_user(id=42)
    tok = backend.on(
        AuthentificationApi,
        "token",
        returns=model(TokenRsp, access_token="ACCESS", refresh_token="REFRESH", token_type="bearer"),
    )
    revoke = backend.on(AuthentificationApi, "revoke_token")
    backend.on(UsersApi, "show_current_user", returns=user)
    rsp = anon_client.post(
        "/gui/login", data={"email": "user@example.org", "password": "Secret#123", "next": "https://evil.example/gui/prj/"}
    )
    assert rsp.status_code == 302
    # next is kept but its domain is dropped
    assert rsp.headers["Location"] == "/gui/prj/"
    tok.assert_called_once_with("user@example.org", "Secret#123")
    assert revoke.call_args.args[0].refresh_token == "REFRESH"
    with anon_client.session_transaction() as sess:
        assert str(sess["_user_id"]) == "42"


def test_login_bad_password(anon_client, backend):
    backend.on(AuthentificationApi, "token", raises=api_exception(403, "bad"))
    rsp = anon_client.post("/gui/login", data={"email": "user@example.org", "password": "wrong"})
    assert rsp.status_code == 302
    assert rsp.headers["Location"].rstrip("/").endswith("/gui/login")
    with anon_client.session_transaction() as sess:
        assert "_user_id" not in sess


def test_logout(user_client):
    rsp = user_client.get("/gui/logout")
    assert rsp.status_code == 302
    assert rsp.headers["Location"].rstrip("/").endswith("/gui/login")
    with user_client.session_transaction() as sess:
        assert "_user_id" not in sess


def test_i18n_json(anon_client):
    rsp = anon_client.get("/gui/i18n")
    assert rsp.status_code == 200
    assert isinstance(rsp.get_json(), dict)


@pytest.mark.parametrize("url", ["/gui/about/", "/gui/privacy/", "/gui/colors/"])
def test_public_pages(anon_client, url):
    rsp = anon_client.get(url)
    assert rsp.status_code == 200, url


def test_help_register(anon_client):
    assert anon_client.get("/gui/help/register").status_code == 200
