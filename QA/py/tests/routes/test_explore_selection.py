"""
Selection on the map of the explore page: taxonomy stats for one sample, usual projects table for several.
"""

import json
from types import SimpleNamespace

from fakes import api_exception, make_min_user, make_project, model
from to_back.ecotaxa_cli_py.api import ObjectsApi, ProjectsApi, SamplesApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import (
    ObjectSetQueryRsp,
    SampleModel,
    SampleTaxoStatsModel,
    TaxonModel,
)

MAP_URL = "/gui/explore/map/projects"
SAMPLE = dict(
    sampleid=7, projid=1, orig_id="sample_7", latitude=10.0, longitude=20.0, free_columns={}
)


def one_sample(backend, stats=None):
    backend.on(SamplesApi, "sample_query", returns=model(SampleModel, **SAMPLE))
    backend.on(ProjectsApi, "project_query", returns=make_project(1, title="The project"))
    backend.on(
        ObjectsApi,
        "get_object_set",
        returns=model(ObjectSetQueryRsp, object_ids=[], details=[], total_ids=0),
    )
    if stats is not None:
        backend.on(SamplesApi, "sample_set_get_stats", **stats)


def taxo_stats():
    return dict(
        returns=[
            model(
                SampleTaxoStatsModel,
                sample_id=7,
                used_taxa=[-1, 11, 12],
                nb_unclassified=1,
                nb_validated=222,
                nb_dubious=3,
                nb_predicted=4,
            )
        ]
    )


def test_one_sample_displays_its_taxo_stats(anon_client, backend):
    one_sample(backend, taxo_stats())
    backend.on(
        TaxonomyTreeApi,
        "query_taxa_set",
        returns=[
            model(TaxonModel, id=11, display_name="Copepoda", status="A"),
            model(TaxonModel, id=12, display_name="Oldname", status="D"),
        ],
    )
    rsp = anon_client.post(MAP_URL, data={"samples": "7", "projects": "1"})
    assert rsp.status_code == 200
    html = rsp.data.decode()
    assert "The project" in html and "sample_7" in html
    assert "222" in html
    assert "<li>Copepoda</li>" in html
    assert '<li class="deprecated">Oldname</li>' in html
    assert "notfound" not in html
    # the stats are the ones of the sample, not the project ones
    assert not backend.api(ProjectsApi).project_set_get_stats.called


def test_one_sample_is_displayed_without_stats(anon_client, backend):
    one_sample(backend, dict(raises=api_exception(500)))
    rsp = anon_client.post(MAP_URL, data={"samples": "7", "projects": "1"})
    assert rsp.status_code == 200
    assert "sample_7" in rsp.data.decode()


def test_one_sample_refused(anon_client, backend):
    backend.on(SamplesApi, "sample_query", raises=api_exception(403))
    rsp = anon_client.post(MAP_URL, data={"samples": "7", "projects": "1"})
    assert rsp.status_code == 200
    assert "Access denied" in rsp.data.decode()


def test_several_samples_need_no_back_end_call(anon_client, backend):
    # unexpected back-end calls would fail the test
    rsp = anon_client.post(MAP_URL, data={"samples": "7,8,9", "projects": "2,1,x,2"})
    assert rsp.status_code == 200
    html = rsp.data.decode()
    assert 'data-from="exploreprojects"' in html
    assert 'data-fromid="1,2"' in html
    # the details are for logged users
    assert "data-details" not in html


def test_several_samples_logged_user_has_details(user_client, backend):
    rsp = user_client.post(MAP_URL, data={"samples": "7,8", "projects": "1"})
    assert "data-detailsurl=/gui/prj/about/" in rsp.data.decode()


def projects_search(backend, granted, others):
    def search(**kw):
        return others if kw.get("not_granted") else granted

    return backend.on(ProjectsApi, "search_projects", side_effect=search)


def table_rows(client, ids):
    rsp = client.get("/gui/explore/projects/" + ids)
    assert rsp.status_code == 200
    table = json.loads(rsp.data)
    names = list(table["columns"].keys())
    return [dict(zip(names, row)) for row in table["data"]]


def test_table_anonymous_only_open_projects(anon_client, backend):
    # as the boosted client answers an anonymous call: no attribute for the members
    public = [
        SimpleNamespace(projid=i, title=" Prj %d " % i, instrument="UVP6", status="Annotate",
                        access=access, objcount=10.0, pctvalidated=50.0)
        for i, access in ((1, "2"), (2, "1"), (3, "2"), (4, "2"))
    ]
    projects_search(backend, public, public)
    rows = table_rows(anon_client, "1,2,3")
    # 2 is public, not open. 4 is not asked for. No duplicate from the 2 searches
    assert [row["projid"] for row in rows] == [1, 3]
    assert rows[0]["title"] == ["Prj 1", 0]
    assert rows[0]["contact"] == ""
    assert "V" in rows[0]["select"]
    assert "M" not in rows[0]["select"]
    # no access request and no status for an anonymous user, the cells staying under their columns
    assert "R" not in rows[0]["select"]
    assert "status" not in rows[0]
    assert rows[0]["instrument"] == "UVP6"
    assert rows[0]["objcount"] == 10.0


def test_table_logged_user_rights(user_client, backend):
    me = make_min_user(id=42)
    mine = make_project(1, managers=[me], contact=me)
    other = make_project(2, managers=[make_min_user(id=9, name="Other")], access="1")
    projects_search(backend, [mine], [other])
    rows = table_rows(user_client, "1,2")
    assert [row["projid"] for row in rows] == [1, 2]
    assert "M" in rows[0]["select"]
    assert rows[0]["title"][1] == 1
    assert "M" not in rows[1]["select"] and "V" in rows[1]["select"]
    assert "R" in rows[1]["select"]
    assert rows[1]["status"]
    assert rows[1]["title"][1] == 0
    assert rows[1]["contact"]["name"] == "Other"
