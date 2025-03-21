from flask import request, render_template
from werkzeug.exceptions import NotFound
from flask_login import current_user
from typing import Union, Optional

from appli.gui.users.users import get_organizations
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    GuestsApi,
    GuestModel,
    ApiException,
)

from appli.gui.users.users import (
    get_country_list,
    person_posted_data,
    make_person_response,
)
from appli.gui.staticlistes import py_user


ACCOUNT_CREATE = "create"
ACCOUNT_EDIT = "edit"
GUEST_FIELDS = [
    "email",
    "organisation",
    "country",
    "orcid",
]


def check_is_guests_admin() -> bool:
    # app admins are users admins
    return current_user.is_authenticated and current_user.is_admin == True


def guest_create():
    return guest_account(guestid=-1, action=ACCOUNT_CREATE)


def guest_edit(guestid: int) -> tuple:
    return guest_account(guestid, action=ACCOUNT_EDIT)


def organization_edit(personid: int) -> tuple:
    return guest_account(personid, action=ACCOUNT_EDIT)


def person_create():
    return guest_account(guestid=-1, action=ACCOUNT_CREATE)


def api_get_guest(guestid: int) -> Union[GuestModel, tuple]:
    try:
        with ApiClient(GuestsApi, request) as api:
            if isinstance(guestid, int) and guestid > 0:
                if check_is_guests_admin():
                    guest = api.get_guests(ids=str(guestid))
                    if len(guest):
                        return guest[0]
    except ApiException as ae:
        return make_person_response(None, "", ae, "guest")


def api_guest_create(posted: dict) -> tuple:
    new_guest = GuestModel(**posted)
    print("_____posted", posted)
    with ApiClient(GuestsApi, request) as api:
        try:
            guest_id = api.create_guest(guest_model=new_guest)
            if guest_id == -1:
                return make_person_response(
                    1, py_user["profileerror"]["create"], None, "guest"
                )
            else:
                message = py_user["profilesuccess"]["create"]
            return make_person_response(
                0,
                message,
                None,
                "guest",
                {
                    "id": guest_id,
                    "name": new_guest.name,
                    "email": new_guest.email,
                },
            )
        except ApiException as ae:
            return make_person_response(None, "", ae)


def guest_account(guestid: int, action: str = None) -> tuple:
    if action is not None:
        if not isinstance(guestid, int):
            return make_person_response(None, py_user["invaliddata"], None, "guest")

    # TODO isfrom manager or admin
    isfrom = False
    posted = person_posted_data(guestid, isfrom, GUEST_FIELDS)
    if action == ACCOUNT_EDIT:
        if guestid == -1:
            return 1, "noguestid"
        elif current_user.id == guestid:
            return 1, "erroruserisguest"
        else:
            api_guest = GuestModel(**posted).to_dict()
        with ApiClient(GuestsApi, request) as api:
            try:
                guest_id = api.update_guest(guest_id=guestid, guest_model=api_guest)
            except ApiException as ae:
                return make_person_response(None, "", ae)
        if guest_id == -1:
            return make_person_response(1, py_user["notmodified"])
        else:
            message = py_user["profilesuccess"]["update"]
            return make_person_response(
                0,
                message,
                None,
                "guest",
                {"id": id, "name": posted["name"], "email": posted["email"]},
            )
    elif action == ACCOUNT_CREATE:
        if guestid != -1:
            return make_person_response(
                1,
                py_user["errusrid"],
                None,
                "guest",
                {
                    "id": id,
                    "name": posted["firstname"] + " " + posted["lastname"],
                    "email": posted["email"],
                },
            )
        else:
            response = api_guest_create(posted)
            return response
    else:
        return make_person_response(1, py_user["usernoaction"])


def account_page(
    action: str, guestid: int, template: str, person: Optional[bool] = False
) -> str:
    if action != ACCOUNT_CREATE and not isinstance(guestid, int):
        raise NotFound()
    if action == ACCOUNT_CREATE:
        guest = {"id": -1}
    else:
        guest = api_get_guest(guestid)
        if guest is None:
            raise NotFound(description=py_user["notfound"])
    # TODO search organizations
    organisations = get_organizations()
    country_list = get_country_list()
    countries = sorted(country_list)
    return render_template(
        template,
        guest=guest,
        countries=countries,
        organisations=organisations,
        createaccount=(action == ACCOUNT_CREATE),
        person=person,
    )
