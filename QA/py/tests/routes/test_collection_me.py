import gzip
import json

import pytest
import responses

BACK = "http://backend.test"


def _coll_json(id=1, title="My collection", project_ids=(1, 2)):
    user = {"id": 42, "name": "Test User", "email": "user@example.org", "organisation": "Org"}
    return {
        "id": id,
        "title": title,
        "short_title": "MC",
        "external_id": "",
        "external_id_system": "",
        "citation": "",
        "license": "CC BY 4.0",
        "abstract": "",
        "description": "",
        "project_ids": list(project_ids),
        "provider_user": user,
        "contact_user": user,
        "creator_users": [],
        "creator_organisations": [],
        "associate_users": [],
        "associate_organisations": [],
        "display_order": None,
        "is_private": False,
    }


def test_collections_page(user_client):
    assert user_client.get("/gui/collection/").status_code == 200


def test_collections_list_json(user_client, backend):
    backend.requests.add(responses.GET, BACK + "/collections", json=[_coll_json(1), _coll_json(2, "Second")])
    rsp = user_client.get("/gui/collectionlist/?project_ids=1,2")
    assert rsp.status_code == 200
    assert rsp.headers["Content-Encoding"] == "gzip"
    body = json.loads(gzip.decompress(rsp.data))
    assert set(body) >= {"columns", "data"}
    assert len(body["data"]) == 2
    (call,) = backend.requests.calls
    assert "project_ids=1%2C2" in call.request.url


def test_me_page(user_client):
    rsp = user_client.get("/gui/me")
    assert rsp.status_code == 200


def test_me_files_page(user_client):
    rsp = user_client.get("/gui/me/files")
    assert rsp.status_code == 200


def test_me_upload_is_gone(user_client):
    # dead async route removed, uploads go through /gui/files/upload
    assert user_client.get("/gui/me/upload").status_code == 404
