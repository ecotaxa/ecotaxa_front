import enum
import json

import pytest

from appli.gui import commontools as ct
from fakes import api_exception


# ------------------------------------------------------------------ breadcrumbs


def _crumbs(app, path, default=None):
    with app.test_request_context(path):
        return ct.breadcrumbs(default)


def test_breadcrumb_lookup():
    from appli.gui.staticlistes import apptree

    text, child = ct.breadcrumb(apptree, "prj")
    assert text == "Projects" and "edit" in child
    assert ct.breadcrumb(child, "edit") == ("settings", None)
    assert ct.breadcrumb(apptree, "unknown") == (None, None)
    assert ct.breadcrumb("leaf", "whatever") == ("leaf", None)


def test_breadcrumbs_static_is_empty(app):
    assert _crumbs(app, "/static/gui/x.css") == []


def test_breadcrumbs_project_settings(app):
    crumbs = _crumbs(app, "/gui/prj/edit/123")
    assert [c["text"] for c in crumbs] == ["Home", "Projects", "settings"]
    assert crumbs[1]["url"] == "/prj"


def test_breadcrumbs_job_view_uses_jobs_crumb(app):
    # old /gui/job/... route, shown like projects: Home > Jobs > View
    crumbs = _crumbs(app, "/gui/job/show/12")
    assert [c["text"] for c in crumbs] == ["Home", "Jobs", "View"]
    assert crumbs[1]["url"] == "/gui/jobs"


def test_breadcrumbs_jobs_list(app):
    crumbs = _crumbs(app, "/gui/jobs/listall")
    assert [c["text"] for c in crumbs] == ["Home", "Jobs"]


def test_breadcrumbs_carry_trailing_id(app):
    # /gui/prj/123: the "Projects" crumb is followed by the project id
    crumbs = _crumbs(app, "/gui/prj/123")
    assert crumbs[-1]["text"] == "Projects"
    assert crumbs[-1]["id"] == "123"


def test_breadcrumbs_no_id_when_not_numeric(app):
    crumbs = _crumbs(app, "/gui/prj/edit")
    assert all("id" not in c for c in crumbs)


# ------------------------------------------------------------------ misc helpers


def test_html_to_text():
    assert ct.html_to_text("<b>bold</b> &amp; <i>it</i>&#123;") == "bold  it"


class _Color(enum.Enum):
    RED = 1


class _Slotted:
    __slots__ = ("a", "b")

    def __init__(self):
        self.a = 1
        self.b = [_Color.RED]


class _Plain:
    def __init__(self):
        self.x = {"k": _Slotted()}


def test_todict_recurses():
    assert ct.todict(_Plain()) == {"x": {"k": {"a": 1, "b": ["_Color.RED"]}}}
    assert ct.todict("str") == "str"
    assert ct.todict(3) == 3


def test_crsf_token_shape():
    tok = ct.crsf_token()
    assert len(tok) == 45 and tok.isalnum()
    assert tok != ct.crsf_token()


def test_make_response():
    assert ct.make_response(0, "ok") == {"status": 0, "message": "ok"}


def test_format_exception_json_detail():
    status, msg = ct.format_exception(api_exception(422, "bad field"))
    assert status == 422
    assert msg == "422 - bad field"


def test_format_exception_500_keeps_raw_body():
    exc = api_exception(500)
    exc.body = "Internal Server Error"
    assert ct.format_exception(exc) == (500, "500 - Internal Server Error")


def test_format_exception_plain_exception():
    assert ct.format_exception(ValueError("x")) == (None, "")


def test_format_exception_non_json_body():
    exc = api_exception(502)
    exc.body = "<html>Bad Gateway</html>"
    status, msg = ct.format_exception(exc)
    assert status == 502
    assert msg == "502 - <html>Bad Gateway</html>"


def test_format_exception_json_not_an_object():
    exc = api_exception(422)
    exc.body = '["a"]'
    assert ct.format_exception(exc) == (422, "422 - ")


@pytest.mark.parametrize(
    "url, location",
    [
        ("https://evil.example/prj/1?x=1#top", "/prj/1?x=1#top"),
        ("//evil.example/prj/1", "/prj/1"),
        ("/gui/prj/", "/gui/prj/"),
        # would leave the site: browsers read "/\host" and "//host" as another host
        ("/\\evil.example/", "/evil.example/"),
        ("https://x//evil.example/p", "/evil.example/p"),
        ("\\\\evil.example", "/evil.example"),
    ],
)
def test_safe_url_redir_strips_domain(app, url, location):
    with app.test_request_context("/"):
        rsp = ct.safe_url_redir(url)
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == location


def test_safe_url_redir_empty(app):
    with app.test_request_context("/"):
        assert ct.safe_url_redir("  ") == ""


def test_safe_url_redir_backslash(app):
    with app.test_request_context("/"):
        rsp = ct.safe_url_redir("/\\evil.example/")
    assert not rsp.headers["Location"].startswith("/\\")


def test_is_partial_request(app):
    with app.test_request_context("/", headers={"X-Requested-With": "XMLHttpRequest"}):
        assert ct.is_partial_request()
    with app.test_request_context("/"):
        assert not ct.is_partial_request()


@pytest.mark.parametrize("kind", [None, "project", "collection", "jobs", "unknown"])
def test_py_get_messages_merges(app, kind):
    from appli.gui.staticlistes import py_messages

    with app.test_request_context("/"):
        msgs = ct.py_get_messages(kind)
    assert set(py_messages).issubset(msgs)
    json.dumps({k: str(v) for k, v in msgs.items()})
