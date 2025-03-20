from typing import List, Dict
from flask_login import login_required
from flask import make_response, request, jsonify, render_template
from appli import app, gvg
import json
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import GuestsApi, UsersApi, OrganizationsApi


def render_content_json(content):
    gz = gvg("gzip")
    encoding = "utf-8"
    if gz:
        import gzip

        content = gzip.compress(content, 7)
        encoding = "gzip"
    response = make_response(content)
    response.headers["Content-length"] = len(content)
    response.headers["Content-Encoding"] = encoding
    response.headers["Content-Type"] = "application/json"

    return response


def allguests_list(ids: str = ""):
    with ApiClient(GuestsApi, request) as api:
        guests = api.guet_guests(ids)
    from appli.gui.admin.users_list_interface_json import (
        guest_table_columns,
        render_for_js,
    )

    columns = guest_table_columns()
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(guests, columns),
        }
    )
    return tabledef


def persons_list(persons):
    from appli.gui.admin.users_list_interface_json import (
        guest_table_columns,
        render_for_js,
    )

    columns = guest_table_columns()
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(persons, columns),
        }
    )
    return tabledef


def all_guests_json(ids: str = ""):
    with ApiClient(GuestsApi, request) as api:
        ret = api.get_guests(ids=ids)
    guests = [u.to_dict() for u in ret]
    content = json.dumps(persons_list(guests), separators=(",", ":")).encode("utf-8")
    return render_content_json(content)


def organizations_list(organizations):
    from appli.gui.admin.users_list_interface_json import (
        organization_table_columns,
        render_for_js,
    )

    columns = organization_table_columns()
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(organizations, columns),
        }
    )
    return tabledef


def all_organizations_json():
    with ApiClient(OrganizationsApi, request) as api:
        ret = api.get_organizations()
    organizations = [
        {"id": u.id, "name": u.name, "directories": u.directories} for u in ret
    ]
    content = json.dumps(
        organizations_list(organizations), separators=(",", ":")
    ).encode("utf-8")
    return render_content_json(content)


@app.route("/gui/guestslist/", methods=["GET"])
@login_required
def gui_guestlist():
    ids = gvg("ids", "")
    return all_guests_json(ids)


@app.route("/gui/organizationslist/", methods=["GET"])
@login_required
def gui_organizationlist():
    return all_organizations_json()


@app.route("/gui/personslist/", methods=["GET"])
@login_required
def gui_personlist():
    ids = gvg("ids", "")
    persons: List = []
    with ApiClient(UsersApi, request) as api:
        users = api.get_users(ids=ids)
    persons.extend([u.to_dict() for u in users])
    with ApiClient(GuestsApi, request) as api:
        guests = api.get_guests(ids=ids)
    persons.extend([u.to_dict() for u in guests])
    persons = sorted(persons, key=lambda p: p["name"].strip())
    content = json.dumps(persons, separators=(",", ":")).encode("utf-8")
    return render_content_json(content)


@app.route("/gui/search_persons", methods=["GET"])
@login_required
def gui_search_persons():
    persons: List = []
    name = gvg("name", "")
    with ApiClient(UsersApi, request) as api:
        users = api.search_user(by_name=name)
        persons.extend([p.to_dict() for p in users])
    with ApiClient(GuestsApi, request) as api:
        guests = api.search_guest(by_name=name)
        persons.extend([p.to_dict() for p in guests])
    persons = sorted(persons, key=lambda p: p["name"].strip())
    with ApiClient(OrganizationsApi, request) as api:
        organisations = api.search_organizations(name=name)
        persons.extend(
            [
                {"id": "org_" + str(p.id), "name": p.name, "organisation": p.name}
                for p in organisations
            ]
        )
    content = json.dumps(persons, separators=(",", ":")).encode("utf-8")
    return render_content_json(content)


@app.route("/gui/persons/create", methods=["GET", "POST"])
@app.route("/gui/persons/create/", methods=["GET", "POST"])
@login_required
def gui_person_create():
    _type = gvg("type", "")
    if request.method == "POST":
        response: Dict = {}
        if _type == "organization":
            from appli.gui.organizations.organizations import organization_create

            resp = organization_create()
        elif _type == "guest":
            from appli.gui.guests.guests import guest_create

            resp = guest_create()
        else:
            resp = [1, "no type"]
        if resp[0] == 0:
            response["success"] = True
            response["message"] = resp[1]
            if len(resp) > 2:
                response[_type] = resp[2]
        else:
            response["error"] = 1
            response["message"] = resp[1]
        return make_response(jsonify(response), resp[0])
    else:
        if _type == "organization":
            from appli.gui.organizations.organizations import (
                ACCOUNT_CREATE,
                account_page,
            )

            return account_page(
                action=ACCOUNT_CREATE,
                id=-1,
                template="v2/admin/organization.html",
                partial=True,
            )
        elif _type == "guest":
            from appli.gui.guests.guests import ACCOUNT_CREATE, account_page

            return account_page(
                action=ACCOUNT_CREATE,
                guestid=-1,
                template="v2/admin/guest.html",
                person="guest",
            )
        else:
            return render_template("v2/admin/person.html", partial=True)
