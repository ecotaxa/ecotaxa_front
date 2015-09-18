# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList
from flask import Blueprint, render_template, g, flash,request
import logging,os,csv,re
import zipfile,psycopg2.extras
from time import time
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask,DoTaskClean
from appli.database import GetAll

class TaskExportTxt(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.ProjectId=None
                self.what=None  # TSV, XML, IMG , Summary
                self.Details=None
                self.OutFile=None


    def __init__(self,task=None):
        super().__init__(task)
        if task==None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon for Txt Export")
        self.pgcur=db.engine.raw_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)

    def CreateTSV(self):
        self.UpdateProgress(1,"Start export")
        TInit = time()
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        sql1="""SELECT o.objid ,o.orig_id as object_id,o.latitude as object_lat,o.longitude as object_lon
                ,to_char(objdate,'YYYYMMDD') as object_date
                ,to_char(objtime,'HH24MISS') as object_time
                ,object_link,depth_min as object_depth_min,depth_max as object_depth_max
                ,o.classif_id,to1.name as object_annotation_category
                ,case o.classif_qual when 'V' then 'validated' when 'P' then 'predicted' when 'D' then 'dubios' ELSE o.classif_qual end object_annotation_status
                ,o.classif_who,uo1.name object_annotation_person_name,uo1.email object_annotation_person_email
                ,to_char(o.classif_when,'YYYYMMDD') object_annotation_date
                ,to_char(o.classif_when,'HH24MISS') object_annotation_time
                ,o.classif_auto_id,to2.name classif_auto_name,classif_auto_score,classif_auto_when
                ,random_value,sunpos     """
        sql2=""" FROM objects o
                LEFT JOIN taxonomy to1 on o.classif_id=to1.id
                LEFT JOIN users uo1 on o.classif_who=uo1.id
                LEFT JOIN taxonomy to2 on o.classif_auto_id=to2.id
                LEFT JOIN samples s on o.sampleid=s.sampleid """
        sql3=" where o.projid=%(projid)s "
        params={'projid':int(self.param.ProjectId)}
        if self.param.samplelist!="":
            sql3+=" and s.orig_id= any(%(samplelist)s) "
            params['samplelist']=self.param.samplelist.split(",")


        if self.param.commentsdata=='1':
            sql1+="\n,complement_info"
        if self.param.objectdata=='1':
            sql1+="\n"
            Mapping=DecodeEqualList(Prj.mappingobj)
            for k,v in Mapping.items() :
                sql1+=",o.%s as object_%s "%(k,re.sub("[^a-zA-Z]","_",v))
        if self.param.sampledata=='1':
            sql1+="\n,s.sampleid as sampleid_internal,s.orig_id sample_id,s.latitude sample_latitude,s.longitude sample_longitude,s.dataportal_descriptor as sample_dataportal_descriptor "
            Mapping=DecodeEqualList(Prj.mappingsample)
            for k,v in Mapping.items() :
                sql1+=",s.%s as sample_%s "%(k,re.sub("[^a-zA-Z]","_",v))
        if self.param.processdata=='1':
            sql1+="\n,p.processid as processid_internal,p.orig_id process_id"
            Mapping=DecodeEqualList(Prj.mappingprocess)
            for k,v in Mapping.items() :
                sql1+=",s.%s as process_%s "%(k,re.sub("[^a-zA-Z]","_",v))
            sql2+=" left join process p on o.processid=p.processid "
        if self.param.acqdata=='1':
            sql1+="\n,o.acquisid as acquisid_internal,a.orig_id acquis_id"
            Mapping=DecodeEqualList(Prj.mappingprocess)
            for k,v in Mapping.items() :
                sql1+=",s.%s as acquis_%s "%(k,re.sub("[^a-zA-Z]","_",v))
            sql2+=" left join acquisitions a on o.acquisid=a.acquisid "

        if self.param.histodata=='1':
            if self.param.samplelist!="":
                samplefilter=" join samples s on o.sampleid=s.sampleid and s.orig_id= any(%(samplelist)s) "
            else: samplefilter=""
            sql1+=" ,oh.classif_date histoclassif_date,classif_type histoclassif_type,to3.name histoclassif_name,oh.classif_qual histoclassif_qual,uo3.name histoclassif_who,classif_score histoclassif_score"
            sql2+=""" left join (SELECT o.objid,classif_date,classif_type,och.classif_id,och.classif_qual,och.classif_who,classif_score
                    from objectsclassifhisto och
                    join objects o on o.objid=och.objid and o.projid=1 {0}
                    union all
                    SELECT o.objid,o.classif_when classif_date,'C' classif_type,classif_id,classif_qual,classif_who,NULL
                    from objects o {0} where o.projid=1
                    )oh on o.objid=oh.objid
                    LEFT JOIN taxonomy to3 on oh.classif_id=to3.id
                    LEFT JOIN users uo3 on oh.classif_who=uo3.id
                    """.format(samplefilter)


        sql=sql1+" "+sql2+" "+sql3
        logging.info("Execute SQL : %s"%(sql))
        logging.info("Params : %s"%(params))
        self.pgcur.execute(sql,params)

        self.param.OutFile="export.tsv"
        fichier=os.path.join(self.GetWorkingDir(),self.param.OutFile)
        logging.info("Creating file %s"%(fichier))
        with open(fichier,'w',encoding='latin_1') as csvfile:
            # lecture en mode dictionnaire basé sur la premiere ligne
            wtr = csv.writer(csvfile, delimiter='\t', quotechar='"',lineterminator='\n' )
            colnames = [desc[0] for desc in self.pgcur.description]
            coltypes=[desc[1] for desc in self.pgcur.description]
            FloatType=coltypes[2] # on lit le type de la colonne 2 alias latitude pour determiner le code du type double
            wtr.writerow(colnames)
            for r in self.pgcur:
                # on supprime les CR des commentaires.
                if self.param.commentsdata=='1' and r['complement_info']:
                    r['complement_info']=' '.join(r['complement_info'].splitlines())
                if self.param.usecomasepa=='1': # sur les decimaux on remplace . par ,
                    for i,t in zip(range(1000),coltypes):
                        if t==FloatType and r[i] is not None:
                            r[i]=str(r[i]).replace('.',',')
                wtr.writerow(r)
        logging.info("Extracted %d rows",self.pgcur.rowcount)


    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__))
        if self.param.what=="TSV":
            self.CreateTSV()
        else:
            raise Exception("Unsupported exportation type : %s"%(self.param.what,))

        self.task.taskstate="Done"
        self.UpdateProgress(100,"Export successfull")

        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")


    def QuestionProcess(self):
        Prj=database.Projects.query.filter_by(projid=gvg("p")).first()
        txt="<a href='/prj/%d'>Back to project</a>"%Prj.projid
        if not Prj.CheckRight(1):
            return PrintInCharte("ACCESS DENIED for this project<br>"+txt)
        txt+="<h3>Text export Task creation</h3>"
        txt+="<h5>Exported Project : #%d - %s</h5>"%(Prj.projid,Prj.title)
        errors=[]
        if self.task.taskstep==0:
            # Le projet de base est choisi second écran ou validation du second ecran
            if gvp('starttask')=="Y":
                # validation du second ecran
                self.param.ProjectId=gvg("p")
                self.param.what=gvp("what")
                self.param.samplelist=gvp("samplelist")
                self.param.objectdata=gvp("objectdata")
                self.param.processdata=gvp("processdata")
                self.param.acqdata=gvp("acqdata")
                self.param.sampledata=gvp("sampledata")
                self.param.histodata=gvp("histodata")
                self.param.commentsdata=gvp("commentsdata")
                self.param.usecomasepa=gvp("usecomasepa")

                # Verifier la coherence des données
                # errors.append("TEST ERROR")
                if self.param.what=='' : errors.append("You must select What you want to export")
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else: # Pas d'erreur, on lance la tache
                    return self.StartTask(self.param)
            else: # valeurs par default
                pass
            #recupere les samples
            sql="""select sampleid,orig_id
                    from samples where projid =%(projid)s
                    order by orig_id"""
            g.SampleList=GetAll(sql,{"projid":gvg("p")},cursor_factory=None)
            return render_template('task/textexport_create.html',header=txt,data=self.param)



    def GetResultFile(self):
        return self.param.OutFile
