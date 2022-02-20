#
# Utility defs not depending on the Flask app.
#
from typing import Type, TypeVar, Generic, Union, Dict, List, Optional

from flask import Request, request
from werkzeug.local import LocalProxy

from appli.constants import BACKEND_URL
from to_back import booster
from to_back.ecotaxa_cli_py import ApiClient as _ApiClient, ProjectModel, ApiException
from to_back.ecotaxa_cli_py.api import AuthentificationApi, ProjectsApi, UsersApi, ObjectsApi, SamplesApi, \
    AcquisitionsApi, ProcessesApi, ObjectApi, TaxonomyTreeApi, MiscApi, InstrumentsApi, FilesApi, JobsApi, AdminApi

# Lol, generics in python
A = TypeVar('A', AuthentificationApi, ProjectsApi, UsersApi, ObjectsApi, ObjectApi,
            SamplesApi, AcquisitionsApi, ProcessesApi, TaxonomyTreeApi,
            MiscApi, InstrumentsApi, FilesApi, JobsApi, AdminApi)


class ApiClient(Generic[A]):
    """ A client with guaranteed resource released """

    def __init__(self, api_class: Type[A], token: Union[str, LocalProxy, Request]):
        api_client = _ApiClient()
        booster.boost(api_client)
        if isinstance(token, LocalProxy):
            token = token.cookies.get('session')  # type:ignore
        api_client.configuration.access_token = token
        # Note: No trailing / in URL
        api_client.configuration.host = BACKEND_URL
        # Call constructor on base class
        self.under: A = api_class(api_client)

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


def get_all_visible_projects() -> List[ProjectModel]:
    with ApiClient(ProjectsApi, request) as api:
        try:
            projects: List[ProjectModel] = api.search_projects(title_filter="%")
            return [prj for prj in projects if prj.visible]  # Narrow to visible ones, even for logged users
        except ApiException as ae:
            return []


def ScaleForDisplay(v) -> str:
    """
    Permet de supprimer les decimales supplementaires des flottant en fonction de la valeur et de ne rien faire au reste
    :param v: Valeur à ajuster
    :return: Texte formaté
    """
    if isinstance(v, float):
        if abs(v) < 100:
            return "%0.2f" % v
        else:
            return "%0.f" % v
    elif v is None:
        return ""
    elif isinstance(v, str):
        return v
    else:
        return str(v)


def ntcv(v: Optional[str]) -> str:
    """
    Permet de récuperer une chaine que la source soit une chaine ou un None issue d'une DB
    :param v: Chaine potentiellement None
    :return: V ou chaine vide
    """
    if v is None:
        return ""
    return v


def DecodeEqualList(txt: str) -> Dict[str, str]:
    res = {}
    for l in txt.splitlines():
        ls = l.split('=', 1)
        if len(ls) == 2:
            res[ls[0].strip().lower()] = ls[1].strip().lower()
    return res


def EncodeEqualList(map: Dict[str, str]) -> str:
    l = ["%s=%s" % (k, v) for k, v in map.items()]
    l.sort()
    return "\n".join(l)
