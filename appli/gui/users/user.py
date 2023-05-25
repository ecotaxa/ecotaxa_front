#
# Manage users exclusively on the back-end.
#
from typing import List

from flask import request
from flask_login import (
    login_user,
    current_user,
)
from flask.sessions import SecureCookieSessionInterface

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    UserModelWithRights,
    LoginReq,
    ApiException,
    MinUserModel,
)
from to_back.ecotaxa_cli_py.api import UsersApi, AuthentificationApi


class ApiUserWrapper(object):
    def __init__(self, api_user):
        self.api_user: UserModelWithRights = api_user
        self.password = "X"

    @property
    def is_authenticated(self) -> bool:
        return self.api_user.id > 0

    @property
    def is_active(self) -> bool:
        return self.api_user.active

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> int:
        return self.api_user.id

    def has_role(self, role: str) -> bool:
        return role == AdministratorLabel and 2 in self.api_user.can_do

    @property
    def roles(self) -> List:
        if 2 in self.api_user.can_do:
            return [AdministratorRole()]
        return []

    @property
    def fs_uniquifier(self) -> int:
        return self.id

    @fs_uniquifier.setter
    def fs_uniquifier(self, value):
        self.id = value

    def __getattr__(self, item):
        return getattr(self.api_user, item)


anon_user = MinUserModel(id=-1, email="", name="Anonymous")


class UserModelForSecurity(UserModelWithRights):
    fs_uniquifier = None


class BackEndUser:
    """
    This is a very partial implementation, maybe more methods to implement if it fails
    in one of the 'raise' below.
    """

    def __init__(self):
        # Args are for mapping an ORM, which is unused in our case
        # But we need the Security module for forms
        super().__init__(UserModelForSecurity, UserModelWithRights)


def backend_user(user):
    """
    It's assumed that the call is made from current request.
    """
    from appli.constants import is_static_unprotected

    if is_static_unprotected(request.path):
        # Save an API call for unprotected routes
        return None

    assert "fs_uniquifier" in user
    id_ = user["fs_uniquifier"]
    try:
        with ApiClient(UsersApi, request) as api:
            curr_user: UserModelWithRights = api.show_current_user()
        assert str(curr_user.id) == str(id_), "%s vs %s" % (curr_user.id, id_)
    except (ApiException, AssertionError):
        return None
    # This will feed 'current_user' Flask global
    return ApiUserWrapper(curr_user)


def login_validate():
    """
    Validate using back-end call
    """
    # Don't call base form validation, it gives a bit too much information.
    # if not super(LoginForm, self).validate():
    #     return False
    # Go to back-end
    from flask import flash
    from appli import gvp

    email = gvp("email", None)
    password = gvp("password", "")

    req = LoginReq(username=email, password=password)
    try:
        with ApiClient(AuthentificationApi, "") as api:
            token: str = api.login(req)
        with ApiClient(UsersApi, token) as api:
            curr_user: UserModelWithRights = api.show_current_user()
    except ApiException as ae:
        flash("INVALID_PASSWORD")
        return False
    ret = login_user(ApiUserWrapper(curr_user))
    return ret


def new_password_validate():
    from flask import flash

    if not super(ChangePasswordForm, self).validate():
        return False
    try:
        from appli import gvp

        req = LoginReq(username=current_user.email, password=gvp("password"))
        with ApiClient(AuthentificationApi, "") as api:
            api.login(req)
    except ApiException as ae:
        return False
    if gvp("password") == gvp("new_password"):
        flash("PASSWORD_IS_THE_SAME")
        return False
    return True
