import os
import flask
from flask import request, url_for, render_template, redirect, flash, escape
from werkzeug.exceptions import Forbidden
from flask_login import current_user, login_required
from flask_babel import _
from typing import List
from appli import app, gvg, gvp
from appli.constants import (
    AdministratorLabel,
    UserAdministratorLabel,
    API_GLOBAL_ROLES,
)
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    AdminApi,
    UsersApi,
    MinUserModel,
    UserModelWithRights,
    ApiException,
)
from appli.security_on_backend import gui_roles_accepted
from markupsafe import Markup


def admins_list(role=None, all=False):
    admin_users: List[MinUserModel]
    if not current_user.is_authenticated:
        return None
    with ApiClient(UsersApi, request) as api:
        if role == None or role == AdministratorLabel:
            admin_users = api.get_admin_users()
        elif role == UserAdministratorLabel:
            admin_users = api.get_users_admins()
    return admin_users


@app.route("/gui/admin", methods=["GET"])
@app.route("/gui/admin/", methods=["GET"])
@gui_roles_accepted(AdministratorLabel, UserAdministratorLabel)
@login_required
def admin_home():
    admin_users = dict(
        {
            "application": admins_list(),
            "users": admins_list(UserAdministratorLabel),
        }
    )
    return render_template(
        "v2/admin/index.html",
        admin_users=admin_users,
    )


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


def _users_list(listall: bool = False, filt: dict = None) -> List[UserModelWithRights]:
    with ApiClient(UsersApi, request) as api:
        users: List[UserModelWithRights] = api.get_users()
    return users


def _check_is_admin(user=None):
    if user == None:
        user = current_user.api_user
    thisuser: UserModelWithRights = user
    return thisuser and (2 in thisuser.can_do)


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
@gui_roles_accepted(AdministratorLabel, UserAdministratorLabel)
@login_required
def gui_userlist(listall: bool = False) -> str:

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
@app.route("/gui/admin/users", methods=["GET"])
@gui_roles_accepted(AdministratorLabel, UserAdministratorLabel)
@login_required
def gui_users_list_page(
    listall: bool = False,
    partial: bool = False,
) -> str:

    if not current_user.is_authenticated:
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    if partial == True:
        template = "v2/admin/_userslistcontainer.html"
    else:
        template = "v2/admin/users.html"
    return render_template(
        template,
        listall=listall,
        partial=partial,
    )


@app.route(
    "/gui/admin/users/activate/<int:usrid>", defaults={"token": None}, methods=["GET"]
)
@app.route(
    "/gui/admin/users/activate/<int:usrid>/",
    defaults={"status_name": None},
    methods=["GET", "POST"],
)
@app.route(
    "/gui/admin/users/activate/<int:usrid>/<status_name>", methods=["GET", "POST"]
)
@gui_roles_accepted(AdministratorLabel, UserAdministratorLabel)
@login_required
def gui_user_activate(usrid: int, status_name: str = None) -> str:
    if not current_user.is_authenticated:
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    from appli.gui.users.users import api_get_user
    from appli.back_config import get_user_constants

    (
        ApiUserStatus,
        API_PASSWORD_REGEXP,
        API_EMAIL_VERIFICATION,
        API_ACCOUNT_VALIDATION,
        SHORT_TOKEN_AGE,
        PROFILE_TOKEN_AGE,
        RECAPTCHAID,
        ADD_TICKET,
    ) = get_user_constants(request)

    if request.method == "GET" and status_name != "active":
        user = api_get_user(usrid)
        if status_name != None and status_name in ApiUserStatus.keys():
            user.status = ApiUserStatus[status_name]
        return render_template(
            "v2/admin/activate.html",
            user=user,
            status_name=status_name,
            add_ticket=ADD_TICKET,
        )
    from appli.gui.users.users import api_user_activate

    reason = gvp("status_admin_comment", None)

    if ADD_TICKET != "":
        ticket = gvp("ticket", None)
        if ticket != None:
            reason = ticket + ADD_TICKET + reason
    if reason != None and status_name != "blocked":
        status = ApiUserStatus["pending"]
    else:
        status = int(gvp("status", 1))
    response = api_user_activate(usrid, status, reason=reason)
    if response[0] == 0:
        type = "success"
    else:
        type = "error"

    message = "User " + str(usrid) + " " + response[1]
    flash(message, type)
    if type == "error":
        return redirect(
            url_for("gui_user_activate", usrid=usrid, status_name=status_name)
        )
    return redirect(url_for("gui_users_list_page"))

    return render_template(
        "./v2/admin/users.html",
        isadmin=_check_is_admin(current_user.api_user),
    )


@app.route("/gui/admin/users/create", methods=["GET", "POST"])
@app.route("/gui/admin/users/create/", methods=["GET", "POST"])
@gui_roles_accepted(AdministratorLabel, UserAdministratorLabel)
@login_required
def gui_user_create():
    from appli.gui.users.users import (
        user_create,
        account_page,
        ACCOUNT_USER_CREATE,
    )

    if request.method == "POST":
        response = user_create(usrid=-1, isfrom=True)
        if response == 0:
            flash("user created", "success")
        else:
            flash(response[1], "error")
            return redirect(url_for("gui_users_list_page"))
    return account_page(
        action=ACCOUNT_USER_CREATE,
        usrid=-1,
        isfrom=True,
        template="v2/admin/user.html",
    )


@app.route("/gui/admin/users/edit/", defaults={"usrid": -1}, methods=["GET", "POST"])
@app.route("/gui/admin/users/edit/<int:usrid>", methods=["GET", "POST"])
@gui_roles_accepted(AdministratorLabel, UserAdministratorLabel)
@login_required
def gui_user_edit(usrid):
    if usrid == -1:
        return redirect(url_for("gui_user_create"))
    from appli.gui.users.users import (
        user_edit,
        account_page,
        ACCOUNT_USER_EDIT,
    )

    if request.method == "POST":
        reponse = user_edit(usrid, isfrom=True)
        if reponse[0] == 0:
            flash(reponse[1], "success")
            return redirect(url_for("gui_user_edit", usrid=usrid))
        else:
            message = reponse[1]
            flash(message, "error")
            return redirect(url_for("gui_users_list_page"))
    return account_page(
        action=ACCOUNT_USER_EDIT,
        usrid=usrid,
        isfrom=True,
        template="v2/admin/user.html",
    )


@app.route("/gui/admin/messages", defaults={"msgkey": None}, methods=["GET"])
@app.route("/gui/admin/messages/", defaults={"msgkey": None}, methods=["GET"])
@app.route("/gui/admin/messages/<msgkey>", methods=["GET", "POST"])
@gui_roles_accepted(AdministratorLabel, UserAdministratorLabel)
@login_required
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
        return redirect(request.referrer)

    return render_template("v2/admin/messages.html", msgkey=msgkey, messages=messages)


#######################DB utils ###########################


@app.route("/gui/admin/db/viewsizes")
@login_required
@gui_roles_accepted(AdministratorLabel)
def gui_dbadmin_viewsizes():
    sql = """SELECT c.relname, c.relkind, CASE WHEN c.relkind='i' THEN c2.tablename ELSE c.relname END fromtable,pg_relation_size(('"' || c.relname || '"')::regclass)/(1024*1024) szMB
FROM
 pg_namespace ns,
 pg_class c LEFT OUTER JOIN
 pg_indexes c2 ON c.relname = c2.indexname
WHERE c.relnamespace = ns.oid
 AND ns.nspname = 'public'
 AND c.relkind IN ('r' ,'i')
ORDER BY c.relkind DESC, pg_relation_size(('"' || c.relname || '"')::regclass) DESC
"""
    with ApiClient(AdminApi, request) as api:
        res = api.db_direct_query(q=sql)
    txt = (
        "<h2 class='mx-auto mt-2 mb-8'>Database objects size (public schema only)</h2>"
    )
    txt += """<div id='db_viewsizes' class='js js-datatable block w-full overflow-x-hidden'><table >
            <tr><th width=200>Object</td><th witdth=200>Table</td><th width=100>Size (Mb)</th></tr>"""
    for r in res["data"]:
        txt += """<tr><td>{0}</td>
        <td>{2}</td>
        <td>{3}</td>

        </tr>""".format(
            *r
        )
    txt += "</table></div>"

    return render_template("v2/admin/db_page.html", body=Markup(txt))


@app.route("/gui/admin/db/viewbloat")
@login_required
@gui_roles_accepted(AdministratorLabel)
def gui_dbadmin_viewbloat():
    sql = """SELECT
        schemaname, tablename, reltuples::bigint, relpages::bigint, otta,
        ROUND(CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::numeric END,1) AS tbloat,
        relpages::bigint - otta AS wastedpages,
        bs*(sml.relpages-otta)::bigint AS wastedbytes,
        pg_size_pretty((bs*(relpages-otta))::bigint) AS wastedsize,
        iname, ituples::bigint, ipages::bigint, iotta,
        ROUND(CASE WHEN iotta=0 OR ipages=0 THEN 0.0 ELSE ipages/iotta::numeric END,1) AS ibloat,
        CASE WHEN ipages < iotta THEN 0 ELSE ipages::bigint - iotta END AS wastedipages,
        CASE WHEN ipages < iotta THEN 0 ELSE bs*(ipages-iotta) END AS wastedibytes,
        CASE WHEN ipages < iotta THEN '0' ELSE pg_size_pretty((bs*(ipages-iotta))::bigint) END AS wastedisize
      FROM (
        SELECT
          schemaname, tablename, cc.reltuples, cc.relpages, bs,
          CEIL((cc.reltuples*((datahdr+ma-
            (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta,
          COALESCE(c2.relname,'?') AS iname, COALESCE(c2.reltuples,0) AS ituples, COALESCE(c2.relpages,0) AS ipages,
          COALESCE(CEIL((c2.reltuples*(datahdr-12))/(bs-20::float)),0) AS iotta -- very rough approximation, assumes all cols
        FROM (
          SELECT
            ma,bs,schemaname,tablename,
            (datawidth+(hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)))::numeric AS datahdr,
            (maxfracsum*(nullhdr+ma-(case when nullhdr%ma=0 THEN ma ELSE nullhdr%ma END))) AS nullhdr2
          FROM (
            SELECT
              schemaname, tablename, hdr, ma, bs,
              SUM((1-null_frac)*avg_width) AS datawidth,
              MAX(null_frac) AS maxfracsum,
              hdr+(
                SELECT 1+count(*)/8
                FROM pg_stats s2
                WHERE null_frac<>0 AND s2.schemaname = s.schemaname AND s2.tablename = s.tablename
              ) AS nullhdr
            FROM pg_stats s, (
              SELECT
                (SELECT current_setting('block_size')::numeric) AS bs,
                CASE WHEN substring(v,12,3) IN ('8.0','8.1','8.2') THEN 27 ELSE 23 END AS hdr,
                CASE WHEN v ~ 'mingw32' THEN 8 ELSE 4 END AS ma
              FROM (SELECT version() AS v) AS foo
            ) AS constants
            GROUP BY 1,2,3,4,5
          ) AS foo
        ) AS rs
        JOIN pg_class cc ON cc.relname = rs.tablename
        JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname
        LEFT JOIN pg_index i ON indrelid = cc.oid
        LEFT JOIN pg_class c2 ON c2.oid = i.indexrelid
      ) AS sml
      WHERE sml.relpages - otta > 0 OR ipages - iotta > 10
      ORDER BY wastedbytes DESC, wastedibytes DESC
"""
    with ApiClient(AdminApi, request) as api:
        res = api.db_direct_query(q=sql)
    txt = "<h2 class='mx-auto mt-2 mb-8'>Database objects wasted space</h2>"
    txt += "<div id='db_viewbloat' class='js js-datatable block w-full overflow-x-hidden'><table class='datatable'>"
    txt += "<tr><th>" + ("</th><th>".join(res["header"])) + "</th></tr>"
    for r in res["data"]:
        txt += "<tr><td>" + ("</td><td>".join([str(x) for x in r])) + "</td></tr>"
    txt += "</table></div>"
    return render_template("v2/admin/db_page.html", body=Markup(txt))


@app.route("/gui/admin/db/recomputestat")
@login_required
@gui_roles_accepted(AdministratorLabel)
def gui_dbadmin_recomputestat():
    # TODO: API call, if we leave the menu entry...
    return render_template(
        "v2/admin/db_page.html",
        body="Statistics recompute is not possible anymore in the UI",
    )


@app.route("/gui/admin/db/console", methods=["GET", "POST"])
@login_required
@gui_roles_accepted(AdministratorLabel)
def gui_dbadmin_console():
    sql = gvp("sql")
    if (
        len(request.form) > 0 and request.referrer != request.url
    ):  # si post doit venir de cette page
        txt = "Invalid referer"
    else:
        txt = "<div class='alert is-danger'>Warning : This screen must be used only by experts</div>"
        txt += (
            "<form method=post action="
            + request.path
            + ">SQL : <textarea name=sql rows=15 cols=100 class='form-input'>%s</textarea><br>"
            % escape(sql)
        )
        txt += """<input type=submit class='button is-primary' name=doselect value='Execute Select'>
    <input type=submit class='button is-primary' name=dodml value='Execute DML'>
    Note : For DML ; can be used, but only the result of the last query displayed
    </form>"""
        if gvp("doselect"):
            txt += "<br>Select Result :"
            try:
                with ApiClient(AdminApi, request) as api:
                    res = api.db_direct_query(q=sql)
                txt += (
                    "<div id='db_console' class='js js-datatable large-table'><table>"
                )
                for c in res["header"]:
                    txt += "<th>%s</th>" % c
                for r in res["data"]:
                    s = "<tr>"
                    for c in r:
                        s += "<td>%s</td>" % c
                    txt += s + "</tr>"
                txt += "</table></div>"
            except Exception as e:
                txt += "<br>Error = %s" % e
        if gvp("dodml"):
            txt = "Under review"
            # txt += "<br>DML Result :"
            # cur = db.engine.raw_connection().cursor()
            # try:
            #     cur.execute(sql)
            #     txt += "%s rows impacted" % cur.rowcount
            #     cur.connection.commit()
            # except Exception as e:
            #     txt += "<br>Error = %s" % e
            #     cur.connection.rollback()
            # finally:
            #     cur.close()

    return render_template("v2/admin/db_page.html", body=Markup(txt))


#######################


@app.context_processor
def utility_admin_processor():
    def admin_menu():
        menu = dict(
            {
                "messages": {
                    "label": _("Messages"),
                    "url": url_for("gui_site_message"),
                },
                "users": {
                    "label": _("Users"),
                    "links": {
                        "list": {
                            "label": _("List"),
                            "url": url_for("gui_users_list_page"),
                        },
                        "create": {
                            "label": _("Create"),
                            "url": url_for("gui_user_create"),
                        },
                    },
                },
                "job": {
                    "label": _("Tasks"),
                    "comment": _("View all users tasks"),
                    "url": url_for("gui_list_jobs", seeall="Y"),
                },
                "database": {
                    "label": _("Database"),
                    "links": {
                        "dbsize": {
                            "label": _("View DB Size"),
                            "url": url_for("gui_dbadmin_viewsizes"),
                        },
                        "dbbloat": {
                            "label": _("View DB Bloat"),
                            "url": url_for("gui_dbadmin_viewbloat"),
                        },
                        "sqlconsole": {
                            "label": _("SQL Console"),
                            "url": url_for("gui_dbadmin_console"),
                        },
                        "recomputestat": {
                            "label": _("Recompute Projects and Taxo stat"),
                            "comment": _("can be long"),
                            "url": url_for("gui_dbadmin_recomputestat"),
                        },
                    },
                },
            }
        )

        if current_user.is_app_admin != True:
            del menu["database"]
            del menu["job"]
            del menu["messages"]
        return menu

    return dict(admin_menu=admin_menu)
