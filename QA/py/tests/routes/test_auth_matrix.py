"""
Who can reach which /gui page.

Every rule served by appli.gui.* (the new UI) is required to send anonymous users to the login page,
unless it is listed in PUBLIC. Admin pages must answer 403 to users without the role.
A new route, or a changed protection, makes this file fail until the tables are updated.
"""

import re

import pytest

# Endpoints reachable without login (they may still check a token or answer 403 themselves)
PUBLIC = {
    "gui_index",
    "gui_about",
    "gui_alert",
    "gui_check_captcha",
    "gui_explore",
    "gui_explore_map_projects",
    "gui_graphicpalette",
    "gui_help_nologin",
    "gui_i18n",
    "gui_login",
    "gui_me_activate",
    "gui_me_forgotten",
    "gui_privacy",
    "gui_register",
    "gui_server_folder_select_json",
    "gui_setmsgcookie",
    "openid_login",
    "openid_callback",
}

# Endpoints for application admins and users admins
ADMIN = {
    "gui_admin",
    "gui_userlist",
    "gui_users_list_page",
    "gui_user_activate",
    "gui_user_create",
    "gui_user_edit",
    "gui_site_message",
    "gui_admin_guestlist",
    "gui_guest_edit",
    "gui_organization_edit",
}
# Endpoints for application admins only
APP_ADMIN = {
    "gui_dbadmin_viewsizes",
    "gui_dbadmin_viewbloat",
    "gui_dbadmin_recomputestat",
    "gui_dbadmin_console",
}


def _sample_url(rule: str) -> str:
    return re.sub(r"<(?:(\w+):)?(\w+)>", lambda m: "1" if m.group(1) == "int" else "x", rule)


def _gui_rules():
    import appli

    rules = [
        r
        for r in appli.app.url_map.iter_rules()
        if appli.app.view_functions[r.endpoint].__module__.startswith("appli.gui")
    ]
    return sorted(rules, key=lambda r: (r.rule, r.endpoint))


def _ids(rules):
    return [r.rule for r in rules]


def _method(rule):
    return "GET" if "GET" in rule.methods else "POST"


def _call(client, rule):
    url = _sample_url(rule.rule)
    rsp = client.open(url, method=_method(rule))
    if rsp.status_code == 308:  # strict_slashes redirect
        rsp = client.open(rsp.headers["Location"], method=_method(rule))
    return rsp


PROTECTED_RULES = [r for r in _gui_rules() if r.endpoint not in PUBLIC]
ADMIN_RULES = [r for r in _gui_rules() if r.endpoint in ADMIN | APP_ADMIN]
APP_ADMIN_RULES = [r for r in _gui_rules() if r.endpoint in APP_ADMIN]


def test_tables_match_existing_endpoints(app):
    endpoints = {r.endpoint for r in _gui_rules()}
    assert PUBLIC - endpoints == set(), "PUBLIC lists unknown endpoints"
    assert (ADMIN | APP_ADMIN) - endpoints == set(), "ADMIN lists unknown endpoints"


@pytest.mark.parametrize("rule", PROTECTED_RULES, ids=_ids(PROTECTED_RULES))
def test_anonymous_is_sent_to_login(anon_client, rule):
    rsp = _call(anon_client, rule)
    assert rsp.status_code == 302, (rule.endpoint, rsp.status_code)
    assert "/gui/login" in rsp.headers["Location"], rsp.headers["Location"]


@pytest.mark.parametrize("rule", ADMIN_RULES, ids=_ids(ADMIN_RULES))
def test_plain_user_gets_403_on_admin_pages(user_client, rule):
    rsp = _call(user_client, rule)
    assert rsp.status_code == 403, (rule.endpoint, rsp.status_code)


@pytest.mark.parametrize("rule", APP_ADMIN_RULES, ids=_ids(APP_ADMIN_RULES))
def test_users_admin_gets_403_on_db_pages(users_admin_client, rule):
    rsp = _call(users_admin_client, rule)
    assert rsp.status_code == 403, (rule.endpoint, rsp.status_code)
