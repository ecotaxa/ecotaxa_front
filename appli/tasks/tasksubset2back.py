# -*- coding: utf-8 -*-
import datetime
import time

from flask import render_template, g

from appli import database, PrintInCharte, gvg, db, XSSEscape
from appli.project import sharedfilter
from appli.tasks.importcommon import *
from appli.tasks.taskmanager import AsyncTask
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ImportRealReq, ProjectsApi, CreateProjectReq, SubsetReq, SubsetRsp


class TaskSubsetToBack(AsyncTask):
    """
        Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    class Params(AsyncTask.Params):
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr is None:  # Valeurs par defaut ou vide pour init
                self.ProjectId = None  # Projet de reference
                self.valtype = None  # P,V = Pourcentage ou Valeur Absolue
                self.valeur = None
                self.subsetproject = None  # N° du projet destination
                self.subsetprojecttitle = ""
                self.withimg = "Y"
                self.filtres = {}

    def __init__(self, task=None):
        super().__init__(task)
        if task is None:
            self.param = self.Params()
        else:
            self.param = self.Params(task.inputparam)

    # noinspection PyMethodMayBeStatic
    def SPCommon(self):
        """ Executed before each step, i.e. in subprocess """
        logging.info("Execute SPCommon for Extract Subset")

    def _CreateDialogStep0(self, prj: database.Projects):
        """ In UI/flask, task.taskstep = 0 AKA initial dialog """
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(prj.projid, XSSEscape(prj.title))
        errors = []
        # Extract filter values and store them in session
        self.param.filtres = {}
        for k in sharedfilter.FilterList:
            if gvg(k, "") != "":
                self.param.filtres[k] = gvg(k, "")
        # If subset was required on a filtered view, remind it in the page
        filtertxt = ""
        if len(self.param.filtres) > 0:
            filtertxt += ",".join([k + "=" + v for k, v in self.param.filtres.items() if v != ""])
            g.headcenter = "<h4><a href='/prj/{0}?{2}'>{1}</a></h4>".format(prj.projid, XSSEscape(prj.title),
                                                                            "&".join([k + "=" + v for k, v in
                                                                                      self.param.filtres.items() if
                                                                                      v != ""]))
        prevpost = {}
        if gvp("vvaleur"):
            prevpost["vvaleur"] = gvp("vvaleur")
        if gvp("pvaleur"):
            prevpost["pvaleur"] = gvp("pvaleur")
        # Le projet de base est choisi second écran ou validation du second ecran
        if gvp('starttask') == "Y":
            # validation du second ecran
            self.param.withimg = gvp("withimg")
            self.param.subsetprojecttitle = gvp("subsetprojecttitle")
            self.param.valtype = gvp("valtype")
            if len(self.param.subsetprojecttitle) < 5:
                errors.append("Project name too short")
            if self.param.valtype == 'V':
                try:
                    self.param.valeur = int(gvp("vvaleur"))
                    if self.param.valeur <= 0:
                        errors.append("Absolute value not in range")
                except:  # noqa
                    errors.append("Invalid absolute value")
            elif self.param.valtype == 'P':
                try:
                    self.param.valeur = int(gvp("pvaleur"))
                    if self.param.valeur <= 0 or self.param.valeur > 100:
                        errors.append("% value not in range")
                except:  # noqa
                    errors.append("Invalid % value")

            # Verifier la coherence des données
            # errors.append("TEST ERROR")
            if self.param.valtype == '':
                errors.append("You must select the object selection parameter '% of values' or '# of objects'")
            if len(errors) > 0:
                for e in errors:
                    flash(e, "error")
            else:  # Pas d'erreur, on lance la tache
                return self.StartTask(self.param)
        else:
            # default values
            self.param.subsetprojecttitle = (prj.title + " - Subset created on " + (
                datetime.date.today().strftime('%Y-%m-%d')))[0:255]
            self.param.valtype = 'V'
            prevpost['vvaleur'] = 200

        html = "<h3>Extract subset</h3>"
        return render_template('task/subset_create.html', header=html, data=self.param, prevpost=prevpost,
                               filtertxt=filtertxt)

    def SPStep1(self):
        """ In subprocess, task.taskstep = 1 """
        self.UpdateProgress(0, "Waiting for backend")
        logging.info("Input Param = %s" % (self.param.__dict__,))
        src_prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        # self.param.IntraStep=0
        if getattr(self.param, 'IntraStep', 0) == 0:
            self.param.IntraStep = 1
            # Create destination project on back-end
            dest_title = self.param.subsetprojecttitle
            with ApiClient(ProjectsApi, self.cookie) as api:
                req = CreateProjectReq(clone_of_id=self.param.ProjectId,
                                       title=dest_title,
                                       visible=False)
                # TODO: The new project has status ANNOTATE. Is it important?
                rsp: int = api.create_project_projects_create_post(req)
            self.param.subsetproject = rsp
            self.UpdateProgress(5, "Subset Project %d Created : %s" % (rsp, dest_title))
        if self.param.IntraStep == 1:
            # Do the cloning
            with ApiClient(ProjectsApi, self.cookie) as api:
                req = SubsetReq(task_id=self.task.id,
                                filters=self.param.filtres,
                                dest_prj_id=self.param.subsetproject,
                                limit_type=self.param.valtype,
                                limit_value=self.param.valeur,
                                do_images=(self.param.withimg == 'Y'))
                rsp: SubsetRsp = api.project_subset_projects_project_id_subset_post(project_id=self.param.ProjectId,
                                                                                    subset_req=req)
            if len(rsp.errors) == 0:
                self.task.taskstate = "Done"
                self.UpdateProgress(100, "Subset created successfully")
            else:
                self.task.taskstate = "Error"
                self.UpdateProgress(100, "Errors, see logs")

    def QuestionProcess(self):
        """ Called from tasking framework """
        self.param.ProjectId = gvg("p")
        prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        if not prj.CheckRight(1):
            return PrintInCharte("ACCESS DENIED for this project<br>" + prj.title)
        if self.task.taskstep == 0:
            return self._CreateDialogStep0(prj)
        return ""

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId = self.param.ProjectId
        time.sleep(1)
        # DoTaskClean(self.task.id)
        return ("""<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Original project</a>
        <a href='/prj/{1}' class='btn btn-primary btn-sm'  role=button>Go to Subset Project</a> """
                .format(PrjId, self.param.subsetproject))
