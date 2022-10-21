# list : full project list table def - homepage
# import-[...] settings table def - projectsettings page create or update
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    MinUserModel,
)

from flask_babel import _


def project_table_columns(typeimport: str) -> list:
    if typeimport == "":
        selection = "list"
    else:
        selection = "import"
    columns = {
        "list": [
            {
                "label": "ID",
                "sortable": "desc",
                "field": "projid",
                "format": "number",
            },
            {
                "label": _("Instrument"),
                "field": "instrument",
                "autocomplete": "instrument",
            },
            {
                "label": "Title",
                "field": "title",
                "request": "about",
                "subfield": "contact",
                "sublabel": " - manager or contact",
            },
            {"label": "contact", "hidden": "true", "field": "contact"},
            {"label": "Status", "field": "status"},
            {
                "label": "Visibility",
                "field": "visible",
                "format": "check",
                "value": "Y",
            },
            {"label": "License", "field": "license", "format": "license"},
            {"label": "Nb objects", "field": "objcount", "format": "number"},
            {
                "label": "%validated",
                "field": "pctvalidated",
                "format": "progress",
                "default": "0.0",
            },
            # hidden columns
            # {"label": "Description", "field": "description", "hidden": "true"},
            # {"label": "Free columns", "field": "obj_free_cols", "hidden": "true"},
            # {"label": "Members", "field": "privileges", "hidden": "true"},
        ],
        "import": {
            "commons": [
                {
                    "label": "ID",
                    "field": "projid",
                    "format": "number",
                },
                {
                    "label": "Instrument",
                    "field": "instrument",
                    "autocomplete": "instrument",
                },
                {
                    "label": "Title",
                    "field": "title",
                },
            ],
            "taxo": [
                {
                    "label": "Preset categories",
                    "field": "preset",
                    "format": "taxons",
                },
                {
                    "label": "Extra categories used",
                    "field": "objtaxonnotinpreset",
                    "format": "taxons",
                },
            ],
            "privileges": [
                {"label": "Members", "field": "privileges"},
                {"label": "contact", "hidden": "true", "field": "contact"},
            ],
            "fields": [
                {"label": "presets", "field": "popoverfieldlist", "format": "text"},
            ],
            "settings": [
                {"label": "status", "field": "status"},
                {"label": "description", "field": "description", "hidden": "true"},
                {"label": "comments", "field": "comments", "hidden": "true"},
                {"label": "contact", "field": "contact", "hidden": "true"},
                {"label": "members", "field": "privileges"},
                {"label": "license", "field": "license"},
                {
                    "label": "visible",
                    "field": "visible",
                    "format": "check",
                    "value": "Y",
                    "hidden": "true",
                },
                {"label": "presets", "field": "popoverfieldlist", "format": "text"},
                {
                    "label": "init classif",
                    "field": "init_classif_list",
                    "hidden": "true",
                },
                {"label": "Deep feature ext.", "field": "cnn_network_id"},
            ],
        },
    }
    select = {
        "taxo": {
            "field": "select",
            "select": "taxo",
            "parts": ["preset", "objtaxonnotinpreset"],
            "selectcells": [
                "preset",
                "objtaxonnotinpreset",
            ],
        },
        "privileges": {
            "field": "select",
            "select": "privileges",
            "parts": ["privileges"],
            "selectcells": ["privileges", "contact"],
        },
        "fields": {
            "field": "select",
            "select": "fields",
            "selectcells": ["popoverfieldlist"],
        },
        "settings": {
            "label": _("select"),
            "field": "select",
            "select": "settings",
            "selectcells": [
                "title",
                "description",
                "comments",
                "instrument",
                "contact",
                "cnn_network_id",
                "visible",
                "status",
                "license",
                "popoverfieldlist",
                "init_classif_list",
                "privileges",
            ],
        },
    }

    if selection == "import":
        ths = (
            [select[typeimport]]
            + columns["import"]["commons"]
            + columns["import"][typeimport]
        )
        # tag seletected columns to import
        for i, th in enumerate(ths):
            ths[i]["data"] = dict({})
            if "autocomplete" in th:
                ths[i]["data"].update({"autocomplete": th["autocomplete"]})
            if "parts" in th:
                ths[i]["data"].update({"parts": th["parts"]})
            if "value" in th:
                ths[i]["data"].update({"value": th["value"]})
            if th["field"] in select[typeimport]["selectcells"]:
                ths[i]["data"].update({"name": th["field"]})

            elif th["field"] == "select":
                ths[i]["data"].update({"what": typeimport})

        return ths
    else:
        return [{"field": "select", "select": "controls"}] + columns[selection]


def render_stat_proj(prj: ProjectModel) -> dict:
    return dict(
        {
            "projid": prj.projid,
            "title": prj.title,
            "description": prj.description,
            "privileges": _render_privileges(prj),
            "cnn_network_id": prj.cnn_network_id,
        }
    )


def render_for_js(prjs: list, columns: list, can_access: list, isadmin: bool) -> list:

    jsonprjs = list([])
    for prj in prjs:
        jsonprj = list([])

        for column in columns:

            if column["field"] == "privileges":
                privileges = _render_privileges(prj)
                jsonprj.append(privileges)

            else:

                # if subfield  append object which will be formatted by the js component
                if column["field"] == "select":
                    if column["select"] == "controls":
                        select = dict({})
                        if prj.status != "ExploreOnly" and (
                            (
                                prj.projid
                                in can_access["Manage"] + can_access["Annotate"]
                            )
                            or isadmin
                        ):
                            select.update(dict({"A": "Annotate"}))
                        elif prj.projid in can_access["View"] or isadmin:
                            select.update(dict({"V": "View"}))
                        else:
                            if prj.visible:
                                select.update(dict({"V": "View"}))
                            select.update(dict({"R": "Request Access"}))
                        if prj.projid in can_access["Manage"] or isadmin:
                            select.update(dict({"M": "Manage"}))
                        attrvalue = select
                    else:
                        attrvalue = ""

                elif type(prj) == dict:
                    # data come from different types (if taxo it's  dict)
                    attrvalue = prj[column["field"]]

                else:
                    attrvalue = getattr(prj, column["field"])

                if "request" in column:
                    if column["request"] == "about":
                        if (
                            isadmin
                            or (prj.status == "Annotate" or prj.status == "View")
                            and (
                                prj.projid
                                in can_access["View"]
                                + can_access["Manage"]
                                + can_access["Annotate"]
                            )
                        ):
                            attrvalue = list([attrvalue, 1])
                        else:
                            attrvalue = list([attrvalue, 0])
                if "hidden" in column:
                    if column["field"] == "contact":
                        if prj.contact:
                            attrvalue = prj.contact.to_dict()
                            attrvalue.update({"contact": 1})

                        elif len(prj.managers):
                            attrvalue = prj.managers[0].to_dict()
                        else:
                            attrvalue = ""

                jsonprj.append(attrvalue)
        jsonprjs.append(jsonprj)
    return jsonprjs


def _render_privileges(prj: ProjectModel) -> dict:
    privileges = dict({})
    rights = dict(
        {
            "managers": prj.managers,
            "annotators": prj.annotators,
            "viewers": prj.viewers,
        }
    )
    for keypriv, right in rights.items():
        privileges.update(dict({keypriv: []}))

        for u in right:

            privileges[keypriv].append(u.to_dict())
    return privileges
