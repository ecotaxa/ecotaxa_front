#
# Utility defs not depending on the Flask app.
#
from contextlib import AbstractContextManager
from typing import Type, TypeVar, Generic

from to_back.ecotaxa_cli_py import ApiClient as _ApiClient, ProjectsApi, UsersApi
from appli.api_proxy import BACKEND_URL

# Lol, generics in python
A = TypeVar('A', ProjectsApi, UsersApi)


class ApiClient(Generic[A]):
    """ A client with guaranteed resource released """

    def __init__(self, api_class: Type[A], token: str):
        api_client = _ApiClient()
        api_client.configuration.access_token = token
        # Note: No trailing / in URL
        api_client.configuration.host = BACKEND_URL
        # Call constructor on base class
        self.under = api_class(api_client)

    def __enter__(self) -> A:
        return self.under

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO: pool management
        pass
