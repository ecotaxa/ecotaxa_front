# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList
from PIL import Image
from flask import render_template,  flash,request
import logging,os,csv,sys
import datetime,shutil,random,zipfile
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask,LoadTask,DoTaskClean
from appli.database import GetAll


PredefinedTables=['object','sample','process','acq']
# PredefinedTypes={'[float]':'n','[int]':'n','[text]':'t'}
PredefinedTypes={'[f]':'n','[t]':'t'}
PredefinedFields={
    'object_id':{'table':'object','field':'orig_id','type':'t'},
    'sample_id':{'table':'sample','field':'orig_id','type':'t'},
    'acq_id':{'table':'acq','field':'orig_id','type':'t'},
    'process_id':{'table':'process','field':'orig_id','type':'t'},
    'object_lat':{'table':'object','field':'latitude','type':'n'},
    'object_lon':{'table':'object','field':'longitude','type':'n'},
    'object_date':{'table':'object','field':'objdate','type':'t'},
    'object_time':{'table':'object','field':'objtime','type':'t'},
    'object_link':{'table':'object','field':'object_link','type':'t'},
    'object_depth_min':{'table':'object','field':'depth_min','type':'n'},
    'object_depth_max':{'table':'object','field':'depth_max','type':'n'},
    'object_annotation_category':{'table':'object','field':'classif_id','type':'t'},
    'object_annotation_person_email':{'table':'object','field':'tmp_annotemail','type':'t'},
    'object_annotation_date':{'table':'object','field':'classif_when','type':'t'},
    'object_annotation_time':{'table':'object','field':'tmp_annottime','type':'t'},
    'object_annotation_person_name':{'table':'object','field':'classif_who','type':'t'},
    'object_annotation_status':{'table':'object','field':'classif_qual','type':'t'},
    'img_rank':{'table':'image','field':'imgrank','type':'n'},
    'img_file_name':{'table':'image','field':'orig_file_name','type':'t'},
    'annotation_person_first_name':{'table':'object','field':'tmp_todelete1','type':'t'},
    'sample_dataportal_descriptor':{'table':'sample','field':'dataportal_descriptor','type':'t'},
}
# Purge les espace et converti le Nan en vide
def CleanValue(v):
    v=v.strip()
    if v.lower()=='nan':
        v=''
    return v;
# retourne le flottant image de la chaine en faisant la conversion ou None
def ToFloat(value):
    if value=='': return None
    try:
        return float(value)
    except ValueError:
        return None

class TaskImport(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr==None: # Valeurs par defaut ou vide pour init
                self.InData='My In Data'
                self.ProjectId=None
                # self.Mapping={x:{} for x in PredefinedTables}
                self.Mapping={}
                self.TaxoMap={}


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
        if getattr(self.param,'IntraStep',0)==0:
            #Sous tache 1 On dezippe ou on pointe sur le repertoire source.
            if self.param.InData.lower().endswith("zip"):
                logging.info("SubTask0 : Unzip File on temporary folder")
                self.UpdateProgress(1,"Unzip File on temporary folder")
                self.param.SourceDir=os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../temptask/task%06d/data"%(int(self.task.id))))
                if not os.path.exists(self.param.SourceDir):
                    os.mkdir(self.param.SourceDir)
                with zipfile.ZipFile(self.param.InData, 'r') as z:
                    z.extractall(self.param.SourceDir)
            else:
                self.param.SourceDir=self.param.InData
            self.param.IntraStep=1

        if self.param.IntraStep==1:
            self.param.Mapping={} # Reset à chaque Tentative
            # Import du mapping existant dans le projet
            Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
            for k,v in DecodeEqualList(Prj.mappingobj).items():
                self.param.Mapping['object_'+v]={'table': 'object', 'title': v, 'type': k[0], 'field': k}
            for k,v in DecodeEqualList(Prj.mappingsample).items():
                self.param.Mapping['sample_'+v]={'table': 'sample', 'title': v, 'type': k[0], 'field': k}
            for k,v in DecodeEqualList(Prj.mappingacq).items():
                self.param.Mapping['acq_'+v]={'table': 'acq', 'title': v, 'type': k[0], 'field': k}
            for k,v in DecodeEqualList(Prj.mappingprocess).items():
                self.param.Mapping['process_'+v]={'table': 'process', 'title': v, 'type': k[0], 'field': k}
            self.param.TaxoFound={} # Reset à chaque Tentative
            self.param.UserFound={} # Reset à chaque Tentative
            self.param.steperrors=[] # Reset des erreurs
            # recuperation de toutes les paire objet/Images du projet
            self.ExistingObject=set()
            self.pgcur.execute(
                "SELECT concat(o.orig_id,'*',i.orig_file_name) from images i join objects o on i.objid=o.objid where o.projid="+str(self.param.ProjectId))
            for rec in self.pgcur:
                self.ExistingObject.add(rec[0])
            logging.info("SubTask1 : Analyze TSV Files")
            self.UpdateProgress(2,"Analyze TSV Files")
            self.LastNum={x:{'n':0,'t':0} for x in PredefinedTables}
            # Extraction des Max des champs
            for m in self.param.Mapping.values():
                v=int(m['field'][1:])
                if v>self.LastNum[m['table']][m['field'][0]]:
                    self.LastNum[m['table']][m['field'][0]]=v
            sd=Path(self.param.SourceDir)
            self.param.TotalRowCount=0
            Seen=set()
            for CsvFile in sd.glob("**/*.tsv"):
                relname=CsvFile.relative_to(sd) # Nom relatif à des fins d'affichage uniquement
                logging.info("Analyzing file %s"%(relname.as_posix()))
                with open(CsvFile.as_posix(),encoding='latin_1') as csvfile:
                    # lecture en mode dictionnaire basé sur la premiere ligne
                    rdr = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
                    #lecture la la ligne des types (2nd ligne du fichier
                    LType=rdr.__next__()
                    # Fabrication du mapping
                    for champ in rdr.fieldnames:
                        if champ in self.param.Mapping:
                            continue # Le champ à déjà été détecté
                        ColName=champ.strip(" \t").lower()
                        ColSplitted=ColName.split("_",1)
                        if len(ColSplitted)!=2:
                            self.LogErrorForUser("Invalid Header '%s' in file %s. Format must be Table_Field. Field ignored"%(ColName,relname.as_posix()))
                            continue
                        Table=ColSplitted[0] # On isole la partie table avant le premier _
                        if ColName in PredefinedFields:
                            Table=PredefinedFields[champ]['table']
                            self.param.Mapping[champ]=PredefinedFields[champ]
                        else: # champs non predefinis donc dans nXX ou tXX
                            if not Table in PredefinedTables:
                                self.LogErrorForUser("Invalid Header '%s' in file %s. Table Incorrect. Field ignored"%(ColName,relname.as_posix()))
                                continue
                            if Table!='object': # Dans les autres tables les types sont forcés à texte
                                SelType='t'
                            else:
                                if LType[champ] not in PredefinedTypes:
                                    self.LogErrorForUser("Invalid Type '%s' for Field '%s' in file %s. Incorrect Type. Field ignored"%(LType[champ],ColName,relname.as_posix()))
                                    continue
                                SelType=PredefinedTypes[LType[champ]]
                            self.LastNum[Table][SelType]+=1
                            self.param.Mapping[champ]={'table':Table,'field':SelType+"%02d"%self.LastNum[Table][SelType],'type':SelType,'title':ColSplitted[1]}
                            logging.info("New field %s found in file %s",champ,relname.as_posix())
                    # Test du contenu du fichier
                    RowCount=0
                    for lig in rdr:
                        RowCount+=1
                        for champ in rdr.fieldnames:
                            m=self.param.Mapping.get(champ,None)
                            if m is None:
                                continue # Le champ n'est pas considéré
                            v=CleanValue(lig[champ])
                            if v!="": # si pas de valeurs, pas de controle
                                Seen.add(champ)
                                # if m.get('Seen',None)==None: #marque si on a vu au moins une valeur.
                                #     self.param.Mapping[champ]["Seen"]=True
                                if m['type']=='n':
                                    vf=ToFloat(v)
                                    if vf==None:
                                        self.LogErrorForUser("Invalid float value '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))
                                    elif champ=='object_lat':
                                        if vf<-90 or vf>90:
                                            self.LogErrorForUser("Invalid Lat. value '%s' for Field '%s' in file %s. Incorrect range -90/+90°."%(v,champ,relname.as_posix()))
                                    elif champ=='object_long':
                                        if vf<-180 or vf>180:
                                            self.LogErrorForUser("Invalid Long. value '%s' for Field '%s' in file %s. Incorrect range -180/+180°."%(v,champ,relname.as_posix()))
                                elif champ=='object_date':
                                    try:
                                        datetime.date(int(v[0:4]), int(v[4:6]), int(v[6:8]))
                                    except ValueError:
                                        self.LogErrorForUser("Invalid Date value '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))
                                elif champ=='object_time':
                                    try:
                                        v=v.zfill(6)
                                        datetime.time(int(v[0:2]), int(v[2:4]), int(v[4:6]))
                                    except ValueError:
                                        self.LogErrorForUser("Invalid Time value '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))
                                elif champ=='object_annotation_category':
                                    v=self.param.TaxoMap.get(v,v) # Applique le mapping
                                    self.param.TaxoFound[v.lower()]=None #creation d'une entrée dans le dictionnaire.
                                elif champ=='object_annotation_person_name':
                                    self.param.UserFound[v]={'email':CleanValue(lig.get('object_annotation_person_email',''))}
                                elif champ=='object_annotation_status':
                                    if v!='noid' and v.lower() not in database.ClassifQualRevert:
                                        self.LogErrorForUser("Invalid Annotation Status '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))

                        #Analyse l'existance du fichier Image
                        ObjectId=CleanValue(lig.get('object_id',''))
                        if ObjectId=='':
                            self.LogErrorForUser("Missing ObjectId on line '%s' in file %s. "%(RowCount,relname.as_posix()))
                        ImgFileName=CleanValue(lig.get('img_file_name','MissingField img_file_name'))
                        ImgFilePath=CsvFile.with_name(ImgFileName)
                        if not ImgFilePath.exists():
                            self.LogErrorForUser("Missing Image '%s' in file %s. "%(ImgFileName,relname.as_posix()))
                        else:
                            try:
                                im=Image.open(ImgFilePath.as_posix())
                            except:
                                self.LogErrorForUser("Error while reading Image '%s' in file %s. %s"%(ImgFileName,relname.as_posix(),sys.exc_info()[0]))
                        CleExistObj=ObjectId+'*'+ImgFileName
                        if CleExistObj in self.ExistingObject:
                            self.LogErrorForUser("Duplicate object %s Image '%s' in file %s. "%(ObjectId,ImgFileName,relname.as_posix()))
                        self.ExistingObject.add(CleExistObj)
                    logging.info("File %s : %d row analysed",relname.as_posix(),RowCount)
                    self.param.TotalRowCount+=RowCount
            if self.param.TotalRowCount==0:
                self.LogErrorForUser("No object found")
            self.UpdateProgress(15,"TSV File Parsed"%())
            print(self.param.Mapping)
            logging.info("Taxo Found = %s",self.param.TaxoFound)
            logging.info("Users Found = %s",self.param.UserFound)
            logging.info("For Information Not Seen Fields %s",
                         [k for k in self.param.Mapping if k not in Seen])
            if len(self.param.steperrors)>0:
                self.task.taskstate="Error"
                self.task.progressmsg="Some errors founds during file parsing "
                db.session.commit()
                return
            self.param.IntraStep=2
        if self.param.IntraStep==2:
            logging.info("Start Sub Step 1.2")
            self.pgcur.execute("select id,lower(name),email from users where lower(name) = any(%s) or email= any(%s) ",([x for x in self.param.UserFound.keys()],[x.get('email') for x in self.param.UserFound.values()]))
            # Résolution des noms à partir du nom ou de l'email
            for rec in self.pgcur:
                for u in self.param.UserFound:
                    if u==rec[1] or self.param.UserFound[u].get('email')==rec[2]:
                        self.param.UserFound[u]['id']=rec[0]
            logging.info("Users Found = %s",self.param.UserFound)
            NotFoundUser=[k for k,v in self.param.UserFound.items() if v.get("id")==None]
            if len(NotFoundUser)>0:
                logging.info("Some Users Not Found = %s",NotFoundUser)
            # récuperation des ID des taxo trouvées
            self.pgcur.execute("select id,name from taxonomy where lower(name) = any(%s) ",([x.lower() for x in self.param.TaxoFound.keys()],))
            for rec in self.pgcur:
                self.param.TaxoFound[rec[1]]=rec[0]
            logging.info("Taxo Found = %s",self.param.TaxoFound)
            NotFoundTaxo=[k for k,v in self.param.TaxoFound.items() if v==None]
            if len(NotFoundTaxo)>0:
                logging.info("Some Taxo Not Found = %s",NotFoundTaxo)
            if len(NotFoundUser)==0 and len(NotFoundTaxo)==0: # si tout est déjà résolue on enchaine sur la phase 2
                self.SPStep2()
            else:
                self.task.taskstate="Question"
            self.UpdateProgress(20,"Taxo automatic resolution Done"%())
            #sinon on pose une question


    def SPStep2(self):
        logging.info("Start Step 2 : Effective data import")
        logging.info("Taxo Mapping = %s",self.param.TaxoFound)
        logging.info("Users Mapping = %s",self.param.UserFound)
        # Mise à jour du mapping en base
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        Prj.mappingobj=EncodeEqualList({v['field']:v.get('title') for k,v in self.param.Mapping.items() if v['table']=='object' and v['field'][0]in ('t','n') and v.get('title')!=None})
        Prj.mappingsample=EncodeEqualList({v['field']:v.get('title') for k,v in self.param.Mapping.items() if v['table']=='sample' and v['field'][0]in ('t','n') and v.get('title')!=None})
        Prj.mappingacq=EncodeEqualList({v['field']:v.get('title') for k,v in self.param.Mapping.items() if v['table']=='acq' and v['field'][0]in ('t','n') and v.get('title')!=None})
        Prj.mappingprocess=EncodeEqualList({v['field']:v.get('title') for k,v in self.param.Mapping.items() if v['table']=='process' and v['field'][0]in ('t','n') and v.get('title')!=None})
        db.session.commit()
        Ids={"acq":{"tbl":"acquisitions","pk":"acquisid"},"sample":{"tbl":"samples","pk":"sampleid"},"process":{"tbl":"process","pk":"processid"}}
        #recupération des orig_id des acq,sample,process
        for i in Ids:
            sql="select orig_id,"+Ids[i]['pk']+" from "+Ids[i]['tbl']+" where projid="+str(self.param.ProjectId)
            Ids[i]["ID"]={}
            for r in GetAll(sql):
                Ids[i]["ID"][r[0]]=int(r[1])
        # recuperation de les ID objet du projet
        self.ExistingObject={}
        self.pgcur.execute(
            "SELECT o.orig_id,o.objid from objects o where o.projid="+str(self.param.ProjectId))
        for rec in self.pgcur:
            self.ExistingObject[r[0]]=r[1]
        #logging.info("Ids = %s",Ids)
        random.seed()
        sd=Path(self.param.SourceDir)
        TotalRowCount=0
        for CsvFile in sd.glob("**/*.tsv"):
            relname=CsvFile.relative_to(sd) # Nom relatif à des fins d'affichage uniquement
            logging.info("Analyzing file %s"%(relname.as_posix()))
            with open(CsvFile.as_posix(),encoding='latin_1') as csvfile:
                # lecture en mode dictionnaire basé sur la premiere ligne
                rdr = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
                #lecture la la ligne des types (2nd ligne du fichier
                LType=rdr.__next__()
                # Chargement du contenu du fichier
                RowCount=0
                for lig in rdr:
                    Objs={"acq":database.Acquisitions(),"sample":database.Samples(),"process":database.Process()
                        ,"object":database.Objects(),"image":database.Images()}
                    RowCount+=1
                    TotalRowCount+=1
                    for champ in rdr.fieldnames:
                        m=self.param.Mapping.get(champ,None)
                        FieldName=m.get("field",None)
                        FieldTable=m.get("table",None)
                        FieldValue=None
                        if m is None:
                            continue # Le champ n'est pas considéré
                        v=CleanValue(lig[champ])
                        if v!="": # si pas de valeurs, on laisse le champ null
                            if m['type']=='n':
                                FieldValue=ToFloat(v)
                            elif champ=='object_date':
                                FieldValue=datetime.date(int(v[0:4]), int(v[4:6]), int(v[6:8]))
                            elif champ=='object_time':
                                    v=v.zfill(6)
                                    FieldValue=datetime.time(int(v[0:2]), int(v[2:4]), int(v[4:6]))
                            elif FieldName=='classif_when':
                                v2=CleanValue(lig.get('object_annotation_time','000000')).zfill(6)
                                FieldValue=datetime.datetime(int(v[0:4]), int(v[4:6]), int(v[6:8]),int(v2[0:2]), int(v2[2:4]), int(v2[4:6]))
                            elif FieldName=='classif_id':
                                v=self.param.TaxoMap.get(v,v) # Applique le mapping initial d'entrée
                                FieldValue=self.param.TaxoFound[v]
                            elif FieldName=='classif_who':
                                FieldValue=self.param.UserFound[v].get('id',None)
                            elif FieldName=='classif_qual':
                                FieldValue=database.ClassifQualRevert.get(v.lower())
                            else: # c'est un champ texte sans rien de special
                                FieldValue=v
                            if FieldTable in Objs:
                                # if FieldName in Objs[FieldTable].__dict__:
                                if  hasattr(Objs[FieldTable],FieldName):
                                    setattr(Objs[FieldTable],FieldName,FieldValue)
                                    # logging.info("setattr %s %s %s",FieldTable,FieldName,FieldValue)
                                # else:
                                    # logging.info("skip F %s %s %s",FieldTable,FieldName,FieldValue)
                            else:
                                logging.info("skip T %s %s %s",FieldTable,FieldName,FieldValue)
                    # Affectation des ID Sample, Acq & Process et creation de ces dernier si necessaire
                    for t in Ids:
                        if Objs[t].orig_id is not None:
                            if Objs[t].orig_id in Ids[t]["ID"]:
                                setattr(Objs["object"],Ids[t]["pk"],Ids[t]["ID"][Objs[t].orig_id])
                            else:
                                Objs[t].projid=self.param.ProjectId
                                db.session.add(Objs[t])
                                db.session.commit()
                                Ids[t]["ID"][Objs[t].orig_id]=getattr(Objs[t],Ids[t]["pk"])
                                setattr(Objs["object"],Ids[t]["pk"],Ids[t]["ID"][Objs[t].orig_id])
                                logging.info("IDS %s %s",t,Ids[t])
                    self.pgcur.execute("select nextval('seq_images')" )
                    Objs["image"].imgid=self.pgcur.fetchone()[0]
                    # Recherche de l'objet si c'est une images complementaire
                    if Objs["object"].orig_id in self.ExistingObject:
                        Objs["object"].objid=self.ExistingObject[Objs["object"].orig_id]
                    else: # ou Creation de l'objet
                        Objs["object"].projid=self.param.ProjectId
                        Objs["object"].random_value=random.randint(1,99999999)
                        Objs["object"].img0id=Objs["image"].imgid
                        db.session.add(Objs["object"])
                        db.session.commit()
                        self.ExistingObject[Objs["object"].orig_id]=Objs["object"].objid # Provoque un select object sauf si 'expire_on_commit':False
                    #Gestion de l'image, creation DB et fichier dans Vault
                    Objs["image"].objid=Objs["object"].objid
                    ImgFilePath=CsvFile.with_name(Objs["image"].orig_file_name)
                    VaultFolder="%04d"%(Objs["image"].imgid//10000)
                    vaultroot=Path("../../vault")
                    #creation du repertoire contenant les images si necessaire
                    if not vaultroot.joinpath(VaultFolder).exists():
                        vaultroot.joinpath(VaultFolder).mkdir()
                    vaultfilename     ="%s/%04d%s"     %(VaultFolder,Objs["image"].imgid%10000,ImgFilePath.suffix)
                    vaultfilenameThumb="%s/%04d_mini%s"%(VaultFolder,Objs["image"].imgid%10000,'.jpg') #on Impose le format de la miniature
                    Objs["image"].file_name=vaultfilename
                    #copie du fichier image
                    shutil.copyfile(ImgFilePath.as_posix(),vaultroot.joinpath(vaultfilename).as_posix())
                    im=Image.open(vaultroot.joinpath(vaultfilename).as_posix())
                    Objs["image"].width=im.size[0]
                    Objs["image"].height=im.size[1]
                    SizeLimit=app.config['THUMBSIZELIMIT']
                    # génération d'une miniature si une image est trop grande.
                    if (im.size[0]>SizeLimit) or (im.size[1]>SizeLimit) :
                            im.thumbnail((SizeLimit,SizeLimit))
                            im.save(vaultroot.joinpath(vaultfilenameThumb).as_posix())
                            Objs["image"].thumb_file_name=vaultfilenameThumb
                            Objs["image"].thumb_width=im.size[0]
                            Objs["image"].thumb_height=im.size[1]
                    #ajoute de l'image en DB
                    db.session.add(Objs["image"])
                    db.session.commit()
                    if (TotalRowCount%100)==0:
                        self.UpdateProgress(100*TotalRowCount/self.param.TotalRowCount,"Processing files %d/%d"%(TotalRowCount,self.param.TotalRowCount))
                logging.info("File %s : %d row Loaded",relname.as_posix(),RowCount)
        self.pgcur.execute("""update objects o
                            set imgcount=(select count(*) from images where objid=o.objid)
                            ,img0id=(select imgid from images where objid=o.objid order by imgrank asc limit 1 )
                            where projid="""+str(self.param.ProjectId))
        self.pgcur.connection.commit()
        self.pgcur.execute("""update samples s set latitude=sll.latitude,longitude=sll.longitude
              from (select o.sampleid,min(o.latitude) latitude,min(o.longitude) longitude
              from objects o
              where projid=%(projid)s and o.latitude is not null and o.longitude is not null
              group by o.sampleid) sll where s.sampleid=sll.sampleid and projid=%(projid)s and s.longitude is null""",{'projid':self.param.ProjectId})
        self.pgcur.connection.commit()
        self.task.taskstate="Done"
        self.UpdateProgress(100,"Processing done")

    def QuestionProcess(self):
        ServerRoot=Path(app.config['SERVERLOADAREA'])
        txt="<h1>Text File Importation Task</h1>"
        errors=[]
        if self.task.taskstep==0:
            txt+="<h3>Task Creation</h3>"
            Prj=database.Projects.query.filter_by(projid=gvg("p")).first()
            txt="<a href='/prj/%d'>Back to project</a>"%Prj.projid
            if Prj.CheckRight(2)==False:
                return PrintInCharte("ACCESS DENIED for this project");
            if gvp('starttask')=="Y":
                FileToSave=None
                FileToSaveFileName=None
                self.param.ProjectId=gvg("p")
                # for k,v  in self.param.__dict__.items():
                #     setattr(self.param,k,gvp(k))
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
            else: # valeurs par default
                self.param.ProjectId=gvg("p")
            return render_template('task/import_create.html',header=txt,data=self.param,ServerPath=gvp("ServerPath"),TxtTaxoMap=gvp("TxtTaxoMap"))
        if self.task.taskstep==1:
            # self.param.TaxoFound['agreia pratensis']=None #Pour TEST A EFFACER
            NotFoundTaxo=[k for k,v in self.param.TaxoFound.items() if v==None]
            NotFoundUsers=[k for k,v in self.param.UserFound.items() if v.get('id')==None]
            app.logger.info("Pending Taxo Not Found = %s",NotFoundTaxo)
            app.logger.info("Pending Users Not Found = %s",NotFoundUsers)
            if gvp('starttask')=="Y":
                app.logger.info("Form Data = %s",request.form)
                for i in range(1,1+len(NotFoundTaxo)):
                    orig=gvp("orig%d"%(i)) #Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
                    newvalue=gvp("taxolb%d"%(i))
                    if orig in NotFoundTaxo and newvalue!="":
                        t=database.Taxonomy.query.filter(database.Taxonomy.id==int(newvalue)).first()
                        app.logger.info(orig+" associated to "+t.name)
                        self.param.TaxoFound[orig]=t.id
                    else:
                        errors.append("Taxonomy Manual Mapping : Invalid value '%s' for '%s'"%(newvalue,orig))
                for i in range(1,1+len(NotFoundUsers)):
                    orig=gvp("origuser%d"%(i)) #Le nom original est dans origXX et la nouvelle valeur dans taxolbXX
                    newvalue=gvp("userlb%d"%(i))
                    if orig in NotFoundUsers and newvalue!="":
                        t=database.users.query.filter(database.users.id==int(newvalue)).first()
                        app.logger.info("User "+orig+" associated to "+t.name)
                        self.param.UserFound[orig]['id']=t.id
                    else:
                        errors.append("User Manual Mapping : Invalid value '%s' for '%s'"%(newvalue,orig))
                app.logger.info("Final Taxofound = %s",self.param.TaxoFound)
                self.UpdateParam() # On met à jour ce qui à été accepté
                # Verifier la coherence des données
                if len(errors)==0:
                    return self.StartTask(self.param,step=2)
                for e in errors:
                    flash(e,"error")
                NotFoundTaxo=[k for k,v in self.param.TaxoFound.items() if v==None]
                NotFoundUsers=[k for k,v in self.param.UserFound.items() if v.get('id')==None]
            return render_template('task/import_question1.html',header=txt,taxo=NotFoundTaxo,users=NotFoundUsers)
        return PrintInCharte(txt)
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
        DoTaskClean(self.task.id)
        return """<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>
        <a href='/Task/Create/TaskClassifAuto?p={0}' class='btn btn-primary btn-sm'  role=button>Go to Automatic Classification Screen</a> """.format(PrjId)
