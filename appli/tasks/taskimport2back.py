# -*- coding: utf-8 -*-
import time
from pathlib import Path

from flask import render_template, flash, request, g

from appli import app, database, PrintInCharte, gvp, gvg, GetAppManagerMailto, \
    UtfDiag, db
from appli.tasks.importcommon import *
from appli.tasks.taskmanager import AsyncTask, DoTaskClean
from to_back.ecotaxa_cli_py import DefaultApi, ImportPrepReq, ImportPrepRsp, ApiClient, ImportRealReq


class TaskImportToBack(AsyncTask):
    """
        Import, just GUI here, bulk of job subcontracted to back-end.
    """

    class Params(AsyncTask.Params):
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr is None:  # Valeurs par defaut ou vide pour init
                self.InData = 'My In Data'
                self.ProjectId = None
                self.SkipAlreadyLoadedFile = "N"  # permet de dire si on
                self.SkipObjectDuplicate = "N"
                # mapping, stored at project level
                self.Mapping = {}
                self.TaxoMap = {}
                # Extra params added during steps
                self.TotalRowCount = 0
                self.TaxoFound = {}
                self.UserFound = {}
                # Errors displayed to user
                self.steperrors = []

    def __init__(self, task=None):
        super().__init__(task)
        if task is None:
            self.param = self.Params()
        else:
            self.param = self.Params(task.inputparam)
        # TODO: Can be a singleton/higher in classes
        api_client = ApiClient()
        # No trailing /
        api_client.configuration.host = "http://localhost:8000"
        self.api = DefaultApi(api_client)

    # noinspection PyMethodMayBeStatic
    def SPCommon(self):
        """ Executed before each step, i.e. in subprocess """
        logging.info("Execute SPCommon")

    def _CreateDialogStep0(self):
        """ In UI/flask, task.taskstep = 0 AKA initial dialog """
        ServerRoot = Path(app.config['SERVERLOADAREA'])
        Prj = database.Projects.query.filter_by(projid=gvg("p")).first()
        g.prjtitle = Prj.title
        g.prjprojid = Prj.projid
        g.prjmanagermailto = Prj.GetFirstManagerMailto()
        txt = ""
        if not Prj.CheckRight(1):
            return PrintInCharte("ACCESS DENIED for this project")
        g.appmanagermailto = GetAppManagerMailto()

        if gvp('starttask') == "Y":
            # Form Submit -> check and store values to use
            errors = []
            FileToSave = None
            FileToSaveFileName = None
            self.param.ProjectId = gvg("p")
            self.param.SkipAlreadyLoadedFile = gvp("skiploaded")
            self.param.SkipObjectDuplicate = gvp("skipobjectduplicate")
            TaxoMap = {}
            for lig in gvp('TxtTaxoMap').splitlines():
                ls = lig.split('=', 1)
                if len(ls) != 2:
                    errors.append("Taxonomy Mapping : Invalid format for line %s" % lig)
                else:
                    TaxoMap[ls[0].strip().lower()] = ls[1].strip().lower()
            # Verifier la coherence des données
            uploadfile = request.files.get("uploadfile")
            if uploadfile is not None and uploadfile.filename != '':  # import d'un fichier par HTTP
                FileToSave = uploadfile  # La copie est faite plus tard, car à ce moment là, le repertoire
                # de la tache n'est pas encore créé
                FileToSaveFileName = "uploaded.zip"
                self.param.InData = "uploaded.zip"
            elif len(gvp("ServerPath")) < 2:
                errors.append("Input Folder/File Too Short")
            else:
                sp = ServerRoot.joinpath(Path(gvp("ServerPath")))
                if not sp.exists():  # verifie que le repertoire existe
                    errors.append("Input Folder/File Invalid")
                    UtfDiag(errors, str(sp))
                else:
                    self.param.InData = sp.as_posix()
            if len(errors) > 0:
                for e in errors:
                    flash(e, "error")
            else:
                self.param.TaxoMap = TaxoMap  # on stocke le dictionnaire et pas la chaine
                # start Step1, in a subprocess as we're in UI process, reusing log files
                return self.StartTask(self.param, step=1, FileToSave=FileToSave, FileToSaveFileName=FileToSaveFileName)
        else:  # valeurs par default
            self.param.ProjectId = gvg("p")
        return render_template('task/import_create.html', header=txt, data=self.param, ServerPath=gvp("ServerPath"),
                               TxtTaxoMap=gvp("TxtTaxoMap"))

    def SPStep1(self):
        """ In subprocess, task.taskstep = 1 """
        self.UpdateProgress(0, "Waiting for backend")
        logging.info("Input Param = %s" % self.param.__dict__)
        logging.info("Start Step 1 : Data validation and preparation")
        req = ImportPrepReq(task_id=self.task.id,
                            source_path=self.param.InData,
                            taxo_mappings=self.param.TaxoMap,
                            skip_loaded_files=(self.param.SkipAlreadyLoadedFile == "Y"),
                            skip_existing_objects=(self.param.SkipObjectDuplicate == "Y"))
        rsp: ImportPrepRsp = self.api.api_import_import_prep_project_id_post(self.param.ProjectId, req)
        # Copy back into params the eventually amended fields in response
        self.param.InData = rsp.source_path
        self.param.TaxoFound = rsp.found_taxa
        self.param.UserFound = rsp.found_users
        self.param.Mapping = rsp.mappings
        self.param.TotalRowCount = rsp.rowcount
        self.UpdateParam()
        if len(rsp.errors) != 0:
            msg = "Some errors were found during file parsing"
            logging.error(msg + ":")
            for an_err in rsp.errors:
                logging.error(an_err)
            self.task.taskstate = "Error"
            self.task.progressmsg = msg
            self.param.steperrors = rsp.errors[:1000]
            self.UpdateParam()
        elif len(self._notFoundTaxoInParam()) > 0 or len(self._notFoundUsersInParam()) > 0:
            self.task.taskstate = "Question"
            db.session.commit()
        else:
            # We're still in spawned subprocess so we can import right away
            self.SPStep2()

    def _MappingDialogStep1(self):
        """ In UI/flask, task.taskstep = 1 AKA mapping of not found entities """
        txt = "<h1>Text File Importation Task</h1>"
        errors = []
        PrjId = self.param.ProjectId
        Prj = database.Projects.query.filter_by(projid=PrjId).first()
        g.prjtitle = Prj.title
        g.prjprojid = Prj.projid
        g.appmanagermailto = GetAppManagerMailto()
        NotFoundTaxo = self._notFoundTaxoInParam()
        NotFoundUsers = self._notFoundUsersInParam()
        app.logger.info("Pending Taxo Not Found = %s", NotFoundTaxo)
        app.logger.info("Pending Users Not Found = %s", NotFoundUsers)
        if gvp('starttask') == "Y":
            # Submit -> check and store values to use
            app.logger.info("Form Data = %s", request.form)
            for i in range(1, 1 + len(NotFoundTaxo)):
                orig = gvp("orig%d" % i)  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
                newvalue = gvp("taxolb%d" % i)
                if orig in NotFoundTaxo and newvalue != "":
                    t = database.Taxonomy.query.filter(database.Taxonomy.id == int(newvalue)).first()
                    app.logger.info(orig + " associated to " + t.name)
                    self.param.TaxoFound[orig] = t.id
                else:
                    errors.append("Taxonomy Manual Mapping : Invalid value '%s' for '%s'" % (newvalue, orig))
            for i in range(1, 1 + len(NotFoundUsers)):
                orig = gvp("origuser%d" % i)  # Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
                newvalue = gvp("userlb%d" % i)
                if orig in NotFoundUsers and newvalue != "":
                    t = database.users.query.filter(database.users.id == int(newvalue)).first()
                    app.logger.info("User " + orig + " associated to " + t.name)
                    self.param.UserFound[orig]['id'] = t.id
                else:
                    errors.append("User Manual Mapping : Invalid value '%s' for '%s'" % (newvalue, orig))
            app.logger.info("Final Taxofound = %s", self.param.TaxoFound)
            self.UpdateParam()  # On met à jour ce qui à été accepté
            # Verifier la coherence des données
            if len(errors) == 0:
                # start Step2, subprocess as we're in UI process
                return self.StartTask(self.param, step=2)
            for e in errors:
                flash(e, "error")
            NotFoundTaxo = [k for k, v in self.param.TaxoFound.items() if v is None]
            NotFoundUsers = [k for k, v in self.param.UserFound.items() if v.get('id') is None]
        return render_template('task/import_question1.html', header=txt, taxo=NotFoundTaxo, users=NotFoundUsers,
                               task=self.task)

    def SPStep2(self):
        """ In subprocess, task.taskstep = 2 """
        self.UpdateProgress(0, "Waiting for backend")
        logging.info("Input Param = %s" % self.param.__dict__)
        logging.info("Start Step 2 : Effective data import")
        req = ImportRealReq(task_id=self.task.id,
                            taxo_mappings=self.param.TaxoMap,
                            skip_loaded_files=(self.param.SkipAlreadyLoadedFile == "Y"),
                            skip_existing_objects=(self.param.SkipObjectDuplicate == "Y"),
                            source_path=self.param.InData,  # from prep
                            mappings=self.param.Mapping,  # from prep
                            rowcount=self.param.TotalRowCount,  # from prep
                            found_users=self.param.UserFound,  # from prep & UI
                            found_taxa=self.param.TaxoFound  # from prep & UI
                            )
        self.api.api_import_import_real_project_id_post(self.param.ProjectId, req)
        self.task.taskstate = "Done"
        self.UpdateProgress(100, "Processing done")

    def QuestionProcess(self):
        """ Called from tasking framework """
        txt = "<h1>Text File Importation Task</h1>"
        if self.task.taskstep == 0:
            return self._CreateDialogStep0()
        if self.task.taskstep == 1:
            return self._MappingDialogStep1()
        return PrintInCharte(txt)

    def ShowCustomDetails(self):
        txt = "<p><u>Used mapping, usable for next import</u></p>"
        taxo = database.GetAssoc2Col("select id,name from taxonomy where id = any(%s)",
                                     (list(set(self.param.TaxoFound.values())),))
        for k, v in self.param.TaxoFound.items():
            if v in taxo:
                txt += "{0}={1}<br>".format(k, taxo[v])
        return PrintInCharte(txt)

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle ou auto
        PrjId = self.param.ProjectId
        time.sleep(1)
        DoTaskClean(self.task.id)
        return "<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>" \
               "<a href='/Task/Create/TaskClassifAuto2?projid={0}' class='btn btn-primary btn-sm'" \
               "role=button>Go to Automatic Classification Screen</a> ".format(PrjId)

    def _notFoundTaxoInParam(self):
        return [k for k, v in self.param.TaxoFound.items() if v is None]

    def _notFoundUsersInParam(self):
        return [k for k, v in self.param.UserFound.items() if v.get('id') is None]
