# -*- coding: utf-8 -*-
from appli import db,app, database ,PrintInCharte,gvp,gvg,DecodeEqualList,ntcv
from flask import render_template, g, flash,request
import logging,os,csv,re,datetime
import zipfile,psycopg2.extras
from flask_login import current_user
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask
from appli.database import GetAll,GetAssoc
from appli.part.part_main import GetFilteredSamples
from appli.part import PartDetClassLimit,PartRedClassLimit,GetClassLimitTxt,CTDFixedColByKey,GetPartClassLimitListText
import appli.part.uvp_sample_import as uvp_sample_import
from appli.part.drawchart import GetTaxoHistoWaterVolumeSQLExpr
import bz2,shutil

class TaskPartExport(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.what=None  # RAW,DET,RED
                self.fileformat=None
                self.filtres={}
                self.redfiltres= {}
                self.user_name = ""
                self.user_email = ""
                self.samples=[]
                self.samplesdict = {}
                self.excludenotliving=False
                self.includenotvalidated=False
                self.OutFile=None
                self.putfileonftparea = ''


    def __init__(self,task=None):
        self.pgcur =None
        self.OwnerList=None
        super().__init__(task)
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon for Part Export")
        self.pgcur=db.engine.raw_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)
    def GetSamples(self):
        logging.info("samples = %s" % (self.param.samples,))
        sql = """SELECT  p.cruise,s.stationid site,s.profileid station,'HDR'||s.filename rawfilename
                        ,p.instrumtype ,s.instrumsn,coalesce(ctd_origfilename,'') ctd_origfilename
                        ,to_char(s.sampledate,'YYYY-MM-DD HH24:MI:SS') sampledate,concat(p.do_name,'(',do_email,')') dataowner
                        ,s.latitude,s.longitude,s.psampleid,s.acq_pixel,acq_aa,acq_exp
                        from part_samples s
                        join part_projects p on s.pprojid = p.pprojid
                        where s.psampleid in (%s)
                        order by s.profileid
                        """ % ((",".join([str(x[0]) for x in self.param.samples])),)
        samples=database.GetAll(sql)
        self.OwnerList = {S['dataowner'] for S in samples}
        return samples
    def WriteODVCommentArea(self,f):
        f.write("//<Creator>%s (%s)</Creator>\n" % (self.param.user_name,self.param.user_email))
        f.write("//<CreateTime>%s</CreateTime>\n" % (datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")))
        f.write(
            "//<DataField>Ocean</DataField>\n//<DataType>Profiles</DataType>\n//<Method>Particle abundance and volume from the Underwater Vision Profiler. The Underwater Video Profiler is designed for the quantification of particles and of large zooplankton in the water column. Light reflected by undisturbed target objects forms a dark-field image.</Method>\n")
        for O in self.OwnerList:
            f.write("//<Owner1>{}</Owner1>\n".format(O))

    def CreateRED(self):
        logging.info("CreateRED Input Param = %s"%(self.param.__dict__))
        AsODV=(self.param.fileformat=='ODV')
        samples=self.GetSamples()
        DTNomFichier = datetime.datetime.now().strftime("%Y%m%d_%H_%M")
        BaseFileName="export_reduced_{0:s}".format(DTNomFichier )
        self.param.OutFile= BaseFileName+".zip"
        zfile = zipfile.ZipFile(os.path.join(self.GetWorkingDir(), self.param.OutFile)
                                , 'w', allowZip64=True, compression=zipfile.ZIP_DEFLATED)
        CTDFixedCols=list(CTDFixedColByKey.keys())
        CTDFixedCols.remove('datetime')
        CTDFixedCols.extend(["extrames%02d" % (i + 1) for i in range(20)])
        ctdsql=",".join(["avg({0}) as ctd_{0} ".format(c) for c in CTDFixedCols])
        ctdsql="""select floor(depth/5)*5+2.5 tranche ,{0}
                from part_ctd t
                where psampleid=(%s)
                group by tranche""".format(ctdsql)
        DepthFilter = ""
        if self.param.redfiltres.get('filt_depthmin'):
            DepthFilter += " and depth>=%d" % int(self.param.redfiltres.get('filt_depthmin'))
        if self.param.redfiltres.get('filt_depthmax'):
            DepthFilter += " and depth<=%d" % int(self.param.redfiltres.get('filt_depthmax'))

        sqlhisto="""select h.*,to_char(datetime,'YYYY-MM-DD HH24:MI:SS') fdatetime,ctd.* 
                from part_histopart_reduit h 
                left join ({0}) ctd on h.depth=ctd.tranche
                where psampleid=(%s) {1}
                order by h.datetime,h.depth """.format(ctdsql,DepthFilter)
        sqlWV = " select {0} tranche,sum(watervolume) from part_histopart_det where psampleid=%(psampleid)s group by tranche".format(
            GetTaxoHistoWaterVolumeSQLExpr("depth","middle"))
        logging.info("sql = %s" % sqlhisto)
        logging.info("samples = %s" % samples)
        # -------------------------- Fichier Particules --------------------------------
        if AsODV:
            nomfichier = BaseFileName + "_PAR_odv.txt"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier,'w',encoding='latin-1') as f:
                self.WriteODVCommentArea(f)
                f.write("Cruise:METAVAR:TEXT:40;Site:METAVAR:TEXT:20;Station:METAVAR:TEXT:20;DataOwner:METAVAR:TEXT:20;Rawfilename:METAVAR:TEXT:20;Instrument:METAVAR:TEXT:10;SN:METAVAR:TEXT:10;CTDrosettefilename:METAVAR:TEXT:40;yyyy-mm-dd hh:mm:METAVAR:TEXT:40;Latitude [degrees_north]:METAVAR:DOUBLE;Longitude [degrees_east]:METAVAR:DOUBLE;Depth [m]:PRIMARYVAR:DOUBLE;Sampled volume[L]")
                for i in range(1,len(PartRedClassLimit)):
                    f.write(";LPM (%s)[# l-1]"%(GetClassLimitTxt(PartRedClassLimit,i)))
                for i in range(1,len(PartRedClassLimit)):
                    f.write(";LPM biovolume (%s)[mm3 l-1]" % (GetClassLimitTxt(PartRedClassLimit, i)))
                for c in CTDFixedCols:
                    f.write(";%s" % (CTDFixedColByKey.get(c,c)))

                f.write("\n")
                for S in samples:
                    L=[S['cruise'],S['site'],S['station'],S['dataowner'],S['rawfilename'],S['instrumtype'],S['instrumsn'],S['ctd_origfilename'],S['sampledate'],S['latitude'],S['longitude']]
                    self.pgcur.execute(sqlhisto, [S["psampleid"],S["psampleid"]])
                    for h in self.pgcur:
                        if ntcv(h['fdatetime'])=='':
                            L[8]=S['sampledate']
                        else: L[8]=h['fdatetime']
                        if not AsODV: # si TSV
                            L=[S['station'],S['rawfilename'],L[7]] # station + rawfilename + sampledate
                        L.extend([h['depth'],h['watervolume']])
                        L.extend((((h['class%02d' % i]/h['watervolume'])if h['watervolume'] else '') for i in range(1,len(PartRedClassLimit))))
                        L.extend((h['biovol%02d' % i] for i in range(1, len(PartRedClassLimit))))
                        f.write(";".join((str(ntcv(x)) for x in L)))
                        for c in CTDFixedCols:
                            f.write(";%s" % (ntcv(h["ctd_"+c])))
                        f.write("\n")
                        L=['','','','','','','','','','','']
            zfile.write(nomfichier)
        else:  # -------- Particule TSV --------------------------------
            for S in samples:
                nomfichier = BaseFileName + "_PAR_"+S['station']+".tsv" # nommé par le profileid qui est dans le champ station
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier, 'w', encoding='latin-1') as f:
                    f.write("Profile\tRawfilename\tyyyy-mm-dd hh:mm\tDepth [m]\tSampled volume[L]")
                    for i in range(1,len(PartRedClassLimit)):
                        f.write("\tLPM (%s)[# l-1]" % (GetClassLimitTxt(PartRedClassLimit, i)))
                    for i in range(1,len(PartRedClassLimit)):
                        f.write("\tLPM biovolume (%s)[mm3 l-1]" % (GetClassLimitTxt(PartRedClassLimit, i)))
                    for c in CTDFixedCols:
                        f.write("\t%s" % (CTDFixedColByKey.get(c, c)))

                    f.write("\n")
                    self.pgcur.execute(sqlhisto, [S["psampleid"],S["psampleid"]])
                    for h in self.pgcur:
                        if ntcv(h['fdatetime']) == '':
                            L = [S['station'], S['rawfilename'], S['sampledate'] ]
                        else:
                            L = [S['station'], S['rawfilename'], h['fdatetime'] ]
                        L.extend([h['depth'], h['watervolume']])
                        L.extend((((h['class%02d' % i]/h['watervolume'])if h['watervolume'] else '') for i in range(1, len(PartRedClassLimit))))
                        L.extend((h['biovol%02d' % i] for i in range(1, len(PartRedClassLimit))))
                        f.write("\t".join((str(ntcv(x)) for x in L)))
                        for c in CTDFixedCols:
                            f.write("\t%s" % (ntcv(h["ctd_"+c])))
                        f.write("\n")
                zfile.write(nomfichier)

        # --------------- Traitement fichier par categorie -------------------------------
        TaxoList=self.param.redfiltres.get('taxo',[])
        # On liste les categories pour fixer les colonnes de l'export
        # if self.param.redfiltres.get('taxochild','')=='1' and len(TaxoList)>0:
        if len(TaxoList) > 0:
            # c'est la liste des taxo passées en paramètres
            sqllstcat = """select t.id,concat(t.name,'('||t1.name||')') nom
        , rank() over (order by t14.name,t13.name,t12.name,t11.name,t10.name,t9.name,t8.name,t7.name,t6.name,t5.name,t4.name,t3.name,t2.name,t1.name,t.name)-1 idx
,concat(t14.name||'>',t13.name||'>',t12.name||'>',t11.name||'>',t10.name||'>',t9.name||'>',t8.name||'>',t7.name||'>',
     t6.name||'>',t5.name||'>',t4.name||'>',t3.name||'>',t2.name||'>',t1.name||'>',t.name) tree
                        from taxonomy t 
                        left join taxonomy t1 on t.parent_id=t1.id
                        left join taxonomy t2 on t1.parent_id=t2.id
                        left join taxonomy t3 on t2.parent_id=t3.id
                        left join taxonomy t4 on t3.parent_id=t4.id
                        left join taxonomy t5 on t4.parent_id=t5.id
                        left join taxonomy t6 on t5.parent_id=t6.id
                        left join taxonomy t7 on t6.parent_id=t7.id
                        left join taxonomy t8 on t7.parent_id=t8.id
                        left join taxonomy t9 on t8.parent_id=t9.id
                        left join taxonomy t10 on t9.parent_id=t10.id
                        left join taxonomy t11 on t10.parent_id=t11.id
                        left join taxonomy t12 on t11.parent_id=t12.id
                        left join taxonomy t13 on t12.parent_id=t13.id
                        left join taxonomy t14 on t13.parent_id=t14.id
                        where t.id in ({0})
                        """.format(",".join([str(x) for x in TaxoList]))
            logging.info("sqllstcat = %s" % sqllstcat)
        else:
            sqllstcat="""select t.id,concat(t.name,'('||t1.name||')') nom
            , rank() over (order by t14.name,t13.name,t12.name,t11.name,t10.name,t9.name,t8.name,t7.name,t6.name,t5.name,t4.name,t3.name,t2.name,t1.name,t.name)-1 idx
,concat(t14.name||'>',t13.name||'>',t12.name||'>',t11.name||'>',t10.name||'>',t9.name||'>',t8.name||'>',t7.name||'>',
     t6.name||'>',t5.name||'>',t4.name||'>',t3.name||'>',t2.name||'>',t1.name||'>',t.name) tree
                    from (select distinct classif_id from part_histocat where psampleid in ( {0}) {1} ) cat
                    join taxonomy t on cat.classif_id=t.id
                    left join taxonomy t1 on t.parent_id=t1.id
                    left join taxonomy t2 on t1.parent_id=t2.id
                    left join taxonomy t3 on t2.parent_id=t3.id
                    left join taxonomy t4 on t3.parent_id=t4.id
                    left join taxonomy t5 on t4.parent_id=t5.id
                    left join taxonomy t6 on t5.parent_id=t6.id
                    left join taxonomy t7 on t6.parent_id=t7.id
                    left join taxonomy t8 on t7.parent_id=t8.id
                    left join taxonomy t9 on t8.parent_id=t9.id
                    left join taxonomy t10 on t9.parent_id=t10.id
                    left join taxonomy t11 on t10.parent_id=t11.id
                    left join taxonomy t12 on t11.parent_id=t12.id
                    left join taxonomy t13 on t12.parent_id=t13.id
                    left join taxonomy t14 on t13.parent_id=t14.id
                    """.format((",".join([str(x[0]) for x in self.param.samples if x[3][1]=='Y'])),DepthFilter)
                            # x[3][1]==Y ==> Zoo exportable
        if self.param.redfiltres.get('taxochild', '') == '1' and len(TaxoList) > 0:
            sqlTaxoTreeFrom = " \njoin taxonomy t0 on h.classif_id=t0.id "
            for i in range(1,15) :
                sqlTaxoTreeFrom += " \nleft join taxonomy t{0} on t{1}.parent_id=t{0}.id ".format(i,i-1)
            sqlhisto = ""
            for taxo in TaxoList:
                sqlTaxoTreeWhere =" and ( h.classif_id = {}  ".format(taxo)
                for i in range(1, 15):
                    sqlTaxoTreeWhere += " or t{0}.id= {1}".format(i,taxo)
                sqlTaxoTreeWhere += ")"
                if sqlhisto != "":
                    sqlhisto += " \nunion all\n "
                sqlhisto+="""select {1} as classif_id, h.psampleid,h.depth,h.lineno,h.avgesd,h.nbr,h.totalbiovolume ,h.watervolume
                    from part_histocat h {2} 
                    where psampleid=%(psampleid)s {0} {3} """.format(DepthFilter,taxo,sqlTaxoTreeFrom,sqlTaxoTreeWhere)
            sqlhisto = """select classif_id,{0} as tranche ,avg(avgesd) avgesd,sum(nbr) nbr,sum(totalbiovolume) totalbiovolume 
                from ({1}) q
                group by classif_id,tranche
                order by tranche """.format(GetTaxoHistoWaterVolumeSQLExpr('depth','middle'),sqlhisto)
        else:
            sqlhisto="""select classif_id,{1} as tranche ,avg(avgesd) avgesd,sum(nbr) nbr,sum(totalbiovolume) totalbiovolume 
                from part_histocat h where psampleid=%(psampleid)s {0}
                group by classif_id,tranche
                order by tranche """.format(DepthFilter,GetTaxoHistoWaterVolumeSQLExpr('depth','middle'))
        lstcat=GetAssoc(sqllstcat)
        if AsODV: # ------------ RED Categories AS ODV
            nomfichier = BaseFileName + "_ZOO_odv.txt"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier, 'w', encoding='latin-1') as f:
                self.WriteODVCommentArea(f)
                f.write(
                    "Cruise:METAVAR:TEXT:40;Site:METAVAR:TEXT:20;Station:METAVAR:TEXT:20;DataOwner:METAVAR:TEXT:20;Rawfilename:METAVAR:TEXT:20;Instrument:METAVAR:TEXT:10;SN:METAVAR:TEXT:10;CTDrosettefilename:METAVAR:TEXT:40;yyyy-mm-dd hh:mm:METAVAR:TEXT:40;Latitude [degrees_north]:METAVAR:DOUBLE;Longitude [degrees_east]:METAVAR:DOUBLE;Depth [m]:PRIMARYVAR:DOUBLE;Sampled volume[L]")
                if self.param.redfiltres.get('taxochild', '') == '1':
                    HeaderSuffix="w/ children"
                else:
                    HeaderSuffix = "w/o children"
                LstHead = sorted(lstcat.values(), key=lambda cat: cat['idx'])
                for v in LstHead:
                    f.write(";%s %s[# m-3]" % (v['nom'],HeaderSuffix))
                for v in LstHead:
                    f.write(";%s biovolume %s[mm3 l-1]" % (v['nom'],HeaderSuffix))
                for v in LstHead:
                    f.write(";%s avgesd %s[mm]" % (v['nom'],HeaderSuffix))
                f.write("\n")
                for S in samples:
                    if self.samplesdict[S["psampleid"]][3][1] != 'Y': # 3 = visibility, 1 =Second char=Zoo visibility
                        continue # pas les permission d'exporter le ZOO de ce sample le saute
                    L=[S['cruise'],S['site'],S['station'],S['dataowner'],S['rawfilename'],S['instrumtype'],S['instrumsn'],S['ctd_origfilename'],S['sampledate'],S['latitude'],S['longitude']]
                    t = [None for i in range(3 * len(lstcat))]
                    logging.info("sqlhisto = %s ; %s" % (sqlhisto,S["psampleid"]))
                    CatHisto=GetAll(sqlhisto, {'psampleid':S["psampleid"]})
                    WV = database.GetAssoc2Col(sqlWV, {'psampleid': S["psampleid"]})
                    for i in range(len(CatHisto)):
                        h=CatHisto[i]
                        idx=lstcat[h['classif_id']]['idx']
                        WaterVolumeTranche =WV.get(h['tranche'],0)
                        if WaterVolumeTranche >0:
                            t[idx] = 1000*h['nbr']/WaterVolumeTranche
                        else: t[idx] =""
                        biovolume=""
                        if h['totalbiovolume'] and WaterVolumeTranche>0:
                            biovolume=h['totalbiovolume']/WaterVolumeTranche
                        t[idx+len(lstcat)] = biovolume
                        t[idx + 2*len(lstcat)] = h['avgesd']
                        EOL=False
                        if (i+1)==len(CatHisto): # Derniere ligne du dataset
                            EOL = True
                        elif CatHisto[i]['tranche']!=CatHisto[i+1]['tranche']: # on change de ligne
                            EOL = True

                        if EOL:
                            L.extend([h['tranche'],WaterVolumeTranche])
                            L.extend(t)
                            f.write(";".join((str(ntcv(x)) for x in L)))
                            f.write("\n")
                            t = [None for i in range(3 * len(lstcat))]
                            L=['','','','','','','','','','','']
            zfile.write(nomfichier)
        else: # ------------ RED Categories AS TSV
            ZooFileParStation={}
            for S in samples:
                if self.samplesdict[S["psampleid"]][3][1] != 'Y':  # 3 = visibility, 1 =Second char=Zoo visibility
                    continue  # pas les permission d'exporter le ZOO de ce sample le saute
                CatHisto = GetAll(sqlhisto, {'psampleid':S["psampleid"]})
                if len(CatHisto)==0: continue # on ne genere pas les fichiers vides.
                nomfichier = BaseFileName + "_ZOO_"+S['station']+".tsv" # nommé par le profileid qui est dans le champ station
                ZooFileParStation[S['station']]=nomfichier
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier, 'w', encoding='latin-1') as f:
                    f.write("Profile\tRawfilename\tyyyy-mm-dd hh:mm\tDepth [m]\tSampled volume[L]")
                    LstHead = sorted(lstcat.values(), key=lambda cat: cat['idx'])
                    for v in LstHead:
                        f.write("\t%s[# m-3]" % (v['tree']))
                    for v in LstHead:
                        f.write("\t%s biovolume[mm3 l-1]" % (v['tree']))
                    for v in LstHead:
                        f.write("\t%s avgesd[mm]" % (v['tree']))
                    f.write("\n")
                    t = [None for i in range(3 * len(lstcat))]
                    WV = database.GetAssoc2Col(sqlWV, {'psampleid': S["psampleid"]})
                    for i in range(len(CatHisto)):
                        h = CatHisto[i]
                        idx = lstcat[h['classif_id']]['idx']
                        WaterVolumeTranche =WV.get(h['tranche'],0)
                        if WaterVolumeTranche >0:
                            t[idx] = 1000*h['nbr']/WaterVolumeTranche
                        else: t[idx] =""
                        t[idx + len(lstcat)] = h['totalbiovolume']
                        t[idx + 2 * len(lstcat)] = h['avgesd']
                        EOL = False
                        if (i + 1) == len(CatHisto):  # Derniere ligne du dataset
                            EOL = True
                        elif CatHisto[i]['tranche'] != CatHisto[i + 1]['tranche']:  # on change de ligne
                            EOL = True

                        if EOL:
                            L = [S['station'], S['rawfilename'],S['sampledate'],h['tranche'], WaterVolumeTranche]
                            L.extend(t)
                            f.write("\t".join((str(ntcv(x)) for x in L)))
                            f.write("\n")
                            t = [None for i in range(3 * len(lstcat))]
                zfile.write(nomfichier)

    # -------------------------- Fichier Synthèse TSV only --------------------------------
        if not AsODV:
            nomfichier = BaseFileName + "_Export_metadata_summary.tsv"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier,'w',encoding='latin-1') as f:
                f.write("profile\tCruise\tSite\tDataOwner\tRawfilename\tInstrument\tCTDrosettefilename\tyyyy-mm-dd hh:mm\tLatitude \tLongitude\taa\texp\tPixel size\tParticle filename\tPlankton filename\n")

                for S in samples:
                    visibility=self.samplesdict[S["psampleid"]][3]
                    L = [S['station'],S['cruise'], S['site'],  S['dataowner'], S['rawfilename'], S['instrumtype'],
                         S['ctd_origfilename'], S['sampledate'], S['latitude'], S['longitude'],S['acq_aa'],S['acq_exp'],S['acq_pixel']]
                    L.append(BaseFileName + "_PAR_"+S['station']+".tsv")
                    L.append(ZooFileParStation[S['station']] if S['station'] in ZooFileParStation else "no data available")
                    f.write("\t".join((str(ntcv(x)) for x in L)))
                    f.write("\n")
            zfile.write(nomfichier)

    def CreateDET(self):
        logging.info("CreateDET Input Param = %s"%(self.param.__dict__,))
        AsODV=(self.param.fileformat=='ODV')
        # Prj=partdatabase.part_projects.query.filter_by(pprojid=self.param.pprojid).first()
        logging.info("samples = %s" % (self.param.samples ))
        samples = self.GetSamples()
        DTNomFichier = datetime.datetime.now().strftime("%Y%m%d_%H_%M")
        BaseFileName="export_detailed_{0:s}".format(DTNomFichier)
        self.param.OutFile= BaseFileName+".zip"
        zfile = zipfile.ZipFile(os.path.join(self.GetWorkingDir(), self.param.OutFile)
                                , 'w', allowZip64=True, compression=zipfile.ZIP_DEFLATED)
        CTDFixedCols=list(CTDFixedColByKey.keys())
        CTDFixedCols.remove('datetime')
        CTDFixedCols.extend(["extrames%02d" % (i + 1) for i in range(20)])
        ctdsql=",".join(["avg({0}) as ctd_{0} ".format(c) for c in CTDFixedCols])
        ctdsql="""select floor(depth/5)*5+2.5 tranche ,{0}
                from part_ctd t
                where psampleid=(%s)
                group by tranche""".format(ctdsql)
        DepthFilter = ""
        if self.param.redfiltres.get('filt_depthmin'):
            DepthFilter += " and depth>=%d" % int(self.param.redfiltres.get('filt_depthmin'))
        if self.param.redfiltres.get('filt_depthmax'):
            DepthFilter += " and depth<=%d" % int(self.param.redfiltres.get('filt_depthmax'))

        sqlhisto="""select h.*,to_char(datetime,'YYYY-MM-DD HH24:MI:SS') fdatetime,ctd.* 
                from part_histopart_det h 
                left join ({0}) ctd on h.depth=ctd.tranche
                where psampleid=(%s) {1}
                order by h.datetime,h.depth """.format(ctdsql,DepthFilter)
        logging.info("sql = %s" % sqlhisto)
        logging.info("samples = %s" % samples)
        # -------------------------- Fichier Particules --------------------------------
        if AsODV:
            nomfichier = BaseFileName + "_PAR_odv.txt"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier,'w',encoding='latin-1') as f:
                self.WriteODVCommentArea(f)
                f.write("Cruise:METAVAR:TEXT:40;Site:METAVAR:TEXT:20;Station:METAVAR:TEXT:20;DataOwner:METAVAR:TEXT:20;Rawfilename:METAVAR:TEXT:20;Instrument:METAVAR:TEXT:10;SN:METAVAR:TEXT:10;CTDrosettefilename:METAVAR:TEXT:40;yyyy-mm-dd hh:mm:METAVAR:TEXT:40;Latitude [degrees_north]:METAVAR:DOUBLE;Longitude [degrees_east]:METAVAR:DOUBLE;Depth [m]:PRIMARYVAR:DOUBLE;Sampled volume[L]")
                for i in range(1,len(PartDetClassLimit)):
                    f.write(";LPM (%s)[# l-1]"%(GetClassLimitTxt(PartDetClassLimit,i)))
                for i in range(1,len(PartDetClassLimit)):
                    f.write(";LPM biovolume (%s)[mm3 l-1]" % (GetClassLimitTxt(PartDetClassLimit, i)))
                for c in CTDFixedCols:
                    f.write(";%s" % (CTDFixedColByKey.get(c,c)))

                f.write("\n")
                for S in samples:
                    L=[S['cruise'],S['site'],S['station'],S['dataowner'],S['rawfilename'],S['instrumtype'],S['instrumsn'],S['ctd_origfilename'],S['sampledate'],S['latitude'],S['longitude']]
                    self.pgcur.execute(sqlhisto, [S["psampleid"],S["psampleid"]])
                    for h in self.pgcur:
                        if ntcv(h['fdatetime'])=='':
                            L[8]=S['sampledate']
                        else: L[8]=h['fdatetime']
                        if not AsODV: # si TSV
                            L=[S['station'],S['rawfilename'],L[7]] # station + rawfilename + sampledate
                        L.extend([h['depth'],h['watervolume']])
                        L.extend((((h['class%02d' % i]/h['watervolume'])if h['watervolume'] else '') for i in range(1,len(PartDetClassLimit))))
                        L.extend((h['biovol%02d' % i] for i in range(1, len(PartDetClassLimit))))
                        f.write(";".join((str(ntcv(x)) for x in L)))
                        for c in CTDFixedCols:
                            f.write(";%s" % (ntcv(h["ctd_"+c])))
                        f.write("\n")
                        L=['','','','','','','','','','','']
            zfile.write(nomfichier)
        else:  # -------- Particule TSV --------------------------------
            for S in samples:
                nomfichier = BaseFileName + "_PAR_"+S['station']+".tsv" # nommé par le profileid qui est dans le champ station
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier, 'w', encoding='latin-1') as f:
                    f.write("Profile\tRawfilename\tyyyy-mm-dd hh:mm\tDepth [m]\tSampled volume[L]")
                    for i in range(1,len(PartDetClassLimit)):
                        f.write("\tLPM (%s)[# l-1]" % (GetClassLimitTxt(PartDetClassLimit, i)))
                    for i in range(1,len(PartDetClassLimit)):
                        f.write("\tLPM biovolume (%s)[mm3 l-1]" % (GetClassLimitTxt(PartDetClassLimit, i)))
                    for c in CTDFixedCols:
                        f.write("\t%s" % (CTDFixedColByKey.get(c, c)))

                    f.write("\n")
                    self.pgcur.execute(sqlhisto, [S["psampleid"],S["psampleid"]])
                    for h in self.pgcur:
                        if ntcv(h['fdatetime']) == '':
                            L = [S['station'], S['rawfilename'], S['sampledate'] ]
                        else:
                            L = [S['station'], S['rawfilename'], h['fdatetime'] ]
                        L.extend([h['depth'], h['watervolume']])
                        L.extend((((h['class%02d' % i]/h['watervolume'])if h['watervolume'] else '') for i in range(1, len(PartDetClassLimit))))
                        L.extend((h['biovol%02d' % i] for i in range(1, len(PartDetClassLimit))))
                        f.write("\t".join((str(ntcv(x)) for x in L)))
                        for c in CTDFixedCols:
                            f.write("\t%s" % (ntcv(h["ctd_"+c])))
                        f.write("\n")
                zfile.write(nomfichier)

        # --------------- Traitement fichier par categorie -------------------------------
        TaxoList=self.param.redfiltres.get('taxo',[])
        # On liste les categories pour fixer les colonnes de l'export
        # liste toutes les cat pour les samples et la depth
        sqllstcat = """select distinct classif_id from part_histocat hc where psampleid in ( {0}) {1} 
                            """.format((",".join([str(x[0]) for x in self.param.samples if x[3][1]=='Y'])), DepthFilter)
                                                                        # x[3][1]==Y ==> Zoo exportable
        if self.param.excludenotliving: # On ne prend que ceux qui ne sont pas desendant de not-living
            sqlTaxoTreeFrom = " \njoin taxonomy t0 on hc.classif_id=t0.id "
            for i in range(1, 15):
                sqlTaxoTreeFrom += " \nleft join taxonomy t{0} on t{1}.parent_id=t{0}.id ".format(i, i - 1)
            sqllstcat=sqllstcat.replace(" hc"," hc"+sqlTaxoTreeFrom)
            for i in range(0, 15):
                sqllstcat += " and (t{0}.id is null or t{0}.name!='not-living') ".format(i)

        logging.info("sqllstcat = %s" % sqllstcat)
        lstcatwhere = GetAll(sqllstcat)
        if lstcatwhere:
            lstcatwhere=",".join((str(x[0]) for x in lstcatwhere)) # extraction de la 1ère colonne seulement et mise en format in
        else :
            lstcatwhere = "-1"
        logging.info("lstcatwhere = %s" % lstcatwhere)
        sqllstcat="""with RECURSIVE th(id ) AS (
    SELECT t.id
    FROM taxonomy t
    WHERE t.id IN ({0})
union ALL
select distinct tlink.parent_id
from th join taxonomy tlink on tlink.id=th.id
where tlink.parent_id is not null
)
select id,nom,rank() over (order by tree)-1 idx,tree
from (
SELECT t0.id,concat(t0.name,'('||t1.name||')') nom
,concat(t14.name||'>',t13.name||'>',t12.name||'>',t11.name||'>',t10.name||'>',t9.name||'>',t8.name||'>',t7.name||'>',
     t6.name||'>',t5.name||'>',t4.name||'>',t3.name||'>',t2.name||'>',t1.name||'>',t0.name) tree
from
(select distinct * from th) thd
join taxonomy t0 on thd.id=t0.id
left join taxonomy t1 on t0.parent_id=t1.id
left join taxonomy t2 on t1.parent_id=t2.id
left join taxonomy t3 on t2.parent_id=t3.id
left join taxonomy t4 on t3.parent_id=t4.id
left join taxonomy t5 on t4.parent_id=t5.id
left join taxonomy t6 on t5.parent_id=t6.id
left join taxonomy t7 on t6.parent_id=t7.id
left join taxonomy t8 on t7.parent_id=t8.id
left join taxonomy t9 on t8.parent_id=t9.id
left join taxonomy t10 on t9.parent_id=t10.id
left join taxonomy t11 on t10.parent_id=t11.id
left join taxonomy t12 on t11.parent_id=t12.id
left join taxonomy t13 on t12.parent_id=t13.id
left join taxonomy t14 on t13.parent_id=t14.id )q
order by tree""".format(lstcatwhere)
        lstcat = GetAssoc(sqllstcat)
        logging.info("lstcat = %s" % lstcat)

        sqlhisto="""select classif_id,lineno,psampleid,depth,watervolume ,avgesd,nbr,totalbiovolume from part_histocat h where psampleid=%(psampleid)s {0} and classif_id in ({1})
             """.format(DepthFilter,lstcatwhere)
        # Ajout calcul des cumul sur les parents via un requete récursive qui duplique les données sur toutes la hierarchie
        # Puis qui somme à chaque niveau
        sqlhisto="""with recursive t(classif_id,lineno,psampleid,depth,watervolume ,avgesd,nbr,totalbiovolume)   
              as ( {0} 
            union all
            select taxonomy.parent_id classif_id,t.lineno,t.psampleid,t.depth,t.watervolume ,t.avgesd,t.nbr,t.totalbiovolume
            from taxonomy join t on taxonomy.id=t.classif_id
            where taxonomy.parent_id is not null
            )
            select classif_id,lineno,psampleid,depth,watervolume,
                  avg(avgesd) avgesd,sum(nbr) nbr,sum(totalbiovolume) totalbiovolume
            from t
            group by classif_id,lineno,psampleid,depth,watervolume              
        """.format(sqlhisto)
        sqlhisto+=" order by lineno"
        if AsODV:
            nomfichier = BaseFileName + "_ZOO_odv.txt"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier, 'w', encoding='latin-1') as f:
                self.WriteODVCommentArea(f)
                f.write(
                    "Cruise:METAVAR:TEXT:40;Site:METAVAR:TEXT:20;Station:METAVAR:TEXT:20;DataOwner:METAVAR:TEXT:20;Rawfilename:METAVAR:TEXT:20;Instrument:METAVAR:TEXT:10;SN:METAVAR:TEXT:10;CTDrosettefilename:METAVAR:TEXT:40;yyyy-mm-dd hh:mm:METAVAR:TEXT:40;Latitude [degrees_north]:METAVAR:DOUBLE;Longitude [degrees_east]:METAVAR:DOUBLE;Depth [m]:PRIMARYVAR:DOUBLE;Sampled volume[L]")
                # if self.param.redfiltres.get('taxochild', '') == '1':
                #     HeaderSuffix="w/ children"
                # else:
                #     HeaderSuffix = "w/o children"
                HeaderSuffix = ""
                LstHead=sorted(lstcat.values(),key=lambda cat:cat['idx'])
                for v in LstHead:
                    f.write(";%s %s[# m-3]" % (v['nom'],HeaderSuffix))
                for v in LstHead:
                    f.write(";%s biovolume %s[mm3 l-1]" % (v['nom'],HeaderSuffix))
                for v in LstHead:
                    f.write(";%s avgesd %s[mm]" % (v['nom'],HeaderSuffix))
                f.write("\n")
                for S in samples:
                    if self.samplesdict[S["psampleid"]][3][1] != 'Y': # 3 = visibility, 1 =Second char=Zoo visibility
                        continue # pas les permission d'exporter le ZOO de ce sample le saute
                    L=[S['cruise'],S['site'],S['station'],S['dataowner'],S['rawfilename'],S['instrumtype'],S['instrumsn'],S['ctd_origfilename'],S['sampledate'],S['latitude'],S['longitude']]
                    t = [None for i in range(3 * len(lstcat))]
                    logging.info("sqlhisto=%s"%sqlhisto)
                    CatHisto=GetAll(sqlhisto, {'psampleid':S["psampleid"]})
                    for i in range(len(CatHisto)):
                        h=CatHisto[i]
                        idx=lstcat[h['classif_id']]['idx']
                        if h['watervolume'] and h['watervolume']>0:
                            t[idx] = h['nbr']*1000/h['watervolume']
                        else: t[idx] =""
                        biovolume=""
                        if h['totalbiovolume'] and h['watervolume']:
                            biovolume=h['totalbiovolume']/h['watervolume']
                        t[idx+len(lstcat)] = biovolume
                        t[idx + 2*len(lstcat)] = h['avgesd']
                        EOL=False
                        if (i+1)==len(CatHisto): # Derniere ligne du dataset
                            EOL = True
                        elif CatHisto[i]['lineno']!=CatHisto[i+1]['lineno']: # on change de ligne
                            EOL = True

                        if EOL:
                            L.extend([h['depth'],h['watervolume']])
                            L.extend(t)
                            f.write(";".join((str(ntcv(x)) for x in L)))
                            f.write("\n")
                            t = [None for i in range(3 * len(lstcat))]
                            L=['','','','','','','','','','','']
            zfile.write(nomfichier)
        else: # ------------ Categories AS TSV
            ZooFileParStation = {}
            for S in samples:
                if self.samplesdict[S["psampleid"]][3][1] != 'Y':  # 3 = visibility, 1 =Second char=Zoo visibility
                    continue  # pas les permission d'exporter le ZOO de ce sample le saute
                CatHisto = GetAll(sqlhisto, {'psampleid': S["psampleid"]})
                if len(CatHisto)==0: continue # on ne genere pas les fichiers vides.
                nomfichier = BaseFileName + "_ZOO_"+S['station']+".tsv" # nommé par le profileid qui est dans le champ station
                ZooFileParStation[S['station']] = nomfichier
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier, 'w', encoding='latin-1') as f:
                    f.write("Profile\tRawfilename\tyyyy-mm-dd hh:mm\tDepth [m]\tSampled volume[L]")
                    LstHead = sorted(lstcat.values(), key=lambda cat: cat['idx'])
                    for v in LstHead:
                        f.write("\t%s[# m-3]" % (v['tree']))
                    for v in LstHead:
                        f.write("\t%s biovolume[mm3 l-1]" % (v['tree']))
                    for v in LstHead:
                        f.write("\t%s avgesd[mm]" % (v['tree']))
                    f.write("\n")
                    t = [None for i in range(3 * len(lstcat))]
                    for i in range(len(CatHisto)):
                        h = CatHisto[i]
                        idx = lstcat[h['classif_id']]['idx']
                        if h['watervolume'] :
                            t[idx] = 1000*h['nbr']/h['watervolume']
                        else: t[idx] =""
                        biovolume=""
                        if h['totalbiovolume'] and h['watervolume']:
                            biovolume=h['totalbiovolume']/h['watervolume']
                        t[idx + len(lstcat)] = biovolume
                        t[idx + 2 * len(lstcat)] = h['avgesd']
                        EOL = False
                        if (i + 1) == len(CatHisto):  # Derniere ligne du dataset
                            EOL = True
                        elif CatHisto[i]['lineno'] != CatHisto[i + 1]['lineno']:  # on change de ligne
                            EOL = True

                        if EOL:
                            L = [S['station'], S['rawfilename'],S['sampledate'],h['depth'], h['watervolume']]
                            L.extend(t)
                            f.write("\t".join((str(ntcv(x)) for x in L)))
                            f.write("\n")
                            t = [None for i in range(3 * len(lstcat))]
                zfile.write(nomfichier)

    # -------------------------- Fichier Synthèse TSV only --------------------------------
        if not AsODV:
            nomfichier = BaseFileName + "_Export_metadata_summary.tsv"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier,'w',encoding='latin-1') as f:
                f.write("profile\tCruise\tSite\tDataOwner\tRawfilename\tInstrument\tCTDrosettefilename\tyyyy-mm-dd hh:mm\tLatitude \tLongitude\taa\texp\tPixel size\tParticle filename\tPlankton filename\n")

                for S in samples:
                    visibility = self.samplesdict[S["psampleid"]][3]
                    L = [S['station'],S['cruise'], S['site'],  S['dataowner'], S['rawfilename'], S['instrumtype'],
                         S['ctd_origfilename'], S['sampledate'], S['latitude'], S['longitude'],S['acq_aa'],S['acq_exp'],S['acq_pixel']
                         ,BaseFileName + "_PAR_"+S['station']+".tsv"]
                    L.append(ZooFileParStation[S['station']] if S['station'] in ZooFileParStation else "no data available")

                    f.write("\t".join((str(ntcv(x)) for x in L)))
                    f.write("\n")
            zfile.write(nomfichier)
    def CreateRAW(self):
        logging.info("CreateRAW Input Param = %s"%(self.param.__dict__,))
        logging.info("samples = %s" % (self.param.samples ))
        DTNomFichier=datetime.datetime.now().strftime("%Y%m%d_%H_%M")
        BaseFileName="export_raw_{0:s}".format(DTNomFichier)
        self.param.OutFile= BaseFileName+".zip"
        zfile = zipfile.ZipFile(os.path.join(self.GetWorkingDir(), self.param.OutFile)
                                , 'w', allowZip64=True, compression=zipfile.ZIP_DEFLATED)
        sql="""select s.*
          ,pp.ptitle,pp.rawfolder,concat(u.name,' ('||u.email||')') ownerid,pp.projid,pp.instrumtype,pp.op_name,pp.op_email,pp.cs_name,pp.cs_email
          ,pp.do_name,pp.do_email,pp.prj_info,pp.prj_acronym,pp.cruise,pp.ship,pp.default_instrumsn,pp.default_depthoffset
          ,(select count(*) from part_histocat where psampleid=s.psampleid) nbrlinetaxo
          ,(select count(*) from part_ctd where psampleid=s.psampleid) nbrlinectd
          ,p.mappingobj
        from part_samples s
        join part_projects pp on s.pprojid=pp.pprojid
        LEFT JOIN projects p on pp.projid=p.projid
        LEFT JOIN users u on pp.ownerid=u.id
        where s.psampleid in (%s)
        order by s.profileid
        """ % ((",".join([str(x[0]) for x in self.param.samples])),)
        samples=GetAll(sql)
        # Fichiers particule
        for S in samples:
            if S['histobrutavailable'] and S['instrumtype']=='uvp5':
                nomfichier="{0}_{1}_PAR_raw_{2}.tsv".format(S['filename'],S['profileid'],DTNomFichier )
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                raworigfile= uvp_sample_import.GetPathForRawHistoFile(S['psampleid'])
                with bz2.open(raworigfile,'rb') as rf,open(fichier,"wb") as rawtargetfile:
                    shutil.copyfileobj(rf,rawtargetfile)
                zfile.write(nomfichier)
                os.unlink(nomfichier)
        # fichiers CTD
        CTDFileParPSampleID = {}
        for S in samples:
            if S['nbrlinectd'] > 0:
                nomfichier="{0}_{1}_CTD_raw_{2}.tsv".format(S['filename'],S['profileid'],DTNomFichier)
                CTDFileParPSampleID[S["psampleid"]] = nomfichier
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier,"wt") as f:
                    cols=sorted(CTDFixedColByKey.keys())
                    cols.remove('datetime')
                    res=GetAll("""select to_char(datetime,'YYYYMMDDHH24MISSMS') as datetime,{},{} 
                                      from part_ctd where psampleid=%s 
                                      ORDER BY lineno""".format(
                                    ",".join(cols),",".join(["extrames%02d" % (i + 1) for i in range(20)]))
                               ,(S['psampleid'],))
                    cols.remove('depth')
                    cols = ["depth", "datetime"] + cols # passe dept et datetime en premieres colonnes
                    colsname = [CTDFixedColByKey[x] for x in cols]
                    CtdCustomCols=DecodeEqualList(S['ctd_desc'])
                    CtdCustomColsKeys=sorted(['extrames%s' % x for x in CtdCustomCols.keys()])
                    cols.extend(CtdCustomColsKeys)
                    colsname.extend([CtdCustomCols[x[-2:]] for x in CtdCustomColsKeys])

                    f.write("\t".join(colsname) + "\n")
                    for R in res:
                        L = [R[c] for c in cols]
                        f.write("\t".join((str(ntcv(x)) for x in L)))
                        f.write("\n")
                zfile.write(nomfichier)
        # Fichiers ZOO
        ZooFileParPSampleID = {}
        for S in samples:
            DepthOffset = S['acq_depthoffset']
            if DepthOffset is None:
                DepthOffset = S['default_depthoffset']
            if DepthOffset is None:
                DepthOffset = 0

            if self.samplesdict[S["psampleid"]][3][1] != 'Y':  # 3 = visibility, 1 =Second char=Zoo visibility
                continue  # pas les permission d'exporter le ZOO de ce sample le saute
            if S['nbrlinetaxo'] > 0:
                TaxoReverseMapping ={v:k for k,v in DecodeEqualList(ntcv(S['mappingobj'])).items()}
                nomfichier="{0}_{1}_ZOO_raw_{2}.tsv".format(S['filename'],S['profileid'],DTNomFichier)
                ZooFileParPSampleID[S["psampleid"]]=nomfichier
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier,"wt") as f:
                    # excludenotliving
                    sql="""select of.*
                        ,t0.display_name as "name", classif_qual ,ps.psampleid                        
                        ,((oh.depth_min+oh.depth_max)/2)+{DepthOffset} as depth_including_offset,objid
                        ,concat(t14.name||'>',t13.name||'>',t12.name||'>',t11.name||'>',t10.name||'>',t9.name||'>',t8.name||'>',t7.name||'>',
                                t6.name||'>',t5.name||'>',t4.name||'>',t3.name||'>',t2.name||'>',t1.name||'>',t0.name) taxo_hierarchy
                      from part_samples ps
                      join obj_head oh on ps.sampleid=oh.sampleid 
                      join obj_field of on of.objfid=oh.objid                      
                        join taxonomy t0 on oh.classif_id=t0.id
                        left join taxonomy t1 on t0.parent_id=t1.id
                        left join taxonomy t2 on t1.parent_id=t2.id
                        left join taxonomy t3 on t2.parent_id=t3.id
                        left join taxonomy t4 on t3.parent_id=t4.id
                        left join taxonomy t5 on t4.parent_id=t5.id
                        left join taxonomy t6 on t5.parent_id=t6.id
                        left join taxonomy t7 on t6.parent_id=t7.id
                        left join taxonomy t8 on t7.parent_id=t8.id
                        left join taxonomy t9 on t8.parent_id=t9.id
                        left join taxonomy t10 on t9.parent_id=t10.id
                        left join taxonomy t11 on t10.parent_id=t11.id
                        left join taxonomy t12 on t11.parent_id=t12.id
                        left join taxonomy t13 on t12.parent_id=t13.id
                        left join taxonomy t14 on t13.parent_id=t14.id                                           
                      where ps.psampleid=%s """.format(DepthOffset=DepthOffset)
                    if self.param.excludenotliving:
                        sql+=" and coalesce(t14.name,t13.name,t12.name,t11.name,t10.name,t9.name,t8.name,t7.name,t6.name,t5.name,t4.name,t3.name,t2.name,t1.name,t0.name)!='not-living' "
                    if self.param.includenotvalidated==False:
                        sql += " and oh.classif_qual='V' "
                    res = GetAll(sql,(S['psampleid'],))
                    cols=['orig_id','objid','name','taxo_hierarchy','classif_qual','depth_including_offset','psampleid']
                    extracols=list(TaxoReverseMapping.keys())
                    extracols.sort()
                    colsname=cols[:]
                    if extracols:
                        colsname.extend(extracols)
                        cols.extend([TaxoReverseMapping.get(x,None) for x in extracols])
                    f.write("\t".join(colsname) + "\n")
                    for R in res:
                        L = [R[c] if c else '' for c in cols]
                        f.write("\t".join((str(ntcv(x)) for x in L)))
                        f.write("\n")
                zfile.write(nomfichier)
        # Summary File
        cols = (
        'psampleid', 'pprojid', 'profileid', 'filename', 'sampleid', 'latitude', 'longitude', 'organizedbydeepth',
        'histobrutavailable',
        'qualitytaxo', 'qualitypart', 'daterecalculhistotaxo', 'winddir', 'winspeed', 'seastate', 'nebuloussness',
        'comment', 'stationid', 'firstimage',
        'lastimg', 'lastimgused', 'bottomdepth', 'yoyo', 'sampledate', 'op_sample_name', 'op_sample_email',
        'ctd_desc', 'ctd_origfilename', 'ctd_import_name',
        'ctd_import_email', 'ctd_import_datetime', 'ctd_status', 'instrumsn', 'acq_aa', 'acq_exp', 'acq_volimage',
        'acq_depthoffset', 'acq_pixel', 'acq_shutterspeed',
        'acq_smzoo', 'acq_exposure', 'acq_gain', 'acq_filedescription', 'acq_eraseborder', 'acq_tasktype',
        'acq_threshold', 'acq_choice', 'acq_disktype',
        'acq_smbase', 'acq_ratio', 'acq_descent_filter', 'acq_presure_gain', 'acq_xsize', 'acq_ysize',
        'acq_barcode', 'proc_datetime', 'proc_gamma', 'proc_soft',
        'lisst_zscat_filename', 'lisst_kernel', 'txt_data01', 'txt_data02', 'txt_data03', 'txt_data04',
        'txt_data05', 'txt_data06', 'txt_data07', 'txt_data08',
        'txt_data09', 'txt_data10', 'ptitle', 'rawfolder', 'ownerid', 'projid', 'instrumtype', 'op_name',
        'op_email', 'cs_name', 'cs_email', 'do_name', 'do_email',
        'prj_info', 'prj_acronym', 'cruise', 'ship', 'default_instrumsn', 'default_depthoffset')
        nomfichier = BaseFileName + "_Export_metadata_summary.tsv"
        fichier = os.path.join(self.GetWorkingDir(), nomfichier)
        with open(fichier, 'w', encoding='latin-1') as f:
            f.write("\t".join(cols) + "\tParticle filename\tCTD filename\tPlankton filename\n")
            for S in samples:
                L = [S[c] for c in cols]
                for i, v in enumerate(L):
                    if isinstance(v, str):
                        L[i] = '"' + v.replace('\n', '$') + '"'
                # L = [str(S[c]).replace('\n','$') for c in cols]
                L.extend(
                    [
                        "{0}_{1}_PAR_raw_{2}.tsv".format(S['filename'], S['profileid'], DTNomFichier) if S[
                            'histobrutavailable'] else None,
                        CTDFileParPSampleID[S["psampleid"]] if S["psampleid"] in CTDFileParPSampleID else "no data available",
                        ZooFileParPSampleID[S["psampleid"]] if S["psampleid"] in ZooFileParPSampleID else "no data available"
                    ])
                f.write("\t".join((str(ntcv(x)) for x in L)))
                f.write("\n")
        zfile.write(nomfichier)

    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__,))
        # dictionnaire par sample
        self.samplesdict={int(x[0]):x for x in self.param.samples}
        if self.param.what=="RED":
            self.CreateRED()
        elif self.param.what == "DET":
            self.CreateDET()
        elif self.param.what == "RAW":
            self.CreateRAW()
        else:
            raise Exception("Unsupported exportation type : %s"%(self.param.what,))

        if self.param.putfileonftparea=='Y':
            fichier = Path(self.GetWorkingDir()) /  self.param.OutFile
            fichierdest=Path(app.config['FTPEXPORTAREA'])
            if not fichierdest.exists():
                fichierdest.mkdir()
            NomFichier= "task_%d_%s"%(self.task.id,self.param.OutFile)
            fichierdest = fichierdest / NomFichier
            # fichier.rename(fichierdest) si ce sont des volumes sur des devices differents ça ne marche pas
            shutil.copyfile(fichier.as_posix(), fichierdest.as_posix())
            self.param.OutFile=''
            self.task.taskstate = "Done"
            self.UpdateProgress(100, "Export successfull : File '%s' is available on the 'Exported_data' FTP folder"%NomFichier)
        else:
            self.task.taskstate = "Done"
            self.UpdateProgress(100, "Export successfull")
        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")


    def QuestionProcess(self):
        backurl="/part/?{0}".format(str(request.query_string,'utf-8'))
        txt="<a href='{0}'>Back to Particle Module Home page</a>".format(backurl)
        txt+="<h3>Particle sample data export</h3>"
        errors=[]
        for k in request.args:
            if k in ('gpr','gpd','ctd'):
                None # ces champs sont completement ignorés
            elif k == 'taxolb':
                self.param.redfiltres['taxo'] = request.args.getlist('taxolb')
            elif k in ('taxochild','filt_depthmax','filt_depthmin') and gvg(k, "") != "":
                self.param.redfiltres[k] = gvg(k)
            elif gvg(k, "") != "" :
                self.param.filtres[k] = gvg(k, "")
        if len(self.param.filtres) > 0:
            TxtFiltres = ",".join([k + "=" + v for k, v in self.param.filtres.items() if v != ""])
        else: TxtFiltres=""
        # applique le filtre des sample et passe la liste à la tache car besoin de currentuser
        self.param.samples=GetFilteredSamples(Filter=self.param.filtres,GetVisibleOnly=True
                                  # Les exports Reduit Particule se contente de la visibité les autres requiert l'export
                                  # Pour le Zoo c'est traité dans la routine d'export elle même
                                  ,RequiredPartVisibility=('V' if self.param.what=='RED' else 'Y') )

        if self.task.taskstep==0:
            # Le projet de base est choisi second écran ou validation du second ecran
            if gvp('starttask')=="Y":
                # validation du second ecran
                self.param.what=gvp("what")
                self.param.user_name = current_user.name
                self.param.user_email = current_user.email
                self.param.fileformat=gvp("fileformat")
                self.param.putfileonftparea = gvp("putfileonftparea")
                if self.param.what == 'DET':
                    self.param.fileformat = gvp("fileformatd")
                    self.param.excludenotliving = (gvp("excludenotlivingd")=='Y')
                if self.param.what == 'RAW':
                    self.param.excludenotliving = (gvp("excludenotlivingr") == 'Y')
                    self.param.includenotvalidated=(gvp("includenotvalidatedr") == 'Y')
                self.param.CustomReturnLabel="Back to particle module"
                self.param.CustomReturnURL=gvp("backurl")

                if self.param.what=='' : errors.append("You must select What you want to export")
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else: # Pas d'erreur, on lance la tache
                    return self.StartTask(self.param)
            else: # valeurs par default
                self.param.what ="RED"
                self.param.fileformat = "ODV"

            LstUsers = database.GetAll("""select distinct u.email,u.name,Lower(u.name)
            FROM users_roles ur join users u on ur.user_id=u.id
            where ur.role_id=2
            and u.active=TRUE and email like '%@%'
            order by Lower(u.name)""")
            g.LstUser=",".join(["<a href='mailto:{0}'>{0}</a></li> ".format(*r) for r in LstUsers])

            return render_template('task/partexport_create.html',header=txt,data=self.param
                                   ,SampleCount=len(self.param.samples)
                                   ,RedFilter=",".join(("%s=%s"%(k,v) for k,v in self.param.redfiltres.items()))
                                   ,TxtFiltres=TxtFiltres
                                   ,GetPartDetClassLimitListTextResult=GetPartClassLimitListText(PartDetClassLimit)
                                   ,GetPartRedClassLimitListTextResult=GetPartClassLimitListText(PartRedClassLimit)
                                   ,backurl=backurl
                                   )



    def GetResultFile(self):
        return self.param.OutFile
