#
# Utility defs not depending on the Flask app.
#
import datetime
import json
import re
from types import MethodType
from typing import Type, TypeVar, Generic, Union, Dict, Tuple

from dateutil.parser import parse
from flask import Request
from werkzeug.local import LocalProxy

import to_back
from appli.api_proxy import BACKEND_URL
from to_back.ecotaxa_cli_py import ApiClient as _ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi, ObjectsApi, SamplesApi, \
    AcquisitionsApi, ProcessesApi, ObjectApi, TaxonomyTreeApi, MiscApi, InstrumentApi, FilesApi, JobsApi

# Lol, generics in python
A = TypeVar('A', ProjectsApi, UsersApi, ObjectsApi, ObjectApi,
            SamplesApi, AcquisitionsApi, ProcessesApi, TaxonomyTreeApi,
            MiscApi, InstrumentApi, FilesApi, JobsApi)


class ModelFromJSON(object):
    # Receiver for JSON deser
    def __init__(self, openapi_types):
        self.openapi_types = openapi_types
        self.attribute_map = {k: k for k in openapi_types.keys()}

    def to_dict(self):
        return self.__dict__


openapi_classes: Dict[Union[str, Type], Type] = {}
openapi_compo: Dict[Union[str, Type], Union[str, Type, Dict]] = {}
NATIVE_TYPES_MAPPING = {
    'int': int,
    'long': int,  # noqa: F821
    'float': float,
    'str': str,
    'bool': bool,
    'date': datetime.date,
    'datetime': datetime.datetime,
    'object': object,
}
for nat_klass_str, nat_klass in NATIVE_TYPES_MAPPING.items():
    openapi_classes[nat_klass_str] = nat_klass
    openapi_classes[nat_klass] = nat_klass
atomic_types = set(NATIVE_TYPES_MAPPING.values())
atomic_types.remove(object)


def get_openapi_class(klass_str: str) -> Tuple[Type, Type]:
    try:
        return openapi_classes[klass_str], openapi_compo.get(klass_str)
    except KeyError:
        add_openapi_class(klass_str)
        return openapi_classes[klass_str], openapi_compo.get(klass_str)


def add_openapi_class(klass_str: str):
    if klass_str.startswith('list['):
        sub_kls_str = re.match(r'list\[(.*)]', klass_str).group(1)
        sub_kls, compo = get_openapi_class(sub_kls_str)
        openapi_classes[klass_str] = list
        if compo is None:
            openapi_compo[klass_str] = sub_kls
        else:
            openapi_compo[klass_str] = sub_kls_str
    elif klass_str.startswith('dict('):
        sub_kls_str = re.match(r'dict\(([^,]*), (.*)\)', klass_str).group(2)
        sub_kls, compo = get_openapi_class(sub_kls_str)
        openapi_classes[klass_str] = dict
        if compo is None:
            openapi_compo[klass_str] = sub_kls
        else:
            openapi_compo[klass_str] = sub_kls_str
    else:
        klass = getattr(to_back.ecotaxa_cli_py.models, klass_str)
        assert klass is not None
        openapi_classes[klass_str] = klass
        openapi_compo[klass_str] = klass.openapi_types
        openapi_classes[klass] = klass
        openapi_compo[klass_str] = klass.openapi_types


def to_obj(json_obj, klass):
    """
        Faster-than-generated-code decoder from JSON to OpenAPI models & types.
    """
    # The decoding is _driven_ by OpenAPI type, not by received type.
    try:
        type1 = openapi_classes[klass]
    except KeyError:
        add_openapi_class(klass)
        type1 = openapi_classes[klass]

    if type1 in atomic_types:
        if type(json_obj) == type1:
            return json_obj
        else:
            if json_obj is None:
                return None
            if type1 in (datetime.datetime, datetime.date):
                ret = parse(json_obj)
                if type1 == datetime.date:
                    return ret.date()
                else:
                    return ret
            else:
                return type1(json_obj)

    type2 = openapi_compo.get(klass)
    if type1 == list:
        return [to_obj(o, type2) for o in json_obj]
    if type1 == dict:
        for k, v in json_obj.items():
            v2 = to_obj(v, type2)
            if v2 is not v:
                json_obj[k] = v2
        return json_obj

    if type2 is not None:
        # Object AKA Model creation
        ret = ModelFromJSON(type2)
        if type(json_obj) == dict:
            for fld, tpe in type2.items():
                val = json_obj[fld]
                val = to_obj(val, tpe)
                setattr(ret, fld, val)
        else:
            if json_obj is None:
                return None
            for fld, tpe in type2.items():
                val = getattr(json_obj, fld)
                val = to_obj(val, tpe)
                setattr(ret, fld, val)
        return ret


def sped_up_deser(self, response, response_type):
    """Deserializes response into an object.

    :param self: APIClient instance (this is injected code)
    :param response: RESTResponse object to be deserialized.
    :param response_type: class literal for
        deserialized object, or string of class name.

    :return: deserialized object.
    """
    # handle file downloading
    # save response body into a tmp file and return the instance
    if response_type == "file":
        return self._ApiClient__deserialize_file(response)

    # fetch data from response object
    try:
        data = json.loads(response.data)
        data2 = to_obj(data, response_type)
        return data2
    except ValueError:
        data = response.data

    return self._ApiClient__deserialize(data, response_type)


class ApiClient(Generic[A]):
    """ A client with guaranteed resource released """

    def __init__(self, api_class: Type[A], token: Union[str, LocalProxy, Request]):
        api_client = _ApiClient()
        # Piggy-back a faster version of deserialize
        assert "deserialize" in dir(api_client)
        api_client.deserialize = MethodType(sped_up_deser, api_client)
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


def format_date_time(rec: Dict, date_cols=(), time_cols=()):
    """
        Format known date & time columns from their JSON representation.
        Minimal sanity check of the input.
    """
    for a_col in date_cols:
        val = rec.get(a_col)
        if val is None:
            continue
        if len(val) < 17 or val[10] != "T":
            continue
        # 2020-09-17T13:15:37.441179 -> 2020-09-17 13:15
        rec[a_col] = val[:10] + " " + val[11:16]
    for a_col in time_cols:
        val = rec.get(a_col)
        if val is None:
            continue
        if len(val) < 6 or val[2] != ":":
            continue
        # 13:15:37 -> 13:15
        rec[a_col] = val[:5]


# if __name__ == '__main__':
#     import time
#
#     json_fic = open("search.json").read()
#     bef = time.time()
#     json_loaded = json.loads(json_fic)
#     dur = time.time() - bef
#     print("load: %0.3f" % dur)
#     bef = time.time()
#     to_obj(json_loaded, "list[ProjectModel]")
#     dur = time.time() - bef
#     print("deser: %0.3f" % dur)
#     bef = time.time()
#     _ApiClient()._ApiClient__deserialize(json_loaded, "list[ProjectModel]")
#     dur = time.time() - bef
#     print("client: %0.3f" % dur)
