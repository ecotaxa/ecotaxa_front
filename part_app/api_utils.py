#
# Utility defs not depending on the Flask app.
#
from typing import Type, TypeVar, Generic, Union

from flask import Request
from werkzeug.local import LocalProxy

from to_back import booster
from to_back.ecotaxa_cli_py import ApiClient as _ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi, ObjectsApi, SamplesApi, \
    AcquisitionsApi, ProcessesApi, ObjectApi, TaxonomyTreeApi, MiscApi, InstrumentsApi, FilesApi, JobsApi

# Lol, generics in python
A = TypeVar('A', ProjectsApi, UsersApi, ObjectsApi, ObjectApi,
            SamplesApi, AcquisitionsApi, ProcessesApi, TaxonomyTreeApi,
            MiscApi, InstrumentsApi, FilesApi, JobsApi)

BACKEND_HOST = "localhost"
BACKEND_PORT = 8000
# noinspection HttpUrlsUsage
BACKEND_URL = "http://%s:%d" % (BACKEND_HOST, BACKEND_PORT)

class ApiClient(Generic[A]):
    """ A client with guaranteed resource released """

    def __init__(self, api_class: Type[A], token: Union[str, LocalProxy, Request]):
        api_client = _ApiClient()
        booster.boost(api_client)
        if isinstance(token, LocalProxy):
            token = token.cookies.get('session')
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
