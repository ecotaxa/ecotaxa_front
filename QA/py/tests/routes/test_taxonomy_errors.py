import json

import pytest

from fakes import api_exception, model
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi, JobsApi
from to_back.ecotaxa_cli_py.models import TaxonModel


def _taxon(id, name, children=(), nb=1, nbc=0, status="A"):
    return model(TaxonModel, id=id, name=name, children=list(children), nb_objects=nb, nb_children_objects=nbc, status=status)


def test_taxotree_roots(user_client, backend):
    backend.on(TaxonomyTreeApi, "query_root_taxa", returns=[_taxon(2, "zeta", [5]), _taxon(1, "alpha", nb=3, nbc=4)])
    rsp = user_client.get("/gui/search/taxotreejson?id=%23")
    assert rsp.status_code == 200
    assert json.loads(rsp.data) == [
        {"id": "1", "parent": "#", "name": "alpha", "num": 7, "children": False, "status": "A"},
        {"id": "2", "parent": "#", "name": "zeta", "num": 1, "children": True, "status": "A"},
    ]


def test_taxotree_children(user_client, backend):
    qset = backend.on(
        TaxonomyTreeApi,
        "query_taxa_set",
        side_effect=lambda ids: [_taxon(10, "parent", [11, 12])] if ids == "10" else [_taxon(12, "b"), _taxon(11, "a", [99])],
    )
    rsp = user_client.get("/gui/search/taxotreejson?id=10")
    assert [(n["id"], n["parent"], n["children"]) for n in json.loads(rsp.data)] == [("11", "10", True), ("12", "10", False)]
    assert [c.kwargs["ids"] for c in qset.call_args_list] == ["10", "11+12"]


def test_taxotree_empty_id(user_client):
    rsp = user_client.get("/gui/search/taxotreejson?id=")
    assert json.loads(rsp.data) == []


def test_unknown_gui_page_is_404(user_client):
    rsp = user_client.get("/gui/this/does/not/exist/really")
    assert rsp.status_code == 404


def test_unknown_url_404(anon_client):
    rsp = anon_client.get("/nowhere-at-all")
    assert rsp.status_code == 404
    assert b"<html" in rsp.data.lower()


def test_unhandled_api_error_renders_error_page(user_client, backend):
    # /gui/job/status does not catch ApiException: the generic handler must answer
    backend.on(JobsApi, "get_job", raises=api_exception(500, "boom"))
    rsp = user_client.get("/gui/job/status/5")
    assert rsp.status_code == 500
