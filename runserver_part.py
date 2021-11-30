# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)


import logging.handlers
import sys

from part_app.app import part_app

if __name__ == '__main__':
    # app.debug = True
    handler = logging.StreamHandler()
    # handler = logging.handlers.RotatingFileHandler('MyAppli.log', maxBytes=1000000, backupCount=1)
    # handler = logging.FileHandler('MyAppli.log')
    handler.setLevel(logging.INFO)
    LoggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(logging.Formatter(LoggingFormat))
    part_app.logger.addHandler(handler)
    part_app.logger.info("EcoPart (dev) Startup")
    # L'executable est l'interpreteur qui a permis de lancer, mais en WSGI c'est écrasé par le lanceur WSGI
    if part_app.PythonExecutable == "TBD":  # si pas forcé par un fichier de configuration
        part_app.PythonExecutable = sys.executable

    part_app.run(host='0.0.0.0', port=5002, threaded=True)
