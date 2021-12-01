# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import logging
import os
import traceback

from flask import g

from part_app.app import part_app
from part_app.funcs.nightly import ComputeOldestSampleDateOnProject
from part_app.remote import EcoTaxaInstance
from part_app.tasks.taskmanager import TasksCleanup, AsyncTask
from part_app.views.prj import GlobalTaxoCompute

if __name__ == "__main__":

    part_app.logger.setLevel(logging.DEBUG)
    for h in part_app.logger.handlers:
        h.setLevel(logging.DEBUG)
    part_app.logger.info("Start Daily Task")
    cookie = os.environ.get(AsyncTask.ECOTAXA_COOKIE)
    try:
        ecotaxa_if = EcoTaxaInstance(cookie)
        with part_app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
            g.db = None
            part_app.logger.info("EcoPart...")
            ComputeOldestSampleDateOnProject()
            GlobalTaxoCompute(ecotaxa_if, part_app.logger)
            part_app.logger.info("EcoPart tasks+EcoTaxa one...")
            # Keep EcoPart auto clean
            part_app.logger.info(TasksCleanup())
    except Exception as e:
        s = str(e)
        tb_list = traceback.format_tb(e.__traceback__)
        for i in tb_list[::-1]:
            s += "\n" + i
        part_app.logger.error("Exception in Daily Task : %s" % s)
    part_app.logger.info("End Daily Task")
