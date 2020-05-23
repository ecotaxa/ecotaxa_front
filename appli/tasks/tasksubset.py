# -*- coding: utf-8 -*-
import copy
import datetime
import logging
import shutil
import time
from pathlib import Path

import psycopg2.extras
from flask import render_template, g, flash, request
from sqlalchemy import text
from sqlalchemy.orm.session import make_transient

import appli.project.sharedfilter as sharedfilter
from appli import db, database, PrintInCharte, gvp, gvg, XSSEscape, CreateDirConcurrentlyIfNeeded
from appli.database import GetAll
from appli.tasks.taskmanager import AsyncTask, DoTaskClean


class TaskSubset(AsyncTask):
    class Params(AsyncTask.Params):
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr is None:  # Valeurs par defaut ou vide pour init
                self.ProjectId = None  # Projet de reference
                self.what = None  # V,D,P,N (N=No flag)
                self.valtype = None  # P,V = Pourcentage ou Valeur Absolue
                self.valeur = None
                self.extraprojects = None  # projets complementaires
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
        self.samples = {}
        self.processes_by_id = {}
        self.acquisitions_by_id = {}

    def SPCommon(self):
        logging.info("Execute SPCommon for Txt Export")
        self.pgcur = db.engine.raw_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)

    def GetSampleID(self, oldid):
        if oldid is None: return None
        if oldid in self.samples:
            return self.samples[oldid]
        r = database.Samples.query.filter_by(sampleid=oldid).first()
        db.session.expunge(r)
        make_transient(r)
        r.sampleid = None
        r.projid = self.param.subsetproject
        db.session.add(r)
        db.session.commit()
        self.samples[oldid] = r.sampleid
        # noinspection PyStringFormat
        logging.info("Created Sample %d as duplicate of %d" % (r.sampleid, oldid))
        return r.sampleid

    def GetProcessID(self, oldid):
        if oldid is None: return None
        if oldid in self.processes_by_id:
            return self.processes_by_id[oldid]
        r = database.Process.query.filter_by(processid=oldid).first()
        db.session.expunge(r)
        make_transient(r)
        r.processid = None
        r.projid = self.param.subsetproject
        db.session.add(r)
        db.session.commit()
        self.processes_by_id[oldid] = r.processid
        # noinspection PyStringFormat
        logging.info("Created Process %d as duplicate of %d" % (r.processid, oldid))
        return r.processid

    def GetAcquisID(self, oldid):
        if oldid is None: return None
        if oldid in self.acquisitions_by_id:
            return self.acquisitions_by_id[oldid]
        r = database.Acquisitions.query.filter_by(acquisid=oldid).first()
        db.session.expunge(r)
        make_transient(r)
        r.acquisid = None
        r.projid = self.param.subsetproject
        db.session.add(r)
        db.session.commit()
        self.acquisitions_by_id[oldid] = r.acquisid
        # noinspection PyStringFormat
        logging.info("Created Acquisition %d as duplicate of %d" % (r.acquisid, oldid))
        return r.acquisid

    def SPStep1(self):
        logging.info("Input Param = %s" % (self.param.__dict__,))
        # self.param.ProjectId="2"
        Prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        # self.param.IntraStep=0
        if getattr(self.param, 'IntraStep', 0) == 0:
            self.param.IntraStep = 1
            db.session.expunge(Prj)
            NewPrj = Prj
            Prj = copy.copy(NewPrj)  # Si on fait une copy on arrive plus à insérer.
            make_transient(NewPrj)
            NewPrj.title = self.param.subsetprojecttitle
            NewPrj.projid = None
            NewPrj.visible = False
            db.session.add(NewPrj)
            db.session.commit()
            pp = database.ProjectsPriv()
            pp.member = self.task.owner_id
            pp.privilege = "Manage"
            NewPrj.projmembers.append(pp)
            db.session.commit()
            self.param.subsetproject = NewPrj.projid
            # noinspection PyStringFormat
            self.UpdateProgress(5, "Subset Project %d Created : %s" % (NewPrj.projid, NewPrj.title))

        if self.param.IntraStep == 1:
            vaultroot = Path("../../vault")
            sqlparam = {'projid': self.param.ProjectId}
            sqlwhere = ""
            if self.param.extraprojects:
                sqlparam['projid'] += "," + self.param.extraprojects
            sqlparam['ranklimit'] = self.param.valeur
            if self.param.valtype == 'V':
                rankfunction = 'rank'
            elif self.param.valtype == 'P':
                rankfunction = '100*percent_rank'
            else:
                rankfunction = 'FunctionError'
            # if self.param.samplelist:
            #     sqlwhere+=" and s.orig_id in (%s) "%(",".join(["'%s'"%x for x in self.param.samplelist.split(",")]))
            # sqlwhere+=" and (o.classif_qual in (%s) "%(",".join(["'%s'"%x for x in self.param.what.split(",")]))
            # if self.param.what.find('N')>=0:
            #     sqlwhere+=" or o.classif_qual is null "
            # sqlwhere+=")"
            sqlwhere += sharedfilter.GetSQLFilter(self.param.filtres, sqlparam, str(self.task.owner_id))
            logging.info("SQLParam=%s", sqlparam)
            sql = """select objid from (
                SELECT """ + rankfunction + """() OVER (partition by classif_id order by random() )rang,o.objid
                      from objects o left join samples s on o.sampleid=s.sampleid
                      where o.projid in ( %(projid)s ) """ + sqlwhere + """ ) sr
                where rang<=%(ranklimit)s """
            logging.info("SQL=%s %s", sql, sqlparam)
            # for obj in db.session.query(database.Objects).from_statement( text(sql) ).all():
            LstObjects = GetAll(sql, sqlparam)
            logging.info("matched %s objects", len(LstObjects))
            if len(LstObjects) == 0:
                self.task.taskstate = "Error"
                self.UpdateProgress(10, "No object to include in the subset project")
            NbrObjects = 0
            for objid in LstObjects:
                obj = db.session.query(database.Objects).filter_by(objid=objid[0]).first()
                objf = db.session.query(database.ObjectsFields).filter_by(objfid=objid[0]).first()
                objcnn = db.session.query(database.Objects_cnn_features).filter_by(objcnnid=objid[0]).first()
                NbrObjects += 1
                # noinspection PyUnusedLocal
                oldobjid = obj.objid
                if self.param.withimg == 'Y':
                    for img in obj.images:
                        db.session.expunge(img)
                        make_transient(img)
                        self.pgcur.execute("select nextval('seq_images')")
                        img.imgid = self.pgcur.fetchone()[0]
                        # print("New Image id=",img.imgid)
                        SrcImg = img.file_name
                        SrcImgMini = img.thumb_file_name
                        VaultFolder = "%04d" % (img.imgid // 10000)
                        # creation du repertoire contenant les images si necessaire
                        CreateDirConcurrentlyIfNeeded(vaultroot.joinpath(VaultFolder))
                        img.file_name = "%s/%04d%s" % (VaultFolder, img.imgid % 10000, Path(SrcImg).suffix)
                        shutil.copyfile(vaultroot.joinpath(SrcImg).as_posix(),
                                        vaultroot.joinpath(img.file_name).as_posix())
                        if SrcImgMini is not None:
                            img.thumb_file_name = "%s/%04d_mini%s" % (
                                VaultFolder, img.imgid % 10000, Path(SrcImgMini).suffix)
                            shutil.copyfile(vaultroot.joinpath(SrcImgMini).as_posix(),
                                            vaultroot.joinpath(img.thumb_file_name).as_posix())

                db.session.expunge(obj)
                make_transient(obj)
                obj.objid = None
                obj.img0id = None
                obj.projid = self.param.subsetproject
                obj.sampleid = self.GetSampleID(obj.sampleid)
                obj.processid = self.GetProcessID(obj.processid)
                obj.acquisid = self.GetAcquisID(obj.acquisid)
                db.session.add(obj)
                db.session.commit()
                # noinspection PyUnusedLocal
                dummy = objf.n01  # permet de forcer l'etat de objf sinon perd ses données sur les instruction suivantes.
                db.session.expunge(objf)
                make_transient(objf)
                objf.objfid = obj.objid
                db.session.add(objf)
                if objcnn:
                    # noinspection PyUnusedLocal
                    dummy = objcnn.cnn01  # permet de forcer l'etat de objcnn sinon perd ses données sur les instruction suivantes.
                    db.session.expunge(objcnn)
                    make_transient(objcnn)
                    objcnn.objcnnid = obj.objid
                    db.session.add(objcnn)
                db.session.commit()
                if NbrObjects % 20 == 0:
                    self.UpdateProgress(5 + 95 * NbrObjects / len(LstObjects), "Subset creation in progress")
                # print (oldobjid,obj.objid)
            # Recalcule les valeurs de Img0
            self.pgcur.execute("""update obj_head o
                                set imgcount=(select count(*) from images where objid=o.objid)
                                ,img0id=(select imgid from images where objid=o.objid order by imgrank asc limit 1 )
                                where projid=""" + str(self.param.subsetproject))
            self.pgcur.connection.commit()
        import appli.project.main
        appli.project.main.RecalcProjectTaxoStat(self.param.subsetproject)
        appli.project.main.UpdateProjectStat(self.param.subsetproject)
        self.task.taskstate = "Done"
        self.UpdateProgress(100, "Subset created successfully")

        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")

    def QuestionProcess(self):
        self.param.ProjectId = gvg("p")
        Prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        if not Prj.CheckRight(1):
            return PrintInCharte("ACCESS DENIED for this project<br>" + Prj.title)
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid, XSSEscape(Prj.title))
        errors = []
        if self.task.taskstep == 0:
            if gvg('eps') == "":  # eps = Extra Project selected
                # Premier écran de configuration, choix du projet de base
                html = "<h3>SUBSET PROJECT SELECTION Page (1/2)</h3>"
                html += """<h4>SELECT ADDITIONAL PROJECT TO INCLUDE IN THE SUBSET</h4>
                <form action="?p={0}&eps=y" method=post>
                """.format(Prj.projid)

                from flask_login import current_user
                sql = "select projid,title from projects "
                if not current_user.has_role(database.AdministratorLabel):
                    sql += " where projid in (select projid from projectspriv where member=%d and privilege='Manage')" % current_user.id
                sql += " order by title"
                ProjList = database.GetAll(sql)
                html += """<select name=extraprojects id= extraprojects multiple>"""
                for r in ProjList:
                    html += "<option value='{0}'>{1} ({0})</option>".format(*r)
                html += """</select><br><br>
                <input class="btn btn-primary" type=submit value="Go to the next page">
                <script>
                $(document).ready(function() {
                        $("#extraprojects").select2();
                        });
                </script>
                </form>
                <br><br>
                <div class='panel panel-default' style="width:600px;margin-left:10px;">
A SUBSET is a selection of images (objects) randomly copied from one or more source projects<br>
A SUBSET can have different usages:<br>
<ul>
<li>It can be utilized as a Learning Set for the automatic classification
<li>It can be utilized as a Test Set to evaluate the quality of the prediction or the validation
</ul>
                </div>
                """
                return PrintInCharte(html)

            self.param.filtres = {}
            for k in sharedfilter.FilterList:
                if gvg(k, "") != "":
                    self.param.filtres[k] = gvg(k, "")
            filtertxt = ""
            if len(self.param.filtres) > 0:
                filtertxt += ",".join([k + "=" + v for k, v in self.param.filtres.items() if v != ""])
                g.headcenter = "<h4><a href='/prj/{0}?{2}'>{1}</a></h4>".format(Prj.projid, XSSEscape(Prj.title),
                                                                                "&".join([k + "=" + v for k, v in
                                                                                          self.param.filtres.items() if
                                                                                          v != ""]))

            # Le projet de base est choisi second écran ou validation du second ecran
            if gvp('starttask') == "Y":
                # validation du second ecran
                self.param.extraprojects = gvp("extraprojects")
                self.param.samplelist = gvp("samplelist")
                self.param.withimg = gvp("withimg")
                self.param.subsetprojecttitle = gvp("subsetprojecttitle")
                self.param.valtype = gvp("valtype")
                if self.param.valtype == 'V':
                    try:
                        self.param.valeur = int(gvp("vvaleur"))
                        if self.param.valeur <= 0:
                            errors.append("Absolute value not in range")
                    except: # noqa
                        errors.append("Invalid Absolute value")
                if self.param.valtype == 'P':
                    try:
                        self.param.valeur = int(gvp("pvaleur"))
                        if self.param.valeur <= 0 or self.param.valeur > 100:
                            errors.append("% value not in range")
                    except:
                        errors.append("Invalid % value")

                tmp = []
                if gvp('what_v'):
                    tmp.append('V')
                if gvp('what_d'):
                    tmp.append('D')
                if gvp('what_p'):
                    tmp.append('P')
                if gvp('what_n'):
                    tmp.append('N')
                self.param.what = ",".join(tmp)
                # Verifier la coherence des données
                # errors.append("TEST ERROR")
                # if self.param.what=='' : errors.append("You must select at least one Flag")
                if self.param.valtype == '':
                    errors.append("You must select the object selection parameter '% of values' or '# of objects'")
                if len(errors) > 0:
                    for e in errors:
                        flash(e, "error")
                else:  # Pas d'erreur, on lance la tache
                    return self.StartTask(self.param)
            else:  # valeurs par default
                self.param.what = "V"
                self.param.subsetprojecttitle = (Prj.title + " - Subset created on " + (
                    datetime.date.today().strftime('%Y-%m-%d')))[0:255]
                self.param.extraprojects = ",".join(request.form.getlist('extraprojects'))
                if filtertxt != "":  # s'il y a un filtre on coche toutes les cases et on masque la zone à l'affichage
                    self.param.what = "V,D,P,N"

            html = "<h3>SUBSET SETTINGS Page (2/2)</h3>"
            if self.param.extraprojects:
                ExtraPrj = database.Projects.query.filter(text("projid in (%s)" % self.param.extraprojects)).all()
                g.dispextraprojects = " ".join(["<br>- {1} ({0}) ".format(r.projid, r.title) for r in ExtraPrj])
                for p in ExtraPrj:
                    if p.mappingobj != Prj.mappingobj:
                        flash(
                            "Object variables and metadata differ on project %d (%s). "
                            "The subset should not be utilized as a Learning Set"
                            % (p.projid, p.title), "warning")
                    if p.mappingsample != Prj.mappingsample:
                        flash("Sample variables mapping differ on project %d (%s)."
                        % (p.projid, p.title), "warning")
                    if p.mappingacq != Prj.mappingacq:
                        flash("Acquisition variables mapping differ on project %d (%s)" % (p.projid, p.title),
                              "warning")
                    if p.mappingprocess != Prj.mappingprocess:
                        flash("Process variables mapping differ on project %d (%s)" % (p.projid, p.title), "warning")
            else:
                g.dispextraprojects = "None"
                # recupere les samples
                sql = """select sampleid,orig_id
                        from samples where projid =%(projid)s
                        order by orig_id"""
                g.SampleList = GetAll(sql, {"projid": gvg("p")}, cursor_factory=None)
            return render_template('task/subset_create.html', header=html, data=self.param, prevpost=request.form,
                                   filtertxt=filtertxt)

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId = self.param.ProjectId
        time.sleep(1)
        DoTaskClean(self.task.id)
        return ("""<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Original project</a>
        <a href='/prj/{1}' class='btn btn-primary btn-sm'  role=button>Go to Subset Project</a> """
                .format(PrjId, self.param.subsetproject))
