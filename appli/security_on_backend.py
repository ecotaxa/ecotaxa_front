#
# Manage users exclusively on the back-end.
#
from typing import List
import json
from datetime import timedelta
from flask import request, redirect, url_for, abort, flash
from flask_login import login_user, current_user, logout_user
from appli.constants import AdministratorLabel, is_static_unprotected
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    UserModelWithRights,
    LoginReq,
    ApiException,
    MinUserModel,
)
from to_back.ecotaxa_cli_py.api import UsersApi, AuthentificationApi
from appli.constants import (
    AdministratorLabel,
    UserAdministratorLabel,
    API_GLOBAL_ROLES,
)
from appli.back_config import get_user_constants
from functools import wraps


class AdministratorRole:
    name: str = AdministratorLabel


class UserAdministratorRole:
    name: str = UserAdministratorLabel


class ApiUserWrapper(object):
    def __init__(self, api_user, ApiUserStatus):
        if api_user is not None:
            self.api_user: UserModelWithRights = api_user
            self.password = "?"

    @property
    def is_authenticated(self) -> bool:
        return self.api_user.id > 0

    @property
    def is_active(self) -> bool:
        return self.api_user.status == 1  # ApiUserStatus["active"]

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> int:
        return self.api_user.id

    def get_mail_status(self) -> str:
        return self.api_user.mail_status

    def has_role(self, rolename: str) -> bool:
        rolebynames = {lbl: int(num) for num, lbl in API_GLOBAL_ROLES.items()}
        if rolename in rolebynames:
            role = rolebynames[rolename]
            if role in self.api_user.can_do:
                return True
        return False

    @property
    def roles(self) -> List:
        roles = []
        for rolevalue, rolename in API_GLOBAL_ROLES.items():
            if rolevalue in self.api_user.can_do:
                roles.append(rolename)
        return roles

    @property
    def is_admin(self) -> bool:
        if self.has_role(AdministratorLabel) or self.has_role(UserAdministratorLabel):
            return True
        return False

    @property
    def is_app_admin(self) -> bool:
        if self.has_role(AdministratorLabel):
            return True
        return False

    @property
    def is_users_admin(self) -> bool:
        if self.has_role(UserAdministratorLabel):
            return True
        return False

    @property
    def fs_uniquifier(self) -> int:
        return self.id

    @fs_uniquifier.setter
    def fs_uniquifier(self, value):
        self.id = value

    def __getattr__(self, item):
        if item == "active":
            return self.is_active
        elif item == "last_used_projects" or item == "can_do":
            if hasattr(self.api_user, item):
                return self.api_user.last_used_projects
            return []
        elif hasattr(self.api_user, item):
            return getattr(self.api_user, item)
        return None


anon_user = MinUserModel(id=-1, email="", name="Anonymous")


def user_from_api(user_id):
    (
        ApiUserStatus,
        API_PASSWORD_REGEXP,
        API_EMAIL_VERIFICATION,
        API_ACCOUNT_VALIDATION,
        SHORT_TOKEN_AGE,
        PROFILE_TOKEN_AGE,
    ) = get_user_constants(request)
    try:
        with ApiClient(UsersApi, request) as api:
            curr_user: UserModelWithRights = api.show_current_user()
        if user_id != -1 and str(user_id) != str(curr_user.id):
            raise ApiException(status=403, reason="Bad ID")
    except (ApiException):
        if current_user.is_athenticated:
            logout_user()
        curr_user = anon_user
    curr_user = ApiUserWrapper(curr_user, ApiUserStatus)
    return curr_user


def login_validate(email: str, password: str, remember: bool = False):
    """
    Validate using back-end call
    """
    # Go to back-end
    from appli import gvp

    (
        ApiUserStatus,
        API_PASSWORD_REGEXP,
        API_EMAIL_VERIFICATION,
        API_ACCOUNT_VALIDATION,
        SHORT_TOKEN_AGE,
        PROFILE_TOKEN_AGE,
    ) = get_user_constants(request)
    req = LoginReq(username=email, password=password)

    try:
        with ApiClient(AuthentificationApi, "") as api:
            token: str = api.login(req)
        with ApiClient(UsersApi, token) as api:
            curr_user: UserModelWithRights = api.show_current_user()
    except ApiException as ae:
        from appli.gui.staticlistes import py_user

        if ae.status == 401 and "detail" in ae.body:
            message = json.loads(ae.body)["detail"][0].split("#")
            if len(message) > 2:
                user_status = message[0]
                user_id = message[2]
                if message[0] in py_user["statusnotauthorized"]:
                    if (
                        int(message[0]) == ApiUserStatus["inactive"]
                        and message[1] == "W"
                    ):
                        flash(py_user["statusnotauthorized"][message[1]], "warning")
                        return False, None
                    else:
                        flash(py_user["statusnotauthorized"][message[0]], "warning")
                        if int(message[0]) == ApiUserStatus["pending"]:
                            return False, url_for(
                                "gui_me_activate", user_id=int(user_id)
                            )
                else:
                    flash(py_user["not_authorized"], "error")
        else:
            flash(py_user["invalidpassword"], "error")
        return False, None
    # TODO LOGIN_DURATION
    LOGIN_DURATION = timedelta(days=30)
    ret = login_user(
        ApiUserWrapper(curr_user, ApiUserStatus),
        remember=remember,
        duration=LOGIN_DURATION,
    )
    return ret, None


def gui_roles_accepted(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            norole = True
            if current_user.is_authenticated:
                for role in roles:
                    if current_user.has_role(role):
                        norole = False
                        break
            if norole == True:
                abort(403)
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper
