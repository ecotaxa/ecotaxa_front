# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import appli.part.views.prj
from appli.part.ecopart_blueprint import ECOTAXA_URL
from appli.part.funcs.nightly import ComputeOldestSampleDateOnProject
from appli.part.remote import EcoTaxaInstance

if __name__ == "__main__":
    # RefreshTaxoStat()
    from appli import app
    from flask import g
    import logging
    import traceback
    from appli.part.tasks.taskmanager import AutoClean

    app.logger.setLevel(logging.DEBUG)
    for h in app.logger.handlers:
        h.setLevel(logging.DEBUG)
    app.logger.info("Start Daily Task")
    # TODO: Temporary, my admin cookie on my dev PC
    cookie = ".eJxVkMtuAzEIRf_F6yzAL0x-ZoRtUKdN02rsWUX99zrKpr3LczkS8HCbHTre3HUep17ctnd3dVjBk3SBKlZqYFJsQrX0jK00tUgVWMFDodAogpfGSbD1ykQSwUTKc1g8JDJqCkZAPiTCxN2AcrWEuRfOrDEQAXjTIAYNV2vu4to4bJtfH3pf-wQM1DFl0WfIExfvmQvWmiNy4Kw9-KjL-z7ebb_Nbb-PddHnkv_Acdah8z-b-7zpC51Dj9cDKIP7-QXMy1Om.YZO5pQ.8BtwVVxs_A-bWSg17Wx9HSrDf0k"
    try:
        ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, cookie)
        with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
            g.db = None
            app.logger.info("EcoPart...")
            ComputeOldestSampleDateOnProject()
            appli.part.views.prj.GlobalTaxoCompute(ecotaxa_if, app.logger)
            app.logger.info("EcoPart tasks+EcoTaxa one...")
            # Keep EcoPart auto clean
            app.logger.info(AutoClean())
    except Exception as e:
        s = str(e)
        tb_list = traceback.format_tb(e.__traceback__)
        for i in tb_list[::-1]:
            s += "\n" + i
        app.logger.error("Exception in Daily Task : %s" % s)
    app.logger.info("End Daily Task")
