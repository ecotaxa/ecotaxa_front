# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
#
# A proxy to relay http calls to /api domain
#
import time
import types
from http.client import HTTPConnection, HTTPResponse
from urllib.parse import urlencode

from flask import request, Response
from werkzeug.wsgi import wrap_file

from appli import app

BACKEND_HOST = "localhost"
BACKEND_PORT = 8000
# noinspection HttpUrlsUsage
BACKEND_URL = "http://%s:%d" % (BACKEND_HOST, BACKEND_PORT)


@app.route('/api/<path:path>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def proxy_request(path):
    start = time.time()
    # Prepare request data
    method = request.method
    url = f'/api/{path}'
    body = request.get_data()  # Copy body, e.g. json params
    headers = _copy_headers_and_session(request.headers)
    if method == 'POST':
        params = request.args  # re-encode URL params if any
        if path == "login":
            # Proxy the login which is here and not in backend yet
            # TODO
            pass
    elif method == 'GET':
        # From URL
        params = request.values  # join of request.args and request.form
    elif method == 'DELETE':
        params = request.args
    elif method == 'PUT':
        params = request.args
    else:
        return "Not implemented"
    # Do the call itself
    req = HTTPConnection(host=BACKEND_HOST, port=BACKEND_PORT)
    if params:
        url += "?" + urlencode(params)
    req.request(method=method, url=url, body=body, headers=headers)
    rsp: HTTPResponse = req.getresponse()
    app.logger.debug("API call duration: %0.2fms", ((time.time() - start) * 1000))
    # Reply to caller
    rsp_headers = _copy_back_headers(rsp)
    # For chunked content we need http 1.1. Firefox cares when Chrome doesn't (surprise!)
    is_chunked = ("transfer-encoding", "chunked") in rsp_headers
    app.logger.debug("Chunked: %s", is_chunked)
    _piggyback_response(rsp, is_chunked)
    # Sort of stream the response
    response = Response(wrap_file({}, rsp, 1024), rsp.status, rsp_headers, direct_passthrough=True)
    app.logger.debug("API relay duration: %0.2fms", ((time.time() - start) * 1000))
    return response


def _copy_headers_and_session(req_headers):
    """ Copy incoming headers into relayed request """
    # Clone headers as they are immutable
    ret = {name: value for (name, value) in req_headers.items()}
    # If there is a session cookie then transform it into a security bearer,
    # to authenticate GETs from browsers also connected to main site.
    session_cookie = request.cookies.get('session')
    if session_cookie is not None:
        ret["Authorization"] = "Bearer " + session_cookie
    return ret


def _copy_back_headers(response: HTTPResponse):
    """ Copy response headers into relayed response """
    excluded_headers = {}  # ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    rsp_headers = [(name.lower(), value.lower()) for (name, value) in response.getheaders()
                   if name.lower() not in excluded_headers]
    return rsp_headers


def _piggyback_response(response: HTTPResponse, is_chunked: bool):
    """ Inject below reader into the HTTPResponse """
    response.orig_read = response.read
    response.nb_bytes = 0
    response.is_chunked = is_chunked
    response.read = types.MethodType(_my_read, response)


def _my_read(self, amt):
    """ Add into stream the chunk markers when needed """
    ret = self.orig_read(amt)
    at_eof = len(ret) == 0
    if self.is_chunked:
        # Re-chunk the chunked response
        chunk = hex(len(ret))[2:] + "\r\n"
        # OK we add a few bytes but anyway the call only gives an indication of size
        ret = bytes(chunk, "utf-8") + ret + b"\r\n"
    if at_eof:
        # At EOF stop sending chunks, i.e. blocks of size 3, otherwise it loops forever on reader side
        # if it's not chunks-aware.
        self.is_chunked = False
    self.nb_bytes += len(ret)
    # app.logger.debug("%d response bytes read", self.nb_bytes)
    return ret
