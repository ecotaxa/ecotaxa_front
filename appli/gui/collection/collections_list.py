# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
#
# V2 new font interface projects list
#
from flask import request, render_template
from flask_login import current_user

from appli.utils import ApiClient
from werkzeug.exceptions import Forbidden
from to_back.ecotaxa_cli_py.api import CollectionsApi
from to_back.ecotaxa_cli_py.models import (
    CollectionModel,
    UserModelWithRights,
)

# flash and errors messages translated
from appli.gui.staticlistes import py_messages


def _collections_list_api_toback(project_ids: str = None) -> list:
    with ApiClient(CollectionsApi, request) as apicoll:

        colls: list[CollectionModel] = apicoll.list_collections(project_ids=project_ids)
    return colls


def _collections_list_api(project_ids: str = None) -> list:
    import requests

    colls = list([])

    payload = dict(
        {
            "project_ids": project_ids,
        }
    )
    with ApiClient(CollectionsApi, request) as apicoll:
        url = (
            apicoll.api_client.configuration.host + "/collections"
        )  # endpoint is nowhere available as a const :(
        token = apicoll.api_client.configuration.access_token
        headers = {
            "Authorization": "Bearer " + token,
        }
        r = requests.get(url, headers=headers, params=payload)
        if r.status_code == 200:
            colls.extend(r.json())
        else:
            r.raise_for_status()

    return colls


def collections_list(
    partial: bool = False,
    selection="list",
    project_ids: str = None,
    typeimport: str = "",
) -> str:
    import datetime

    # projects ids and rights for current_user
    if not current_user.is_authenticated:
        return dict(
            {
                "error": True,
                "status": 403,
                "title": "403",
                "message": py_messages["access403"],
            }
        )

    can_access = {}
    colls = []
    # current_user is either an ApiUserWrapper or an anonymous one from flask,
    # but we're in @login_required, so
    user: UserModelWithRights = current_user.api_user
    isadmin = current_user.is_app_admin == True
    colls = _collections_list_api(project_ids=project_ids)
    # from appli.gui.collection.collist import colls

    now = datetime.datetime.now()
    from appli.gui.collection.collections_list_interface_json import (
        collection_table_columns,
        render_for_js,
    )

    columns = collection_table_columns(typeimport, selection=selection)
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(colls, columns),
        }
    )
    return tabledef


# project list page without projects list data


def collections_list_page(
    partial: bool = False,
    typeimport: str = "",
) -> str:
    # collections ids and rights for current_user
    if not current_user.is_authenticated:
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    # current_user is either an ApiUserWrapper or an anonymous one from flask,
    # but we're in @login_required, so
    user: UserModelWithRights = current_user.api_user
    # no more project creator
    if user.id:
        CanCreate = True
    else:
        CanCreate = False
    isadmin = current_user.is_app_admin == True

    from appli.gui.collection.collections_list_interface_json import (
        collection_table_columns,
    )

    if typeimport == "" and not partial:
        template = "v2/collection/index.html"
    else:
        template = "v2/collection/_listcontainer.html"

    return render_template(
        template,
        CanCreate=CanCreate,
        partial=partial,
        isadmin=isadmin,
        # columns=json.dumps(columns),
        typeimport=typeimport,
    )
