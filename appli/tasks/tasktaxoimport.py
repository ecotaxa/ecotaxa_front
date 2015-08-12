# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList
from flask.ext.login import current_user
from PIL import Image
from flask import Blueprint, render_template, g, flash,request
from io import StringIO
import html,functools,logging,json,time,os,csv
import datetime,shutil,random,zipfile
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask,LoadTask
from appli.database import GetAll,ExecSQL
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class TaskTaxoImport(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr==None: # Valeurs par defaut ou vide pour init
                self.InData='My In Data'


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

        # self.param.IntraStep=0
        if getattr(self.param,'IntraStep',0)==0:
            fichier=os.path.join(self.GetWorkingDir(),"uploaded.txt")
            logging.info("Analyzing file %s"%(fichier))
            with open(fichier,encoding='latin_1') as csvfile:
                # lecture en mode dictionnaire basé sur la premiere ligne
                rdr = csv.reader(csvfile, delimiter='\t', quotechar='"',)
                #lecture la la ligne des titre
                LType=rdr.__next__()
                # Lecture du contenu du fichier
                RowCount=0
                ExecSQL("truncate table temp_taxo")
                sqlinsert="INSERT INTO temp_taxo(idparent,idtaxo,name,status,typetaxo) values(%s,%s,%s,%s,%s)"
                for lig in rdr:
                    database.ExecSQL(sqlinsert,(lig[0].strip(),lig[1].strip(),lig[2].strip(),lig[3].strip(),lig[4].strip()) )
                    if RowCount%1000==0:
                        logging.info("Inserted %s lines"% RowCount)

                    RowCount+=1
                logging.info("count=%d"%RowCount)
            self.param.IntraStep=1
        if self.param.IntraStep==1:


            # MAJ des IDFinal dans la table temp pour tout ce qui existe.
            n=ExecSQL("""UPDATE temp_taxo tt set idfinal=tf.id
                        from taxonomy tf where tf.id_source=tt.idtaxo or lower(tf.name)=lower(tt.name)""")
            logging.info("%d Nodes already exists "%n)

            # insertion des nouveaux noeud racines
            n=ExecSQL("""INSERT INTO taxonomy (id, parent_id, name, id_source)
            select nextval('seq_taxonomy'),NULL,t.name,t.idtaxo from temp_taxo t where idparent='-1' and idfinal is null""")
            logging.info("Inserted %d Root Nodes"%n)

            # MAJ de la table import existante
            n=ExecSQL("""UPDATE temp_taxo tt set idfinal=tf.id
                        from taxonomy tf where tf.id_source=tt.idtaxo
                        and tt.idfinal is null and idparent='-1'""")
            logging.info("Updated %d inserted Root Nodes"%n)

            while True:
                # insertion des nouveaux noeud enfants à partir des parents deja insérés
                n=ExecSQL("""INSERT INTO taxonomy (id, parent_id, name, id_source)
                    select nextval('seq_taxonomy'),ttp.idfinal,tt.name,tt.idtaxo from temp_taxo tt join temp_taxo ttp on tt.idparent=ttp.idtaxo
                    where tt.idfinal is null and ttp.idfinal is not null""")
                logging.info("Inserted %d Root Nodes"%n)

                # MAJ de la table import existante
                n=ExecSQL("""UPDATE temp_taxo tt set idfinal=tf.id
                            from taxonomy tf where tf.id_source=tt.idtaxo
                            and tt.idfinal is null """)
                logging.info("Updated %d inserted Root Nodes"%n)

                if n==0:
                    logging.info("No more data to import")
                    break;

        self.task.taskstate="Error"
        self.UpdateProgress(10,"Test Error")

    def QuestionProcess(self):
        txt="<h1>Taxonomy Text File Importation Task</h1>"
        errors=[]
        if self.task.taskstep==0:
            txt+="<h3>Task Creation</h3>"
            if not current_user.has_role(database.AdministratorLabel):
                return PrintInCharte("ACCESS DENIED reserved to administrators");
            if gvp('starttask')=="Y":
                FileToSave=None
                FileToSaveFileName=None
                # Verifier la coherence des données
                uploadfile=request.files.get("uploadfile")
                if uploadfile is not None and uploadfile.filename!='' : # import d'un fichier par HTTP
                    FileToSave=uploadfile # La copie est faite plus tard, car à ce moment là, le repertoire de la tache n'est pas encore créé
                    FileToSaveFileName="uploaded.txt"
                    self.param.InData="uploaded.txt"
                else:
                    errors.append("txt file is missing")
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else:
                    return self.StartTask(self.param,FileToSave=FileToSave,FileToSaveFileName=FileToSaveFileName)
            else: # valeurs par default
                pass
            return render_template('task/taxoimport_create.html',header=txt,data=self.param,ServerPath=gvp("ServerPath"),TxtTaxoMap=gvp("TxtTaxoMap"))
        return PrintInCharte(txt)


