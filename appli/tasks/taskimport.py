# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp
from PIL import Image
from flask import Blueprint, render_template, g, flash,request
from io import StringIO
import html,functools,logging,json,time,os,csv
import datetime,shutil,random
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask,LoadTask
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


PredefinedTables=['object','sample','process','acq']
PredefinedTypes={'[float]':'n','[int]':'n','[text]':'t'}
PredefinedFields={
    'object_id':{'table':'object','field':'orig_id','type':'t'},
    'sample_id':{'table':'sample','field':'orig_id','type':'t'},
    'acq_id':{'table':'acq','field':'orig_id','type':'t'},
    'process_id':{'table':'process','field':'orig_id','type':'t'},
    'object_lat':{'table':'object','field':'latitude','type':'n'},
    'object_lon':{'table':'object','field':'longitude','type':'n'},
    'object_date':{'table':'object','field':'objdate','type':'t'},
    'object_time':{'table':'object','field':'objtime','type':'t'},
    'object_depth_min':{'table':'object','field':'depth_min','type':'n'},
    'object_depth_max':{'table':'object','field':'depth_max','type':'n'},
    'annotation_name':{'table':'object','field':'tmp_annotname','type':'t'},
    'annotation_email':{'table':'object','field':'tmp_annotemail','type':'t'},
    'annotation_date':{'table':'object','field':'tmp_annotdate','type':'t'},
    'annotation_time':{'table':'object','field':'tmp_annottime','type':'t'},
    'annotation_person_last_name':{'table':'object','field':'tmp_annotauthor','type':'t'},
    'annotation_status':{'table':'object','field':'classif_qual','type':'t'},
    'img_rank':{'table':'image','field':'imgrank','type':'n'},
    'img_file_name':{'table':'image','field':'tmp_file','type':'t'},
    'annotation_person_first_name':{'table':'object','field':'tmp_todelete1','type':'t'},
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
                self.ProjectId=1
                # self.Mapping={x:{} for x in PredefinedTables}
                self.Mapping={}
                self.TaxoMap={}

    def __init__(self,task=None):
        super().__init__(task)
        if task==None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def LogErrorForUser(self,Msg):
        # On ne trace dans les 2 zones ques les milles premieres erreurs.
        if len(self.param.steperrors)<1000:
            self.param.steperrors.append(Msg)
            logging.warning("%s",Msg)
        elif len(self.param.steperrors)==1000:
            self.param.steperrors.append("More errors truncated")
            logging.warning("More errors truncated")
    def SPCommon(self):
        logging.info("Execute SPCommon")
        self.pgcur=db.engine.raw_connection().cursor()

    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__))
        logging.info("Start Step 1")
        if getattr(self.param,'IntraStep',0)==0:
            #Sous tache 1 Copie
            if self.param.InData.lower().endswith("zip"):
                logging.info("SubTask1 : TODO Unzip File on temporary folder")
                #TODO penser à renseigner self.param.SourceDir
            else:
                self.param.SourceDir=self.param.InData
            self.param.IntraStep=1

        if self.param.IntraStep==1:
            self.param.Mapping={} # Reset à chaque Tentative
            self.param.TaxoFound={} # Reset à chaque Tentative
            self.param.UserFound={} # Reset à chaque Tentative
            self.param.steperrors=[] # Reset des erreurs
            # recuperation de toutes les paire objet/Images du projet
            self.ExistingObject=set()
            self.pgcur.execute(
                "SELECT concat(o.orig_id,'*',i.file_name) from images i join objects o on i.objid=o.objid where o.projid=1")
            for rec in self.pgcur:
                self.ExistingObject.add(r[0])
            logging.info("SubTask1 : Analyze CSV Files")
            #Todo importer le mapping existant pour le completer
            self.LastNum={x:{'n':0,'t':0} for x in PredefinedTables}
            #Todo extraire les max du mapping existant.
            sd=Path(self.param.SourceDir)
            for CsvFile in sd.glob("**/*.csv"):
                relname=CsvFile.relative_to(sd) # Nom relatif à des fins d'affichage uniquement
                logging.info("Analyzing file %s"%(relname.as_posix()))
                with open(CsvFile.as_posix()) as csvfile:
                    # lecture en mode dictionnaire basé sur la premiere ligne
                    rdr = csv.DictReader(csvfile, delimiter=';', quotechar='"')
                    #lecture la la ligne des types (2nd ligne du fichier
                    LType=rdr.__next__()
                    # Fabrication du mapping
                    for champ in rdr.fieldnames:
                        if champ in self.param.Mapping:
                            continue # Le champ à déjà été détecté
                        ColName=champ.strip(" .\t").lower()
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
                                if m.get('Seen',None)==None: #marque si on a vu au moins une valeur.
                                    self.param.Mapping[champ]["Seen"]=True
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
                                elif champ=='annotation_name':
                                    v=self.param.TaxoMap.get(v,v) # Applique le mapping
                                    self.param.TaxoFound[v]=None #creation d'une entrée dans le dictionnaire.
                                elif champ=='annotation_person_last_name':
                                    self.param.UserFound[v]={'email':CleanValue(lig.get('annotation_email',''))}

                        #Analyse l'existance du fichier Image
                        ObjectId=CleanValue(lig.get('object_id',''))
                        if ObjectId=='':
                            self.LogErrorForUser("Missing ObjectId on line '%s' in file %s. Incorrect Type. Field ignored"%(RowCount,relname.as_posix()))
                        ImgFileName=CleanValue(lig.get('img_file_name','MissingField img_file_name'))
                        ImgFilePath=CsvFile.with_name(ImgFileName)
                        if not ImgFilePath.exists():
                            self.LogErrorForUser("Missing Image '%s' in file %s. Incorrect Type. Field ignored"%(ImgFileName,relname.as_posix()))
                        CleExistObj=ObjectId+'*'+ImgFileName
                        if CleExistObj in self.ExistingObject:
                            self.LogErrorForUser("Duplicate object %s Image '%s' in file %s. Incorrect Type. Field ignored"%(ImgFileName,relname.as_posix()))
                        self.ExistingObject.add(CleExistObj)
                    logging.info("File %s : %d row analysed",relname.as_posix(),RowCount)

            self.UpdateProgress(15,"CSV File Parsed"%())
            print(self.param.Mapping)
            logging.info("Taxo Found = %s",self.param.TaxoFound)
            logging.info("Users Found = %s",self.param.UserFound)
            logging.info("For Information Not Seen Fields %s",
                         [k for k,v in self.param.Mapping.items() if not v.get('Seen')])
            self.param.IntraStep=2
            #TODO Compter le Nbr de fichier pour ProgressBar plus tard, Verifier >0
        if self.param.IntraStep==2:
            logging.info("Start Sub Step 1.2")
            logging.info("Users Found = %s",self.param.UserFound)
            #todo Resoudre les Nom
            # récuperation des ID des taxo trouvées
            self.pgcur.execute("select id,name from taxonomy where name = any(%s) ",([x for x in self.param.TaxoFound.keys()],))
            for rec in self.pgcur:
                self.param.TaxoFound[rec[1]]=rec[0]
            logging.info("Taxo Found = %s",self.param.TaxoFound)
            self.param.TaxoFound['agreia pratensis']=None #todo Pour TEST A EFFACER
            NotFoundTaxo=[k for k,v in self.param.TaxoFound.items() if v==None]
            if len(NotFoundTaxo)>0:
                logging.info("Some Taxo Not Found = %s",NotFoundTaxo)
            self.task.taskstate="Question"
            self.UpdateProgress(20,"Taxo automatic resolution Done"%())
            #Recherche des valeurs dans la Taxo
            #Remplissage du dico avec ce qui existe
            #Essayer de resoudre les Noms
            #s'il reste des choses à résoudre Faire une Question Phase 1
            #Sinon Basculer Auto en Step 2


    def SPStep2(self):
        logging.info("Start Step 2 : Effective data import")
        logging.info("Taxo Mapping = %s",self.param.TaxoFound)
        logging.info("Users Mapping = %s",self.param.UserFound)


        # for i in range(20,100,20):
        #     time.sleep(0.1)
        #     self.UpdateProgress(i,"My Step 2 Message %d"%(i))
        # logging.info("End Step 2")
        # raise Exception("A Finir")


    def QuestionProcess(self):
        txt="<h1>Text File Importation Task</h1>"
        errors=[]
        if self.task.taskstep==0:
            txt+="<h3>Task Creation</h3>"
            if gvp('starttask')=="Y":
                for k,v  in self.param.__dict__.items():
                    setattr(self.param,k,gvp(k))
                TaxoMap={}
                for l in gvp('TaxoMap').splitlines():
                    ls=l.split('=',1)
                    if len(ls)!=2:
                        errors.append("Taxonomy Mapping : Invalid format for line %s"%(l))
                    TaxoMap[ls[0].strip().lower()]=ls[1].strip().lower()
                # Verifier la coherence des données
                #TODO verifier que le repertoire existe
                #TODO traiter l'import d'un fichier par HTTP
                #TODO verifier les droits sur le projet.
                #TODO Passer le projet en données entrante + Hidden
                if len(self.param.InData)<5:
                    errors.append("Input Folder/File Too Short")
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else:
                    self.param.TaxoMap=TaxoMap # on stocke le dictionnaire et pas la chaine
                    return self.StartTask(self.param)
            return render_template('task/import_create.html',header=txt,data=self.param)
        if self.task.taskstep==1:
            self.param.TaxoFound['agreia pratensis']=None #todo Pour TEST A EFFACER
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

MappingObj= {'object_id':'orig_id',
'object_lat':'latitude ',
'object_lon':'longitude ',
'object_date':'objdate',
'object_time':'objtime',
'object_depth_min':'depth_min',
'object_depth_max':'depth_max',
'object_lat_end':'n01',
'object_lon_end':'n02',
'object_bx':'n03',
'object_by':'n04',
'object_width':'n05',
'object_height':'n06',
'object_area':'n07',
'object_mean':'n08',
'object_major':'n09',
'object_minor':'n10',
'object_feret':'n11',
'object_area_exc':'n12',
'object_thickr':'n13' }
directory=R"D:\dev\_Client\LOV\EcoTaxa\TestData\Zooscan_ptb_jb_2014_pelagos\ecotaxa\jb2014112_tot_1"
fichier=R"ecotaxa_jb2014112_tot_1_dat1_validated.csv"

def LoadHeader():
    NomFichier=os.path.join(directory,fichier)
    print("NomFichier="+NomFichier)
    import csv
    with open(NomFichier) as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        cols=next(reader)
        reader = csv.DictReader(csvfile,cols, dialect=dialect)
        # reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            # print(', '.join(row))
            print(row)
def LoadFile():
    TestTaxo=[(17118424, 'acartia'), (6982464, 'calanus glacialis'), (17119739, 'candacia'), (17152215, 'corycaeus'), (17058254, 'echinodermata'), (17179541, 'poeciloacanthum')]
    NomFichier=os.path.join(directory,fichier)
    print("NomFichier="+NomFichier)
    import csv
    with open(NomFichier) as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        cols=next(reader)
        types=next(reader)
        rows=[]
        for row in reader:
            if row[0]!="":
                rows.append(row)
        print("%d rows to process"%len(rows))
        pgcur=db.engine.raw_connection().cursor()
        pgcur.execute("select nextval('seq_images') from generate_series(1,%d)"%len(rows))
        imagesid=pgcur.fetchall()
        for ImgId,row in zip([x[0] for x in imagesid],rows):
            Obj=database.Objects()
            vaultroot="../../vault"
            #TODO attention pas que du JPG
            vaultfilename="0000/%04d.JPG"%ImgId
            vaultfilenameThumb="0000/%04d_mini.JPG"%ImgId
            for colname,cid in zip(cols,range(0,500)):
                v=row[cid]
                if colname=="img_file_name":
                    shutil.copyfile(os.path.join(directory,v),os.path.join(vaultroot,vaultfilename))
                if "object_" in colname:
                    destcol=MappingObj[colname]
                    if v=="":
                        v=None
                    elif destcol=="objdate":
                        print("%s %s %s %s "%(v,int(v[0:4]),int(v[4:6]),int(v[6:8])))
                        v=datetime.date(int(v[0:4]),int(v[4:6]),int(v[6:8]))
                    elif destcol=="objtime":
                        v=v.zfill(6)
                        v=datetime.time(int(v[0:2]),int(v[2:4]),int(v[4:6]))
                    elif "NAN" == v.upper():
                        v=None
                    setattr(Obj,destcol,v)
            Obj.images=[]
            Obj.classif_id=TestTaxo[random.randint(0,4)][0]
            Obj.img0id=ImgId
            Img=database.Images()
            Img.imgid=ImgId
            Img.file_name=vaultfilename
            Img.imgrank=0
            # TODO si le format en entrée est un BMP le convertir en PNG
            #Calcul de la taille de l'image + generation de la miniature si besoin
            im=Image.open(os.path.join(vaultroot,vaultfilename))
            Img.width=im.size[0]
            Img.height=im.size[1]
            SizeLimit=150
            if (im.size[0]>SizeLimit) or (im.size[1]>SizeLimit) :
                    im.thumbnail((SizeLimit,SizeLimit))
                    im.save(os.path.join(vaultroot,vaultfilenameThumb))
                    Img.thumb_file_name=vaultfilenameThumb
                    Img.thumb_width=im.size[0]
                    Img.thumb_height=im.size[1]
                    Obj.classif_id=17179541 # TEST pour les reperer facilement

            Obj.images.append(Img)
            db.session.add(Obj)
            db.session.commit()

            # break # pour test



if __name__ == '__main__':
    t=LoadTask(1)
    # t.task.taskstate="Running" # permet de forcer l'état
    # print(ObjectToStr(t.param))
    # t.param.IntraStep=1
    # t.UpdateProgress(25,"Test 1")

    t.Process()
    # LoadHeader()
    #LoadFile()