# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2026  Picheral, Colin, Irisson (UPMC-CNRS)
#
# Production WSGI server, @see docker configuration
import os
import sys

# Ensure the application directory is in the path for WSGI
app_dir = os.path.dirname(os.path.realpath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
os.chdir(app_dir)

from appli import app
from logging_conf import setup_logging

setup_logging(app)

app.logger.info("App WSGI Startup")
