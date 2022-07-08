# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os
from typing import List
from flask import request
from flask_login import current_user, login_required
from appli import app

import appli.gui.project.main


@app.route("/gui")
def gui_index():
    from appli.gui.commontools import RenderTemplate, WebStats

    webstats = WebStats(app)

    return RenderTemplate("index", webstats=webstats)


@app.route("/gui/<path:filename>")
def gui_any(filename):
    xhr = request.headers.get("xhr")
    filename = filename.replace("/", "")
    if xhr == "1":
        filename = "project/partials/" + filename
    else:
        if filename == "about":
            from appli.gui.renders import RenderAbout

            return RenderAbout()
        elif filename == "prj" or filename == "prjothers":
            from appli.gui.renders import ListProjects

            if filename == "prj":
                # @login_required
                return ListProjects(Others=False)
            elif filename == "prjothers":
                return ListProjects(Others=True)

    from appli.gui.commontools import RenderTemplate, WebStats

    webstats = WebStats(app)
    return RenderTemplate(filename + "/", webstats=webstats)


@app.route("/gui/prj/<path:filename>")
def gui_prjaction(filename):
    print(filename)
    xhr = request.headers.get("xhr")
    print(xhr)
    if xhr == "1":
        filename = "project/partials/" + filename
    from appli.gui.commontools import RenderTemplate, WebStats

    webstats = WebStats(app)
    return RenderTemplate(filename, webstats=webstats)


# push special infos to admins ( daily maintenance credentials expired to begin with)
def NightlyJobStream(type=None, user_id=None):
    from to_back.ecotaxa_cli_py.api import AdminApi
    from appli.utils import ApiClient
    import json, datetime

    format = "%Y-%m-%d"
    pgformat = "YYYY-MM-DD"
    dt = datetime.date.today().strftime(format)
    sql = (
        "SELECT job.type,job.state,job.creation_date,job.owner_id FROM job WHERE to_char(job.creation_date,'"
        + pgformat
        + "') != '"
        + dt
        + "'"
    )
    if type != None:
        sql += " AND job.type NOT LIKE '" + type + "'"
    if user_id != None:
        sql += " AND job.owner_id != " + user_id

    with ApiClient(AdminApi, request) as api:
        res = api.db_direct_query(q=sql)
        return json.dumps(res["data"])


@app.route("/adminstream/", methods=["GET", "POST"])
def stream():
    return NightlyJobStream(type="NightlyMaintenance", user_id=None)


# utility display functions for jinja template
@app.context_processor
def utility_processor():
    def format_nb(number, f, locale="en_US"):
        from babel.numbers import (
            format_number,
            format_decimal,
            format_percent,
            format_number,
        )

        if f == "number":
            return format_number(number, format, locale)
        elif f == "decimal":
            return format_decimal(number, format, locale)
        elif f == "percent":
            return format_percent(number, format, locale)
        elif f == "scientific":
            return format_scientific(number, format, locale)
        else:
            return number

    return dict(format_nb=format_nb)
