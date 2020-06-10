#
# Utility defs not depending on the Flask app.
#
from to_back.ecotaxa_cli_py import ApiClient, DefaultApi


class APIClientWrapper(DefaultApi):
    """ A client with guaranteed resource released """

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


def get_api_client() -> DefaultApi:
    api_client = ApiClient()
    # Note: No trailing / in URL
    api_client.configuration.host = "http://localhost:8000"
    ret = APIClientWrapper(api_client)
    return ret
