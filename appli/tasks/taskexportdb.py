# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList
from flask import Blueprint, render_template, g, flash,request
import logging,os,csv,re,zlib
import zipfile,psycopg2.extras
from time import time
from pathlib import Path
from zipfile import ZipFile
from flask_login import current_user
from appli.tasks.taskmanager import AsyncTask,DoTaskClean
from appli.database import GetAll,ExecSQL,GetDBToolsDir

table_list=("taxonomy","users","roles","users_roles"
            ,"projects","projectspriv","process","acquisitions","samples"
            ,"obj_head","obj_field","images","objectsclassifhisto","alembic_version")

class TaskExportDb(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.ProjectIds=()


    def __init__(self,task=None):
        super().__init__(task)
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon for DB Export")
        self.pgcur=db.engine.raw_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)



    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__))
        logging.info("Current directory = %s"%os.getcwd())
        # Note liste des tables
        # select ns.oid oidns, ns.nspname, c.relname,c.oid reloid
        # from pg_namespace ns
        # join pg_class c on  relnamespace=ns.oid
        #   where ns.nspname='public' and relkind='r'

        # table_list=("users",) # pour test permet d'exporter moins de données
        toolsdir=GetDBToolsDir()
        os.environ["PGPASSWORD"] = app.config['DB_PASSWORD']
        cmd=os.path.join( toolsdir,"pg_dump")
        cmd+=" -h "+app.config['DB_HOST']+" -U "+app.config['DB_USER']+" -p "+app.config.get('DB_PORT','5432')
        # -s = le schema , -F le format -f le fichier
        cmd+="  --schema-only --format=p  -f schema.sql -E LATIN1 -n public --no-owner  --no-privileges --no-security-labels --no-tablespaces  "+app.config['DB_DATABASE']+"  >dumpschemaout.txt 2>&1"
        logging.info("Export Schema : %s",cmd)
        os.system(cmd)
        zfile=ZipFile('ecotaxadb.zip', 'w',allowZip64 = True,compression= zipfile.ZIP_DEFLATED)
        zfile.write('schema.sql')
        for t in table_list:
            ColList=GetAll("""select a.attname from pg_namespace ns
                              join pg_class c on  relnamespace=ns.oid
                              join pg_attribute a on a.attrelid=c.oid
                              where ns.nspname='public' and relkind='r' and a.attname not like '%.%'
                              and attnum>0  and c.relname='{0}'  order by attnum""".format(t))

            logging.info("Save table %s"%t)
            with open("temp.copy","w",encoding='latin_1') as f:
                query="select %s from %s t"%(",".join(["t."+x[0] for x in ColList]),t)
                if t in ('projects','projectspriv',"process","acquisitions","samples","obj_head"):
                    query+=" where projid in (%s)"%(self.param.ProjectIds,)
                if t in ('objectsclassifhisto','images'):
                    query+=" join obj_head o on o.objid=t.objid where o.projid in (%s)"%(self.param.ProjectIds,)
                if t in ("obj_field"):
                    query+=" join obj_head o on o.objid=t.objfid where o.projid in (%s)"%(self.param.ProjectIds,)
                self.pgcur.copy_to(f,"("+query+")")
            zfile.write("temp.copy",arcname=t+".copy")
        logging.info("Save Images")
        vaultroot=Path("../../vault")
        self.pgcur.execute("select imgid,file_name,thumb_file_name from images i join obj_head o on o.objid=i.objid where o.projid in (%s)"%(self.param.ProjectIds,))
        for r in self.pgcur:
            if r[1]:
                zfile.write(vaultroot.joinpath(r[1]).as_posix(),arcname="images/%s.img"%r[0])
            if r[2]:
                zfile.write(vaultroot.joinpath(r[2]).as_posix(),arcname="images/%s.thumb"%r[0])

        zfile.close()
        self.task.taskstate="Done"
        self.UpdateProgress(100,"Export successfull")

        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")


    def QuestionProcess(self):
        if not current_user.has_role(database.AdministratorLabel):
            return PrintInCharte("ACCESS DENIED for this feature, Admin Required")
        g.headcenter="<h3>DATABASE EXPORT TOOL</h3><a href='/admin/'>Back to admin home</a>"
        txt=""
        errors=[]
        if self.task.taskstep==0:
            # Le projet de base est choisi second écran ou validation du second ecran
            if gvp('starttask')=="Y":
                # validation du second ecran
                self.param.ProjectIds=",".join( (x[4:] for x in request.form if x[0:4]=="prj_") )

                # Verifier la coherence des données
                # errors.append("TEST ERROR")
                if self.param.ProjectIds=='' : errors.append("You must select at least one project")
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else: # Pas d'erreur, on lance la tache
                    return self.StartTask(self.param)
            else: # valeurs par default
                pass
            #recupere les projets
            sql="""select projid,title,status,coalesce(objcount,0),coalesce(pctvalidated,0),coalesce(pctclassified,0)
                    from projects
                    order by lower(title)"""
            PrjList=GetAll(sql,cursor_factory=None)
            txt+="""
            <form method=post action=?>
            <input type=hidden name=starttask value=Y>

            SELECT PROJECT(S) TO INCLUDE IN EXPORTED DATABASE <a name="tbltop" href="#tbltop" onclick="$('#TblPrj input').prop( 'checked', true )">All</a> /
             <a href="#tbltop" onclick="$('#TblPrj input').prop( 'checked', false );">None</a>
            <table id=TblPrj class='table table-verycondensed table-bordered' >
             <tr><th width=70px>ID</td><th>Title</td><th width=100px>Status</th><th width=100px>Nbr Obj</th>
            <th width=100px>% Validated</th><th width=100>% Classified</th></tr>"""
            for r in PrjList:
                txt+="""<tr><td><input type=checkbox name=prj_{0}> {0}</td><td>{1}</td><td>{2}</td>
                <td>{3:0.0f}</td>
                <td>{4:0.2f}</td>
                <td>{5:0.2f}</td>
                </tr>""".format(*r)
            txt+="""</table>
            <input type=submit class='btn btn-primary' value='Start Database Export'>
            </form>
<div class="panel panel-default " style="margin-left: 20px;width: 800px;margin-top:5px;">
<div style="margin:5px;">
Help on common usage of this feature :
<br><span class="glyphicon glyphicon-info-sign"></span> <b>MOVE Project to ANOTHER INSTANCE of APPLICATION</b>
<ul><li>TO MOVE a project :
<br>1.	Export database from one or more project
<br>2.	Import the database into another instance of Ecotaxa
<br>3.	Delete the project from source instance of Ecotaxa (because one project should exists in one database only)
<li>TO PREPARE a mobile version of Ecotaxa for people going at sea for example
<br>1.	Create a NEW project in Ecotaxa (empty)
<br>2.	Move the project into the mobile application as described above (no need to delete the project because it is empty
<br>3.	After the cruise, move (see above) the (full) project from the mobile application to the server application and delete it from the mobile application
</ul><span class="glyphicon glyphicon-info-sign"></span> <b>BACKUP project</b>
<ul><li>TO BACK UP a project :
<ul><li>Export database and save it !
</ul></ul>

</div>
</div>
            """
            return PrintInCharte(txt)

    def GetResultFile(self):
        return 'ecotaxadb.zip'
