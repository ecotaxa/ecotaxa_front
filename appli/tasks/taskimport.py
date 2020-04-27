# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList,ntcv,GetAppManagerMailto,CreateDirConcurrentlyIfNeeded
from PIL import Image
from flask import render_template,  flash,request,g
import logging,os,csv,sys,time,configparser
import datetime,shutil,random,zipfile,re
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask,LoadTask,DoTaskClean
from appli.database import GetAll
import appli.project.main
from appli.tasks.importcommon import *
from appli.tasks.vignettemaker import MakeVignette

class TaskImport(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.InData='My In Data'
                self.ProjectId=None
                self.SkipAlreadyLoadedFile="N" # permet de dire si on
                self.SkipObjectDuplicate="N"
                # self.Mapping={x:{} for x in PredefinedTables}
                self.Mapping={}
                self.TaxoMap={}


    def __init__(self,task=None):
        super().__init__(task)
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)
        self.seqcache={}

    def GetSequenceCached(self,SequenceName):
        if SequenceName not in self.seqcache:
            self.seqcache[SequenceName]={'tbl':[],'next':0}
        if self.seqcache[SequenceName]['next']>=len(self.seqcache[SequenceName]['tbl']):
            self.pgcur.execute("select nextval('%s') FROM generate_series(1,100)"%SequenceName)
            self.seqcache[SequenceName]['tbl']=[x[0] for x in self.pgcur.fetchall()]
            self.seqcache[SequenceName]['next']=0
        ret=self.seqcache[SequenceName]['tbl'][self.seqcache[SequenceName]['next']]
        self.seqcache[SequenceName]['next']+=1
        return ret

    def SPCommon(self):
        logging.info("Execute SPCommon")
        self.pgcur=db.engine.raw_connection().cursor()


    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__))
        logging.info("Start Step 1")
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        LoadedFiles=ntcv(Prj.fileloaded).splitlines()
        logging.info("LoadedFiles = %s",LoadedFiles)
        WarnMessages=[]
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
            for k,v in DecodeEqualList(Prj.mappingobj).items():
                self.param.Mapping['object_'+v]={'table': 'obj_field', 'title': v, 'type': k[0], 'field': k}
            for k,v in DecodeEqualList(Prj.mappingsample).items():
                self.param.Mapping['sample_'+v]={'table': 'sample', 'title': v, 'type': k[0], 'field': k}
            for k,v in DecodeEqualList(Prj.mappingacq).items():
                self.param.Mapping['acq_'+v]={'table': 'acq', 'title': v, 'type': k[0], 'field': k}
            for k,v in DecodeEqualList(Prj.mappingprocess).items():
                self.param.Mapping['process_'+v]={'table': 'process', 'title': v, 'type': k[0], 'field': k}
            ProjectWasEmpty=len(self.param.Mapping)==0
            self.param.TaxoFound={} # Reset à chaque Tentative
            self.param.UserFound={} # Reset à chaque Tentative
            self.param.steperrors=[] # Reset des erreurs
            # recuperation de toutes les paire objet/Images du projet
            self.ExistingObjectAndImage = set()
            self.pgcur.execute(
                "SELECT concat(o.orig_id,'*',i.orig_file_name) from images i join objects o on i.objid=o.objid where o.projid=" + str(
                    self.param.ProjectId))
            for rec in self.pgcur:
                self.ExistingObjectAndImage.add(rec[0])
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
            Seen=set() # Memorise les champs pour lesquels il y a des valeurs
            ClassifIDSeen = set()
            NbrObjectWithoutGPS=0
            for filter in ("**/ecotaxa*.txt","**/ecotaxa*.tsv","**/*Images.zip"):
                for CsvFile in sd.glob(filter):
                    relname=CsvFile.relative_to(sd) # Nom relatif à des fins d'affichage uniquement
                    if relname.as_posix() in LoadedFiles and self.param.SkipAlreadyLoadedFile=='Y':
                        logging.info("File %s skipped, already loaded"%(relname.as_posix()))
                        continue
                    logging.info("Analyzing file %s"%(relname.as_posix()))
                    if relname.name.endswith("Images.zip"): # c'est un format compressé par UVPAPP, chaque sample est dans un.zip
                        SampleDir=Path(self.GetWorkingDir()) / relname.stem
                        SampleCSV=SampleDir/("ecotaxa_"+relname.stem[:-7]+".tsv")
                        if SampleDir.exists():
                            if not SampleCSV.exists(): # dezipage incorrect
                                # SampleDir.rmdir() # on détruit le repertoire et on redezippe
                                shutil.rmtree(SampleDir.as_posix())
                        if not SampleDir.exists():
                            SampleDir.mkdir()
                            with zipfile.ZipFile(CsvFile.as_posix(), 'r') as z:
                                z.extractall(SampleDir.as_posix())
                        CsvFile=SampleCSV

                    with open(CsvFile.as_posix(),encoding='latin_1') as csvfile:
                        # lecture en mode dictionnaire basé sur la premiere ligne
                        rdr = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
                        #lecture la la ligne des types (2nd ligne du fichier
                        LType={champ.strip(" \t").lower():v for champ,v in rdr.__next__().items()}
                        # Fabrication du mapping
                        ListeChamps=[champ.strip(" \t").lower() for champ in rdr.fieldnames]
                        for ColName in ListeChamps:
                            if ColName in self.param.Mapping:
                                continue # Le champ à déjà été détecté
                            ColSplitted=ColName.split("_",1)
                            if len(ColSplitted)!=2:
                                self.LogErrorForUser("Invalid Header '%s' in file %s. Format must be Table_Field. Field ignored"%(ColName,relname.as_posix()))
                                continue
                            Table=ColSplitted[0] # On isole la partie table avant le premier _
                            if ColName in PredefinedFields:
                                Table=PredefinedFields[ColName]['table']
                                self.param.Mapping[ColName]=PredefinedFields[ColName]
                            else: # champs non predefinis donc dans nXX ou tXX
                                if Table=="object":
                                    Table="obj_field"
                                if not Table in PredefinedTables:
                                    self.LogErrorForUser("Invalid Header '%s' in file %s. Table Incorrect. Field ignored"%(ColName,relname.as_posix()))
                                    continue
                                if Table!='obj_head' and Table!='obj_field': # Dans les autres tables les types sont forcés à texte
                                    SelType='t'
                                else:
                                    if LType[ColName] not in PredefinedTypes:
                                        self.LogErrorForUser("Invalid Type '%s' for Field '%s' in file %s. Incorrect Type. Field ignored"
                                                             %(LType[ColName],ColName,relname.as_posix()))
                                        continue
                                    SelType=PredefinedTypes[LType[ColName]]
                                self.LastNum[Table][SelType]+=1
                                self.param.Mapping[ColName]={'table':Table,'field':SelType+"%02d"%self.LastNum[Table][SelType],'type':SelType,'title':ColSplitted[1]}
                                logging.info("New field %s found in file %s",ColName,relname.as_posix())
                                if not ProjectWasEmpty:
                                    WarnMessages.append("New field %s found in file %s"%(ColName,relname.as_posix()))
                        # Test du contenu du fichier
                        RowCount=0
                        for lig in rdr:
                            RowCount+=1
                            latitudeseen=False
                            for champ in rdr.fieldnames:
                                ColName = champ.strip(" \t").lower()
                                m=self.param.Mapping.get(ColName,None)
                                if m is None:
                                    continue # Le champ n'est pas considéré
                                v=CleanValue(lig[champ])
                                Seen.add(ColName) # V1.1 si la colonne est présente c'est considéré Seen, avant il fallait avoir vu une valeur.
                                if v!="": # si pas de valeurs, pas de controle
                                    if ColName == 'object_lat':
                                        latitudeseen = True
                                        vf=ConvTextDegreeToDecimalDegree(v)
                                        if vf < -90 or vf > 90:
                                            self.LogErrorForUser(
                                                "Invalid Lat. value '%s' for Field '%s' in file %s. Incorrect range -90/+90°." % (v, champ, relname.as_posix()))
                                    elif ColName == 'object_lon':
                                        vf = ConvTextDegreeToDecimalDegree(v)
                                        if vf < -180 or vf > 180:
                                            self.LogErrorForUser("Invalid Long. value '%s' for Field '%s' in file %s. Incorrect range -180/+180°." % (
                                            v, champ, relname.as_posix()))

                                    elif m['type']=='n':
                                        vf=ToFloat(v)
                                        if vf is None:
                                            self.LogErrorForUser("Invalid float value '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))

                                        elif ColName=='object_annotation_category_id':
                                            ClassifIDSeen.add(int(v))
                                    elif ColName=='object_date':
                                        try:
                                            datetime.date(int(v[0:4]), int(v[4:6]), int(v[6:8]))
                                        except ValueError:
                                            self.LogErrorForUser("Invalid Date value '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))
                                    elif ColName=='object_time':
                                        try:
                                            v=v.zfill(6)
                                            datetime.time(int(v[0:2]), int(v[2:4]), int(v[4:6]))
                                        except ValueError:
                                            self.LogErrorForUser("Invalid Time value '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))
                                    elif ColName=='object_annotation_category':
                                        if CleanValue(lig.get('object_annotation_category_id',''))=='': # traité que si un ID numérique non spécifié
                                            v=self.param.TaxoMap.get(v.lower(),v) # Applique le mapping
                                            self.param.TaxoFound[v.lower()]=None #creation d'une entrée dans le dictionnaire.
                                    elif ColName=='object_annotation_person_name':
                                        self.param.UserFound[v.lower()]={'email':CleanValue(lig.get('object_annotation_person_email',''))}
                                    elif ColName=='object_annotation_status':
                                        if v!='noid' and v.lower() not in database.ClassifQualRevert:
                                            self.LogErrorForUser("Invalid Annotation Status '%s' for Field '%s' in file %s."%(v,champ,relname.as_posix()))
                            if latitudeseen==False:
                                NbrObjectWithoutGPS+=1
                            #Analyse l'existance du fichier Image
                            ObjectId=CleanValue(lig.get('object_id',''))
                            if ObjectId=='':
                                self.LogErrorForUser("Missing object_id on line '%s' in file %s. "%(RowCount,relname.as_posix()))
                            ImgFileName=CleanValue(lig.get('img_file_name','MissingField img_file_name'))
                            ImgFilePath=CsvFile.parent/ImgFileName
                            if not ImgFilePath.exists():
                                self.LogErrorForUser("Missing Image '%s' in file %s. "%(ImgFileName,relname.as_posix()))
                            else:
                                try:
                                    im=Image.open(ImgFilePath.as_posix())
                                except:
                                    self.LogErrorForUser("Error while reading Image '%s' in file %s. %s"%(ImgFileName,relname.as_posix(),sys.exc_info()[0]))
                            CleExistObj=ObjectId+'*'+ImgFileName
                            if self.param.SkipObjectDuplicate!='Y' and CleExistObj in self.ExistingObjectAndImage:
                                self.LogErrorForUser("Duplicate object %s Image '%s' in file %s. "%(ObjectId,ImgFileName,relname.as_posix()))
                            self.ExistingObjectAndImage.add(CleExistObj)
                        logging.info("File %s : %d row analysed",relname.as_posix(),RowCount)
                        self.param.TotalRowCount+=RowCount
            if self.param.TotalRowCount==0:
                self.LogErrorForUser("No object to import. It maybe due to :<br>*	Empty TSV table<br>* TSV table already imported => 'SKIP TSV' option should be enabled")
            # print(self.param.Mapping)
            if len(ClassifIDSeen)>0:
                ClassifIDFoundInDB=GetAll("select id from taxonomy where id = any (%s)",[list(ClassifIDSeen)])
                ClassifIDFoundInDB={int(r['id']) for r in ClassifIDFoundInDB}
                ClassifIDNotFoundInDB=ClassifIDSeen.difference(ClassifIDFoundInDB)
                if len(ClassifIDNotFoundInDB)>0:
                    msg="Some specified classif_id doesn't exists, correct them prior to reload %s"%(",".join([str(x) for x in ClassifIDNotFoundInDB]))
                    self.param.steperrors.append(msg)
                    logging.error(msg)
            self.UpdateProgress(15,"TSV File Parsed"%())

            logging.info("Taxo Found = %s",self.param.TaxoFound)
            logging.info("Users Found = %s",self.param.UserFound)
            NotSeenField=[k for k in self.param.Mapping if k not in Seen]
            logging.info("For Information Not Seen Fields %s",NotSeenField)
            if len(NotSeenField)>0:
                WarnMessages.append("Some fields configured in the project are not seen in this import {0} ".format(", ".join(NotSeenField)))
            if NbrObjectWithoutGPS>0:
                WarnMessages.append("{0} objects doesn't have GPS information  ".format(NbrObjectWithoutGPS))
            if len(self.param.steperrors)>0:
                self.task.taskstate="Error"
                self.task.progressmsg="Some errors founds during file parsing "
                logging.error(self.task.progressmsg)
                db.session.commit()
                return
            self.param.IntraStep=2
        if self.param.IntraStep==2:
            logging.info("Start Sub Step 1.2")
            self.pgcur.execute("select id,lower(name),lower(email) from users where lower(name) = any(%s) or email= any(%s) ",([x for x in self.param.UserFound.keys()],[x.get('email') for x in self.param.UserFound.values()]))
            # Résolution des noms à partir du nom ou de l'email
            for rec in self.pgcur:
                for u in self.param.UserFound:
                    if u==rec[1] or ntcv(self.param.UserFound[u].get('email')).lower()==rec[2]:
                        self.param.UserFound[u]['id']=rec[0]
            logging.info("Users Found = %s",self.param.UserFound)
            NotFoundUser=[k for k,v in self.param.UserFound.items() if v.get("id")==None]
            if len(NotFoundUser)>0:
                logging.info("Some Users Not Found = %s",NotFoundUser)
            # récuperation des ID des taxo trouvées
            NotFoundTaxo=[]
            ResolveTaxoFound(self.param.TaxoFound, NotFoundTaxo)
            if len(NotFoundTaxo)>0:
                logging.info("Some Taxo Not Found = %s",NotFoundTaxo)
            # raise Exception("TEST")
            if len(NotFoundUser)==0 and len(NotFoundTaxo)==0 and len(WarnMessages)==0: # si tout est déjà résolue on enchaine sur la phase 2
                self.SPStep2()
            else:
                self.task.taskstate="Question"
            if len(WarnMessages)>0:
                self.UpdateProgress(20,"Taxo automatic resolution Done, <span style='color:red;font-weight:bold;'>Some Warning :\n-%s </span>"%("\n-".join(WarnMessages)))
            else:
                self.UpdateProgress(20,"Taxo automatic resolution Done"%())
            #sinon on pose une question

    def SPStep2(self):
        # raise Exception("TEST")
        logging.info("Start Step 2 : Effective data import")
        logging.info("Taxo Mapping = %s",self.param.TaxoFound)
        logging.info("Users Mapping = %s",self.param.UserFound)
        AstralCache={'date':None,'time':None,'long':None,'lat':None,'r':''}
        WorkingDirCache=self.GetWorkingDir() # sans ça, ça rafraichi l'objet Task par une requete à chaque fois
        # Mise à jour du mapping en base
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        LoadedFiles=ntcv(Prj.fileloaded).splitlines()
        logging.info("LoadedFiles = %s",LoadedFiles)
        Prj.mappingobj=EncodeEqualList({v['field']:v.get('title') for k,v in self.param.Mapping.items() if v['table']=='obj_field' and v['field'][0]in ('t','n') and v.get('title')!=None})
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
        self.pgcur.execute("SELECT o.orig_id,o.objid from objects o where o.projid="+str(self.param.ProjectId))
        for rec in self.pgcur:
            self.ExistingObject[rec[0]]=rec[1]
        # recuperation de toutes les paire objet/Images du projet
        self.ExistingObjectAndImage = set()
        if self.param.SkipObjectDuplicate == 'Y': # cette liste n'est necessaire qui si on ignore les doublons
            self.pgcur.execute(  # et doit être recahrgée depuis la base, car la phase 1 y a ajouté tous les objets pour le contrôle des doublons
                "SELECT concat(o.orig_id,'*',i.orig_file_name) from images i join objects o on i.objid=o.objid where o.projid=" + str(
                    self.param.ProjectId))
            for rec in self.pgcur:
                self.ExistingObjectAndImage.add(rec[0])
        #logging.info("Ids = %s",Ids)
        random.seed()
        sd=Path(self.param.SourceDir)
        TotalRowCount=0
        for filter in ("**/ecotaxa*.txt","**/ecotaxa*.tsv","**/*Images.zip"):
            for CsvFile in sd.glob(filter):
                relname=CsvFile.relative_to(sd) # Nom relatif à des fins d'affichage uniquement
                if relname.as_posix() in LoadedFiles and self.param.SkipAlreadyLoadedFile=='Y':
                    logging.info("File %s skipped, already loaded"%(relname.as_posix()))
                    continue
                logging.info("Analyzing file %s"%(relname.as_posix()))
                if relname.name.endswith("Images.zip"):  # c'est un format compressé par UVPAPP, chaque sample est dans un.zip, qui à été décompressé si necessaire lors de l'analyse
                    CsvFile = Path(WorkingDirCache) / relname.stem / ("ecotaxa_" + relname.stem[:-7] + ".tsv")

                VignetteMakerCfg = None
                VignetteMakerCfgkeeporiginal = False
                # if (sd / "config" / "compute_vignette.txt").exists(): # Celui qui est dans config ne contient pas le pixel size
                if (CsvFile.parent / "compute_vignette.txt").exists(): # on prend plutot celui qui est dans chaque sample en plus ça permettrai de marcher en envoyant un ensemble de zip
                    VignetteMakerCfg = configparser.ConfigParser()
                    VignetteMakerCfg.read((CsvFile.parent / "compute_vignette.txt").as_posix())
                    VignetteMakerCfgkeeporiginal = VignetteMakerCfg['vignette'].get('keeporiginal', 'n').lower() == 'y'

                with open(CsvFile.as_posix(),encoding='latin_1') as csvfile:
                    # lecture en mode dictionnaire basé sur la premiere ligne
                    rdr = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
                    #lecture la la ligne des types (2nd ligne du fichier
                    LType = {champ.strip(" \t").lower(): v for champ, v in rdr.__next__().items()}
                    ListeChamps = [champ.strip(" \t").lower() for champ in rdr.fieldnames]
                    # Chargement du contenu du fichier
                    RowCount=0
                    for rawlig in rdr:
                        lig={champ.strip(" \t").lower():v for champ,v in rawlig.items()}
                        Objs={"acq":database.Acquisitions(),"sample":database.Samples(),"process":database.Process()
                            ,"obj_head":database.Objects(),"obj_field":database.ObjectsFields(),"image":database.Images()}
                        RowCount+=1
                        TotalRowCount+=1
                        if 'object_annotation_category_id' in ListeChamps and 'object_annotation_category' in ListeChamps :
                            if CleanValue(lig.get('object_annotation_category_id', '')) != '':
                                del lig['object_annotation_category'] # s'il y a un ID on ignore le texte
                        for champ in ListeChamps:
                            m=self.param.Mapping.get(champ,None)
                            if m is None:
                                continue  # Le champ n'est pas considéré
                            FieldName=m.get("field",None)
                            FieldTable=m.get("table",None)
                            FieldValue=None
                            v=CleanValue(lig.get(champ))
                            if v!="": # si pas de valeurs, on laisse le champ null
                                if champ == 'object_lat': # c'est des type N mais depuis AVPApp ils peuvent contenir une notation avec des ddd°MM.SS
                                    FieldValue = ConvTextDegreeToDecimalDegree(v)
                                elif champ == 'object_lon':
                                    FieldValue = ConvTextDegreeToDecimalDegree(v)
                                elif m['type']=='n':
                                    FieldValue=ToFloat(v)
                                elif champ=='object_date':
                                    FieldValue=datetime.date(int(v[0:4]), int(v[4:6]), int(v[6:8]))
                                elif champ=='object_time':
                                        v=v.zfill(6)
                                        FieldValue=datetime.time(int(v[0:2]), int(v[2:4]), int(v[4:6]))
                                elif FieldName=='classif_when':
                                    v2=CleanValue(lig.get('object_annotation_time','000000')).zfill(6)
                                    FieldValue=datetime.datetime(int(v[0:4]), int(v[4:6]), int(v[6:8]),int(v2[0:2]), int(v2[2:4]), int(v2[4:6]))
                                elif FieldName=='classif_id': # pour la version numerique, c'est traité par if type=n
                                    v=self.param.TaxoMap.get(v.lower(),v) # Applique le mapping initial d'entrée
                                    FieldValue=self.param.TaxoFound[ntcv(v).lower()]
                                elif FieldName=='classif_who':
                                    FieldValue=self.param.UserFound[ntcv(v).lower()].get('id',None)
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
                        # Calcul de la position du soleil
                        if not (AstralCache['date']==Objs["obj_head"].objdate and AstralCache['time']==Objs["obj_head"].objtime \
                            and AstralCache['long']==Objs["obj_head"].longitude and AstralCache['lat']==Objs["obj_head"].latitude) :
                            AstralCache = {'date': Objs["obj_head"].objdate, 'time': Objs["obj_head"].objtime
                                , 'long': Objs["obj_head"].longitude, 'lat': Objs["obj_head"].latitude, 'r': ''}
                            from astral import AstralError
                            try:
                                AstralCache['r'] = appli.CalcAstralDayTime(AstralCache['date'], AstralCache['time'], AstralCache['lat'], AstralCache['long'])
                            except AstralError as e: # dans certains endoit du globe il n'y a jamais de changement nuit/jour certains jours, ca provoque une erreur
                                app.logger.error("Astral error : %s for %s", e,AstralCache)
                            except Exception as e:   # autre erreurs par exemple si l'heure n'est pas valide;
                                app.logger.error("Astral error : %s for %s", e, AstralCache)
                        Objs["obj_head"].sunpos = AstralCache['r']
                        # Affectation des ID Sample, Acq & Process et creation de ces dernier si necessaire
                        for t in Ids:
                            if Objs[t].orig_id is not None:
                                if Objs[t].orig_id in Ids[t]["ID"]:
                                    setattr(Objs["obj_head"],Ids[t]["pk"],Ids[t]["ID"][Objs[t].orig_id])
                                else:
                                    Objs[t].projid=self.param.ProjectId
                                    db.session.add(Objs[t])
                                    db.session.commit()
                                    Ids[t]["ID"][Objs[t].orig_id]=getattr(Objs[t],Ids[t]["pk"])
                                    setattr(Objs["obj_head"],Ids[t]["pk"],Ids[t]["ID"][Objs[t].orig_id])
                                    logging.info("IDS %s %s",t,Ids[t])
                        # self.pgcur.execute("select nextval('seq_images')" )
                        # Objs["image"].imgid=self.pgcur.fetchone()[0]
                        Objs["image"].imgid=self.GetSequenceCached('seq_images')
                        CleExistObj = Objs["obj_field"].orig_id + '*' + Objs["image"].orig_file_name
                        if self.param.SkipObjectDuplicate == 'Y' and CleExistObj in self.ExistingObjectAndImage:
                            continue
                        # Recherche de l'objet si c'est une images complementaire
                        if Objs["obj_field"].orig_id in self.ExistingObject:
                            Objs["obj_head"].objid=self.ExistingObject[Objs["obj_field"].orig_id]
                        else: # ou Creation de l'objet
                            Objs["obj_head"].projid=self.param.ProjectId
                            Objs["obj_head"].random_value=random.randint(1,99999999)
                            Objs["obj_head"].img0id=Objs["image"].imgid
                            db.session.add(Objs["obj_head"])
                            db.session.commit()
                            Objs["obj_field"].objfid=Objs["obj_head"].objid
                            db.session.add(Objs["obj_field"])
                            # db.session.commit() ce commit intermediaire n'est pas necessaire
                            self.ExistingObject[Objs["obj_field"].orig_id]=Objs["obj_head"].objid # Provoque un select object sauf si 'expire_on_commit':False
                        #Gestion de l'image, creation DB et fichier dans Vault
                        Objs["image"].objid=Objs["obj_head"].objid
                        ImgFilePath = OriginalImgFilePath = CsvFile.parent / Objs["image"].orig_file_name
                        if VignetteMakerCfg:
                            ImgFilePath = Path(WorkingDirCache) / "tempvignette.png"
                            MakeVignette(OriginalImgFilePath.as_posix(),ImgFilePath.as_posix(),VignetteMakerCfg)

                        VaultFolder="%04d"%(Objs["image"].imgid//10000)
                        vaultroot=Path("../../vault")
                        #creation du repertoire contenant les images si necessaire
                        CreateDirConcurrentlyIfNeeded(vaultroot.joinpath(VaultFolder))
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
                                if im.mode=='P':
                                    im=im.convert("RGB")
                                im.save(vaultroot.joinpath(vaultfilenameThumb).as_posix())
                                Objs["image"].thumb_file_name=vaultfilenameThumb
                                Objs["image"].thumb_width=im.size[0]
                                Objs["image"].thumb_height=im.size[1]
                        del im
                        #ajoute de l'image en DB
                        if Objs["image"].imgrank is None:
                            Objs["image"].imgrank =0 # valeur par defaut
                        db.session.add(Objs["image"])
                        if VignetteMakerCfgkeeporiginal: # si creation de vignette et qu'on garde l'original on va créer une seconde image pour l'y mettre
                            Objs["image2"]=database.Images()
                            # self.pgcur.execute("select nextval('seq_images')")
                            # Objs["image2"].imgid = self.pgcur.fetchone()[0]
                            Objs["image2"].imgid = self.GetSequenceCached('seq_images')
                            Objs["image2"].imgrank=100
                            Objs["image2"].objid = Objs["obj_head"].objid
                            vaultfilename = "%s/%04d%s" % (VaultFolder, Objs["image2"].imgid % 10000, OriginalImgFilePath.suffix)
                            Objs["image2"].file_name=vaultfilename
                            shutil.copyfile(OriginalImgFilePath.as_posix(),vaultroot.joinpath(vaultfilename).as_posix())
                            im=Image.open(vaultroot.joinpath(vaultfilename).as_posix())
                            Objs["image2"].width,Objs["image2"].height=im.size
                            del im
                            db.session.add(Objs["image2"])
                        db.session.commit()
                        if (TotalRowCount%100)==0:
                            self.UpdateProgress(100*TotalRowCount/self.param.TotalRowCount,"Processing files %d/%d"%(TotalRowCount,self.param.TotalRowCount))
                    logging.info("File %s : %d row Loaded",relname.as_posix(),RowCount)
                    LoadedFiles.append(relname.as_posix())
                    Prj.fileloaded="\n".join(LoadedFiles)
                    db.session.commit()
        # Delete all temporary subfolder of  WorkingDirCache
        for d in [os.path.join(WorkingDirCache, o) for o in os.listdir(WorkingDirCache) if os.path.isdir(os.path.join(WorkingDirCache, o))]:
            try:
                shutil.rmtree(d)
            except: # c'est un menage préalable pas grave s'il y a une erreur
                pass
        self.pgcur.execute("""update obj_head o
                            set imgcount=(select count(*) from images where objid=o.objid)
                            ,img0id=(select imgid from images where objid=o.objid order by imgrank asc limit 1 )
                            where projid="""+str(self.param.ProjectId))
        self.pgcur.connection.commit()
        self.pgcur.execute("""update samples s set latitude=sll.latitude,longitude=sll.longitude
              from (select o.sampleid,min(o.latitude) latitude,min(o.longitude) longitude
              from obj_head o
              where projid=%(projid)s and o.latitude is not null and o.longitude is not null
              group by o.sampleid) sll where s.sampleid=sll.sampleid and projid=%(projid)s """,{'projid':self.param.ProjectId})
        self.pgcur.connection.commit()
        appli.project.main.RecalcProjectTaxoStat(Prj.projid)
        appli.project.main.UpdateProjectStat(Prj.projid)

        self.task.taskstate="Done"
        self.UpdateProgress(100,"Processing done")

    def QuestionProcess(self):
        ServerRoot=Path(app.config['SERVERLOADAREA'])
        txt="<h1>Text File Importation Task</h1>"
        errors=[]
        if self.task.taskstep==0:
            txt+="<h3>Task Creation</h3>"
            Prj=database.Projects.query.filter_by(projid=gvg("p")).first()
            g.prjtitle=Prj.title
            g.prjprojid = Prj.projid
            g.prjmanagermailto=Prj.GetFirstManagerMailto()
            txt=""
            if Prj.CheckRight(1)==False:
                return PrintInCharte("ACCESS DENIED for this project");
            g.appmanagermailto=GetAppManagerMailto()

            if gvp('starttask')=="Y":
                FileToSave=None
                FileToSaveFileName=None
                self.param.ProjectId=gvg("p")
                self.param.SkipAlreadyLoadedFile=gvp("skiploaded")
                self.param.SkipObjectDuplicate = gvp("skipobjectduplicate")
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
            PrjId=self.param.ProjectId
            Prj=database.Projects.query.filter_by(projid=PrjId).first()
            g.prjtitle=Prj.title
            g.prjprojid = Prj.projid
            g.appmanagermailto=GetAppManagerMailto()
            # self.param.TaxoFound['agreia pratensis']=None #Pour TEST A EFFACER
            NotFoundTaxo=[k for k,v in self.param.TaxoFound.items() if v is None]
            NotFoundUsers=[k for k,v in self.param.UserFound.items() if v.get('id') is None]
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
            return render_template('task/import_question1.html',header=txt,taxo=NotFoundTaxo,users=NotFoundUsers,task=self.task)
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
        time.sleep(1)
        DoTaskClean(self.task.id)
        return """<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>
        <a href='/Task/Create/TaskClassifAuto?p={0}' class='btn btn-primary btn-sm'  role=button>Go to Automatic Classification Screen</a> """.format(PrjId)
