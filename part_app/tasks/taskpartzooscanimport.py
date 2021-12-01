# -*- coding: utf-8 -*-
import csv
import logging
import re
import time
from pathlib import Path

from flask import render_template, flash, request, g

from .taskmanager import AsyncTask, DoTaskClean
from ..urls import PART_URL, ECOTAXA_URL
from .. import database as partdatabase
from ..app import part_app, db
from ..constants import LstInstrumType
from ..db_utils import GetAssoc
from ..http_utils import gvg, gvp, ErrorFormat
from ..funcs import histograms
from ..funcs import uvp_sample_import, lisst_sample_import, common_sample_import, uvp6remote_sample_import, nightly
from ..remote import EcoTaxaInstance
from ..views import prj, part_PrintInCharte


class TaskPartZooscanImport(AsyncTask):
    class Params(AsyncTask.Params):
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr == None:  # Valeurs par defaut ou vide pour init
                self.pprojid = None
                self.profilelistinheader = []
                self.profiletoprocess = {}
                self.ProcessOnlyMetadata = False
                self.user_name = ""
                self.user_email = ""

    def __init__(self, task=None):
        super().__init__(task)
        if task == None:
            self.param = self.Params()
        else:
            self.param = self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon")
        self.pgcur = db.engine.raw_connection().cursor()

    def SPStep1(self):
        ecotaxa_if = EcoTaxaInstance(self.cookie)
        logging.info("Input Param = %s" % (self.param.__dict__))
        logging.info("Start Step 1")
        Prj = partdatabase.part_projects.query.filter_by(pprojid=self.param.pprojid).first()
        if Prj.instrumtype == 'uvp6remote':
            RSF = uvp6remote_sample_import.RemoteServerFetcher(int(self.param.pprojid))
            LstSample = []
            for sample in self.param.profilelistinheader:
                if self.param.profiletoprocess.get(sample['profileid']):
                    LstSample.append(sample['profileid'])
            print(LstSample)
            LstSampleID = RSF.FetchServerDataForProject(LstSample)
            print(LstSampleID)
            if not self.param.ProcessOnlyMetadata:
                for psampleid in LstSampleID:
                    logging.info(
                        "uvp6remote Sample %d Metadata processed, Détailled histogram in progress" % (psampleid,))
                    uvp6remote_sample_import.GenerateParticleHistogram(psampleid)

        else:  # process normal par traitement du repertoire des données
            Nbr = 0
            for sample in self.param.profilelistinheader:
                if self.param.profiletoprocess.get(sample['profileid']):
                    Nbr += 1
            if Nbr == 0: Nbr = 1  # pour éviter les div / 0
            NbrDone = 0
            for sample in self.param.profilelistinheader:
                if self.param.profiletoprocess.get(sample['profileid']):
                    logging.info("Process profile %s " % (sample['profileid']))
                    if Prj.instrumtype in ('uvp5', 'uvp6'):
                        psampleid = uvp_sample_import.CreateOrUpdateSample(self.param.pprojid, sample)
                    if Prj.instrumtype == 'lisst':
                        psampleid = lisst_sample_import.CreateOrUpdateSample(self.param.pprojid,
                                                                             sample)
                    self.UpdateProgress(100 * (NbrDone + 0.1) / Nbr,
                                        "Metadata of profile %s  processed" % (sample['profileid']))

                    if not self.param.ProcessOnlyMetadata:
                        if Prj.instrumtype in ('uvp5', 'uvp6'):
                            logging.info("UVP Sample %d Metadata processed, Raw histogram in progress" % (psampleid,))
                            uvp_sample_import.GenerateRawHistogram(psampleid)
                            self.UpdateProgress(100 * (NbrDone + 0.6) / Nbr,
                                                "Raw histogram of profile %s  processed, Particle histogram in progress" % (
                                                    sample['profileid']))
                            uvp_sample_import.GenerateParticleHistogram(psampleid)
                            self.UpdateProgress(100 * (NbrDone + 0.7) / Nbr,
                                                "Particle histogram of profile %s  processed, CTD in progress" % (
                                                    sample['profileid']))
                        if Prj.instrumtype == 'lisst':
                            logging.info(
                                "LISST Sample %d Metadata processed, Particle histogram in progress" % (psampleid,))
                            lisst_sample_import.GenerateParticleHistogram(psampleid)
                            self.UpdateProgress(100 * (NbrDone + 0.7) / Nbr,
                                                "Detailed histogram of profile %s  processed, CTD histogram in progress" % (
                                                    sample['profileid']))

                        if Prj.instrumtype in ('uvp5', 'uvp6', 'lisst'):
                            common_sample_import.ImportCTD(psampleid, self.param.user_name,
                                                           self.param.user_email)
                            self.UpdateProgress(100 * (NbrDone + 0.95) / Nbr,
                                                "CTD of profile %s  processed" % (sample['profileid']))

                    histograms.ComputeHistoDet(psampleid, Prj.instrumtype)
                    histograms.ComputeHistoRed(psampleid, Prj.instrumtype)
                    if Prj.projid is not None:  # on essaye de matcher que si on a un projet Ecotaxa
                        prj.ComputeZooMatch(ecotaxa_if, psampleid, Prj.projid)
                        histograms.ComputeZooHisto(ecotaxa_if, psampleid, Prj.instrumtype)

                    NbrDone += 1

        nightly.ComputeOldestSampleDateOnProject()
        self.task.taskstate = "Done"
        self.UpdateProgress(100, "Processing done")
        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")

    def QuestionProcess(self):
        ecotaxa_if = EcoTaxaInstance(request)
        ecotaxa_user = ecotaxa_if.get_current_user()
        ServerRoot = Path(part_app.config['SERVERLOADAREA'])
        txt = "<h1>Particle ZooScan folder Importation Task</h1>"
        errors = []
        txt += "<h3>Task Creation</h3>"
        Prj = partdatabase.part_projects.query.filter_by(pprojid=gvg("p")).first()
        if Prj is None:
            return part_PrintInCharte(ecotaxa_if, ErrorFormat("This project doesn't exist"));
        if Prj.instrumtype not in LstInstrumType:
            return part_PrintInCharte(ecotaxa_if, ErrorFormat(
                "Instrument type '%s' not in list : %s" % (Prj.instrumtype, ','.join(LstInstrumType))));
        g.prjtitle = Prj.ptitle
        g.prjprojid = Prj.pprojid
        # g.prjowner=Prj.owneridrel.name
        DossierUVPPath = ServerRoot / Prj.rawfolder
        self.param.DossierUVP = DossierUVPPath.as_posix()

        txt = ""
        # TODO gestion sécurité
        # if Prj.CheckRight(2)==False:
        #     return PrintInCharte("ACCESS DENIED for this project");
        self.param.pprojid = gvg("p")
        dbsample = GetAssoc("""select profileid,psampleid,filename,stationid,firstimage,lastimg,lastimgused,comment,histobrutavailable
              ,(select count(*) from part_histopart_det where psampleid=s.psampleid) nbrlinedet
              ,(select count(*) from part_histopart_reduit where psampleid=s.psampleid) nbrlinereduit
              ,(select count(*) from part_histocat where psampleid=s.psampleid) nbrlinetaxo
              from part_samples s
              where pprojid=%s""" % (self.param.pprojid))

        if Prj.instrumtype == 'uvp6remote':
            RSF = uvp6remote_sample_import.RemoteServerFetcher(int(self.param.pprojid))
            Samples = RSF.GetServerFiles()
            # print(Samples)
            for SampleName, Sample in Samples.items():
                r = {'profileid': SampleName, 'filename': Sample['files']['LPM'], 'psampleid': None}
                if r['profileid'] in dbsample:
                    r['psampleid'] = dbsample[r['profileid']]['psampleid']
                    r['histobrutavailable'] = dbsample[r['profileid']]['histobrutavailable']
                    r['nbrlinedet'] = dbsample[r['profileid']]['nbrlinedet']
                    r['nbrlinereduit'] = dbsample[r['profileid']]['nbrlinereduit']
                    r['nbrlinetaxo'] = dbsample[r['profileid']]['nbrlinetaxo']
                self.param.profilelistinheader.append(r)
                self.param.profilelistinheader = sorted(self.param.profilelistinheader, key=lambda r: r['profileid'])

        else:
            DirName = DossierUVPPath.name
            m = re.search(R"([^_]+)_(.*)", DirName)
            if m.lastindex != 2:
                return part_PrintInCharte(ecotaxa_if, ErrorFormat("Le répertoire projet n'a pas un nom standard"))
            else:
                FichierHeader = DossierUVPPath / "meta" / (m.group(1) + "_header_" + m.group(2) + ".txt")

            if not FichierHeader.exists():
                return part_PrintInCharte(ecotaxa_if,
                                          ErrorFormat("Le fichier header n'existe pas :" + FichierHeader.as_posix()))
            else:
                # print("ouverture de " + FichierHeader)
                with open(FichierHeader.as_posix(), encoding="latin_1") as FichierHeaderHandler:
                    F = csv.DictReader(FichierHeaderHandler, delimiter=';')
                    for r in F:
                        r['psampleid'] = None
                        if r['profileid'] in dbsample:
                            r['psampleid'] = dbsample[r['profileid']]['psampleid']
                            r['histobrutavailable'] = dbsample[r['profileid']]['histobrutavailable']
                            r['nbrlinedet'] = dbsample[r['profileid']]['nbrlinedet']
                            r['nbrlinereduit'] = dbsample[r['profileid']]['nbrlinereduit']
                            r['nbrlinetaxo'] = dbsample[r['profileid']]['nbrlinetaxo']
                        self.param.profilelistinheader.append(r)
                        # self.param.profilelistinheader[r['profileid']]=r
                    # Tri par 4eme colonne, profileid
                    self.param.profilelistinheader = sorted(self.param.profilelistinheader,
                                                            key=lambda r: r['profileid'])

        if gvp('starttask') == "Y":
            self.param.ProcessOnlyMetadata = (gvp('onlymeta', 'N') == 'Y')
            self.param.user_name = ecotaxa_user.name
            self.param.user_email = ecotaxa_user.email
            for f in request.form:
                self.param.profiletoprocess[request.form.get(f)] = "Y"

            if len(self.param.profiletoprocess) == 0:
                errors.append("No sample to process selected")
            if len(errors) > 0:
                for e in errors:
                    flash(e, "error")
            else:
                return self.StartTask(self.param)
        else:  # valeurs par default

            if len(self.param.profilelistinheader) == 0:
                return part_PrintInCharte(ecotaxa_if,
                                          ErrorFormat("No sample available in file %s" % (FichierHeader.as_posix())))
            # print("%s"%(self.param.profilelistinheader))
        return render_template('tasks/uvpzooscanimport_create.html', header=txt, data=self.param,
                               ServerPath=gvp("ServerPath"), TxtTaxoMap=gvp("TxtTaxoMap"))

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId = self.param.pprojid
        time.sleep(1)
        DoTaskClean(self.task.id)
        return ("""<a href='%sprj/{0}' class='btn btn-primary btn-sm' role=button>Go to Project page</a> """ % PART_URL) \
            .format(PrjId)
