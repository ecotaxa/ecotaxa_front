"""
Each page renders (200) for the expected kind of user, with the back-end answering plausible data
(fakes.populate). Catches template errors and missing context, not the page logic.
"""

import pytest

from fakes import populate

PAGES = [
    ("user_client", "/gui/me/profile", b"Test User"),
    ("anon_client", "/gui/register/", b"<form"),
    ("admin_client", "/gui/admin/users/", None),
    ("admin_client", "/gui/admin/users/edit/3", b"user@example.org"),
    ("admin_client", "/gui/admin/users/create", b"<form"),
    ("admin_client", "/gui/admin/guests/edit/3", b"g@example.org"),
    ("admin_client", "/gui/admin/organizations/edit/3", b"IMEV"),
    ("user_client", "/gui/admin/guests/create", b"<form"),
    ("user_client", "/gui/admin/organizations/create", b"<form"),
    ("user_client", "/gui/prj/edit/1", b"Test project"),
    ("user_client", "/gui/prj/about/1", b"Test project"),
    ("user_client", "/gui/prj/purge/1", b"Test project"),
    ("user_client", "/gui/prj/merge/1", b"Test project"),
    ("user_client", "/gui/prj/editannot/1", b"Test project"),
    ("user_client", "/gui/prj/editdatamass/1", b"Test project"),
    ("user_client", "/gui/prj/importsettings", None),
    ("user_client", "/gui/collection/create", b"<form"),
    ("user_client", "/gui/collection/edit/1", b"My collection"),
    ("user_client", "/gui/collection/about/1", None),
    ("user_client", "/gui/taxo/browse/", None),
    ("user_client", "/gui/jobs/listall", None),
]


@pytest.mark.parametrize("client_fixture, url, expected", PAGES, ids=[p[1] for p in PAGES])
def test_page_renders(request, backend, client_fixture, url, expected):
    populate(backend)
    client = request.getfixturevalue(client_fixture)
    rsp = client.get(url)
    assert rsp.status_code == 200, url
    if expected is not None:
        assert expected in rsp.data, url


def test_prjsamplestats_json(user_client, backend):
    populate(backend)
    rsp = user_client.get("/gui/prjsamplestats/1")
    assert rsp.status_code == 200
    assert rsp.is_json


def test_project_create_needs_creation_right(user_client, backend):
    populate(backend)
    assert user_client.get("/gui/prj/create").status_code == 403


def test_project_create_for_creator(app, backend):
    from conftest import _client_as
    from fakes import make_user

    populate(backend)
    # right 1 = create projects
    client = _client_as(app, backend, make_user(id=50, roles=(1,)))
    rsp = client.get("/gui/prj/create")
    assert rsp.status_code == 200
    assert b"<form" in rsp.data
