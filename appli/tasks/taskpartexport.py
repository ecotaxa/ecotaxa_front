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
from appli.part import PartDetClassLimit,PartRedClassLimit,GetClassLimitTxt,CTDFixedColByKey

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


    def __init__(self,task=None):
        self.pgcur =None
        super().__init__(task)
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon for Part Export")
        self.pgcur=db.engine.raw_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)

    def CreateRED(self):
        logging.info("CreateRED Input Param = %s"%(self.param.__dict__))
        AsODV=(self.param.fileformat=='ODV')
        # Prj=partdatabase.part_projects.query.filter_by(pprojid=self.param.pprojid).first()
        logging.info("samples = %s" % (self.param.samples ))
        sql="""SELECT  p.cruise,s.stationid site,s.profileid station,'HDR'||s.filename rawfilename
                ,concat(p.instrumtype,'_',s.instrumsn) uvptype,coalesce(ctd_origfilename,'') ctd_origfilename
                ,to_char(s.sampledate,'YYYY-MM-DD HH24:MI:SS') sampledate,concat(p.do_name,'(',do_email,')') dataowner
                ,s.latitude,s.longitude,s.psampleid
                from part_samples s
                join part_projects p on s.pprojid = p.pprojid
                where s.psampleid in (%s)
                """%((",".join([str(x[0]) for x in self.param.samples])))
        samples=database.GetAll(sql)
        BaseFileName="export_reduced_{0:s}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M") )
        self.param.OutFile= BaseFileName+".zip"
        zfile = zipfile.ZipFile(os.path.join(self.GetWorkingDir(), self.param.OutFile)
                                , 'w', allowZip64=True, compression=zipfile.ZIP_DEFLATED)
        CTDFixedCols=list(CTDFixedColByKey.keys())
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
                join ({0}) ctd on h.depth=ctd.tranche
                where psampleid=(%s) {1}
                order by h.datetime,h.depth """.format(ctdsql,DepthFilter)
        logging.info("sql = %s" % (sqlhisto))
        logging.info("samples = %s" % (samples))
        # -------------------------- Fichier Particules --------------------------------
        if AsODV:
            nomfichier = BaseFileName + "_part_odv.txt"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier,'w',encoding='latin-1') as f:
                f.write("//<Creator>%s</Creator>\n"%("marc.picheral@obs-vlfr.fr")) # TODO
                f.write("//<CreateTime>%s</CreateTime>\n" % (datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")))
                f.write("//<DataField>Ocean</DataField>\n//<DataType>Profiles</DataType>\n//<Method>Particle abundance and volume from the Underwater Vision Profiler. The Underwater Video Profiler is designed for the quantification of particles and of large zooplankton in the water column. Light reflected by undisturbed target objects forms a dark-field image.</Method>\n")
            #TODO Ajouter Owner
                f.write("Cruise:METAVAR:TEXT:20;Site:METAVAR:TEXT:20;Station:METAVAR:TEXT:20;DataOwner:METAVAR:TEXT:20;Rawfilename:METAVAR:TEXT:20;UVPtype:METAVAR:TEXT:6;CTDrosettefilename:METAVAR:TEXT:40;yyyy-mm-dd hh:mm:METAVAR:TEXT:40;Latitude [degrees_north]:METAVAR:DOUBLE;Longitude [degrees_east]:METAVAR:DOUBLE;Depth [m]:PRIMARYVAR:DOUBLE;Sampled volume[L]")
                for i in range(len(PartRedClassLimit)):
                    f.write(";LPM (%s)[#/L]"%(GetClassLimitTxt(PartRedClassLimit,i)))
                for i in range(len(PartRedClassLimit)):
                    f.write(";LPM biovolume (%s)[ppm]" % (GetClassLimitTxt(PartRedClassLimit, i)))
                for c in CTDFixedCols:
                    f.write(";%s" % (CTDFixedColByKey.get(c,c)))

                f.write("\n")
                for S in samples:
                    L=[S['cruise'],S['site'],S['station'],S['dataowner'],S['rawfilename'],S['uvptype'],S['ctd_origfilename'],S['sampledate'],S['latitude'],S['longitude']]
                    self.pgcur.execute(sqlhisto, [S["psampleid"],S["psampleid"]])
                    for h in self.pgcur:
                        if ntcv(h['fdatetime'])!='':
                            L[7]=S['sampledate']
                        else: L[7]=h['fdatetime']
                        if not AsODV: # si TSV
                            L=[S['station'],S['rawfilename'],L[7]] # station + rawfilename + sampledate
                        L.extend([h['depth'],h['watervolume']])
                        L.extend((h['class%02d'%i] for i in range(1,16)))
                        L.extend((h['biovol%02d' % i] for i in range(1, 16)))
                        f.write(";".join((str(ntcv(x)) for x in L)))
                        for c in CTDFixedCols:
                            f.write(";%s" % (ntcv(h["ctd_"+c])))
                        f.write("\n")
                        L=['','','','','','','','','','']
            zfile.write(nomfichier)
        else:  # -------- Particule TSV --------------------------------
            for S in samples:
                nomfichier = BaseFileName + "_part_"+S['station']+".tsv" # nommé par le profileid qui est dans le champ station
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier, 'w', encoding='latin-1') as f:
                    f.write("Profile\tRawfilename\tyyyy-mm-dd hh:mm\tDepth [m]\tSampled volume[L]")
                    for i in range(len(PartRedClassLimit)):
                        f.write("\tLPM (%s)[#/L]" % (GetClassLimitTxt(PartRedClassLimit, i)))
                    for i in range(len(PartRedClassLimit)):
                        f.write("\tLPM biovolume (%s)[ppm]" % (GetClassLimitTxt(PartRedClassLimit, i)))
                    f.write("\n")
                    self.pgcur.execute(sqlhisto, [S["psampleid"],S["psampleid"]])
                    for h in self.pgcur:
                        if ntcv(h['fdatetime']) != '':
                            L = [S['station'], S['rawfilename'], S['sampledate'] ]
                        else:
                            L = [S['station'], S['rawfilename'], h['fdatetime'] ]
                        L.extend([h['depth'], h['watervolume']])
                        L.extend((h['class%02d' % i] for i in range(1, 16)))
                        L.extend((h['biovol%02d' % i] for i in range(1, 16)))
                        f.write("\t".join((str(ntcv(x)) for x in L)))
                        f.write("\n")
                zfile.write(nomfichier)

        # --------------- Traitement fichier par categorie -------------------------------
        TaxoList=self.param.redfiltres.get('taxo',[])
        # On liste les categories pour fixer les colonnes de l'export
        # if self.param.redfiltres.get('taxochild','')=='1' and len(TaxoList)>0:
        if len(TaxoList) > 0:
            # c'est la liste des taxo passées en paramètres
            sqllstcat = """select t.id,concat(t.name,'(',p.name,')') nom, rank() over (order by p.name,t.name)-1 idx
                        from taxonomy t 
                        left JOIN taxonomy p on t.parent_id=p.id
                        where t.id in ({0})
                        """.format(",".join([str(x) for x in TaxoList]))
            logging.info("sqllstcat = %s" % (sqllstcat))
        else:
            sqllstcat="""select t.id,concat(t.name,'(',p.name,')') nom, rank() over (order by p.name,t.name)-1 idx
                    from (select distinct classif_id from part_histocat where psampleid in ( {0}) {1} ) cat
                    join taxonomy t on cat.classif_id=t.id
                    left JOIN taxonomy p on t.parent_id=p.id
                    """.format((",".join([str(x[0]) for x in self.param.samples])),DepthFilter)
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
            sqlhisto = """select  classif_id,lineno,psampleid,depth,watervolume ,avg(avgesd) avgesd,sum(nbr) nbr,sum(totalbiovolume) totalbiovolume 
                from ("""+sqlhisto+""" ) q
                group by classif_id,lineno,psampleid,depth,watervolume
                order by lineno """
        else:
            sqlhisto="""select h.* from part_histocat h where psampleid=%(psampleid)s {0}
                order by lineno """.format(DepthFilter)
        lstcat=GetAssoc(sqllstcat)
        if AsODV:
            nomfichier = BaseFileName + "_cat_odv.txt"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier, 'w', encoding='latin-1') as f:
                f.write("//<Creator>%s</Creator>\n" % ("marc.picheral@obs-vlfr.fr"))  # TODO
                f.write("//<CreateTime>%s</CreateTime>\n" % (datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")))
                f.write("//<DataField>Ocean</DataField>\n//<DataType>Profiles</DataType>\n//<Method>Particle abundance and volume from the Underwater Vision Profiler. The Underwater Video Profiler is designed for the quantification of particles and of large zooplankton in the water column. Light reflected by undisturbed target objects forms a dark-field image.</Method>\n")
                # TODO Ajouter Owner
                f.write(
                    "Cruise:METAVAR:TEXT:20;Site:METAVAR:TEXT:20;Station:METAVAR:TEXT:20;DataOwner:METAVAR:TEXT:20;Rawfilename:METAVAR:TEXT:20;UVPtype:METAVAR:TEXT:6;CTDrosettefilename:METAVAR:TEXT:40;yyyy-mm-dd hh:mm:METAVAR:TEXT:40;Latitude [degrees_north]:METAVAR:DOUBLE;Longitude [degrees_east]:METAVAR:DOUBLE;Depth [m]:PRIMARYVAR:DOUBLE;Sampled volume[L]")
                for k,v in lstcat.items():
                    f.write(";%s[#/L]" % (v['nom']))
                for k,v in lstcat.items():
                    f.write(";%s biovolume[ppm]" % (v['nom']))
                for k,v in lstcat.items():
                    f.write(";%s avgesd[mm3]" % (v['nom']))
                f.write("\n")
                for S in samples:
                    L=[S['cruise'],S['site'],S['station'],S['dataowner'],S['rawfilename'],S['uvptype'],S['ctd_origfilename'],S['sampledate'],S['latitude'],S['longitude']]
                    t = [None for i in range(3 * len(lstcat))]
                    CatHisto=GetAll(sqlhisto, {'psampleid':S["psampleid"]})
                    for i in range(len(CatHisto)):
                        h=CatHisto[i]
                        idx=lstcat[h['classif_id']]['idx']
                        t[idx]=h['nbr']
                        t[idx+len(lstcat)] = h['totalbiovolume']
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
                            L=['','','','','','','','','','']
            zfile.write(nomfichier)
        else: # ------------ Categories AS TSV
            for S in samples:
                nomfichier = BaseFileName + "_cat_"+S['station']+".tsv" # nommé par le profileid qui est dans le champ station
                fichier = os.path.join(self.GetWorkingDir(), nomfichier)
                with open(fichier, 'w', encoding='latin-1') as f:
                    f.write("Profile\tRawfilename\tyyyy-mm-dd hh:mm\tDepth [m]\tSampled volume[L]")
                    for k, v in lstcat.items():
                        f.write("\t%s[#/L]" % (v['nom']))
                    for k, v in lstcat.items():
                        f.write("\t%s biovolume[ppm]" % (v['nom']))
                    for k, v in lstcat.items():
                        f.write("\t%s avgesd[mm3]" % (v['nom']))
                    f.write("\n")
                    t = [None for i in range(3 * len(lstcat))]
                    CatHisto = GetAll(sqlhisto, {'psampleid',S["psampleid"]})
                    for i in range(len(CatHisto)):
                        h = CatHisto[i]
                        idx = lstcat[h['classif_id']]['idx']
                        t[idx] = h['nbr']
                        t[idx + len(lstcat)] = h['totalbiovolume']
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
            nomfichier = BaseFileName + "_sum.tsv"
            fichier = os.path.join(self.GetWorkingDir(), nomfichier)
            with open(fichier,'w',encoding='latin-1') as f:
                f.write("profile\tCruise\tSite\tDataOwner\tRawfilename\tUVPtype\tCTDrosettefilename\tyyyy-mm-dd hh:mm\tLatitude \tLongitude\tParticle filename\tCategory filename\n")

                for S in samples:
                    L = [S['station'],S['cruise'], S['site'],  S['dataowner'], S['rawfilename'], S['uvptype'],
                         S['ctd_origfilename'], S['sampledate'], S['latitude'], S['longitude']
                         ,BaseFileName + "_part_"+S['station']+".tsv"
                        , BaseFileName + "_cat_" + S['station'] + ".tsv"]
                    f.write("\t".join((str(ntcv(x)) for x in L)))
                    f.write("\n")
            zfile.write(nomfichier)

    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__,))
        if self.param.what=="TSV":
            self.CreateTSV()
        elif self.param.what=="RED":
            self.CreateRED()
        else:
            raise Exception("Unsupported exportation type : %s"%(self.param.what,))

        self.task.taskstate="Done"
        self.UpdateProgress(100,"Export successfull")
        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")


    def QuestionProcess(self):
        # TODO Sécurité
        txt="<a href='/part/'>Back to Particle Module Home page</a>"
        txt+="<h3>Particle sample data export Task creation</h3>"
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
        self.param.samples=GetFilteredSamples(Filter=self.param.filtres,GetVisibleOnly=True)

        if self.task.taskstep==0:
            # Le projet de base est choisi second écran ou validation du second ecran
            if gvp('starttask')=="Y":
                # validation du second ecran
                self.param.what=gvp("what")
                self.param.user_name = current_user.name
                self.param.user_email = current_user.email
                self.param.fileformat=gvp("fileformat")
                # TODO appliquer le filtre des sample et passer la liste à la tache car besoin de currentuser
                if self.param.what=='' : errors.append("You must select What you want to export")
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else: # Pas d'erreur, on lance la tache
                    return self.StartTask(self.param)
            else: # valeurs par default
                self.param.what ="RED"
                self.param.fileformat = "ODV"



            return render_template('task/partexport_create.html',header=txt,data=self.param
                                   ,SampleCount=len(self.param.samples)
                                   ,RedFilter=",".join(("%s=%s"%(k,v) for k,v in self.param.redfiltres.items()))
                                   ,TxtFiltres=TxtFiltres)



    def GetResultFile(self):
        return self.param.OutFile
