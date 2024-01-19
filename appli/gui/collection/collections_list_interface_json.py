# list : full project list table def - homepage
# import-[...] settings table def - projectsettings page create or update

from to_back.ecotaxa_cli_py.models import (
    CollectionModel,
    MinUserModel,
)

from flask_babel import _


def collection_table_columns(typeimport: str, selection: str = "list") -> list:
    if typeimport == "":
        selection = selection
    else:
        selection = "import"
    columns = {
        "list": dict(
            {
                "id": {
                    "label": _("ID"),
                    "sortable": "desc",
                    "format": "number",
                },
                "provider_user": {"label": _("Provider user"), "format": "user"},
                "title": {
                    "label": _("Title"),
                },
                "contact": {"label": _("Contact"), "hidden": True},
                "creators": {"label": _("Creators"), "format": "user_list"},
                "associates": {"label": _("Associates"), "format": "user_list"},
                "citation": {
                    "label": _("Citation"),
                },
                "abstract": {
                    "label": _("Abstract"),
                },
                "license": {"label": _("License"), "format": "license"},
                "project_ids": {"label": _("Projects id"), "format": "project_list"},
                "external_id": {
                    "label": _("External ID"),
                    "sortable": "asc",
                },
                "external_id_system": {
                    "label": _("External ID System"),
                    "sortable": "asc",
                },
            }
        ),
        "import": {},
    }

    if selection == "import":
        ths = dict(
            {
                **select[typeimport],
                **columns["import"]["commons"],
                **columns["import"][typeimport],
            }
        )
        return ths
    elif selection == "list":
        cols = {
            **{"select": {"select": "select", "field": "id"}},
            **columns[selection],
        }
        return cols
    elif selection == "merge":
        cols = {
            **{"select": {"select": "select", "field": "id"}},
            **columns["list"],
        }
        return cols
    else:
        return columns[selection]


def _extract_items(prj, keepkeys):
    return {k: v for k, v in prj.items() if k in keepkeys}


def render_for_js(colljs: list, columns: list) -> list:
    from appli.gui.staticlistes import py_project_status
    from datetime import datetime
    from flask_login import current_user

    isadmin = current_user.is_authenticated and current_user.is_app_admin == True
    jsoncolljs = list([])
    for coll in colljs:

        jsoncoll = list([])

        for key, column in columns.items():

            if key == "creators":
                jsoncoll.append(
                    dict(
                        {
                            "creator_users": coll["creator_users"],
                            "creator_organisations": coll["creator_organisations"],
                        }
                    )
                )
            elif key == "associates":
                jsoncoll.append(
                    dict(
                        {
                            "associate_users": coll["associate_users"],
                            "associate_organisations": coll["associate_organisations"],
                        }
                    )
                )
            else:
                # if subfield  append object which will be formatted by the js component
                if key == "select":
                    if "select" in column and column["select"] == "edit":
                        select = dict({"edit": _("Edit")})
                        attrvalue = select
                    else:
                        attrvalue = ""
                elif key == "contact":
                    if coll["contact_user"]:
                        attrvalue = coll["contact_user"]
                    else:
                        attrvalue = ""
                elif key == "creators":
                    if coll["creator_users"]:
                        attrvalue = coll["creator_users"]
                    else:
                        attrvalue = ""
                elif key == "associates":
                    if coll["associate_users"]:
                        attrvalue = coll["associate_users"]
                    else:
                        attrvalue = ""
                else:
                    # data come from different types (if taxo it's  dict)
                    attrvalue = coll[key]
                    if isinstance(attrvalue, datetime):
                        attrvalue = attrvalue.isoformat()
                if "request" in column:
                    if column["request"] == "about":
                        attrvalue = list([attrvalue, 1])

                jsoncoll.append(attrvalue)
        jsoncolljs.append(jsoncoll)
    return jsoncolljs


def _render_collection_users(collection: CollectionModel) -> dict:
    all_users = dict(
        {
            "provider": collection.provider_user,
            "contact": collection.contact_user,
            "creators": {
                "users": collection.creator_users,
                "organisations": collection.creator_organisations,
            },
            "associates": {
                "users": collection.associate_users,
                "organisations": collection.associate_organisations,
            },
        }
    )
    return all_users


def render_coll_summary(collection: CollectionModel) -> dict:
    # for jobs
    return dict(
        {
            "id": collection.id,
            "title": collection.title,
            "contact": collection.contact,
        }
    )


def render_coll_summary_json(collection: dict) -> dict:
    # for jobs
    return _extract_items(collection, ["id", "title", "contact"])
