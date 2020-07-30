# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
#
# A simple proxy to relay http calls to /api domain
#
from flask import request, Response

from appli import app
from requests import get, post

BACKEND_URL = "http://localhost:8000"


@app.route('/api/<path:path>', methods=['GET', 'POST'])
def proxy_post(path):
    excluded_headers = [] #['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    if request.method == 'POST':
        resp = post(f'{BACKEND_URL}/{path}', json=request.get_json())
    elif request.method == 'GET':
        if path == "openapi.json":
            resp = get(f'{BACKEND_URL}/api/{path}')
        else:
            # If there is a session cookie then transform it into a security bearer, to authenticate GETs from browsers
            # also connected to main site.
            session_cookie = request.cookies.get('session')
            headers = {}
            if session_cookie is not None:
                headers["Authorization"] = "Bearer "+session_cookie
            resp = get(f'{BACKEND_URL}/{path}', headers=headers)
    # noinspection PyUnboundLocalVariable
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    # noinspection PyUnboundLocalVariable
    return response
