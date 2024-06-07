# list : full users list table def - admin
from flask_babel import _
from flask import url_for


def user_table_columns(selection: str = "list") -> list:
    columns = {
        "list": {
            "select": {
                "select": "controls",
                "field": "id",
                "actions": {
                    "edit": {
                        "link": url_for("gui_user_edit", usrid=-1),
                        "label": _("edit"),
                        "type": "button",
                    }
                },
            },
            "id": {
                "label": _("ID"),
                "sortable": "desc",
                "format": "number",
            },
            "name": {
                "label": _("Name"),
            },
            "email": {
                "label": _("Email"),
            },
            "organisation": {
                "label": _("Organisation"),
            },
            "usercreationdate": {
                "label": _("Creation date"),
            },
            "usercreationreason": {
                "label": _("Creation reason"),
            },
            "country": {
                "label": _("Country"),
            },
            # "can_do": {"label": _("Auth"), "hidden": "true"},
            "mail_status": {"label": _("@Status"), "format": "check"},
            "status": {
                "label": _("Status"),
                "format": "button",
                "link": url_for("gui_user_activate", usrid=-1, token=None),
            },
        },
    }

    return columns[selection]


def render_for_js(users: list, columns: list) -> list:
    from datetime import datetime

    jsonusers = list([])
    translations = dict({})
    status_label = [_("blocked"), _("inactive"), _("active"), _("pending")]
    for user in users:

        jsonuser = list([])

        for key, column in columns.items():
            # if subfield  append object which will be formatted by the js component
            attrvalue = ""
            if key == "select":
                attrvalue = user[column["field"]]
            elif key == "status":
                attrvalue = status_label[user[key] + 1]
            else:
                attrvalue = user[key]

            if isinstance(attrvalue, datetime):
                attrvalue = attrvalue.isoformat()

                if key in translations:
                    if attrvalue in translations[key]:
                        attrvalue = translations[key][attrvalue]

            jsonuser.append(attrvalue)
        jsonusers.append(jsonuser)

    return jsonusers
