# list : full project list table def - homepage
# import-[...] settings table def - projectsettings page create or update


def project_table_columns(action: str, typeimport: str) -> list:
    if action == "":
        selection = "list"
    else:
        selection = "import"
    columns = {
        "list": [
            {
                "label": "ID",
                "sortable": "desc",
                "field": "projid",
            },
            {"label": "Instrument", "field": "instrument"},
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
                "true": "Y",
            },
            {"label": "License", "field": "license"},
            {"label": "Deep feature extractor", "field": "cnn_network_id"},
            {"label": "Nb objects", "field": "objcount", "format": "number"},
            {
                "label": "%validated",
                "field": "pctvalidated",
                "format": "progress",
                "default": "0.0",
            },
        ],
        "import": {
            "commons": [
                {
                    "label": "ID",
                    "field": "projid",
                },
                {
                    "label": "Instrument",
                    "field": "instrument",
                },
                {
                    "label": "Title [ID]",
                    "field": "title",
                    "subfield": "projid",
                },
            ],
            "taxo": [
                {
                    "label": "Preset categories",
                    "field": "preset",
                    "class": "ellipsis",
                    "autocomplete": "presetids",
                },
                {
                    "label": "Extra categories used",
                    "class": "ellipsis",
                    "field": "objtaxonnotinpreset",
                    "autocomplete": "objtaxonids",
                },
                {"label": "presetids", "hidden": "true", "field": "presetids"},
                {"label": "notinpresetids", "field": "objtaxonids", "hidden": "true"},
            ],
            "privileges": [
                {"label": "Members", "field": "privileges"},
                {"label": "contact", "hidden": "true", "field": "contact"},
            ],
            "fields": [
                {"label": "presets", "field": "popoverfieldlist"},
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
                    "icon": "check",
                    "true": "Y",
                    "hidden": "true",
                },
                {"label": "presets", "field": "popoverfieldlist"},
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
            "selectcells": [
                ["preset", "presetids"],
                ["objtaxonnotinpreset", "objtaxonids"],
            ],
        },
        "privileges": {
            "field": "select",
            "select": "privileges",
            "selectcells": ["privileges", "contact"],
        },
        "fields": {
            "field": "select",
            "select": "fields",
            "selectcells": ["popoverfieldlist"],
        },
        "settings": {
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
            if th["field"] in select[typeimport]["selectcells"]:
                ths[i]["data"].update({"name": th["field"], "id": "projid"})
        return ths
    else:
        return [{"field": "select", "select": "controls"}] + columns[selection]


def render_for_js(prjs: list, columns: list, can_access: list, isadmin: bool) -> list:
    jsonprjs = list([])
    for prj in prjs:
        jsonprj = list([])

        for column in columns:

            if column["field"] == "privileges":
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

                jsonprj.append(dict({column["field"]: privileges}))

            else:

                # if subfield  append object which will be formatted by the js component
                if column["field"] == "select":
                    if column["select"] == "controls":
                        select = list([])
                        if prj.status != "ExploreOnly" and (
                            (
                                prj.projid
                                in can_access["Manage"] + can_access["Annotate"]
                            )
                            or isadmin
                        ):
                            select.append(list(["A", "Annotate"]))
                        elif prj.projid in can_access["View"] or isadmin:
                            select.append(list(["V", "View"]))
                        else:
                            if prj.visible:
                                select.append("View")
                            select.append(list(["R", "Request Access"]))
                        if prj.projid in can_access["Manage"] or isadmin:
                            select.append(list(["M", "Manage"]))
                        attrvalue = list(select)
                    else:
                        attrvalue = ""
                else:
                    attrvalue = getattr(prj, column["field"])
                if "request" in column:
                    if column["request"] == "about":
                        if (prj.status == "Annotate" or prj.status == "View") and (
                            isadmin
                            or prj.projid
                            in can_access["View"]
                            + can_access["Manage"]
                            + can_access["Annotate"]
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
