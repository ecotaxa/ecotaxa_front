# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList,ntcv,GetAppManagerMailto,ErrorFormat
from PIL import Image
from flask import render_template,  flash,request,g
import logging,os,csv,sys,time,re
import datetime,shutil,random,zipfile
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask,LoadTask,DoTaskClean
from appli.database import GetAll
import appli.project.main
import appli.uvp.database as uvpdatabase
import appli.uvp.sample_import


class TaskUVPZooscanImport(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr==None: # Valeurs par defaut ou vide pour init
                self.uprojid=None
                self.profilelistinheader=[]
                self.profiletoprocess={}



    def __init__(self,task=None):
        super().__init__(task)
        if task==None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon")
        self.pgcur=db.engine.raw_connection().cursor()


    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__))
        logging.info("Start Step 1")
        Prj=uvpdatabase.uvp_projects.query.filter_by(uprojid=self.param.uprojid).first()
        for sample in self.param.profilelistinheader:
            ProcessType=self.param.profiletoprocess.get(sample['profileid'])
            if ProcessType:
                logging.info("Process profile %s : %s"%(sample['profileid'],ProcessType))
                appli.uvp.sample_import.CreateOrUpdateSample(self.param.uprojid, sample)

        # self.task.taskstate="Done"
        # self.UpdateProgress(100,"Processing done")

    def QuestionProcess(self):
        ServerRoot=Path(app.config['SERVERLOADAREA'])
        txt="<h1>UVP ZooScan folder Importation Task</h1>"
        errors=[]
        txt+="<h3>Task Creation</h3>"
        Prj=uvpdatabase.uvp_projects.query.filter_by(uprojid=gvg("p")).first()
        if Prj is None:
            return PrintInCharte(ErrorFormat("This project doesn't exists"));
        g.prjtitle=Prj.utitle
        g.prjprojid=Prj.uprojid
        # g.prjowner=Prj.owneridrel.name
        DossierUVPPath = ServerRoot / Prj.rawfolder
        self.param.DossierUVP = DossierUVPPath.as_posix()

        txt=""
        # TODO gestion sécurité
        # if Prj.CheckRight(2)==False:
        #     return PrintInCharte("ACCESS DENIED for this project");

        self.param.uprojid = gvg("p")
        DirName = DossierUVPPath.name
        m = re.search(R"([^_]+)_(.*)", DirName)
        if m.lastindex != 2:
            return PrintInCharte(ErrorFormat("Le repertoire projet n'as pas un nom standard"))
        else:
            FichierHeader = DossierUVPPath / "meta" / (m.group(1) + "_header_" + m.group(2) + ".txt")

            if not FichierHeader.exists():
                return PrintInCharte(ErrorFormat("Le fichier header n'existe pas :" + FichierHeader.as_posix()))
            else:
                # print("ouverture de " + FichierHeader)
                with open(FichierHeader.as_posix()) as FichierHeaderHandler:
                    F = csv.DictReader(FichierHeaderHandler, delimiter=';')
                    for r in F:
                        self.param.profilelistinheader.append(r)
                        # self.param.profilelistinheader[r['profileid']]=r
                    # Tri par 4eme colonne, profileid
                    self.param.profilelistinheader = sorted(self.param.profilelistinheader,
                                                            key=lambda r: r['profileid'])

        if gvp('starttask')=="Y":
            for f in request.form:
                if f[0:3] == "new":
                    self.param.profiletoprocess[request.form.get(f)]="new"

            if len(self.param.profiletoprocess)==0:
                errors.append("No sample to process selected")
            if len(errors)>0:
                for e in errors:
                    flash(e,"error")
            else:
                return self.StartTask(self.param)
        else: # valeurs par default


            if len(self.param.profilelistinheader) == 0:
                return PrintInCharte(ErrorFormat("No sample available in file %s"%(FichierHeader.as_posix())))
            print("%s"%(self.param.profilelistinheader))
        return render_template('task/uvpzooscanimport_create.html',header=txt,data=self.param,ServerPath=gvp("ServerPath"),TxtTaxoMap=gvp("TxtTaxoMap"))


    def ShowCustomDetails(self):
        txt="<h3>Import Task details view</h3>"
        txt="<p><u>Used mapping, usable for next import</u></p>"
        taxo=database.GetAssoc2Col("select id,name from taxonomy where id = any(%s)",(list(set(self.param.TaxoFound.values())),))
        for k,v in self.param.TaxoFound.items():
            if v in taxo:
                txt+="{0}={1}<br>".format(k,taxo[v])
        return PrintInCharte(txt)

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId=self.param.ProjectId
        time.sleep(1)
        DoTaskClean(self.task.id)
        return """<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>
        <a href='/Task/Create/TaskClassifAuto?p={0}' class='btn btn-primary btn-sm'  role=button>Go to Automatic Classification Screen</a> """.format(PrjId)
