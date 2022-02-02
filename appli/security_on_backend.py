#
# Manage users exclusively on the back-end.
#
from typing import List

from flask import request
from flask_security.forms import LoginForm
from flask_security.datastore import UserDatastore
from flask_security.utils import get_message

from appli.constants import AdministratorLabel
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UserModel, UserModelWithRights, LoginReq, ApiException
from to_back.ecotaxa_cli_py.api import UsersApi, AuthentificationApi


class AdministratorRole(object):
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
    def roles(self) -> List[str]:
        if 2 in self.api_user.can_do:
            return [AdministratorRole]
        return []

    def __getattr__(self, item):
        return getattr(self.api_user, item)


anon_user = UserModel(id=-1, email="", name="Anonymous")


class BackEndUserDatastore(UserDatastore):
    """
        This is a very partial implementation, maybe more methods to implement if it fails
        in one of the 'raise' below.
    """

    def get_user(self, id_or_email):
        raise

    def find_role(self, *args, **kwargs):
        raise

    def find_user(self, *args, **kwargs):
        """
            It's assumed that the call is made from current request.
        """
        assert args == ()
        assert len(kwargs) == 1
        assert "id" in kwargs
        id_ = kwargs["id"]
        with ApiClient(UsersApi, request) as api:
            curr_user: UserModelWithRights = api.show_current_user()
        assert str(curr_user.id) == str(id_), "%s vs %s" % (curr_user.id, id_)
        # This will feed 'current_user' Flask global
        return ApiUserWrapper(curr_user)

    def commit(self):
        """
            Called by flask_security to ensure that e.g. password went from plain to encrypted in the DB.
        """
        pass


class CustomLoginForm(LoginForm):
    def validate(self):
        """
            Validate using back-end call
        """
        # Call base form for standard validations
        if not super(LoginForm, self).validate():
            return False
        # Got to back-end
        req = LoginReq(username=self.email.data, password=self.password.data)
        try:
            with ApiClient(AuthentificationApi, "") as api:
                token: str = api.login(req)
            with ApiClient(UsersApi, token) as api:
                curr_user: UserModelWithRights = api.show_current_user()
        except ApiException as ae:
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        # noinspection PyAttributeOutsideInit
        self.user = ApiUserWrapper(curr_user)
        return True
