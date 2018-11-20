# -*- coding: utf-8 -*-
from appli import db, database , PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList,app,TempTaskDir,JinjaNl2BR
from flask import  render_template, g, flash,request
import logging,time,re,json,datetime,sys,os
from appli.tasks.taskmanager import AsyncTask,DoTaskClean
from appli.database import GetAll,ExecSQL
from appli.project import sharedfilter
from appli.project.main import RecalcProjectTaxoStat,UpdateProjectStat
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path
from sklearn.externals import joblib
from sklearn.decomposition import PCA
from subprocess import Popen, TimeoutExpired, DEVNULL, PIPE

class TaskClassifAuto2(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.Methode='randomforest'
                self.ProjectId=None
                self.BaseProject=""
                self.CritVar=None
                self.Taxo=""
                self.Perimeter=""
                self.keeplog="no"
                self.learninglimit=""
                self.CustSettings={}
                self.PostTaxoMapping=""
                self.savemodel_foldername=""
                self.savemodel_title = ""
                self.savemodel_comments = ""
                self.usemodel_foldername = ""
                self.filtres = {}
                self.usescn=""

    def __init__(self,task=None):
        super().__init__(task)
        self.pgcur=db.engine.raw_connection().cursor()
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon for Automatic Classification V2 Task %d"%self.task.id)

    def ComputeSCNFeatures(self,Prj):
        logging.info("Start SCN features Computation ")
        if self.param.BaseProject!='':
            PrjListInClause = database.CSVIntStringToInClause(self.param.BaseProject+','+str(self.param.ProjectId))
        else:
            PrjListInClause=str(self.param.ProjectId)
        sql="""select objid,file_name from (
                select oh.objid,  images.file_name,rank() over(partition by oh.objid order by images.imgid) rang
                    from obj_head oh
                    join images on images.objid=oh.objid
                    left join obj_cnn_features cnn on oh.objid=cnn.objcnnid                    
                    where projid in({0}) and cnn.objcnnid is NULL
                    ) Q 
                    where rang=1
                    """.format(PrjListInClause)
        self.pgcur.execute(sql)
        WorkDir=Path(self.GetWorkingDir())
        scn_input=WorkDir/"scn_input.csv"
        output_dir = WorkDir / "scn_output"
        if not output_dir.exists(): output_dir.mkdir()
        vaultdir= (Path(TempTaskDir) / "../vault/").resolve().as_posix()+"/"
        model_dir= (Path(TempTaskDir) / "../SCN_networks"/Prj.cnn_network_id).resolve()
        meta=json.load((model_dir/"meta.json").open('r'))
        TStep = time.time()
        NbrLig=0
        with scn_input.open('w') as finput:
            while True:
                # recupère les images des objets à calculer
                DBRes=self.pgcur.fetchmany(1000)
                if len(DBRes)==0:
                    break
                NbrLig+=len(DBRes)
                finput.writelines(("%s,%s%s\n"%(r[0],vaultdir,r[1]) for r in DBRes ))
        if NbrLig==0:
            logging.info("No Missing SCN Features")
            return
        TStep = time.time()
        env = {
            "MODEL_DIR": model_dir.as_posix(),
            "OUTPUT_DIR": output_dir.resolve().as_posix(),
            # input data
            "UNLABELED_DATA_FN": scn_input.as_posix(),
            # start at the last epoch (NB: this is the previous STOP_EPOCH - 1 because of 0-based indexing)
            "EPOCH": str(meta['epoch']),
            # stop early = do not train
            "STOP_EPOCH": "0",
            # whether to compute features on the input file
            "DUMP_FEATURES": "1"
        }
        # display the current environment
        for k, v in env.items():
            logging.info("{}: {}".format(k, v))

        # time out for the communication with the binary
        # beware, this is for the full execution event while execution can be long for training
        timeout_in_s = 1200

        scn_binary=app.config['SCN_BINARY']
        # recopie toutes les variables d'environnement utile pour l'environnement simulé
        for k,v in os.environ.items():
            env[k]=v
        # TEST sur le PC de laurent avec script de simulation
        if scn_binary=='TEST_PC_LAURENT':
            # for extra in ['PATH','SYSTEMROOT']:
            #     env[extra]= os.environ[extra]
            scn_binary = sys.executable +" "+(Path(TempTaskDir) / "../appli/tasks/simulateur_SCN.py").resolve().as_posix()

        shelloption = scn_binary.find('launch.sh') >=0

        logging.info("scn_binary="+scn_binary)
        # bufsize=1: Line buffering
        with Popen(scn_binary,shell=shelloption , stdin=DEVNULL, stdout=PIPE, stderr=PIPE, env=env, universal_newlines=True, bufsize=1) as p:
            try:
                outs, errs = p.communicate(timeout=timeout_in_s)
            except TimeoutExpired:
                p.kill()
                outs, errs = p.communicate()
        logging.info("Return code: {}".format(p.returncode))
        logging.info("Output: \n%s",outs)
        logging.info("Errors: %s",errs)

        upcur=db.engine.raw_connection().cursor()
        InsSQL="""insert into obj_cnn_features(objcnnid, cnn01, cnn02, cnn03, cnn04, cnn05, cnn06, cnn07, cnn08, cnn09, cnn10, cnn11, cnn12, cnn13, cnn14, cnn15, cnn16, cnn17, cnn18, cnn19, cnn20, cnn21, cnn22, cnn23, cnn24, cnn25, cnn26, cnn27, cnn28, cnn29, cnn30, cnn31, cnn32, cnn33, cnn34, cnn35, cnn36, cnn37, cnn38, cnn39, cnn40, cnn41, cnn42, cnn43, cnn44, cnn45, cnn46, cnn47, cnn48, cnn49, cnn50) 
                    values(%(objcnnid)s,%(cnn01)s,%(cnn02)s,%(cnn03)s,%(cnn04)s,%(cnn05)s,%(cnn06)s,%(cnn07)s,%(cnn08)s,%(cnn09)s,%(cnn10)s,%(cnn11)s,%(cnn12)s,%(cnn13)s,%(cnn14)s,%(cnn15)s,%(cnn16)s,%(cnn17)s,%(cnn18)s,%(cnn19)s,%(cnn20)s,%(cnn21)s,%(cnn22)s,%(cnn23)s,%(cnn24)s,%(cnn25)s,%(cnn26)s,%(cnn27)s,%(cnn28)s,%(cnn29)s,%(cnn30)s,%(cnn31)s,%(cnn32)s,%(cnn33)s,%(cnn34)s,%(cnn35)s,%(cnn36)s,%(cnn37)s,%(cnn38)s,%(cnn39)s,%(cnn40)s,%(cnn41)s,%(cnn42)s,%(cnn43)s,%(cnn44)s,%(cnn45)s,%(cnn46)s,%(cnn47)s,%(cnn48)s,%(cnn49)s,%(cnn50)s )"""

        pca = joblib.load(model_dir/"feature_pca.jbl")

        def ProcessLig():
            nonlocal LigData,InsSQL,upcur,LigID,pca
            # pour générer un fichier de test
            # pca = PCA(n_components=50)
            # pca.fit(np.array(LigData))
            # pca_fn = model_dir/"feature_pca.jbl"
            # joblib.dump(pca, pca_fn)

            pcares=pca.transform(np.array(LigData))
            SQLParam=[ {"cnn%02d"%(i+1):float(x) for i,x in enumerate(feat)} for feat in pcares ]
            for i in range(len(SQLParam)):
                SQLParam[i]['objcnnid']=LigID[i]
            database.ExecSQL("delete from obj_cnn_features where objcnnid= any(%s)",(LigID,))
            upcur.executemany(InsSQL,SQLParam)
            upcur.connection.commit()
            LigData = []
            LigID = []

        with (output_dir/'unlabeled_features.csv').open('r') as fout:
            LigID = []
            LigData=[]
            for l in fout:
                Lig=l.split(',')
                LigID.append(int(Lig[0]))
                LigData.append([float(x) for x in Lig[2:]])
                if len(LigData)>100:
                    ProcessLig()
        if len(LigData)>0:
            ProcessLig()

    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__,))
        logging.info("Start Step 1")
        TInit = time.time()
        Prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        MapPrj = self.GetReverseObjMap(Prj) # Dict NomVariable=>N° colonne ex Area:n42
        CommonKeys = set(MapPrj.keys())
        # PostTaxoMapping décodé sous la forme source:target
        PostTaxoMapping = {int(el[0].strip()): int(el[1].strip()) for el in
                           [el.split(':') for el in self.param.PostTaxoMapping.split(',') if el != '']}
        logging.info("PostTaxoMapping = %s ", PostTaxoMapping)

        if self.param.usemodel_foldername!='': # Utilisation d'un modèle existant
            ModelFolderName = self.param.usemodel_foldername
            ModelFolder = Path("../../RF_models") / ModelFolderName
            if not ModelFolder.is_dir():
                raise Exception("Invalid model directory RF_models/{} ".format(ModelFolderName))
            Meta=json.load((ModelFolder / "meta.json").open("r"))
            if Meta.get('scn_model','')!="":
                self.param.usescn = 'Y'

        CNNCols = ""
        if self.param.usescn=='Y':
            self.ComputeSCNFeatures(Prj)
            CNNCols="".join([",cnn%02d"%(i+1) for i in range(50)])

        if self.param.usemodel_foldername!='': # Utilisation d'un modèle existant
            self.UpdateProgress(1, "Load model from file")
            Classifier=joblib.load( ModelFolder / 'random_forest.jbl')
            zooprocess_fields=Meta.get('zooprocess_fields', Meta.get('zooprocess_fields:'))
            CommonKeys = zooprocess_fields # on utilise un array et pas un set car il faut imperativement respecter l'ordre des colonnes du modèle
            zooprocess_medians=Meta.get('zooprocess_medians')
            DefVal={} # valeurs par défaut pour les données manquantes, clé colonne dans le projet source ex : n61:1.234
            for c,m in zip(zooprocess_fields,zooprocess_medians):
                if c not in MapPrj:
                    raise Exception("Column {} present in model but missing in project".format(c))
                DefVal[MapPrj[c]]=m
            # CommonKeys = CommonKeys.intersection(set(zooprocess_fields))
        else: # Calcul du modèlé à partir de projets sources
            self.UpdateProgress(1, "Retrieve Data from Learning Set")
            PrjListInClause=database.CSVIntStringToInClause(self.param.BaseProject)
            LstPrjSrc=GetAll("select projid,mappingobj from projects where projid in({0})".format(PrjListInClause))
            MapPrjBase={}
            for PrjBase in LstPrjSrc:
                #gènere la reverse mapping
                MapPrjBase[PrjBase['projid']] = self.GetReverseObjMap(PrjBase)
                # et cherche l'intersection des attributs communs
                CommonKeys = CommonKeys.intersection(set(MapPrjBase[PrjBase['projid']].keys()))
            if self.param.learninglimit:
                self.param.learninglimit=int(self.param.learninglimit) # convert
            logging.info("MapPrj %s",MapPrj)
            logging.info("MapPrjBase %s",MapPrjBase)
            CritVar = self.param.CritVar.split(",")
            # ne garde que les colonnes communes qui sont aussi selectionnées.
            CommonKeys = CommonKeys.intersection(set(CritVar))
            # Calcule les mediane
            sql =""
            for BasePrj in LstPrjSrc:
                bprojid=BasePrj['projid']
                if sql !="": sql+=" union all "
                sql+="select 1"
                for c in CommonKeys:
                    sql+=",coalesce(percentile_cont(0.5) WITHIN GROUP (ORDER BY {0}),-9999) as {1}".format(MapPrjBase[bprojid][c],MapPrj[c])
                sql+=" from objects "
                sql += " where projid={0} and classif_id is not null and classif_qual='V'".format(bprojid)
            if self.param.learninglimit:
                LimitHead = """ with objlist as ( select objid from (
                            select objid,row_number() over(PARTITION BY classif_id order by random_value) rang
                            from obj_head
                            where projid in ({0}) and classif_id is not null
                            and classif_qual='V' ) q where rang <={1} ) """.format(PrjListInClause,
                                                                                   self.param.learninglimit)
                LimitFoot = """ and objid in ( select objid from objlist ) """
                sql= LimitHead + sql + LimitFoot
            else : LimitHead=LimitFoot=""
            DefVal=GetAll(sql)[0]
            # Extrait les données du learning set
            sql = ""
            for BasePrj in LstPrjSrc:
                bprojid = BasePrj['projid']
                if sql != "": sql += " \nunion all "
                sql="select classif_id"
                for c in CommonKeys:
                    sql+=",coalesce(case when {0} not in ('Infinity','-Infinity','NaN') then {0} end,{1}) as {2}".format(MapPrjBase[bprojid][c],DefVal[MapPrj[c]],MapPrj[c])
                sql+=CNNCols+" from objects "
                if self.param.usescn == 'Y':
                    sql += " join obj_cnn_features on obj_cnn_features.objcnnid=objects.objid "
                sql+=""" where classif_id is not null and classif_qual='V'
                            and projid in ({0})
                            and classif_id in ({1}) """.format(PrjListInClause,self.param.Taxo)
            if self.param.learninglimit:
                sql = LimitHead + sql + LimitFoot
            # Convertie le LS en tableau NumPy
            DBRes=np.array(GetAll(sql))
            LSSize=DBRes.shape[0]
            learn_cat = DBRes[:,0] # Que la classif
            learn_var = DBRes[:,1:] # exclu l'objid & la classif
            DBRes=None # libere la mémoire
            logging.info('DB Conversion to NP : %0.3f s', time.time() - TInit)
            logging.info("Variable shape %d Row, %d Col",*learn_var.shape)
            # Note : La multiplication des jobs n'est pas forcement plus performante, en tous cas sur un petit ensemble.
            Classifier = RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=1, class_weight="auto")

            # TStep = time.time()
            # cette solution ne convient pas, car lorsqu'on l'applique par bloc de 100 parfois il n'y a pas de valeur dans
            # toute la colonne et du coup la colonne est supprimé car on ne peut pas calculer la moyenne.
            # learn_var = Imputer().fit_transform(learn_var)
            #learn_var[learn_var==np.nan] = -99999 Les Nan sont des NULL dans la base traités parle coalesce
            # logging.info('Clean input variables :  %0.3f s', time.time() - TStep)
            TStep = time.time()
            Classifier.fit(learn_var, learn_cat)
            logging.info('Model fit duration :  %0.3f s', time.time() - TStep)
            if self.param.savemodel_foldername!="": # Il faut sauver le modèle
                ModelFolderName=re.sub('[^\w-]', '_', self.param.savemodel_foldername.strip())
                ModelFolder=Path("../../RF_models") / ModelFolderName
                if not ModelFolder.is_dir():
                    ModelFolder.mkdir()
                joblib.dump(Classifier,ModelFolder/'random_forest.jbl')
                Meta={"zooprocess_fields":[],"zooprocess_medians":[],"name":self.param.savemodel_title
                    , "comments": self.param.savemodel_comments,'date':datetime.datetime.now().isoformat()
                    ,"scn_model":"","type": "RandomForest-ZooProcess","n_objects": LSSize}
                for c in CommonKeys:
                    Meta["zooprocess_fields"].append(c)
                    Meta["zooprocess_medians"].append(DefVal[MapPrj[c]])
                Meta['categories'] = {r[0]: r[1] for r in database.GetTaxoNameFromIdList([int(x) for x in Classifier.classes_])}
                Meta['scn_model'] =""
                if self.param.usescn == 'Y':
                    Meta['scn_model']=Prj.cnn_network_id
                json.dump(Meta,(ModelFolder/"meta.json").open("w"),indent="\t")
        # ------ Fin de la partie apprentissage ou chargement du modèle

        if self.param.Perimeter!='all':
            PerimeterWhere=" and ( classif_qual='P' or classif_qual is null)  "
        else: PerimeterWhere=""
        sqlparam={}
        PerimeterWhere +=sharedfilter.GetSQLFilter(self.param.filtres, sqlparam,-99999)
        NbrItem=GetAll("select count(*) from objects o where projid={0} {1} ".format(Prj.projid,PerimeterWhere),sqlparam)[0][0]
        if NbrItem==0:
            raise Exception ("No object to classify, perhaps all object already classified or you should adjust the perimeter settings as it was probably set to 'Not Validated' ")

        sql="select objid"
        for c in CommonKeys:
            sql += ",coalesce(case when {0} not in ('Infinity','-Infinity','NaN') then {0} end,{1}) as {0}".format(MapPrj[c], DefVal[MapPrj[c]])
        sql += CNNCols + " from objects o "
        if self.param.usescn == 'Y':
            sql += " join obj_cnn_features on obj_cnn_features.objcnnid=o.objid "
        sql+=""" where projid={0} {1}
                    order by objid""".format(Prj.projid,PerimeterWhere)
        self.pgcur.execute(sql,sqlparam)
        # logging.info("SQL=%s",sql)
        upcur=db.engine.raw_connection().cursor()
        ProcessedRows=0
        while True:
            self.UpdateProgress(15+85*(ProcessedRows/NbrItem),"Processed %d/%d"%(ProcessedRows,NbrItem))
            TStep = time.time()
            # recupère les variables des objets à classifier
            DBRes=np.array(self.pgcur.fetchmany(100))
            if len(DBRes)==0:
                break
            ProcessedRows+=len(DBRes)
            Tget_Ids = DBRes[:,0] # Que l'objid
            Tget_var = DBRes[:,1:] # exclu l'objid
            TStep2 = time.time()
            # Tget_var= Imputer().fit_transform(Tget_var) # voir commentaire sur learn_var
            # Tget_var[Tget_var==np.nan] = -99999
            Result=Classifier.predict_proba(Tget_var)
            ResultMaxCol=np.argmax(Result,axis=1)
            # Typage important pour les perf postgresql
            SqlParam=[{'cat':int(Classifier.classes_[mc]),'p':r[mc],'id':int(i)} for i,mc,r in zip(Tget_Ids,ResultMaxCol,Result)]
            for i, v in enumerate(SqlParam):
                if v['cat'] in PostTaxoMapping:
                    SqlParam[i]['cat']=PostTaxoMapping[v['cat']]
            TStep3 = time.time()
            # MAJ dans la base, Si pas de classif devient predicted , Si vide ou predicted, MAJ de la classif
            if self.param.keeplog:
                upcur.executemany("""insert into objectsclassifhisto(objid,classif_date,classif_type,classif_id,classif_qual,classif_score)
                                      select objid,classif_auto_when,'A', classif_auto_id,classif_qual,classif_auto_score
                                        from obj_head
                                        where objid=%(id)s and classif_auto_id!=%(cat)s and classif_auto_id is not null
                                        and classif_auto_when is not null """,SqlParam)
            upcur.executemany("""update obj_head set classif_auto_id=%(cat)s,classif_auto_score=%(p)s,classif_auto_when=now()
                                    ,classif_qual=case when classif_qual in ('D','V') then  classif_qual else 'P'  END
                                    ,classif_id=case when classif_qual in ('D','V') then classif_id  else %(cat)s end
                                    where objid=%(id)s""",SqlParam)
            upcur.connection.commit()
            logging.info('Chunk Db Extract %d/%d, Classification and Db Save :  %0.3f s %0.3f+%0.3f+%0.3f'
                         , ProcessedRows ,NbrItem
                         , time.time() - TStep,TStep2 - TStep,TStep3 - TStep2,time.time() - TStep3)

        RecalcProjectTaxoStat(Prj.projid)
        UpdateProjectStat(Prj.projid)
        self.task.taskstate="Done"
        self.UpdateProgress(100,"Classified %d objects"%ProcessedRows)
        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")
        # if self.param.IntraStep==1:
        #sinon on pose une question

    def QuestionProcessScreenSelectSource(self,Prj):
        # Premier écran de configuration, choix du projet de base
        PreviousTxt = self.GetFilterText()
        d = DecodeEqualList(Prj.classifsettings)
        TargetFeatures = set(DecodeEqualList(Prj.mappingobj).values())
        PreviousLS=d.get("baseproject", "")
        if PreviousLS != "":
            BasePrj = GetAll("select projid,title from projects where projid in ({0})".format(PreviousLS))
            if len(BasePrj):
                PreviousTxt += """<a class='btn btn-primary' href='?{0}&src={1}'>
                            USE previous Learning Set :  {2}</a><br><br>OR USE another project<br><br>""".format(
                    request.query_string.decode("utf-8"),PreviousLS, " + ".join(["#{0} - {1}".format(*r) for r in BasePrj]) )
        from flask_login import current_user
        sql = "select projid,title,round(coalesce(objcount,0)*coalesce(pctvalidated,0)/100),mappingobj,coalesce(cnn_network_id,'') from projects where 1=1 "
        sqlparam=[]

        if gvp('filt_title'):
            sql += " and title ilike (%s) "
            sqlparam.append(("%"+gvp('filt_title')+"%"))
        if gvp('filt_instrum', '') != '':
            sql += " and projid in (select distinct projid from acquisitions where instrument ilike '%%'||(%s) ||'%%' ) "
            sqlparam.append(gvp('filt_instrum'))

        sql += " order by title"
        ProjList = database.GetAll(sql,sqlparam)

        TblBody=""
        for r in ProjList:
            MatchingFeatures = len(set(DecodeEqualList(r['mappingobj']).values()) & TargetFeatures)
            if MatchingFeatures<int(gvp("filt_featurenbr") if gvp("filt_featurenbr") else 10):
                continue
            TblBody += """<tr><td><input type='checkbox' class='selproj' data-prjid='{2}'></td>
                        <td>#{2} - {3}</td><td>{4:0.0f}</td><td>{1}</td><td>{6}</td>
                        </tr>""".format(Prj.projid,MatchingFeatures, *r)

        return render_template('task/classifauto2_create_lstproj.html'
                               ,url=request.query_string.decode('utf-8')
                               ,TblBody=TblBody
                               ,PreviousTxt=PreviousTxt)

    def QuestionProcessScreenSelectSourceTaxo(self,Prj):
        # Second écran de configuration, choix des taxon utilisés dans la source

        # recupere les categories et le nombre d'occurence dans les projet de base/learning
        sql = """select n.classif_id,t.name||case when p1.name is not null and t.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name
                ,n.nbr
                from (select o.classif_id,count(*) nbr
                      from obj_head o where projid in ({0}) and classif_qual='V'
                      group by classif_id) n
                JOIN taxonomy t on n.classif_id=t.id
                left join taxonomy p1 on t.parent_id=p1.id
                order by nbr desc,name""".format(database.CSVIntStringToInClause(gvp('src', gvg('src'))))
        g.TaxoList = GetAll(sql, None, cursor_factory=None)
        s = sum([r[2] for r in g.TaxoList])  # Nbr total d'objet par categorie
        d = DecodeEqualList(Prj.classifsettings)
        TaxoCSV=d.get('seltaxo')
        if TaxoCSV:
            TaxoList={int(x) for x in TaxoCSV.split(',')}
        else: TaxoList = {}
        g.TaxoList = [[r[0], r[1], r[2], round(100 * r[2] / s, 1), 'checked' if len(TaxoList)==0 or r[0] in TaxoList else ''] for r in
                      g.TaxoList]  # Ajout du % d'objet par categorie

        ExtraHeader="<input type='hidden' name='src' value='{}'>".format(gvp('src', gvg('src')))
        ExtraHeader += self.GetFilterText()

        return render_template('task/classifauto2_create_lsttaxo.html'
                               ,url=request.query_string.decode('utf-8')
                               ,ExtraHeader=ExtraHeader,prj=Prj)
    @staticmethod
    def ReadModels():
        ModelFolder = (Path(TempTaskDir)/"../RF_models").resolve()
        Models={}
        for directory in ModelFolder.glob("*"):
            if directory.is_dir() and (directory/"meta.json").is_file():
                Models[directory.name]=json.load((directory/"meta.json").open("r"))
        return Models

    def GetFilterText(self):
        TxtFiltres=sharedfilter.GetTextFilter(self.param.filtres)
        if TxtFiltres:
            return "<p><span style='color:red;font-weight:bold;font-size:large;'>USING Active Project Filters</span><BR>Filters : "+ TxtFiltres+"</p>"
        else:
            return ""

    def QuestionProcessScreenSelectModel(self, Prj):
        Models=self.ReadModels()
        # app.logger.info("Modèles = %s",Models)
        # Premier écran de configuration pour prédiction depuis un modèle, choix du projet du modèle
        PreviousTxt = self.GetFilterText()
        d = DecodeEqualList(Prj.classifsettings)
        g.posttaxomapping=d.get('posttaxomapping',"")
        # TargetFeatures = set(DecodeEqualList(Prj.mappingobj).values())
        TargetFeatures =set(self.GetReverseObjMap(Prj).keys())

        TblBody = ""
        sortedmodellist=sorted(Models.keys(),key=str.lower)
        for modeldir in sortedmodellist:
            r=Models[modeldir]
            # bug sur les fichiers initiaux qui avaient : en trop dans le nom de cette entrée
            ModelFeatures=set(r.get('zooprocess_fields',r.get('zooprocess_fields:')))
            MatchingFeatures = len(ModelFeatures & TargetFeatures)
            if MatchingFeatures < int(gvp("filt_featurenbr") if gvp("filt_featurenbr") else 10):
                continue
            if gvp('filt_title'):
                if r['name'].lower().find(gvp('filt_title').lower())<0 and modeldir.lower().find(gvp('filt_title').lower())<0:
                    continue
            Radio = ""
            #  Pour être compatible foit utiliser le même SCN que le projet ou ne pas en utiliser
            if (r['scn_model']==Prj.cnn_network_id) or (r['scn_model']==''):
                Radio="<input name=selmodel type='radio' class='selmodel ' data-modeldir='{0}' {1}>".format(modeldir
                          ,"checked" if modeldir == d.get('usemodel_foldername') else "")
            if len(ModelFeatures)!=MatchingFeatures:
                MatchingFeatures='Missing'
                Radio = ""
            TaxoDetails=" <span class='showcat'>Show categories</span><span style='display: none'><br>"+', '.join(sorted(r.get('categories',{}).values(),key=lambda v: v.upper()))+"</span>"
            TblBody += """<tr><td> {6}</td>
                        <td>{0} - {1}{7}{5}</td><td>{2:0.0f}</td><td>{3}</td><td>{4}</td>
                        </tr>""".format(modeldir, r['name'],r['n_objects'],MatchingFeatures, r['scn_model']
                                        ,"<br>Comments : "+JinjaNl2BR(r.get('comments')) if r.get('comments') else ""
                                        ,Radio,TaxoDetails)

        return render_template('task/classifauto2_create_selectmodel.html'
                               , url=request.query_string.decode('utf-8')
                               , TblBody=TblBody
                               , PreviousTxt=PreviousTxt)

    def QuestionProcessScreenSelectModelTaxo(self,Prj):
        # Second écran de configuration, mapping des taxon utilisés dans le modele
        PreviousTxt = self.GetFilterText()
        g.modeldir=gvp('modeldir')
        ModelFolder = Path("RF_models") / g.modeldir
        Meta = json.load((ModelFolder / "meta.json").open("r"))
        categories=Meta.get("categories","")
        g.TaxoList = database.GetTaxoNameFromIdList([int(x) for x in categories])
        return render_template('task/classifauto2_create_lsttaxo_frommodel.html'
                               ,url=request.query_string.decode('utf-8')
                               ,prj=Prj, PreviousTxt=PreviousTxt)
    def QuestionProcess(self):
        Prj=database.Projects.query.filter_by(projid=gvg("projid")).first()
        if not Prj.CheckRight(1):
            return PrintInCharte("ACCESS DENIED for this project<br>")
        g.prjtitle=Prj.title
        for k in sharedfilter.FilterList:
            self.param.filtres[k] = gvg(k, "")
        g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title)
        txt=""
        errors=[]
        # Le projet de base est choisi second écran ou validation du second ecran
        if gvp('starttask')=="Y":
            # validation du second ecran
            self.param.ProjectId=gvg("projid")
            if gvg("src",gvp("src",""))!="":
                self.param.BaseProject=database.CSVIntStringToInClause(gvg("src",gvp("src","")))
            self.param.CritVar=gvp("CritVar")
            self.param.Perimeter=gvp("Perimeter")
            self.param.usemodel_foldername = gvp('modeldir', '')
            if gvp('ReadPostTaxoMappingFromLB') =="Y":
                self.param.PostTaxoMapping = ",".join((x[6:] + ":" + gvp(x) for x in request.form if x[0:6] == "taxolb"))
            else:
                self.param.PostTaxoMapping = gvp("PostTaxoMapping")
            self.param.learninglimit = gvp("learninglimit")
            self.param.keeplog=gvp("keeplog")
            self.param.savemodel_foldername = gvp("savemodel_foldername")
            self.param.savemodel_title = gvp("savemodel_title")
            self.param.savemodel_comments = gvp("savemodel_comments")
            self.param.usescn=gvp("usescn","")
            # self.param.Taxo=",".join( (x[4:] for x in request.form if x[0:4]=="taxo") )
            self.param.Taxo =gvp('Taxo')
            self.param.CustSettings=DecodeEqualList(gvp("TxtCustSettings"))
            g.TxtCustSettings=gvp("TxtCustSettings")
            # Verifier la coherence des données
            if self.param.usemodel_foldername=='':
                if self.param.CritVar=='' and self.param.usescn=="":
                    errors.append("You must select some variable")
                if self.param.Taxo=='' : errors.append("You must select some category")
            if len(errors)>0:
                for e in errors:
                    flash(e,"error")
            else: # Pas d'erreur, on memorize les parametres dans le projet et on lance la tache
                # On ajoute les valeurs dans CustSettings pour les sauver dans le ClassifSettings du projet
                PrjCS = DecodeEqualList(Prj.classifsettings)
                d=self.param.CustSettings.copy()
                if gvg("src", gvp("src", "")) != "": # on écrase que si les données sont saisies, sinon on prend dans le projet
                    d['critvar']=self.param.CritVar
                    d['baseproject']=self.param.BaseProject
                    d['seltaxo'] = self.param.Taxo
                    if "usemodel_foldername" in PrjCS: d["usemodel_foldername"]=PrjCS["usemodel_foldername"]
                else:
                    d['usemodel_foldername']=self.param.usemodel_foldername
                    if "critvar" in PrjCS: d["critvar"]=PrjCS["critvar"]
                    if "baseproject" in PrjCS: d["baseproject"]=PrjCS["baseproject"]
                    if "seltaxo" in PrjCS: d["seltaxo"] = PrjCS["seltaxo"]
                d['posttaxomapping'] =self.param.PostTaxoMapping
                Prj.classifsettings=EncodeEqualList(d)
                return self.StartTask(self.param)
        else: # valeurs par default
            if gvp('frommodel', gvg('frommodel')) == "Y":
                if gvp('modeldir')=='':
                    return self.QuestionProcessScreenSelectModel(Prj)
                elif gvp('displaytaxomap')=='Y':
                    return self.QuestionProcessScreenSelectModelTaxo(Prj)
            else:
                if gvp('src', gvg('src')) == "":
                    return self.QuestionProcessScreenSelectSource(Prj)
                elif gvp('seltaxo', gvg('seltaxo')) == "":
                    return self.QuestionProcessScreenSelectSourceTaxo(Prj)

            d=DecodeEqualList(Prj.classifsettings)
            # Certaines variable on leur propre zone d'edition, les autres sont dans la zone texte custom settings
            self.param.CritVar=d.get("critvar","")
            self.param.Taxo=d.get("seltaxo","")
            self.param.Perimeter="nmc"
            self.param.learninglimit = int(gvp("learninglimit","5000"))
            if "critvar" in d : del d["critvar"]
            if "perimeter" in d : del d["perimeter"]
            if "methode" in d: del d["methode"]
            if "learninglimit" in d: del d["learninglimit"]
            if "seltaxo" in d : del d["seltaxo"]
            if "PostTaxoMapping" in d: del d["PostTaxoMapping"]
            if "baseproject" in d : del d["baseproject"]
            g.TxtCustSettings=EncodeEqualList(d)
            self.param.Taxo = ",".join((x[4:] for x in request.form if x[0:4] == "taxo" and x[0:6] != "taxolb"))
            self.param.PostTaxoMapping = ",".join((x[6:]+":"+gvp(x) for x in request.form if x[0:6] == "taxolb"))
        # Determination des criteres/variables utilisées par l'algo de learning
        revobjmap = self.GetReverseObjMap(Prj)
        PrjListInClause=database.CSVIntStringToInClause(gvp("src",gvg("src")))
        LstPrjSrc=GetAll("select projid,mappingobj from projects where projid in({0})".format(PrjListInClause))
        revobjmapbaseByProj={}
        CommonKeys = set(revobjmap.keys())
        for PrjBase in LstPrjSrc:
            revobjmapbaseByProj[PrjBase['projid']] = self.GetReverseObjMap(PrjBase)
            CommonKeys = CommonKeys.intersection(set(revobjmapbaseByProj[PrjBase['projid']].keys()))
        # critlist[NomCol] 0:NomCol , 1:LS % validé rempli , 2:LS Nbr distincte ,3:Cible % rempli ,4:Cible % NV Rempli Inutile ?
        critlist={k:[k,0,0,0,0] for k in CommonKeys}
        # Calcul des stat des projets du LearningSet
        sql="select count(*) nbrtot"
        for k in CommonKeys:
            case="case "
            for PrjBase in LstPrjSrc:
                case +=" when projid={0} then {1} ".format(PrjBase['projid'],revobjmapbaseByProj[PrjBase['projid']][k])
            case+= " end "
            sql+= ",count({0}) {1}_nbr,variance({0})!=0 {1}_dist ".format(case,revobjmap[k]) # on nommeles colonnes avec les colonne du project cible pour eviter les caractères spéciaux
        sql+=" from (select * from objects where projid in ({0}) and classif_qual='V' LIMIT 50000 ) objects ".format(PrjListInClause)
        stat=GetAll(sql)[0]
        g.LsSize=stat['nbrtot']
        if stat['nbrtot']:
            for k in CommonKeys:
                coln=revobjmap[k]
                critlist[k][1]=round(100*(1-stat[coln+'_nbr']/stat['nbrtot'])) # % Missing dans Learning Set
                critlist[k][2] ='Y' if stat[coln+'_dist'] else 'N' # Distinct values N si une seule ou pas de valeur
        # Calcul des stat du projet cible
        sql = "select count(*) nbrtot,0 nbrnotval"
        for k, v in {k:v for k,v in revobjmap.items() if k in CommonKeys}.items():
            sql += ",count({0}) {0}_nbr,variance({0})!=0 {0}_dist".format(v)
        sql += " from (select * from objects where projid={0}  LIMIT 50000 ) objects ".format(Prj.projid)
        stat = GetAll(sql)[0]
        if stat['nbrtot']:
            for k in CommonKeys:
                coln=revobjmap[k]
                critlist[k][3]=round(100*(1-stat[coln+'_nbr']/stat['nbrtot'])) # % Missing dans cible
                critlist[k][4] ='Y' if stat[coln+'_dist'] else 'N' # Distinct values N si une seule ou pas de valeur
        # Calcule des stat de la dispo des données SCN
        g.SCN=None
        if app.config.get("SCN_ENABLED",False):
            sql="""
              select p.projid,p.title,n.nbr,n.nbr-nbrscn miss_scn,cnn_network_id scnmodel
              from projects p
              join (select projid,count(*) nbr,count(cnn.objcnnid) nbrscn  
                    from obj_head oh
                    left join obj_cnn_features cnn on oh.objid=cnn.objcnnid  
                    where projid in({0}) group by projid) N on n.projid=p.projid
              order by p.projid
              """.format(PrjListInClause+(",%d"%Prj.projid))
            g.SCN=GetAll(sql)
            g.SCNImpossible=None
            DistinctSCN={r['scnmodel'] for r in g.SCN}
            if None in DistinctSCN:
                g.SCNImpossible = "Some project are not configured for Deep Learning"
            elif len(DistinctSCN)>1:
                g.SCNImpossible = "All projects must use the same Network"

        g.critlist=list(critlist.values())
        g.critlist.sort(key=lambda t: t[0])
        # app.logger.info(revobjmap)
        data = self.param
        data.src=PrjListInClause
        return render_template('task/classifauto2_create_settings.html',header=txt,data=data,PreviousTxt = self.GetFilterText())

    def GetReverseObjMap(self, Prj):
        mappingobj=getattr(Prj,'mappingobj',None)   #Prj peut être un objet
        if mappingobj is None :  # ou un ligne de requete
            mappingobj=Prj['mappingobj']
        revobjmap = {v: k for k, v in DecodeEqualList(mappingobj).items() if k[0] == 'n'}
        revobjmap['depth_min'] = 'depth_min'
        revobjmap['depth_max'] = 'depth_max'
        return revobjmap

    def GetDoneExtraAction(self):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        PrjId=self.param.ProjectId
        time.sleep(1)
        DoTaskClean(self.task.id)
        return """<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Manual Classification Screen</a>
        <a href='/prjcm/{0}' class='btn btn-primary btn-sm'  role=button>Go to Confusion Matrix</a> """.format(PrjId)

