# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)


import logging.handlers
import sys

from appli import app

if __name__ == '__main__':
    # app.debug = True
    handler = logging.StreamHandler()
    # handler = logging.handlers.RotatingFileHandler('MyAppli.log', maxBytes=1000000, backupCount=1)
    # handler = logging.FileHandler('MyAppli.log')
    handler.setLevel(logging.INFO)
    LoggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(logging.Formatter(LoggingFormat))
    app.logger.addHandler(handler)
    app.logger.info("EcoTaxa (dev) Startup")


    app.run(host='0.0.0.0', port=5001, threaded=True)
