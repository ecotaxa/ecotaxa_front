from flask import request, render_template
from werkzeug.exceptions import NotFound
from typing import Union, Dict
from appli import gvp
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException, OrganizationsApi, OrganizationModel
from appli.gui.users.users import make_person_response
from appli.gui.staticlistes import py_user
from appli.gui.guests.guests import ACCOUNT_CREATE, ACCOUNT_EDIT, check_is_guests_admin

ORGANIZATION_FIELDS = ["name", "edmo"]


def organization_create():
    return organization_account(id=-1, action=ACCOUNT_CREATE)


def organization_edit(id: int) -> tuple:
    return organization_account(id, action=ACCOUNT_EDIT)


def api_get_organization(id: int) -> Union[OrganizationModel, tuple]:
    try:
        with ApiClient(OrganizationsApi, request) as api:
            if isinstance(id, int) and id != -1:
                if check_is_guests_admin():
                    organization = api.get_organizations(ids=str(id))
                    if len(organization):
                        return organization[0]
    except ApiException as ae:
        return make_person_response(None, "", ae, "organization")


def api_organization_create(posted: dict) -> tuple:
    new_org = OrganizationModel(**posted)
    with ApiClient(OrganizationsApi, request) as api:
        try:
            organization = api.create_organization(organization_model=new_org)
            if organization is None:
                return make_person_response(
                    1, py_user["profileerror"]["create"], None, "organization"
                )
            else:
                message = py_user["profilesuccess"]["create"]
            return make_person_response(
                0,
                message,
                None,
                "organization",
                {"id": organization, "name": new_org.name},
            )
        except ApiException as ae:
            return make_person_response(None, "", ae, "organization")


def organization_account(id: int, action: str = None) -> tuple:
    if action is not None:
        if not isinstance(id, int):
            return make_person_response(
                None, py_user["invaliddata"], None, "organization"
            )

    # TODO isfrom manager or admin
    fields = ["name"]
    posted: Dict = {}
    posted.update({a_field: gvp(a_field).strip() for a_field in fields})
    posted["id"] = id
    if action == ACCOUNT_EDIT:
        if id == -1:
            return 1, "noorgname"
        else:
            api_organization = OrganizationModel(**posted).to_dict()
        with ApiClient(OrganizationsApi, request) as api:
            try:
                id = api.update_organization(
                    organization_id=id, organization_model=api_organization
                )
                print("____id", id)
            except ApiException as ae:
                return make_person_response(None, "", ae, "organization")
        if id == -1:
            return make_person_response(1, py_user["notmodified"], None, "organization")
        else:
            message = py_user["profilesuccess"]["update"]
            return make_person_response(
                0, message, None, "organization", {"id": id, "name": posted["name"]}
            )
    elif action == ACCOUNT_CREATE:
        if id != -1:
            return make_person_response(
                1,
                py_user["errusrid"],
                None,
                "organization",
                {"id": id, "name": posted["name"]},
            )
        else:
            response = api_organization_create(posted)
            return response
    else:
        return make_person_response(
            1,
            py_user["usernoaction"],
            None,
            "organization",
            {"id": id, "name": posted["name"]},
        )


def account_page(action: str, id: int, template: str, partial: bool = False) -> str:
    if action != ACCOUNT_CREATE and not isinstance(id, int):
        raise NotFound()
    if action == ACCOUNT_CREATE:
        organization = {"id": -1}
    else:
        organization = api_get_organization(id)
        if organization is None:
            raise NotFound(description=py_user["notfound"])
    return render_template(
        template,
        organization=organization,
        createaccount=(action == ACCOUNT_CREATE),
        partial=partial,
    )
