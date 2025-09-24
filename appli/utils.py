#
# Utility defs not depending on the Flask app.
#
import urllib.parse
from typing import Type, TypeVar, Generic, Union, Dict, List, Optional, Tuple

from flask import Request, request
from flask_login import current_user
from werkzeug.local import LocalProxy

from to_back import booster
from to_back.ecotaxa_cli_py import (
    ApiClient as _ApiClient,
    ProjectModel,
    ApiException,
    MinUserModel,
    UsersApi,
)
from to_back.ecotaxa_cli_py.api import (
    AuthentificationApi,
    ProjectsApi,
    UsersApi,
    ObjectsApi,
    SamplesApi,
    AcquisitionsApi,
    ProcessesApi,
    ObjectApi,
    TaxonomyTreeApi,
    MiscApi,
    InstrumentsApi,
    MyfilesApi,
    JobsApi,
    AdminApi,
)

# Lol, generics in python
A = TypeVar(
    "A",
    AuthentificationApi,
    ProjectsApi,
    UsersApi,
    ObjectsApi,
    ObjectApi,
    SamplesApi,
    AcquisitionsApi,
    ProcessesApi,
    TaxonomyTreeApi,
    MiscApi,
    InstrumentsApi,
    MyfilesApi,
    JobsApi,
    AdminApi,
)


class ApiClient(Generic[A]):
    """A client with guaranteed resource released"""

    def __init__(self, api_class: Type[A], token: Union[str, LocalProxy, Request]):
        api_client = _ApiClient()
        booster.boost(api_client)
        if isinstance(token, LocalProxy):
            token = token.cookies.get("session")  # type:ignore
        api_client.configuration.access_token = token
        # Note: No trailing / in URL
        from appli import backend_url

        api_client.configuration.host = backend_url
        # Call constructor on base class
        self.under: A = api_class(api_client)

    def __enter__(self) -> A:
        return self.under

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO: pool management
        pass


def format_date_time(
    rec: Dict[str, str],
    date_cols: Tuple[str, ...] = (),
    time_cols: Tuple[str, ...] = (),
):
    """
    Format known date & time columns from their JSON representation.
    Minimal sanity check of the input.
    """
    val: Optional[str]
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
            return [
                prj for prj in projects if prj.access != "0"
            ]  # Narrow to visible ones, even for logged users
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


def DecodeEqualList(txt: Optional[str]) -> Dict[str, str]:
    ret: Dict[str, str] = {}
    if txt is None:
        return ret
    for a_line in txt.splitlines():
        ls = a_line.split("=", 1)
        if len(ls) == 2:
            ret[ls[0].strip().lower()] = ls[1].strip().lower()
    return ret


def EncodeEqualList(map: Dict[str, str]) -> str:
    l = ["%s=%s" % (k, v) for k, v in map.items()]
    l.sort()
    return "\n".join(l)


def BuildManagersMail(link_text: str, subject: str = "", body: str = ""):
    """
    Build a mailto link to all app managers.
    """
    admin_users = get_managers()
    emails = ";".join([usr.email for usr in admin_users])
    params = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body
    if params:
        txt_params = "?" + urllib.parse.urlencode(params).replace("+", "%20")
    else:
        txt_params = ""
    return "<a href='mailto:{0}{1}'>{2}</a>".format(emails, txt_params, link_text)


def get_managers() -> List[MinUserModel]:
    ret: List[MinUserModel]
    if current_user.is_authenticated:
        # With a connected user, return administrators
        with ApiClient(UsersApi, request) as api:
            ret = api.get_admin_users()
    else:
        # With an anonymous user, return user administrators (for account issues)
        with ApiClient(UsersApi, request) as api:
            ret = api.get_users_admins()
    return ret
