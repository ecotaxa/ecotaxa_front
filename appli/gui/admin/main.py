import os
import flask
from flask import request, render_template, redirect, flash
from flask_security.decorators import roles_accepted

from flask_login import current_user, login_required
from flask_babel import _
from typing import List
from appli import app, gvg, gvp, constants
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    UsersApi,
    MinUserModel,
    UserModelWithRights,
    ApiException,
)


def managers_list():
    admin_users: List[MinUserModel]
    if current_user.is_authenticated:
        # With a connected user, return administrators
        with ApiClient(UsersApi, request) as api:
            admin_users = api.get_admin_users()
    else:
        # With an anonymous user, return user administrators (for account issues)
        with ApiClient(UsersApi, request) as api:
            admin_users = api.get_users_admins()
    return admin_users


@app.route("/gui/admin", methods=["GET"])
@app.route("/gui/admin/", methods=["GET"])
@login_required
@roles_accepted(constants.AdministratorLabel)
def admin_home():
    return render_template("v2/admin/index.html", admin_users=managers_list())


@roles_accepted(constants.AdministratorLabel)
def _users_list_api(listall: bool = False, filt: dict = None) -> list:
    import requests

    payload = dict({})
    users = list([])
    with ApiClient(UsersApi, request) as apiusr:
        url = (
            apiusr.api_client.configuration.host + "/users/"
        )  # endpoint is nowhere available as a const :(
        token = apiusr.api_client.configuration.access_token

        headers = {
            "Authorization": "Bearer " + token,
        }
        r = requests.get(url, headers=headers, params=payload)
        if r.status_code == 200:
            users.extend(r.json())
        else:
            r.raise_for_status()
    return users


@roles_accepted(constants.AdministratorLabel)
def _users_list(listall: bool = False, filt: dict = None) -> List[UserModelWithRights]:
    with ApiClient(UsersApi, request) as api:
        users: List[UserModelWithRights] = api.get_users()
    return users


def _check_is_admin(user=None):
    if user == None:
        user = current_user.api_user
    thisuser: UserModelWithRights = user
    return thisuser and (2 in thisuser.can_do)


@roles_accepted(constants.AdministratorLabel)
def allusers_list():
    users = _users_list_api()
    from appli.gui.admin.users_list_interface_json import (
        user_table_columns,
        render_for_js,
    )

    columns = user_table_columns()
    tabledef = dict(
        {
            "columns": columns,
            "data": render_for_js(users, columns),
        }
    )
    return tabledef


@app.route("/gui/admin/userslist/", methods=["GET"])
@roles_accepted(constants.AdministratorLabel)
@login_required
def gui_userlist(listall: bool = False) -> str:
    isadmin = _check_is_admin(current_user.api_user)

    # gzip not really necessary - jsonifiy with separators
    from flask import make_response
    import json

    gz = gvg("gzip")
    content = json.dumps(allusers_list(), separators=[",", ":"]).encode("utf-8")

    encoding = "utf-8"
    if gz:
        import gzip

        content = gzip.compress(content, 7)
        encoding = "gzip"
    response = make_response(content)

    response.headers["Content-length"] = len(content)
    response.headers["Content-Encoding"] = encoding
    response.headers["Content-Type"] = "application/json"

    return response


@app.route("/gui/admin/users/", methods=["GET"])
@login_required
@roles_accepted(constants.AdministratorLabel)
def gui_users_list_page(
    listall: bool = False,
    partial: bool = False,
) -> str:

    if not current_user.is_authenticated:
        return render_template(
            "v2/error.html", title="403", message=py_messages["restrictedaccess"]
        )
    if partial == True:
        template = "v2/admin/_userslistcontainer.html"
    else:
        template = "v2/admin/users.html"
    return render_template(
        template,
        listall=listall,
        partial=partial,
        isadmin=_check_is_admin(current_user.api_user),
        experimental="",
    )


@app.route("/gui/admin/users/create", methods=["GET", "POST"])
@app.route("/gui/admin/users/create/", methods=["GET", "POST"])
@login_required
@roles_accepted(constants.AdministratorLabel)
def gui_user_create():

    from appli.gui.users.commontools import (
        user_create,
        account_page,
        ACCOUNT_USER_CREATE,
        IS_FROM_ADMIN,
    )

    if request.method == "POST":
        [user, ret] = user_create(usrid=-1, isfrom=IS_FROM_ADMIN)
        if ret:
            flash(ret, "error")
        else:
            flash("success " + usrid, "success")
    return account_page(
        action=ACCOUNT_USER_CREATE,
        usrid=-1,
        isfrom=IS_FROM_ADMIN,
        template="v2/admin/user.html",
    )


@app.route("/gui/admin/users/edit/<int:usrid>", methods=["GET", "POST"])
@login_required
@roles_accepted(constants.AdministratorLabel)
def gui_user_edit(usrid):
    from appli.gui.users.commontools import (
        user_edit,
        account_page,
        ACCOUNT_USER_EDIT,
        IS_FROM_ADMIN,
    )

    if request.method == "POST":
        [user, err] = user_edit(usrid, isfrom=IS_FROM_ADMIN)
        if err != None:
            flash(err, "error")
        else:
            flash("success : " + str(usrid), "success")

    return account_page(
        action=ACCOUNT_USER_EDIT,
        usrid=usrid,
        isfrom=IS_FROM_ADMIN,
        template="v2/admin/user.html",
    )


@app.route("/gui/admin/messages", defaults={"msgkey": None}, methods=["GET"])
@app.route("/gui/admin/messages/", defaults={"msgkey": None}, methods=["GET"])
@app.route("/gui/admin/messages/<msgkey>", methods=["GET", "POST"])
@login_required
@roles_accepted(constants.AdministratorLabel)
def gui_site_message(msgkey) -> str:
    import json

    file = app.config.get("APP_GUI_MESSAGE_FILE")

    if os.path.exists(file):

        with open(file, "r", encoding="utf-8") as f:
            messages = json.loads(f.read())

    else:
        initcontent = {"content": "", "active": False, "date": ""}
        messages = dict({"info": initcontent, "maintenance": initcontent})

    if request.method == "POST":
        from datetime import datetime

        msg = gvp("msg")
        active = gvp("active", 0)
        messages[msgkey] = {
            "content": msg,
            "active": int(active),
            "date": str(datetime.now()),
        }
        with open(file, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(messages))
        flash("message saved", "success")
        msgkey = ""

    return render_template("v2/admin/messages.html", msgkey=msgkey, messages=messages)


@app.context_processor
def utility_admin_processor():
    def admin_menu():
        return dict(
            {
                "home": {"label": _("Messages"), "url": "/gui/admin/messages/"},
                "users": {
                    "label": _("Users"),
                    "links": {
                        "list": {"label": _("List"), "url": "/gui/admin/users/"},
                        "create": {
                            "label": _("Create"),
                            "url": "/gui/admin/users/create/",
                        },
                        "settings": {
                            "label": _("Settings"),
                            "url": "/gui/admin/users/settings",
                            "comment": _("Validation process selection and parameters"),
                        },
                    },
                },
                "job": {
                    "label": _("Tasks"),
                    "comment": _("View all users tasks"),
                    "url": "/gui/jobs/listall?seeall=Y",
                },
                "database": {
                    "label": _("Database"),
                    "links": {
                        "dbsize": {
                            "label": _("View DB Size"),
                            "url": "/admin/db/viewsizes",
                        },
                        "dbbloat": {
                            "label": _("View DB Bloat"),
                            "url": "/admin/db/viewbloat",
                        },
                        "sqlconsole": {
                            "label": _("SQL Console"),
                            "url": "/admin/db/console",
                        },
                        "recomputestat": {
                            "label": _("Recompute Projects and Taxo stat"),
                            "comment": _("can be long"),
                            "url": "/admin/db/recomputestat",
                        },
                    },
                },
            }
        )

    return dict(admin_menu=admin_menu)
