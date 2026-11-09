"""
Filters of the explore page, on the samples of the map: projects, instrument and lat/lon box.
"""

import json

import pytest

from conftest import page_chrome
from fakes import make_project, model
from to_back.ecotaxa_cli_py.api import ProjectsApi, SamplesApi
from to_back.ecotaxa_cli_py.models import SampleModel

URL = "/search/mappopup/samples/"


def sample(sampleid, projid=1, lat=10.0, lon=20.0):
    return model(
        SampleModel,
        sampleid=sampleid,
        projid=projid,
        orig_id="s%d" % sampleid,
        latitude=lat,
        longitude=lon,
        free_columns={},
    )


def set_projects(backend, projects):
    """Projects of the user, none among the not granted ones."""

    def search(**kw):
        return [] if kw.get("not_granted") else projects

    return backend.on(ProjectsApi, "search_projects", side_effect=search)


def get_ids(client, **args):
    rsp = client.get(URL, query_string=args)
    assert rsp.status_code == 200
    return [a_sam["id"] for a_sam in json.loads(rsp.data)]


@pytest.mark.parametrize(
    "args, expected",
    [
        ({}, [1, 2, 3, 4]),
        ({"MapN": "0"}, [2, 3]),
        ({"MapS": "0"}, [1, 4]),
        ({"MapN": "50", "MapS": "-50"}, [1, 2, 3, 4]),
        ({"MapW": "0"}, [1, 2]),
        ({"MapE": "0"}, [3, 4]),
        ({"MapN": "50", "MapS": "0", "MapW": "0", "MapE": "50"}, [1]),
        # invalid values don't filter
        ({"MapN": "north"}, [1, 2, 3, 4]),
        ({"MapN": "nan", "MapE": "inf", "MapW": ""}, [1, 2, 3, 4]),
        # box across the antimeridian
        ({"MapW": "170", "MapE": "-170"}, [2, 3]),
    ],
)
def test_lat_lon_box(user_client, backend, args, expected):
    backend.on(
        SamplesApi,
        "samples_search",
        returns=[
            sample(1, lat=10, lon=20),
            sample(2, lat=-10, lon=175),
            sample(3, lat=-20, lon=-175),
            sample(4, lat=20, lon=-20),
        ],
    )
    assert get_ids(user_client, projid="1", **args) == expected


def test_no_filter_searches_all_visible_projects(user_client, backend):
    search_prj = set_projects(backend, [make_project(1), make_project(2)])
    search = backend.on(SamplesApi, "samples_search", returns=[sample(1)])
    assert get_ids(user_client) == [1]
    assert search.call_args.kwargs["project_ids"] == "1+2"
    assert "instrument_filter" not in search_prj.call_args.kwargs


def test_projects_filter_needs_no_project_search(user_client, backend):
    # an unexpected ProjectsApi call would fail the test
    search = backend.on(SamplesApi, "samples_search", returns=[sample(1)])
    assert get_ids(user_client, projid="3,4") == [1]
    assert search.call_args.kwargs["project_ids"] == "3+4"


def test_instrument_is_compared_as_a_whole(user_client, backend):
    # the back-end matches a part of the code
    search_prj = set_projects(
        backend,
        [make_project(1, instrument="UVP6"), make_project(2, instrument="UVP6LP")],
    )
    search = backend.on(SamplesApi, "samples_search", returns=[sample(1)])
    assert get_ids(user_client, instrum="UVP6") == [1]
    assert search.call_args.kwargs["project_ids"] == "1"
    assert search_prj.call_args.kwargs["instrument_filter"] == "UVP6"
    assert "instrument" in search_prj.call_args.kwargs["fields"]


def test_instrument_and_projects_are_crossed(user_client, backend):
    set_projects(
        backend,
        [make_project(1, instrument="UVP6"), make_project(2, instrument="UVP6")],
    )
    search = backend.on(SamplesApi, "samples_search", returns=[sample(1)])
    assert get_ids(user_client, instrum="UVP6", projid="2,3") == [1]
    assert search.call_args.kwargs["project_ids"] == "2"


def test_instrument_without_project_returns_nothing(user_client, backend):
    # no samples search: an unexpected SamplesApi call would fail the test
    set_projects(backend, [make_project(1, instrument="Zooscan")])
    assert get_ids(user_client, instrum="UVP6") == []


def test_anonymous_page_has_the_filters(anon_client, backend):
    page_chrome(backend)
    rsp = anon_client.get("/gui/explore/")
    assert rsp.status_code == 200
    assert b'data-filters="explore-filters"' in rsp.data
    assert b'data-type="exploreproject"' in rsp.data
