import re
import time

import pytest
from itsdangerous import URLSafeTimedSerializer, TimestampSigner
from markupsafe import escape

from fakes import api_exception, load_constants, make_user, populate
from to_back.ecotaxa_cli_py.api import UsersApi


def _token(app, payload, salt=None):
    auths = URLSafeTimedSerializer(
        app.config["MAILSERVICE_SECRET_KEY"],
        salt=(salt or app.config["MAILSERVICE_SALT"]).encode("UTF-8"),
        signer=TimestampSigner,
    )
    return auths.dumps(payload)


@pytest.fixture
def users_mod(req_ctx):
    from appli.gui.users import users

    return users


# ------------------------------------------------------------------ tokens


def test_token_value(app, users_mod):
    tok = _token(app, {"id": "-1", "email": "new@example.org"})
    assert users_mod.get_value_from_token(tok, "email") == (False, "new@example.org")
    assert users_mod.is_registration_token(tok)


def test_token_for_existing_user_is_not_registration(app, users_mod):
    assert not users_mod.is_registration_token(_token(app, {"id": "42"}))
    assert not users_mod.is_registration_token("  ")


def test_token_bad_signature(app, users_mod):
    tok = _token(app, {"id": "-1"}, salt="other-salt")
    err, msg = users_mod.get_value_from_token(tok, "id")
    assert err is True and msg


def test_token_expired(app, users_mod, monkeypatch):
    tok = _token(app, {"id": "-1"})
    real_time = time.time
    monkeypatch.setattr(time, "time", lambda: real_time() + 3 * 24 * 3600)
    err, msg = users_mod.get_value_from_token(tok, "id", age=1)
    assert err is True and msg


def test_token_empty_is_forbidden(users_mod):
    from werkzeug.exceptions import Forbidden

    with pytest.raises(Forbidden):
        users_mod.get_value_from_token("", "id")


def test_token_missing_id_means_new_user(app, users_mod):
    assert users_mod.get_value_from_token(_token(app, {"email": "x"}), "id") == (False, "-1")


# ------------------------------------------------------------------ profile


def _profile_form(**kw):
    data = {
        "name": "Test User",
        "email": "user@example.org",
        "currentemail": "user@example.org",
        "organisation": "Test Org",
        "country": "France",
        "orcid": "",
        "usercreationreason": "",
        "newpassword": "",
    }
    data.update(kw)
    return data


def test_profile_update(user_client, backend):
    populate(backend)
    update = backend.on(UsersApi, "update_user", returns=42)
    rsp = user_client.post("/gui/me/profile", data=_profile_form(organisation="New Org"))
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == "/gui/me/profile"
    sent = update.call_args.kwargs["user_model_with_rights"]
    assert update.call_args.kwargs["user_id"] == 42
    assert sent["organisation"] == "New Org"
    # a user cannot change own status, password not sent when not changed
    assert "status" not in sent and "password" not in sent


def test_profile_update_new_password(user_client, backend):
    populate(backend)
    update = backend.on(UsersApi, "update_user", returns=42)
    user_client.post("/gui/me/profile", data=_profile_form(newpassword="NewSecret#123"))
    assert update.call_args.kwargs["user_model_with_rights"]["password"] == "NewSecret#123"


def test_profile_email_change_logs_out(user_client, backend):
    populate(backend)
    backend.on(UsersApi, "update_user", returns=42)
    rsp = user_client.post("/gui/me/profile", data=_profile_form(email="new@example.org"))
    assert rsp.status_code == 302
    with user_client.session_transaction() as sess:
        assert "_user_id" not in sess


def test_profile_update_refused(user_client, backend):
    populate(backend)
    backend.on(UsersApi, "update_user", raises=api_exception(403))
    rsp = user_client.post("/gui/me/profile", data=_profile_form())
    assert rsp.status_code == 302


# ------------------------------------------------------------------ admin edits a user


def test_admin_updates_user_status_and_rights(users_admin_client, backend):
    populate(backend)
    update = backend.on(UsersApi, "update_user", returns=3)
    data = _profile_form(email="other@example.org", currentemail="other@example.org", name="Other", status="1", can_do=["1"])
    rsp = users_admin_client.post("/gui/admin/users/edit/3", data=data)
    assert rsp.status_code in (200, 302)
    sent = update.call_args.kwargs["user_model_with_rights"]
    assert update.call_args.kwargs["user_id"] == 3
    # form values, coerced by the back-end
    assert int(sent["status"]) == 1 and [int(r) for r in sent["can_do"]] == [1]


# ------------------------------------------------------------------ registration


def test_register_asks_email_verification(anon_client, backend):
    populate(backend)
    create = backend.on(UsersApi, "create_user", returns=-2)
    rsp = anon_client.post("/gui/register/", data={"id": "-1", "register_email": "new@example.org"})
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == "/gui/index"
    kw = create.call_args.kwargs
    assert kw["user_model_with_rights"].email == "new@example.org"
    assert kw["token"] is None
    # no_bot = [ip, homemade captcha]
    assert len(kw["no_bot"]) == 2


def test_register_refused_goes_back_to_form(anon_client, backend):
    populate(backend)
    backend.on(UsersApi, "create_user", raises=api_exception(422, "email exists"))
    rsp = anon_client.post("/gui/register/", data={"id": "-1", "register_email": "dup@example.org"})
    assert rsp.status_code == 302
    assert rsp.headers["Location"].rstrip("/").endswith("/gui/register")


def test_register_form_from_mail_token(app, anon_client, backend):
    populate(backend)
    tok = _token(app, {"id": "-1", "email": "new@example.org"})
    rsp = anon_client.get("/gui/register/" + tok)
    assert rsp.status_code == 200
    assert b"<form" in rsp.data


def test_register_bad_token(anon_client):
    rsp = anon_client.get("/gui/register/not-a-token")
    assert rsp.status_code == 403


def test_register_with_token_creates_account(app, anon_client, backend):
    populate(backend)
    create = backend.on(UsersApi, "create_user", returns=77)
    tok = _token(app, {"id": "-1", "email": "new@example.org"})
    rsp = anon_client.post(
        "/gui/register/" + tok,
        data={
            "id": "-1",
            "token": tok,
            "firstname": "Ann",
            "lastname": "Smith",
            "email": "new@example.org",
            "password": "Secret#1234",
            "organisation": "IMEV",
            "country": "France",
            "orcid": "",
            "usercreationreason": "research",
        },
    )
    assert rsp.status_code == 302
    kw = create.call_args.kwargs
    assert kw["token"] == tok
    sent = kw["user_model_with_rights"]
    assert sent.name == "Ann Smith" and sent.email == "new@example.org" and sent.password == "Secret#1234"


# ------------------------------------------------------------------ password fields
# Strength (pattern: password_regexp of the back-end) is checked on a new password only.
# The current password, asked to confirm an action, can be weaker (older accounts).


def _password_inputs(html: str) -> dict:
    tags = re.findall(r'<input[^>]*type="password"[^>]*>', html)
    return {re.search(r'\bid="([^"]*)"', tag).group(1): tag for tag in tags}


@pytest.mark.parametrize(
    "client_fixture, url, fields",
    [
        ("user_client", "/gui/me/profile", ("newpassword", "passwordconfirm")),
        ("anon_client", "/gui/me/forgotten/tok", ("request_password", "request_passwordconfirm")),
    ],
    ids=["profile", "forgotten"],
)
def test_new_password_pattern(request, backend, client_fixture, url, fields):
    from appli.gui.users.users import api_password_regexp

    populate(backend)
    rsp = request.getfixturevalue(client_fixture).get(url)
    assert rsp.status_code == 200
    inputs = _password_inputs(rsp.get_data(as_text=True))
    pattern = 'pattern="%s"' % escape(api_password_regexp())
    for field in fields:
        assert pattern in inputs[field], field


def test_activate_current_password_has_no_pattern(anon_client, backend):
    populate(backend)
    rsp = anon_client.get("/gui/me/activate/tok")
    assert rsp.status_code == 200
    inputs = _password_inputs(rsp.get_data(as_text=True))
    assert "password" in inputs
    assert not [tag for tag in inputs.values() if "pattern=" in tag]


@pytest.mark.parametrize(
    "user",
    [None, {"id": 42, "email": "pending@example.org", "name": "Pending User"}],
    ids=["password-first", "profile-form"],
)
def test_pending_account_current_password_has_no_pattern(app, anon_client, backend, user):
    # account validation: the password of the pending account is asked, then sent again with the profile
    from flask import render_template

    populate(backend)
    with app.test_request_context("/gui/register/tok"):
        html = render_template(
            "v2/register.html",
            usrid=42,
            user=user,
            token="tok",
            createaccount=True,
            api_account_validation=True,
            api_email_verification=True,
            organisations=[],
            countries=[],
        )
    inputs = _password_inputs(html)
    assert "password" in inputs
    assert not [tag for tag in inputs.values() if "pattern=" in tag]


def test_homecaptcha_round_trip(app, backend):
    from appli.gui.users import users

    env = {"REMOTE_ADDR": "backend.test"}
    with app.test_request_context("/", environ_base=env):
        tok = users.encode_homecaptcha()
    rsp = app.test_client().get("/gui/checkcaptcha?r=" + tok, environ_base=env)
    assert rsp.status_code == 200 and rsp.get_json() == {"success": True}
    # from another address
    rsp = app.test_client().get("/gui/checkcaptcha?r=" + tok, environ_base={"REMOTE_ADDR": "10.0.0.9"})
    assert rsp.status_code == 403
