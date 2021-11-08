# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import appli.part.views.prj
from appli.part.database import ComputeOldestSampleDateOnProject

if __name__ == "__main__":
    # RefreshTaxoStat()
    from appli import app
    from flask import g
    import logging
    import traceback
    from appli.tasks.taskmanager import AutoClean

    app.logger.setLevel(logging.DEBUG)
    for h in app.logger.handlers:
        h.setLevel(logging.DEBUG)
    app.logger.info("Start Daily Task")
    try:
        with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
            g.db = None
            app.logger.info("EcoPart...")
            ComputeOldestSampleDateOnProject()
            appli.part.views.prj.GlobalTaxoCompute()
            app.logger.info("EcoPart tasks+EcoTaxa one...")
            # Keep EcoPart auto clean
            app.logger.info(AutoClean())
    except Exception as e:
        s = str(e)
        tb_list = traceback.format_tb(e.__traceback__)
        for i in tb_list[::-1]:
            s += "\n" + i
        app.logger.error("Exception on Daily Task : %s" % s)
    app.logger.info("End Daily Task")
