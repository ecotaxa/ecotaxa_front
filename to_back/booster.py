#
# Some python hacking for speeding-up deserialization of openapi structures
#
import datetime
import re
from types import MethodType
from typing import Dict, Union, Type, Tuple, Optional

import orjson
from dateutil.parser import parse

from . import ecotaxa_cli_py
from .ecotaxa_cli_py import ApiClient

openapi_classes: Dict[Union[str, Type], Type] = {}
openapi_compo: Dict[Union[str, Type], Union[str, Type, int]] = {}
atomic_types = set(ApiClient.NATIVE_TYPES_MAPPING.values())
for nat_klass_str, nat_klass in ApiClient.NATIVE_TYPES_MAPPING.items():
    openapi_classes[nat_klass_str] = nat_klass
    openapi_classes[nat_klass] = nat_klass
atomic_types.remove(object)


def get_openapi_class(klass_str: str) -> Tuple[Type, Union[str, Type, int, None]]:
    try:
        return openapi_classes[klass_str], openapi_compo.get(klass_str)
    except KeyError:
        add_openapi_class(klass_str)
        return openapi_classes[klass_str], openapi_compo.get(klass_str)


def add_openapi_class(klass_str: str):
    if klass_str.startswith('list['):
        cls_re = re.match(r'list\[(.*)]', klass_str)
        assert cls_re
        sub_kls_str = cls_re.group(1)
        sub_kls, compo = get_openapi_class(sub_kls_str)
        openapi_classes[klass_str] = list
        if compo is None:
            openapi_compo[klass_str] = sub_kls
        else:
            openapi_compo[klass_str] = sub_kls_str
    elif klass_str.startswith('dict('):
        cls_re2 = re.match(r'dict\(([^,]*), (.*)\)', klass_str)
        assert cls_re2
        sub_kls_str = cls_re2.group(2)
        sub_kls, compo = get_openapi_class(sub_kls_str)
        openapi_classes[klass_str] = dict
        if compo is None:
            openapi_compo[klass_str] = sub_kls
        else:
            openapi_compo[klass_str] = sub_kls_str
    else:
        # Get the generated class to mimic
        klass = getattr(ecotaxa_cli_py.models, klass_str)
        assert klass is not None
        openapi_classes[klass_str] = openapi_classes[klass] = klass
        openapi_compo[klass_str] = openapi_compo[klass] = 1


# key = generated class, values = mocked one
mocked_classes: Dict[Type, Type] = {}


def _add_mocked_class(gen_class: Type):
    if hasattr(gen_class, "allowable_values"):
        # It's an Enum
        mocked_classes[gen_class] = str
        return
    MyCls = type(gen_class.__name__ + "2", (object,),
                 {"openapi_types": gen_class.openapi_types,
                  "attribute_map": gen_class.attribute_map,
                  "__slots__": list(gen_class.openapi_types.keys()),
                  "to_dict": lambda self: {nm: getattr(self, nm) for nm in self.__slots__}})
    mocked_classes[gen_class] = MyCls
    return MyCls


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

    type2: Optional[type] = openapi_compo.get(klass)

    if type1 == list:
        return [to_obj(o, type2) for o in json_obj]
    if type1 == dict:
        for k, v in json_obj.items():
            v2 = to_obj(v, type2)
            if v2 is not v:
                json_obj[k] = v2
        return json_obj
    if type1 == object:
        return json_obj

    if type2 is not None:
        # Object AKA Model creation
        try:
            ret = mocked_classes.get(type1)()
        except TypeError:
            # Mock was not generated yet
            _add_mocked_class(type1)
            ret = mocked_classes.get(type1)()

        if type(json_obj) == dict:
            for fld, tpe in ret.openapi_types.items():
                val = json_obj[fld]
                val = to_obj(val, tpe)
                setattr(ret, fld, val)
        else:
            if json_obj is None:
                return None
            if isinstance(ret, str):
                # Enums map to str
                return str(json_obj)
            for fld, tpe in ret.openapi_types.items():
                val = getattr(json_obj, fld)
                val = to_obj(val, tpe)
                setattr(ret, fld, val)
        return ret

    raise Exception("Boosted deser issue: In: %s kls: %s Vars: %s and: %s " % (json_obj, klass, type1, type2))


def _sped_up_deser(self, response, response_type):
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

    # Fetch data from response object
    data = response.data
    try:
        loaded = orjson.loads(data)
        ret = to_obj(loaded, response_type)
        return ret
    except ValueError:
        pass

    # Fallback to openapi deserializer
    return self._ApiClient__deserialize(data, response_type)


def boost(api_client: ApiClient):
    # Inject a faster version of deserialize
    assert "deserialize" in dir(api_client)
    api_client.deserialize = MethodType(_sped_up_deser, api_client)  # type:ignore

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
