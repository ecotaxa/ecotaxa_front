# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2026  Picheral, Colin, Irisson (UPMC-CNRS)
import logging
import logging.handlers
import os
import sys
import time

from flask import request, g
from flask_login import current_user

DEFAULT_LOGGING_FORMAT = "%(process)d|%(asctime)s|%(levelname)s %(message)s"

MAX_URL_LOG_LENGTH = 320


def _truncate_url(url: str, max_length: int = MAX_URL_LOG_LENGTH) -> str:
    if len(url) <= max_length:
        return url
    return f"{url[:max_length]}...[TRUNCATED:{len(url)}B]"


def setup_logging(app, log_level=logging.INFO):
    """
    Configures standard application logging.
    Adds a StreamHandler to stdout and optionally a RotatingFileHandler if LOG_TO_FILE env var is set.
    """

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        # Static becomes file serving in uwsgi, we see them in DEV no big deal
        # if request.path.startswith("/static"):
        #     return response

        start_time = getattr(g, "start_time", 0.0)
        duration = (time.time() - start_time) * 1000
        status_code = response.status_code
        user_info = f" | U:{current_user.id}" if current_user.is_authenticated else ""
        path_with_query = _truncate_url(request.full_path.rstrip("?"))
        message = f"{request.method} {path_with_query} {status_code} | {duration:.1f}ms{user_info}"

        if status_code >= 500:
            # Check if currently throwing
            exc_type, exc_val, exc_tb = sys.exc_info()
            if exc_val is not None:
                app.logger.error(message, exc_info=(exc_type, exc_val, exc_tb))
            else:
                app.logger.error(message)
        elif status_code >= 400:
            app.logger.warning(message)
        else:
            app.logger.info(message)

        return response

    formatter = logging.Formatter(fmt=DEFAULT_LOGGING_FORMAT, datefmt="%y-%m-%d %H:%M:%S")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    app.logger.handlers.clear()  # Replace any Flask handlers
    app.logger.propagate = False
    app.logger.setLevel(log_level)
    app.logger.addHandler(stream_handler)

    if os.environ.get("LOG_TO_FILE"):
        app_dir = os.path.dirname(os.path.realpath(__file__))

        log_file = os.path.join(app_dir, "Ecotaxa.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1_000_000, backupCount=2
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
