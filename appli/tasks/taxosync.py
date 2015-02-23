# -*- coding: utf-8 -*-
from appli import db,PrintInCharte,gvp
from flask import render_template, flash
from io import StringIO
import mysql.connector,functools,logging,time
from datetime import datetime
from appli.tasks.taskmanager import AsyncTask

class TaskTaxoSync(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.host='127.0.0.1'
                self.port='7188'
                self.database="col2014ac"
                self.user='root'
                self.password=""

    def __init__(self,task=None):
        super().__init__(task)
        self.dt_debut=datetime.now()
        self.TotalRowCount=0
        self.pgcur=None
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        self.pgcur=db.engine.raw_connection().cursor()


    # Insere un tableau de ligne TSV dans la table via CopyFrom
    def PgImport(self,Data):
        self.pgcur.copy_from(StringIO("\n".join(Data)), 'temp_taxo', columns=('id', 'parent_id', 'nom', 'nodetype'),null="None")
        self.TotalRowCount+=len(Data)
        logging.info("insert temp_taxo %d rows in %s"%(self.TotalRowCount,datetime.now()-self.dt_debut))
        Data.clear()
        self.pgcur.connection.commit()

    def SPStep10(self):
        logging.info("Start Step 1")
        raise Exception("Mon Erreur")
        progress=0
        for i in range(10):
            time.sleep(1)
            progress+=2
            self.UpdateProgress(progress,"My Message %d"%(progress))
        logging.info("End Step 1")

    def SPStep1(self):
        logging.info("Start Step 1")
        # cnx = mysql.connector.connect(user='root', database='col2014ac',host='127.0.0.1',port='7188')
        cnx = mysql.connector.connect(user=self.param.user, database=self.param.database,host=self.param.host, port=self.param.port, password=self.param.password)
        cursor = cnx.cursor()
        logging.info("truncate table temp_taxo")
        self.pgcur.execute("truncate table temp_taxo")
        logging.info("count Records in source DB")
        cursor.execute("select count(*) from taxon_name_element")
        TargetRowCount=cursor.fetchone()[0]
        logging.info("Start query source DB")
        query = """
        select t1.id taxon_id , tn1.parent_id ,--  sn1.name_element name , sn2.name_element parent_name , t1.taxonomic_rank_id rankid ,sn3.name_element parent2_name ,
        case
            when t1.taxonomic_rank_id = 83 then concat(sn2.name_element , ' ' , sn1.name_element)
            when t2.taxonomic_rank_id = 83 then concat(sn3.name_element,' ',sn2.name_element , ' ' , sn1.name_element)
            else sn1.name_element
        end nomcompose,
        case
            when t1.taxonomic_rank_id = 83 then 'E' -- Espece
            when t2.taxonomic_rank_id = 83 then 'S' -- Sous Espece
            else 'O' -- Others
        end typenoeud

        from scientific_name_element sn1 join taxon_name_element tn1 on sn1.id=tn1.scientific_name_element_id
        join taxon t1 on tn1.taxon_id=t1.id
        left join taxon_name_element tn2 on tn2.taxon_id=tn1.parent_id
        left join scientific_name_element sn2  on sn2.id=tn2.scientific_name_element_id
        left join taxon t2 on tn2.taxon_id=t2.id
        left join taxon_name_element tn3 on tn3.taxon_id=tn2.parent_id
        left join scientific_name_element sn3  on sn3.id=tn3.scientific_name_element_id
        -- where tn1.taxon_id in(6903814,17137151,29,30,26,3415510,25,17068483,17058137)
        -- Limit 100000
                """
        cursor.execute(query)
        self.dt_debut=datetime.now()
        Data=[]
        for row in cursor:
            tabbedstr=functools.reduce(lambda a,b:str(a)+"\t"+str(b) if a else str(b),row,"")
            Data.append(tabbedstr)
            #bench 1.87M par 1k:55s ,par 10k:52s ,par 50k:52s, par 100k:56s
            if len(Data)>=10000:
                self.PgImport(Data)
                self.UpdateProgress(int(40*self.TotalRowCount/TargetRowCount),"Loaded %d Rows"%self.TotalRowCount)
        else:
                self.PgImport(Data)
        self.UpdateProgress(40,"Load Done : %d Rows"%self.TotalRowCount)
        cursor.close()
        logging.info("End Step 1")
        self.step(2)

    def SPStep2(self):
        logging.info("Start Step 2")
        self.UpdateProgress(40,"Transferring to Taxonomy Table")



    def QuestionProcess(self):
        txt="<h1>Taxonomy Import Task</h1>"
        if self.task.taskstep==0:
            txt+="<h3>Task Creation</h3>"
            if gvp('starttask')=="Y":
                for k,v  in self.param.__dict__.items():
                    setattr(self.param,k,gvp(k))
                if   len(self.param.host)<7 : flash("Host Field Too short","error")
                elif len(self.param.port)<2 : flash("Port Field Too short","error")
                elif len(self.param.database)<2 : flash("database Field Too short","error")
                else:
                    return self.StartTask(self.param)
            return render_template('task/taxosynccreate.html',header=txt,data=self.param)


        return PrintInCharte(txt)


