#
# Manage users exclusively on the back-end.
#
from typing import List

from flask import request
from flask_login import current_user
from flask_security import RoleMixin
from flask_security.datastore import UserDatastore
from flask_security.forms import LoginForm, ChangePasswordForm
from flask_security.utils import get_message

from appli.constants import AdministratorLabel, is_static_unprotected
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    UserModelWithRights,
    LoginReq,
    ApiException,
    MinUserModel,
)
from to_back.ecotaxa_cli_py.api import UsersApi, AuthentificationApi


class AdministratorRole(RoleMixin):
    name: str = AdministratorLabel


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


class BackEndUserDatastore(UserDatastore):
    """
    This is a very partial implementation, maybe more methods to implement if it fails
    in one of the 'raise' below.
    """

    def __init__(self):
        # Args are for mapping an ORM, which is unused in our case
        # But we need the Security module for forms
        super().__init__(UserModelForSecurity, UserModelWithRights)

    def get_user(self, id_or_email):
        raise

    def find_role(self, *args, **kwargs):
        raise

    def find_user(self, *args, **kwargs):
        """
        It's assumed that the call is made from current request.
        """
        if is_static_unprotected(request.path):
            # Save an API call for unprotected routes
            return None
        assert args == ()
        assert len(kwargs) == 1, "%d args when 1 expected" % len(kwargs)
        assert "fs_uniquifier" in kwargs
        id_ = kwargs["fs_uniquifier"]
        try:
            with ApiClient(UsersApi, request) as api:
                curr_user: UserModelWithRights = api.show_current_user()
            assert str(curr_user.id) == str(id_), "%s vs %s" % (curr_user.id, id_)
        except (ApiException, AssertionError):
            return None
        # This will feed 'current_user' Flask global
        return ApiUserWrapper(curr_user)

    def commit(self):
        """
        Called by flask_security to ensure that e.g. password went from plain to encrypted in the DB.
        """
        pass

    def put(self, user):
        """
        Called by flask_security when a user changes password.
        """
        api_user = current_user.api_user.to_dict()
        api_user["password"] = user.password
        with ApiClient(UsersApi, request) as api:
            api.update_user(api_user["id"], api_user)


class CustomLoginForm(LoginForm):
    def validate(self):
        """
        Validate using back-end call
        """
        # Don't call base form validation, it gives a bit too much information.
        # if not super(LoginForm, self).validate():
        #     return False
        # Go to back-end
        req = LoginReq(username=self.email.data, password=self.password.data)
        try:
            with ApiClient(AuthentificationApi, "") as api:
                token: str = api.login(req)
            with ApiClient(UsersApi, token) as api:
                curr_user: UserModelWithRights = api.show_current_user()
        except ApiException as ae:
            self.password.errors += (get_message("INVALID_PASSWORD")[0],)
            return False
        # noinspection PyAttributeOutsideInit
        self.user = ApiUserWrapper(curr_user)
        return True


class CustomChangePasswordForm(ChangePasswordForm):
    def validate(self):
        # Skip the validation in just-above-class
        if not super(ChangePasswordForm, self).validate():
            return False
        try:
            req = LoginReq(username=current_user.email, password=self.password.data)
            with ApiClient(AuthentificationApi, "") as api:
                api.login(req)
        except ApiException as ae:
            return False
        if self.password.data == self.new_password.data:
            self.password.errors.append(get_message("PASSWORD_IS_THE_SAME")[0])
            return False
        return True
