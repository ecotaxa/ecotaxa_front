# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2024  Picheral, Colin, Irisson (UPMC-CNRS)
import logging
import logging.handlers
import os
import sys

# Ensure the application directory is in the path for WSGI
app_dir = os.path.dirname(os.path.realpath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
os.chdir(app_dir)

from appli import app as application

# Configure logging
log_file = os.path.join(app_dir, 'Ecotaxa.log')
handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=2)
handler.setLevel(logging.INFO)
logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handler.setFormatter(logging.Formatter(logging_format))

application.logger.setLevel(logging.INFO)
application.logger.addHandler(handler)
application.logger.info("App WSGI Startup")
