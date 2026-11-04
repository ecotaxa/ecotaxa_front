"""Content-Encoding is only for compression; the charset goes in Content-Type."""

import gzip
import json

from fakes import make_user
from to_back.ecotaxa_cli_py.api import UsersApi


def _assert_plain_json(rsp):
    assert rsp.status_code == 200
    assert "Content-Encoding" not in rsp.headers
    assert rsp.headers["Content-Type"].startswith("application/json")
    json.loads(rsp.data)


def test_i18n_headers(anon_client):
    _assert_plain_json(anon_client.get("/gui/i18n"))


def test_userslist_plain(admin_client, backend):
    backend.on(UsersApi, "get_users", returns=[make_user(id=3)])
    _assert_plain_json(admin_client.get("/gui/admin/userslist/"))


def test_userslist_gzip(admin_client, backend):
    backend.on(UsersApi, "get_users", returns=[make_user(id=3)])
    rsp = admin_client.get("/gui/admin/userslist/?gzip=1")
    assert rsp.status_code == 200
    assert rsp.headers["Content-Encoding"] == "gzip"
    assert rsp.headers["Content-Type"] == "application/json; charset=utf-8"
    assert "data" in json.loads(gzip.decompress(rsp.data))
