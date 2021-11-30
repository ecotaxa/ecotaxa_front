# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import logging
import os
import sys
import traceback

from flask import g

# Pas d'import relatif ici car c'est un autre process
from part_app.app import db, part_app
from part_app.tasks.taskmanager import LoadTask


def _tweak_stacks():
    """
        Stack traces an very unreadable, especially with all the API overhead.
        So cut uninteresting parts.
    """
    tpe, val, tbk = sys.exc_info()
    tb = traceback.format_exception(tpe, val, tbk)
    rpc_start = 0
    remote_stack = []
    for ndx, a_line in enumerate(tb):
        if a_line.find("ecotaxa_cli_py") != -1 and rpc_start == 0:
            # Entering Api library
            rpc_start = ndx
        if a_line.startswith("ecotaxa_cli_py.exceptions.ApiException"):
            # A single text block with remote trace
            remote_stack = a_line.split("\n")
            for ndx2, a_remote_line in enumerate(remote_stack):
                if a_remote_line.find(" BACK-END ") != -1:
                    remote_stack = remote_stack[ndx2:]
                    break
    if rpc_start and remote_stack:
        return "".join(tb[:rpc_start]) + "\n".join(remote_stack)
    else:
        return "".join(tb)


def main():
    taskid = -9999
    try:
        # print("%s %s"%(sys.argv,len(sys.argv)))
        # print(os.getcwd())
        # On verifie qu'il y a au moins un parametre, c'est le taskid
        if len(sys.argv) == 1:
            raise Exception("Parameter Missing, Task ID required :")
        taskid = int(sys.argv[1])
        # taskid=1
        # On se place dans le repertoire de travail
        tempdir = "../../temptask/task%06d" % int(taskid)
        workingdir = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), tempdir))
        os.chdir(workingdir)
        # On active le logger
        LoggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename='TaskLog.txt', level=logging.INFO, format=LoggingFormat)
        logging_console = logging.StreamHandler()
        logging_console.setLevel(logging.INFO)
        logging_console.setFormatter(logging.Formatter(LoggingFormat))
        logging.getLogger('').addHandler(logging_console)
        with part_app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
            g.db = None
            # logging.warning("Test Warning")
            # raise Exception("TEST")
            # On crée la tache à partir de la base
            task = LoadTask(taskid, cookie_from_env=True)
            task.task.taskstate = "Running"
            # on execute SPCommon s'il existe
            fct = getattr(task, "SPCommon", None)
            if fct is not None:
                fct()
            # on execute le code du step associé
            fctname = "SPStep" + str(task.task.taskstep)
            fct = getattr(task, fctname, None)
            if fct is None:
                raise Exception("Procedure Missing :" + fctname)
            fct()
    except Exception:
        db.session.rollback()  # On essaye d'annuler un max.
        task = LoadTask(taskid, cookie_from_env=True)
        orm_task = task.task
        logging.error("Task :\n%s", task)
        orm_task.taskstate = "Error"
        orm_task.progresspct = -1
        orm_task.progressmsg = "Unhandled SubProcess Exception : " + str(sys.exc_info())
        db.session.commit()
        logging.error("Unhandled SubProcess Exception \n%s", _tweak_stacks())


if __name__ == '__main__':
    main()
