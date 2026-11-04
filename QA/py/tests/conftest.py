"""
Fixtures for the ecotaxa_front test suite.

- The Flask app is the module-level appli.app, configured from QA/py/conftest_config.cfg.
- The back-end is never reached: see fakes.FakeBackend (generated client), `responses`
  (raw `requests` calls) and a socket guard for anything else.
"""

import os
import shutil
import socket
from pathlib import Path

import pytest

QA_PY = Path(__file__).resolve().parent.parent
REPO_ROOT = QA_PY.parent.parent
os.environ["ECOTAXA_FRONT_CONFIG"] = str(QA_PY / "conftest_config.cfg")
# Relative paths in the app (templates, config/*.html, i18n) are resolved from the repo root
os.chdir(REPO_ROOT)

import responses as responses_lib  # noqa: E402

from fakes import (  # noqa: E402
    FakeBackend,
    load_constants,
    make_user,
    ROLE_APP_ADMIN,
    ROLE_USERS_ADMIN,
)


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    import appli

    flask_app = appli.app
    msg_file = tmp_path_factory.mktemp("cfg") / "messages.json"
    shutil.copy(REPO_ROOT / "config" / "messages.json", msg_file)
    flask_app.config.update(
        TESTING=True,
        APP_GUI_MESSAGE_FILE=str(msg_file),
        SERVER_NAME=None,
    )
    return flask_app


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Any real TCP connection is a test bug."""

    def guard(self, address, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise RuntimeError(f"Network access attempted in tests: {address}")
        return orig_connect(self, address, *args, **kwargs)

    orig_connect = socket.socket.connect
    monkeypatch.setattr(socket.socket, "connect", guard)


@pytest.fixture
def backend(app, monkeypatch):
    """Strict fake for the generated API client, plus `responses` for raw requests."""
    from appli.utils import ApiClient
    from to_back.ecotaxa_cli_py.api import MiscApi

    fake = FakeBackend()

    def fake_enter(self):
        mock = fake.api(type(self.under))
        # Real configuration (host, token): some views build raw `requests` calls from it
        mock.api_client = self.under.api_client
        return mock

    monkeypatch.setattr(ApiClient, "__enter__", fake_enter)
    # Constants: the real get_back_constants() code runs, on top of a fixed answer
    fake.on(MiscApi, "used_constants", returns=load_constants())
    for key in [k for k in app.config if k.startswith("API_") and k.endswith("_CONSTANTS")]:
        del app.config[key]
    # Job summary in the page header
    monkeypatch.setattr("appli.jobs.emul._build_jobs_summary", lambda: {})

    with responses_lib.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        fake.requests = rsps
        yield fake

    assert not fake.unexpected, "\n".join(fake.unexpected)


def page_chrome(backend):
    """Back-end calls made by the layout of any page."""
    from datetime import datetime
    from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi, UsersApi
    from to_back.ecotaxa_cli_py.models import TaxonomyTreeStatus
    from fakes import make_min_user

    # managers contact (footer, help)
    backend.on(UsersApi, "get_users_admins", returns=[make_min_user(id=1, name="App Admin", email="admin@example.org")])

    backend.on(
        TaxonomyTreeApi,
        "taxa_tree_status",
        returns=TaxonomyTreeStatus(last_refresh=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
    )


def _client_as(app, backend, user):
    from to_back.ecotaxa_cli_py.api import UsersApi

    client = app.test_client()
    page_chrome(backend)
    if user is not None:
        backend.on(UsersApi, "show_current_user", returns=user)
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True
    client.user = user
    return client


@pytest.fixture
def anon_client(app, backend):
    return _client_as(app, backend, None)


@pytest.fixture
def user_client(app, backend):
    return _client_as(app, backend, make_user(id=42))


@pytest.fixture
def admin_client(app, backend):
    return _client_as(
        app, backend, make_user(id=1, roles=(ROLE_APP_ADMIN,), name="App Admin", email="admin@example.org")
    )


@pytest.fixture
def users_admin_client(app, backend):
    return _client_as(
        app, backend, make_user(id=2, roles=(ROLE_USERS_ADMIN,), name="Users Admin", email="uadmin@example.org")
    )


@pytest.fixture
def req_ctx(app, backend):
    """A request context, for helpers that read flask.request / current_app."""
    with app.test_request_context("/gui/"):
        yield
