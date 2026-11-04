import pytest


@pytest.fixture
def orgs(req_ctx):
    # module import reads back-end user constants (see appli/gui/users/users.py)
    from appli.gui.organizations import organizations

    return organizations


@pytest.mark.parametrize(
    "dirs, code",
    [(None, ""), ("", ""), ("ror:abc", ""), ("edmo:1278", "1278"), ("ror:abc, edmo:42 ,orcid:x", "42")],
)
def test_edmo_code(orgs, dirs, code):
    assert orgs.edmo_code(dirs) == code


@pytest.mark.parametrize(
    "dirs, code, expected",
    [
        (None, "", None),
        (None, "12", "edmo:12"),
        ("ror:abc", "12", "edmo:12,ror:abc"),
        ("edmo:1, ror:abc", "2", "edmo:2,ror:abc"),
        ("edmo:1, ror:abc", "", "ror:abc"),
        ("edmo:1", "", None),
    ],
)
def test_directories_with_edmo(orgs, dirs, code, expected):
    assert orgs.directories_with_edmo(dirs, code) == expected


def test_round_trip(orgs):
    dirs = orgs.directories_with_edmo("ror:abc", "777")
    assert orgs.edmo_code(dirs) == "777"
