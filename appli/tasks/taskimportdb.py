# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList,ntcv
from flask import render_template,  flash,request
import logging,os,csv,sys
import shutil,os
from pathlib import Path
from zipfile import ZipFile
from flask.ext.login import current_user
from appli.tasks.taskmanager import AsyncTask,DoTaskClean
from appli.database import GetAll,ExecSQL,GetDBToolsDir,GetAssoc,GetAssoc2Col
from appli.tasks.taskexportdb import table_list
from psycopg2.extras import  RealDictCursor

def GetColsForTable(schema:str,table:str):
    ColList=GetAll("""select a.attname from pg_namespace ns
                      join pg_class c on  relnamespace=ns.oid
                      join pg_attribute a on a.attrelid=c.oid
                      where ns.nspname='{1}' and relkind='r' and a.attname not like '%.%'
                      and attnum>0  and c.relname='{0}'  order by attnum""".format(table,schema))
    return [x[0] for x in ColList]

class TaskImportDB(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.InData='My In Data'
                self.ProjectId=None # Destination project
                self.ProjectSrcId=None # Source project
                self.TaxoMap={}

    # #############################################################################################################
    def __init__(self,task=None):
        super().__init__(task)
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    # #############################################################################################################
    def SPCommon(self):
        logging.info("Execute SPCommon")
        self.pgcur=db.engine.raw_connection().cursor()

    # #############################################################################################################
    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__,))
        logging.info("Start Step 1")
        zfile=ZipFile(self.param.InData , 'r',allowZip64 = True)
        # self.param.IntraStep=1
        newschema=self.GetWorkingSchema()
        if getattr(self.param,'IntraStep',0)==0:
            logging.info("Extract schema")
            zfile.extract('schema.sql')
            with open ("schema.sql", "r") as schemainfile:
                with open ("schemapatched.sql", "w") as schemaoutfile:
                    for l in schemainfile:
                        schemaoutfile.write(l.replace('public',newschema)+"\n")
            # purge le schema s'il y a eu un import échoué de la DB
            logging.info("Create schema "+newschema)
            ExecSQL("DROP SCHEMA IF EXISTS "+newschema+" CASCADE")
            ExecSQL("CREATE SCHEMA "+newschema)


            toolsdir=GetDBToolsDir()
            cmd=os.path.join( toolsdir,"psql")
            cmd+=" -h "+app.config['DB_HOST']+" -U "+app.config['DB_USER']+" -w --file=schemapatched.sql "+app.config['DB_DATABASE']+" >createschemaout.txt"
            logging.info("Import Schema : %s",cmd)
            os.system(cmd)

            Constraints=GetAll("""select tbl.relname,c.conname from pg_namespace ns
                                join pg_constraint c on  connamespace=ns.oid join pg_class tbl on c.conrelid=tbl.oid
                                where ns.nspname='%s' and contype='f' """%(newschema,))
            logging.info("Drop foreign key")
            for r in Constraints:
                ExecSQL('alter table {0}.{1} drop CONSTRAINT {2}'.format(newschema,*r),debug=False)
            logging.info("Drop Index") # for faster insert and not needed for DB Merge
            for t in ("IS_ObjectsRandom","IS_ObjectsLatLong","IS_ObjectsDepth","IS_ObjectsDate","IS_ObjectsTime","IS_TaxonomySource"):
                ExecSQL('drop index {0}."{1}" '.format(newschema,t),debug=False)

            logging.info("Restore data")
            for t in table_list:
                ColList=GetColsForTable(newschema,t)
                logging.info("Restore table %s "%(t,))
                try:
                    zfile.extract(t+".copy")
                    with open(t+".copy","r") as f:
                        self.pgcur.copy_from(f,newschema+"."+t,columns=ColList)
                        self.pgcur.connection.commit()
                except:
                    logging.error("Error while data restoration %s",str(sys.exc_info()))

            logging.info("Add newid columns")
            for t in ("process","acquisitions","samples","objects","images","users","taxonomy"):
                ExecSQL("alter table {0}.{1} add column newid bigint".format(newschema,t),debug=False)

        self.task.taskstate="Question"
        self.UpdateProgress(5,"Import of temporary Database Done")

    # #############################################################################################################
    def SPStep2(self):
        logging.info("Start Step 2 : Effective data import")
        logging.info("Taxo Mapping = %s",self.param.TaxoFound)
        logging.info("Users Mapping = %s",self.param.UserFound)
        newschema=self.GetWorkingSchema()
        if getattr(self.param,'IntraStep',1)==1:
            logging.info("SubStep 1 : Create Sample, process & Acquisition")
            Ids={"acq":{"tbl":"acquisitions","pk":"acquisid"},"sample":{"tbl":"samples","pk":"sampleid"},"process":{"tbl":"process","pk":"processid"}}
            #Creation des lignes des tables
            for r in Ids.values():
                # Creation des ID dans la colonne New ID
                ExecSQL("UPDATE {0}.{1} set newid=nextval('seq_{1}') where projid={2}".format(newschema,r["tbl"],self.param.ProjectSrcId))
                TblSrc=GetColsForTable(newschema,r["tbl"])
                TblDst=GetColsForTable('public',r["tbl"])
                InsClause=[r["pk"],"projid"]
                SelClause=['newid',str(self.param.ProjectId)]
                for c in TblSrc:
                    if c!=r['pk'] and c!='projid' and c in TblDst:
                        InsClause.append(c)
                        SelClause.append(c)
                sql="insert into public.%s (%s)"%(r["tbl"],",".join(InsClause))
                sql+=" select %s from %s.%s where projid=%s"%(",".join(SelClause),newschema,r['tbl'],self.param.ProjectSrcId)
                N=ExecSQL(sql)
                logging.info("Create %s %s",N,r["tbl"])
            self.param.IntraStep=2


        if self.param.IntraStep==2:
            logging.info("SubStep 2 : Assign NewId to users")
            for k,v in self.param.UserFound.items():
                logging.info("Assign NewId to user %s"%(k,))
                ExecSQL("Update {0}.users set newid={1} where lower(name)=(%s)".format(newschema,v['id']),(k,),debug=False)

            logging.info("SubStep 2 : Create Objects")
            ExecSQL("UPDATE {0}.objects set newid=nextval('seq_objects') where projid={1}".format(newschema,self.param.ProjectSrcId))
            TblSrc=GetColsForTable(newschema,'objects')
            TblDst=GetColsForTable('public','objects')
            CustomMapping={"objid":"o.newid","projid":str(self.param.ProjectId),"sampleid":"samples.newid"
                           ,"processid":"process.newid","acquisid":"acquisitions.newid","classif_who":"users.newid"}
            InsClause=[]
            SelClause=[]
            for c in TblSrc:
                if c in TblDst:
                    InsClause.append(c)
                    SelClause.append(CustomMapping.get(c,"o."+c))
            sql="insert into public.objects (%s)"%(",".join(InsClause),)
            sql+=""" select {0} from {1}.objects o
             left join {1}.samples on o.sampleid=samples.sampleid
             left join {1}.process on o.processid=process.processid
             left join {1}.acquisitions on o.acquisid=acquisitions.acquisid
             left join {1}.users on o.classif_who=users.id
            where o.projid={2}""".format(",".join(SelClause),newschema,self.param.ProjectSrcId)
            N=ExecSQL(sql)
            logging.info("Created %s Objects",N)
            self.param.IntraStep=3

        if self.param.IntraStep==3:
            logging.info("SubStep 3 : Create Images")
            ExecSQL("""UPDATE {0}.images set newid=nextval('seq_images') from {0}.objects o
                    where images.objid=o.objid and o.projid={1}""".format(newschema,self.param.ProjectSrcId))
            TblSrc=GetColsForTable(newschema,'images')
            TblDst=GetColsForTable('public','images')
            zfile=ZipFile(self.param.InData , 'r',allowZip64 = True)
            vaultroot=Path("../../vault")
            cur = db.engine.raw_connection().cursor(cursor_factory=RealDictCursor)
            cur.execute("select images.*,o.newid newobjid from {0}.images join {0}.objects o on images.objid=o.objid where o.projid={1} ".format(newschema,self.param.ProjectSrcId),)
            for r in cur:
                Img=database.Images()
                Img.imgid=r['newid']
                Img.objid=r['newobjid']
                if r['file_name']:
                    zipimagefile="images/%s.img"%r['imgid']
                    zfile.extract(zipimagefile)
                    SrcImg=r['file_name']
                    SrcImgMini=r['thumb_file_name']
                    VaultFolder="%04d"%(Img.imgid//10000)
                    #creation du repertoire contenant les images si necessaire
                    if not vaultroot.joinpath(VaultFolder).exists():
                        vaultroot.joinpath(VaultFolder).mkdir()
                    Img.file_name     ="%s/%04d%s"     %(VaultFolder,Img.imgid%10000,Path(SrcImg).suffix)
                    shutil.move(zipimagefile,vaultroot.joinpath(Img.file_name).as_posix())
                    if r['thumb_file_name']:
                        zipimagefile="images/%s.thumb"%r['imgid']
                        zfile.extract(zipimagefile)
                        Img.thumb_file_name="%s/%04d_mini%s"%(VaultFolder,Img.imgid%10000,Path(SrcImgMini).suffix)
                        shutil.move(zipimagefile,vaultroot.joinpath(Img.thumb_file_name).as_posix())
                for c in TblSrc:
                    if c in TblDst:
                        if c not in ('imgid','objid','file_name','thumb_file_name') and c in TblDst:
                            setattr(Img,c,r[c])
                db.session.add(Img)
                db.session.commit()
            # Recalcule les valeurs de Img0
            self.pgcur.execute("""update objects o
                                set imgcount=(select count(*) from images where objid=o.objid)
                                ,img0id=(select imgid from images where objid=o.objid order by imgrank asc limit 1 )
                                where projid="""+str(self.param.ProjectId))
            self.pgcur.connection.commit()



            cur.close()
        self.task.taskstate="Done"
        self.UpdateProgress(100,"Processing done")
        self.task.taskstate="Error"
        self.UpdateProgress(10,"Test Error")

    # ******************************************************************************************************
    def QuestionProcess(self):
        if not current_user.has_role(database.AdministratorLabel):
            return PrintInCharte("ACCESS DENIED for this feature, Admin Required")
        ServerRoot=Path(app.config['SERVERLOADAREA'])
        txt="<h1>Database Importation Task</h1>"
        errors=[]
        if self.task.taskstep==0: # ################## Question Creation
            txt+="<h3>Task Creation</h3>"

            if gvp('starttask')=="Y":
                FileToSave=None
                FileToSaveFileName=None
                TaxoMap={}
                for l in gvp('TxtTaxoMap').splitlines():
                    ls=l.split('=',1)
                    if len(ls)!=2:
                        errors.append("Taxonomy Mapping : Invalid format for line %s"%(l))
                    else:
                        TaxoMap[ls[0].strip().lower()]=ls[1].strip().lower()
                # Verifier la coherence des données
                uploadfile=request.files.get("uploadfile")
                if uploadfile is not None and uploadfile.filename!='' : # import d'un fichier par HTTP
                    FileToSave=uploadfile # La copie est faite plus tard, car à ce moment là, le repertoire de la tache n'est pas encore créé
                    FileToSaveFileName="uploaded.zip"
                    self.param.InData="uploaded.zip"
                elif len(gvp("ServerPath"))<2:
                    errors.append("Input Folder/File Too Short")
                else:
                    sp=ServerRoot.joinpath(Path(gvp("ServerPath")))
                    if not sp.exists(): #verifie que le repertoire existe
                        errors.append("Input Folder/File Invalid")
                    else:
                        self.param.InData=sp.as_posix()
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else:
                    self.param.TaxoMap=TaxoMap # on stocke le dictionnaire et pas la chaine
                    return self.StartTask(self.param,FileToSave=FileToSave,FileToSaveFileName=FileToSaveFileName)
            return render_template('task/importdb_create.html',header=txt,data=self.param,ServerPath=gvp("ServerPath"),TxtTaxoMap=gvp("TxtTaxoMap"))

        newschema=self.GetWorkingSchema()
        # self.task.taskstep=1
        if self.task.taskstep==1: # ################## Question Post Import DB
            if gvg("src")=="" : # il faut choisir le projet source
                txt+="<h3>Select project to import</h3>"
                PrjList=GetAll("select projid,title,status from {0}.projects order by lower(title)".format(newschema),cursor_factory=None)
                txt+="""<table class='table table-condensed table-bordered' style='width:600px;'>"""
                for r in PrjList:
                    txt+="<tr><td><a class='btn btn-primary' href='?src={0}'>Select {0}</a></td><td>{1}</td><td>{2}</td></tr>".format(*r)
                txt+="""</table>""";
                return PrintInCharte(txt);
            if gvg("dest")=="" : # il faut choisir le projet destination
                PrjList=GetAll("select projid,title,status from projects order by lower(title)",cursor_factory=None)
                txt+="<h3>Select project destination project</h3> or <a class='btn btn-primary' href='?src={0}&dest=new'>New project</a>".format(gvg("src"))
                txt+="""<table class='table table-condensed table-bordered' style='width:600px;'>"""
                for r in PrjList:
                    txt+="<tr><td><a class='btn btn-primary' href='?src={0}&dest={1}'>Select {1}</a></td><td>{2}</td><td>{3}</td></tr>".format(gvg("src"),*r)
                txt+="""</table>""";
                return PrintInCharte(txt);


            if gvg("prjok")=="" : # Creation du projet destination ou MAJ des attributs & detection des Taxo&Users Founds
                SrcPrj=GetAll("select * from {0}.projects where projid={1}".format(newschema,gvg("src")),cursor_factory=RealDictCursor)
                if gvg("dest")=="new" : # Creation du projet destination
                    Prj=database.Projects()
                    Prj.title="IMPORT "+SrcPrj[0]['title']
                    db.session.add(Prj)
                else: # MAJ du projet
                    Prj=database.Projects.query.filter_by(projid=int(gvg("dest"))).first()
                    NbrObj=GetAll("select count(*) from objects WHERE projid="+gvg("dest"))[0][0]
                    if NbrObj>0:
                        flash("Destination project must be empty",'error')
                        return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
                for k,v in SrcPrj[0].items():
                    if k not in ("projid","title"):
                        setattr(Prj,k,v)
                db.session.commit()
                flash("Project %s:%s created or updated successfuly"%(Prj.projid,Prj.title),'success')
                # Controle du mapping Taxo
                sql="""select DISTINCT t.id,lower(t.name) as name,t.parent_id
                          from {0}.objects o join {0}.taxonomy t on o.classif_id=t.id
                        where o.projid={1}
                        union select DISTINCT t.id,lower(t.name) as name,t.parent_id
                          from {0}.objects o join {0}.taxonomy t on o.classif_auto_id=t.id
                        where o.projid={1} order by 2""".format(newschema,gvg("src"))
                self.param.TaxoFound=GetAssoc(sql,cursor_factory=RealDictCursor,keyid='id')
                app.logger.info("TaxoFound=%s",self.param.TaxoFound)
                TaxoInDest=GetAssoc2Col("select id,lower(name) as name from taxonomy where id = any (%s)",( list(self.param.TaxoFound.keys()) ,) )
                # print(TaxoInDest)
                for id,v in self.param.TaxoFound.items():
                    self.param.TaxoFound[id]['newid']=None # par defaut pas de correspondance
                    if id in TaxoInDest:
                        if TaxoInDest[id].lower()==v['name']:
                            self.param.TaxoFound[id]['newid']=id # ID inchangé
                lst=[t["name"] for t in self.param.TaxoFound.values() if t["newid"] is None] # liste des Taxon sans mapping
                TaxoInDest=GetAssoc2Col("select lower(name) as name,id from taxonomy where lower(name) = any (%s)",(lst ,) )
                for id,v in self.param.TaxoFound.items() :
                    if v['newid'] is None:
                        if v["name"] in TaxoInDest:
                                self.param.TaxoFound[id]['newid']=TaxoInDest[v["name"]] # ID du même nom dans la base de destination
                NotFoundTaxo=[t["name"] for t in self.param.TaxoFound.values() if t["newid"] is None] # liste des Taxon sans mapping restant
                app.logger.info("NotFoundTaxo=%s",NotFoundTaxo)
                # Controle du mapping utilisateur
                sql="""select DISTINCT lower(t.name) as name,lower(email) as email
                          from {0}.objects o join {0}.users t on o.classif_who=t.id
                        where o.projid={1}""".format(newschema,gvg("src"))
                self.param.UserFound=GetAssoc(sql,cursor_factory=RealDictCursor,keyid='name')
                self.pgcur=db.engine.raw_connection().cursor()
                self.pgcur.execute("select id,lower(name),lower(email) from users where lower(name) = any(%s) or email= any(%s) "
                                   ,(list(self.param.UserFound.keys()),[x.get('email') for x in self.param.UserFound.values()]))
                # Résolution des noms à partir du nom ou de l'email
                for rec in self.pgcur:
                    for u in self.param.UserFound:
                        if u==rec[1] or self.param.UserFound[u].get('email')==rec[2]:
                            self.param.UserFound[u]['id']=rec[0]
                logging.info("Users Found = %s",self.param.UserFound)
                NotFoundUser=[k for k,v in self.param.UserFound.items() if v.get("id")==None]
                if len(NotFoundUser)>0:
                    logging.info("Some Users Not Found = %s",NotFoundUser)
                self.UpdateParam() # On met à jour la Taxo
                if len(NotFoundUser)>0 or len(NotFoundTaxo)>0 :
                    txt+="<a class='btn btn-primary' href='?src={0}&dest={1}&prjok=1'>Continue</a>".format(gvg("src"),Prj.projid)
                else:
                    txt+="<a class='btn btn-primary' href='?src={0}&dest={1}&prjok=2'>Continue</a>".format(gvg("src"),Prj.projid)

                return PrintInCharte(txt);

            if gvg("prjok")=="1" or gvg("prjok")=="2": # 2 pas de mapping requis, simule un start task
                NotFoundTaxo=[t["name"] for t in self.param.TaxoFound.values() if t["newid"] is None] # liste des Taxon sans mapping restant
                NotFoundUsers=[k for k,v in self.param.UserFound.items() if v.get("id")==None]
                app.logger.info("NotFoundTaxo=%s",NotFoundTaxo)
                app.logger.info("NotFoundUser=%s",NotFoundUsers)

                if gvp('starttask')=="Y" or gvg("prjok")=="2":
                    app.logger.info("Form Data = %s",request.form)
                    for i in range(1,1+len(NotFoundTaxo)):
                        orig=gvp("orig%d"%(i)) #Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
                        action=gvp("action%d"%(i))
                        newvalue=gvp("taxolb%d"%(i))
                        if orig in NotFoundTaxo and action!="":
                            if action=="M":
                                if newvalue=="":
                                    errors.append("Taxonomy Manual Mapping : No Value Selected  for '%s'"%(orig,))
                                else:
                                    t=database.Taxonomy.query.filter(database.Taxonomy.id==int(newvalue)).first()
                                    app.logger.info(orig+" associated to "+t.name)
                                    self.param.TaxoFound[orig]['newid']=t.id
                            elif action=="U": #create Under
                                if newvalue=="":
                                    errors.append("Taxonomy Manual Mapping : No Parent Value Selected  for '%s'"%(orig,))
                                else:
                                    t=database.Taxonomy()
                                    t.name=orig
                                    t.parent_id=int(newvalue)
                                    db.session.add(t)
                                    db.session.commit()
                                    self.param.TaxoFound[orig]=t.id
                                    app.logger.info(orig+" created under "+t.name)
                            else:
                                errors.append("Taxonomy Manual Mapping : No Action Selected  for '%s'"%(orig,))
                        else:
                            errors.append("Taxonomy Manual Mapping : Invalid value '%s' for '%s'"%(newvalue,orig))
                    for i in range(1,1+len(NotFoundUsers)):
                        orig=gvp("origuser%d"%(i)) #Le nom original est dans origuserXX et la nouvelle valeur dans userlbXX
                        newvalue=gvp("userlb%d"%(i))
                        if orig in NotFoundUsers and newvalue!="":
                            t=database.users.query.filter(database.users.id==int(newvalue)).first()
                            app.logger.info("User "+orig+" associated to "+t.name)
                            self.param.UserFound[orig]['id']=t.id
                        else:
                            errors.append("User Manual Mapping : Invalid value '%s' for '%s'"%(newvalue,orig))
                    app.logger.info("Final Taxofound = %s",self.param.TaxoFound)
                    self.param.ProjectId=int(gvg("dest"))
                    self.param.ProjectSrcId=int(gvg("src"))
                    self.param.IntraStep=1
                    self.UpdateParam() # On met à jour ce qui à été accepté
                    # Verifier la coherence des données
                    if len(errors)==0:
                        return self.StartTask(self.param,step=2)
                    for e in errors:
                        flash(e,"error")
                    NotFoundTaxo=[k for k,v in self.param.TaxoFound.items() if v==None]
                    NotFoundUsers=[k for k,v in self.param.UserFound.items() if v.get('id')==None]
                return render_template('task/importdb_question1.html',header=txt,taxo=NotFoundTaxo,users=NotFoundUsers)
            return PrintInCharte(txt)
    # #############################################################################################################
    def ShowCustomDetails(self):
        txt="<h3>Import Task details view</h3>"
        txt="<p><u>Used mapping, usable for next import</u></p>"
        taxo=database.GetAssoc2Col("select id,name from taxonomy where id = any(%s)",(list(set(self.param.TaxoFound.values())),))
        for k,v in self.param.TaxoFound.items():
            if v in taxo:
                txt+="{0}={1}<br>".format(k,taxo[v])
        return PrintInCharte(txt)
    # #############################################################################################################
    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId=self.param.ProjectId
        DoTaskClean(self.task.id)
        return """<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>
        <a href='/Task/Create/TaskClassifAuto?p={0}' class='btn btn-primary btn-sm'  role=button>Go to Automatic Classification Screen</a> """.format(PrjId)
