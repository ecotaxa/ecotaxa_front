# -*- coding: utf-8 -*-
import sys,os
from appli import app
import logging,sys
import logging.handlers
# on fait le activate avant de lancer apache car sinon il trouve pas python 3.4 car sur mon PC default = 2.7
# #activate_this = R'D:\dev\_Client\LOV\EcoTaxa\Python\Scripts\activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read())
if sys.platform.startswith('win32'):
    # sys.path.insert(0, R'D:\dev\_Client\LOV\EcoTaxa\EcoTaxa')
    sys.path.insert(0,os.path.normpath(os.path.dirname(os.path.realpath(__file__))))
    os.chdir(os.path.normpath(os.path.dirname(os.path.realpath(__file__))))
    # sys.path.insert(0, R'D:\dev\_Client\LOV\EcoTaxa\Python\Lib\site-packages')
    sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), R"..\Python\Lib\site-packages")))
    # sys.path.insert(0, R'D:\dev\_Client\LOV\EcoTaxa\Python\Lib\site-packages\psycopg2-2.6-py3.4-win32.egg')
    sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), R"..\Python\Lib\site-packages\psycopg2-2.6-py3.4-win32.egg")))


handler = logging.handlers.RotatingFileHandler('Ecotaxa.log', maxBytes=1000000, backupCount=2)
handler.setLevel(logging.INFO)
LoggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handler.setFormatter(logging.Formatter(LoggingFormat))
app.logger.addHandler(handler)
app.logger.info("App WSGI Startup")

if sys.platform.startswith('win32'):
    app.PythonExecutable=os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), R"..\Python\Scripts\python.exe"))
else:
    app.PythonExecutable='/usr/local/bin/python3'
