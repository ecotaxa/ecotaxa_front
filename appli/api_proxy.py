# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
#
# A proxy to relay http calls to /api domain
#
from flask import request, Response
import requests

from appli import app
from requests import get, post

BACKEND_URL = "http://localhost:8000"
session = requests.sessions.Session()


@app.route('/api/<path:path>', methods=['GET', 'POST'])
def proxy_post(path):
    import time; start = time.time()
    req_headers = request.headers
    if request.method == 'POST':
        if path == "login":
            # Proxy the login which is here and not in backend yet
            # TODO
            pass
        resp = post(f'{BACKEND_URL}/{path}', json=request.get_json(), headers=req_headers, stream=True)
    elif request.method == 'GET':
        # From URL
        req_args = request.args
        # From form
        req_params = request.form
        if path == "openapi.json":
            # Plain page with no need for tricks on headers
            resp = get(f'{BACKEND_URL}/api/{path}')
        else:
            # If there is a session cookie then transform it into a security bearer, to authenticate GETs from browsers
            # also connected to main site.
            session_cookie = request.cookies.get('session')
            if session_cookie is not None:
                # Clone headers as they are immutable
                req_headers = {name: value for (name, value) in req_headers.items()}
                req_headers["Authorization"] = "Bearer " + session_cookie
            #resp = get(f'{BACKEND_URL}/{path}', headers=req_headers)
            resp = session.get(f'{BACKEND_URL}/{path}', params=req_args, headers=req_headers, stream=True)
            app.logger.info("API call duration: %0.2f"%((time.time()-start)*1000))
    excluded_headers = []  # ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    rsp_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.iter_content(chunk_size=10*1024), resp.status_code, rsp_headers)
    app.logger.info("API relay duration: %0.2f"%((time.time()-start)*1000))
    return response
