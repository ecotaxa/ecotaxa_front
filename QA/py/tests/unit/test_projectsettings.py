import json

import pytest

from appli.gui.project.projectsettings import (
    _manage_prefixes,
    _formulae_str_to_dict,
    _formulae_to_json_str,
)


@pytest.mark.parametrize(
    "back, front",
    [
        ("sam.tot_vol/1000", "sample.tot_vol/1000"),
        ("1/ssm.sub_part", "1/subsample.sub_part"),
        ("obj.area*ssm.pixel_size", "object.area*subsample.pixel_size"),
    ],
)
def test_manage_prefixes_round_trip(back, front):
    assert _manage_prefixes(back, direction=True) == front
    assert _manage_prefixes(front, direction=False) == back


def test_manage_prefixes_subsample_not_mangled_by_sample():
    assert _manage_prefixes("subsample.x + sample.y", direction=False) == "ssm.x + sam.y"


@pytest.mark.parametrize("alias", ["acquisition", "process"])
def test_manage_prefixes_acq_process_go_to_ssm(alias):
    assert _manage_prefixes(alias + ".x", direction=False) == "ssm.x"


def test_manage_prefixes_blanks_legacy_defaults():
    assert _manage_prefixes("total_water_volume/1000") == ""
    assert _manage_prefixes("1/subsampling_coefficient", direction=False) == ""


@pytest.mark.parametrize("empty", [None, "None", "", "   ", "{}"])
def test_formulae_str_to_dict_empty(empty):
    assert _formulae_str_to_dict(empty) is None


def test_formulae_str_to_dict_dict_and_json():
    d = {"subsample_coef": "1/ssm.sub_part"}
    assert _formulae_str_to_dict(d) is d
    assert _formulae_str_to_dict(json.dumps(d)) == d


@pytest.mark.parametrize("sep", ["\n", "\r\n", "\r", " ", ""])
def test_formulae_str_to_dict_legacy(sep):
    txt = sep.join(
        [
            "subsample_coef: 1/ssm.sub_part",
            "total_water_volume: sam.tot_vol/1000",
            "individual_volume: None",
        ]
    )
    assert _formulae_str_to_dict(txt) == {
        "subsample_coef": "1/ssm.sub_part",
        "total_water_volume": "sam.tot_vol/1000",
        "individual_volume": None,
    }


def test_formulae_to_json_str():
    d = {"subsample_coef": "1/ssm.sub_part"}
    assert json.loads(_formulae_to_json_str(d)) == d
    assert _formulae_to_json_str({}) == "{}"
    assert _formulae_to_json_str(None) == "{}"
    assert _formulae_to_json_str('{"a": 1}') == '{"a": 1}'
    assert _formulae_str_to_dict(_formulae_to_json_str(d)) == d
