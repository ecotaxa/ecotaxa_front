# -*- coding: utf-8 -*-
from appli import app
import logging
import logging.handlers

if __name__ == '__main__':
    app.debug = True
    handler = logging.handlers.RotatingFileHandler('MyAppli.log', maxBytes=10000, backupCount=1)
    #handler = logging.FileHandler('MyAppli.log')
    handler.setLevel(logging.INFO)
    LoggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(logging.Formatter(LoggingFormat))
    app.logger.addHandler(handler)
    app.logger.info("App Startup")
    app.run()
