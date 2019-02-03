# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import sys,os
import logging,sys
import logging.handlers
from pathlib import Path
# on fait le activate avant de lancer apache car sinon il trouve pas python 3.4 car sur mon PC default = 2.7
# #activate_this = R'D:\dev\_Client\LOV\EcoTaxa\Python\Scripts\activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read())
if sys.platform.startswith('win32'):
    sys.path.insert(0,os.path.normpath(os.path.dirname(os.path.realpath(__file__))))
    os.chdir(os.path.normpath(os.path.dirname(os.path.realpath(__file__))))
    sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), R"..\Python\Lib\site-packages")))
    sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), R"..\Python\Lib\site-packages\psycopg2-2.6-py3.4-win32.egg")))

#Le from doit être aprés la modification du path et du chdir
from appli import app as application

handler = logging.handlers.RotatingFileHandler('Ecotaxa.log', maxBytes=1000000, backupCount=2)
#handler.setLevel(logging.INFO) loggue tout par defaut.
LoggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handler.setFormatter(logging.Formatter(LoggingFormat))
application.logger.addHandler(handler)
application.logger.info("App WSGI Startup")

if application.PythonExecutable=="TBD":
    if sys.platform.startswith('win32'):
        # version Virtual Env
        # application.PythonExecutable=os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), R"..\Python\Scripts\python.exe"))
        if not Path(application.PythonExecutable).exists(): # version Ecotaxa portable
            application.PythonExecutable= "python.exe" # sous apache il n'as pas le nom de l'exe, grace � venv il est dans le path
    else:
        application.PythonExecutable='/usr/local/bin/python3'
