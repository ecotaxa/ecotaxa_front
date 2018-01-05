# -*- coding: utf-8 -*-
from appli import db,app, database ,PrintInCharte,gvp,gvg,DecodeEqualList
from flask import render_template, g, flash
import logging,os,csv,re,datetime
import zipfile,psycopg2.extras
from pathlib import Path
from appli.tasks.taskmanager import AsyncTask
from appli.database import GetAll
import xml.etree.ElementTree as ET
import appli.project.sharedfilter as sharedfilter

class TaskExportTxt(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            self.steperrors=[]
            super().__init__(InitStr)
            if InitStr is None: # Valeurs par defaut ou vide pour init
                self.ProjectId=None
                self.what=None  # TSV, XML, IMG , Summary
                self.Details=None
                self.OutFile=None
                self.filtres={}
                self.samplelist=""
                self.commentsdata = ''
                self.objectdata = ''
                self.sampledata = ''
                self.processdata = ''
                self.acqdata=''
                self.histodata = ''
                self.splitcsvby=''
                self.usecomasepa=''
                self.sumsubtotal=''
                self.internalids=''
                self.typeline=''
                self.putfileonftparea=''
                self.use_internal_image_name=''
                self.exportimages = ''



    def __init__(self,task=None):
        self.pgcur =None
        super().__init__(task)
        if task is None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon for Txt Export")
        self.pgcur=db.engine.raw_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)

    def CreateTSV(self):
        self.UpdateProgress(1,"Start TSV export")
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        sql1="""SELECT o.orig_id as object_id,o.latitude as object_lat,o.longitude as object_lon
                ,to_char(objdate,'YYYYMMDD') as object_date
                ,to_char(objtime,'HH24MISS') as object_time
                ,object_link,depth_min as object_depth_min,depth_max as object_depth_max
                ,case o.classif_qual when 'V' then 'validated' when 'P' then 'predicted' when 'D' then 'dubious' ELSE o.classif_qual end object_annotation_status                
                ,uo1.name object_annotation_person_name,uo1.email object_annotation_person_email
                ,to_char(o.classif_when,'YYYYMMDD') object_annotation_date
                ,to_char(o.classif_when,'HH24MISS') object_annotation_time
                ,img.orig_file_name as img_file_name
                    """
        if self.param.typeline == '1':
            sql1 += """,concat(to1.name,' ('||to1p.name||')') as object_annotation_category """
        else:
            sql1 += """,to1.name as object_annotation_category
                ,to1p.name as object_annotation_parent_category
                ,(WITH RECURSIVE rq(id,name,parent_id) as ( select id,name,parent_id,1 rang FROM taxonomy where id =o.classif_id
                        union
                        SELECT t.id,t.name,t.parent_id, rang+1 rang FROM rq JOIN taxonomy t ON t.id = rq.parent_id)
                        select string_agg(name,'>') from (select name from rq order by rang desc)q) object_annotation_hierarchy """

        sql2=""" FROM objects o
                LEFT JOIN taxonomy to1 on o.classif_id=to1.id
                LEFT JOIN taxonomy to1p on to1.parent_id=to1p.id
                LEFT JOIN users uo1 on o.classif_who=uo1.id
                LEFT JOIN taxonomy to2 on o.classif_auto_id=to2.id
                LEFT JOIN samples s on o.sampleid=s.sampleid 
                LEFT JOIN images img on o.img0id = img.imgid """
        sql3=" where o.projid=%(projid)s "
        params={'projid':int(self.param.ProjectId)}
        OriginalColName={} # Nom de colonneSQL => Nom de colonne permet de traiter le cas de %area
        if self.param.samplelist!="":
            sql3+=" and s.orig_id= any(%(samplelist)s) "
            params['samplelist']=self.param.samplelist.split(",")


        if self.param.commentsdata=='1':
            sql1+="\n,complement_info"
        if self.param.objectdata=='1':
            sql1+="\n"
            Mapping=DecodeEqualList(Prj.mappingobj)
            for k,v in Mapping.items() :
                AliasSQL='object_%s'%re.sub(R"[^a-zA-Z0-9\.\-]","_",v)
                OriginalColName[AliasSQL]='object_%s'%v
                sql1+=',o.%s as "%s" '%(k,AliasSQL)
        if self.param.sampledata=='1':
            sql1+="\n,s.orig_id sample_id,s.dataportal_descriptor as sample_dataportal_descriptor "
            Mapping=DecodeEqualList(Prj.mappingsample)
            for k,v in Mapping.items() :
                sql1+=',s.%s as "sample_%s" '%(k,re.sub(R"[^a-zA-Z0-9\.\-]","_",v))
        if self.param.processdata=='1':
            sql1+="\n,p.orig_id process_id"
            Mapping=DecodeEqualList(Prj.mappingprocess)
            for k,v in Mapping.items() :
                sql1+=',p.%s as "process_%s" '%(k,re.sub(R"[^a-zA-Z0-9\.\-]","_",v))
            sql2+=" left join process p on o.processid=p.processid "
        if self.param.acqdata=='1':
            sql1+="\n,a.orig_id acq_id,a.instrument as acq_instrument"
            Mapping=DecodeEqualList(Prj.mappingacq)
            for k,v in Mapping.items() :
                sql1+=',a.%s as "acq_%s" '%(k,re.sub(R"[^a-zA-Z0-9\.\-]","_",v))
            sql2+=" left join acquisitions a on o.acquisid=a.acquisid "
        if self.param.internalids == '1':
            sql1 += """\n,o.objid,o.acquisid as acq_id_internal,o.processid as processid_internal,o.sampleid as sample_id_internal,o.classif_id,o.classif_who
                        ,o.classif_auto_id,to2.name classif_auto_name,classif_auto_score,classif_auto_when
                        ,o.random_value object_random_value,o.sunpos object_sunpos """
            if self.param.sampledata == '1':
                sql1 += "\n,s.latitude sample_lat,s.longitude sample_long "

        if self.param.histodata=='1':
            if self.param.samplelist!="": # injection du filtre sur les echantillons dans les historique
                samplefilter=" join samples s on o.sampleid=s.sampleid and s.orig_id= any(%(samplelist)s) "
            else: samplefilter=""
            sql1+=" ,oh.classif_date histoclassif_date,classif_type histoclassif_type,to3.name histoclassif_name,oh.classif_qual histoclassif_qual,uo3.name histoclassif_who,classif_score histoclassif_score"
            sql2+=""" left join (SELECT o.objid,classif_date,classif_type,och.classif_id,och.classif_qual,och.classif_who,classif_score
                    from objectsclassifhisto och
                    join objects o on o.objid=och.objid and o.projid=1 {0}
                    union all
                    SELECT o.objid,o.classif_when classif_date,'C' classif_type,classif_id,classif_qual,classif_who,NULL
                    from objects o {0} where o.projid=1
                    )oh on o.objid=oh.objid
                    LEFT JOIN taxonomy to3 on oh.classif_id=to3.id
                    LEFT JOIN users uo3 on oh.classif_who=uo3.id
                    """.format(samplefilter)

        sql3+=sharedfilter.GetSQLFilter(self.param.filtres,params,self.task.owner_id)
        splitfield="object_id" # cette valeur permet d'éviter des erreurs plus loins dans r[splitfield]
        if self.param.splitcsvby=="sample":
            sql3+=" order by s.orig_id, o.objid "
            splitfield = "sample_id"
        if self.param.splitcsvby=="taxo":
            sql1 += "\n,concat(to1p.name,'_',to1.name) taxo_parent_child "
            sql3+=" order by taxo_parent_child, o.objid "
            splitfield = "taxo_parent_child"

        sql=sql1+" "+sql2+" "+sql3
        logging.info("Execute SQL : %s"%(sql,))
        logging.info("Params : %s"%(params,))
        self.pgcur.execute(sql,params)
        splitcsv = (self.param.splitcsvby != "")
        self.param.OutFile= "export_{0:d}_{1:s}.{2}".format(Prj.projid
                                                            ,datetime.datetime.now().strftime("%Y%m%d_%H%M")
                                                            ,"zip"  )

        zfile = zipfile.ZipFile(os.path.join(self.GetWorkingDir(),self.param.OutFile)
                                , 'w', allowZip64=True, compression=zipfile.ZIP_DEFLATED)
        if splitcsv:
            csvfilename='temp.tsv'
            prevvalue = "NotAssigned"
        else:
            csvfilename =self.param.OutFile.replace('.zip','.tsv')
            prevvalue = self.param.OutFile.replace('.zip', '')
        fichier=os.path.join(self.GetWorkingDir(),csvfilename)
        csvfile=None
        for r in self.pgcur:
            if (csvfile is None and (splitcsv == False)) or ((prevvalue!=r[splitfield]) and splitcsv ):
                if csvfile :
                    csvfile.close()
                    if zfile :
                        zfile.write(fichier,"ecotaxa_"+prevvalue+".tsv")
                if splitcsv:
                    prevvalue = r[splitfield]
                logging.info("Creating file %s" % (fichier,))
                csvfile=open(fichier,'w',encoding='latin_1')
                wtr = csv.writer(csvfile, delimiter='\t', quotechar='"',lineterminator='\n',quoting=csv.QUOTE_NONNUMERIC  )
                colnames = [desc[0] for desc in self.pgcur.description]
                coltypes=[desc[1] for desc in self.pgcur.description]
                FloatType=coltypes[2] # on lit le type de la colonne 2 alias latitude pour determiner le code du type double
                wtr.writerow([OriginalColName.get(c,c) for c in colnames])
                if self.param.typeline=='1':
                    wtr.writerow(['[f]' if x==FloatType else '[t]' for x in coltypes])
            # on supprime les CR des commentaires.
            if self.param.commentsdata == '1' and r['complement_info']:
                r['complement_info'] = ' '.join(r['complement_info'].splitlines())
            if self.param.usecomasepa == '1':  # sur les decimaux on remplace . par ,
                for i, t in zip(range(1000), coltypes):
                    if t == FloatType and r[i] is not None:
                        r[i] = str(r[i]).replace('.', ',')
            wtr.writerow(r)
        if csvfile:
            csvfile.close()
            if zfile:
                zfile.write(fichier, "ecotaxa_"+str(prevvalue) + ".tsv")
                zfile.close()
        logging.info("Extracted %d rows", self.pgcur.rowcount)

    def CreateXML(self):
        self.UpdateProgress(1,"Start XML export")
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()

        self.param.OutFile= "export_{0:d}_{1:s}.xml".format(Prj.projid,
                                                             datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        fichier=os.path.join(self.GetWorkingDir(),self.param.OutFile)
        logging.info("Creating file %s"%(fichier,))
        root = ET.Element('projects',{ "xmlns":"http://typo.oceanomics.abims.sbr.fr/ecotaxa-export"
                 ,"xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance"
                 ,"xsi:schemaLocation":"http://typo.oceanomics.abims.sbr.fr/ecotaxa-export platform:/resource/typo-shared/src/main/resources/ecotaxa-export-1.1.xsd"})

        Project=ET.SubElement(root, 'project',{'id':"ecotaxa:%d"%Prj.projid})
        projectdescription=ET.SubElement(Project, 'projectdescription')
        projectdescriptionname=ET.SubElement(projectdescription, 'name')
        projectdescriptionname.text=Prj.title
        ET.SubElement(projectdescription, 'link',{"url":"%sprj/%d"%(app.config['SERVERURL'],Prj.projid)})
        projectdescriptionmanagers=ET.SubElement(projectdescription, 'managers')
        projectdescriptionanno=ET.SubElement(projectdescription, 'contributors')
        for pm in Prj.projmembers:
            if pm.privilege=="Manage":
                m=ET.SubElement(projectdescriptionmanagers, 'manager')
            elif pm.privilege=="Annotate":
                m=ET.SubElement(projectdescriptionanno, 'contributor')
            else: continue
            ET.SubElement(m, 'name').text=pm.memberrel.name
            ET.SubElement(m, 'email').text=pm.memberrel.email

        sql1="""SELECT s.sampleid,s.orig_id,s.dataportal_descriptor
                 From samples s
                   where projid=%(projid)s """
        sql3=" "
        params={'projid':int(self.param.ProjectId)}
        if self.param.samplelist!="":
            sql3+=" and s.orig_id= any(%(samplelist)s) "
            params['samplelist']=self.param.samplelist.split(",")

        sql=sql1+" "+sql3
        logging.info("Execute SQL : %s"%(sql,))
        logging.info("Params : %s"%(params,))
        self.pgcur.execute(sql,params)

        samples=ET.SubElement(Project, 'samples')
        for r in self.pgcur:
            sel=ET.SubElement(samples, 'sample')
            dtpdesc=ET.fromstring(r['dataportal_descriptor'])
            sel.append(dtpdesc)
            ET.SubElement(sel, 'sampleregistryreference',barcode=r['orig_id'])

            sql= """SELECT distinct to1.name
                FROM objects o
                LEFT JOIN taxonomy to1 on o.classif_id=to1.id
                where o.sampleid={0:d}
                """.format(r['sampleid'], )
            taxo=GetAll(sql)
            taxoel=ET.SubElement(sel, 'taxonomicassignments')
            for r in taxo:
                ET.SubElement(taxoel, 'taxonomicassignment',taxon=r[0])

        ET.ElementTree(root).write(fichier,encoding="UTF-8", xml_declaration=True)

    def CreateIMG(self):
        self.CreateTSV()
        tsvfile=self.param.OutFile
        self.UpdateProgress(1,"Start Image export")
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        self.param.OutFile= "exportimg_{0:d}_{1:s}.zip".format(Prj.projid,
                                                             datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        fichier=os.path.join(self.GetWorkingDir(),self.param.OutFile)
        logging.info("Creating file %s"%(fichier,))
        zfile=zipfile.ZipFile(fichier, 'w',allowZip64 = True,compression= zipfile.ZIP_DEFLATED)
        zfile.write(tsvfile)

        sql="""SELECT i.objid,i.file_name,i.orig_file_name,t.name,concat(to1p.name,'_',t.name) taxo_parent_child
                 From objects o left join samples s on o.sampleid=s.sampleid
                 join images i on o.objid=i.objid
                 left join taxonomy t on o.classif_id=t.id
                 LEFT JOIN taxonomy to1p on t.parent_id=to1p.id
                   where o.projid=%(projid)s """
        params={'projid':int(self.param.ProjectId)}
        if self.param.samplelist!="":
            sql+=" and s.orig_id= any(%(samplelist)s) "
            params['samplelist']=self.param.samplelist.split(",")

        sql+=sharedfilter.GetSQLFilter(self.param.filtres,params,self.task.owner_id)

        logging.info("Execute SQL : %s"%(sql,))
        logging.info("Params : %s"%(params,))
        self.pgcur.execute(sql,params)
        vaultroot=Path("../../vault")
        for r in self.pgcur:
            if self.param.use_internal_image_name != '1': # r0=objod, r2=orig_file_name,r4 parent_taxo
                zfile.write(vaultroot.joinpath(r[1]).as_posix(), arcname="{0}/{1}".format(r[4], r[2]))
            else:
                zfile.write(vaultroot.joinpath(r[1]).as_posix(),arcname="{2}/{0}_{1}".format(r[0],r[2],r[4]))

    def CreateSUM(self):
        self.UpdateProgress(1,"Start Summary export")
        Prj=database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        grp="to1.name"
        if self.param.sumsubtotal=="A":
            grp="a.orig_id,"+grp
        if self.param.sumsubtotal=="S":
            grp="s.orig_id,"+grp
        sql1="SELECT "+grp+" ,count(*) Nbr "
        sql2=""" FROM objects o
                LEFT JOIN taxonomy to1 on o.classif_id=to1.id
                LEFT JOIN samples s on o.sampleid=s.sampleid
                LEFT JOIN acquisitions a on o.acquisid=a.acquisid """
        sql3=" where o.projid=%(projid)s "
        params={'projid':int(self.param.ProjectId)}
        if self.param.samplelist!="":
            sql3+=" and s.orig_id= any(%(samplelist)s) "
            params['samplelist']=self.param.samplelist.split(",")
        sql3+= sharedfilter.GetSQLFilter(self.param.filtres, params, self.task.owner_id)
        sql3+=" group by "+grp
        sql3+=" order by "+grp
        sql=sql1+" "+sql2+" "+sql3
        logging.info("Execute SQL : %s"%(sql,))
        logging.info("Params : %s"%(params,))
        self.pgcur.execute(sql,params)

        self.param.OutFile= "export_summary_{0:d}_{1:s}.tsv".format(Prj.projid,
                                                             datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        fichier=os.path.join(self.GetWorkingDir(),self.param.OutFile)
        logging.info("Creating file %s"%(fichier,))
        with open(fichier,'w',encoding='latin_1') as csvfile:
            # lecture en mode dictionnaire basé sur la premiere ligne
            wtr = csv.writer(csvfile, delimiter='\t', quotechar='"',lineterminator='\n' )
            colnames = [desc[0] for desc in self.pgcur.description]
            wtr.writerow(colnames)
            for r in self.pgcur:
                wtr.writerow(r)
        logging.info("Extracted %d rows",self.pgcur.rowcount)

    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__,))
        if self.param.what=="TSV":
            if self.param.exportimages=='1':
                self.CreateIMG()
            else:
                self.CreateTSV()
        elif self.param.what=="XML":
            self.CreateXML()
        elif self.param.what=="SUM":
            self.CreateSUM()
        else:
            raise Exception("Unsupported exportation type : %s"%(self.param.what,))

        if self.param.putfileonftparea=='Y':
            fichier = Path(self.GetWorkingDir()) /  self.param.OutFile
            fichierdest=Path(app.config['FTPEXPORTAREA'])
            if not fichierdest.exists():
                fichierdest.mkdir()
            NomFichier= "task_%d_%s"%(self.task.id,self.param.OutFile)
            fichierdest = fichierdest / NomFichier
            fichier.rename(fichierdest)
            self.param.OutFile=''
            self.task.taskstate = "Done"
            self.UpdateProgress(100, "Export successfull : File '%s' is available on the 'Exported_data' FTP folder"%NomFichier)
        else:
            self.task.taskstate = "Done"
            self.UpdateProgress(100, "Export successfull")


        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")


    def QuestionProcess(self):
        Prj=database.Projects.query.filter_by(projid=gvg("projid")).first()
        txt="<a href='/prj/%d'>Back to project</a>"%Prj.projid
        if not Prj.CheckRight(1):
            return PrintInCharte("ACCESS DENIED for this project<br>"+txt)
        txt+="<h3>Text export Task creation</h3>"
        txt+="<h5>Exported Project : #%d - %s</h5>"%(Prj.projid,Prj.title)
        errors=[]
        self.param.filtres = {}
        for k in sharedfilter.FilterList:
            if gvg(k, "") != "":
                self.param.filtres[k] = gvg(k, "")
        if len(self.param.filtres) > 0:
            TxtFiltres = ",".join([k + "=" + v for k, v in self.param.filtres.items() if v != ""])
        else: TxtFiltres=""

        if self.task.taskstep==0:
            # Le projet de base est choisi second écran ou validation du second ecran
            if gvp('starttask')=="Y":
                # validation du second ecran
                self.param.ProjectId=gvg("projid")
                self.param.what=gvp("what")
                self.param.samplelist=gvp("samplelist")
                self.param.objectdata=gvp("objectdata")
                self.param.processdata=gvp("processdata")
                self.param.acqdata=gvp("acqdata")
                self.param.sampledata=gvp("sampledata")
                self.param.histodata=gvp("histodata")
                self.param.commentsdata=gvp("commentsdata")
                self.param.usecomasepa=gvp("usecomasepa")
                self.param.sumsubtotal=gvp("sumsubtotal")
                self.param.internalids = gvp("internalids")
                self.param.use_internal_image_name = gvp("use_internal_image_name")
                self.param.exportimages = gvp("exportimages")
                self.param.typeline = gvp("typeline")
                self.param.splitcsvby = gvp("splitcsvby")
                self.param.putfileonftparea = gvp("putfileonftparea")
                if self.param.splitcsvby=='sample': # si on splitte par sample, il faut les données du sample
                    self.param.sampledata='1'
                # Verifier la coherence des données
                # errors.append("TEST ERROR")
                if self.param.what=='' : errors.append("You must select What you want to export")
                if len(errors)>0:
                    for e in errors:
                        flash(e,"error")
                else: # Pas d'erreur, on lance la tache
                    return self.StartTask(self.param)
            else: # valeurs par default
                self.param.what ="TSV"
                self.param.objectdata = "1"
                self.param.processdata = "1"
                self.param.acqdata = "1"
                self.param.sampledata = "1"
                self.param.splitcsvby="sample"
            #recupere les samples
            sql="""select sampleid,orig_id
                    from samples where projid =%(projid)s
                    order by orig_id"""
            g.SampleList=GetAll(sql,{"projid":gvg("projid")},cursor_factory=None)
            g.headcenter="<h4>Project : <a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title);
            if TxtFiltres!="":
                g.headcenter = "<h4>Project : <a href='/prj/{0}?{2}'>{1}</a></h4>".format(Prj.projid, Prj.title,
                    "&".join([k + "=" + v for k, v in self.param.filtres.items() if v != ""]))
            LstUsers = database.GetAll("""select distinct u.email,u.name,Lower(u.name)
                        FROM users_roles ur join users u on ur.user_id=u.id
                        where ur.role_id=2
                        and u.active=TRUE and email like '%@%'
                        order by Lower(u.name)""")
            g.LstUser = ",".join(["<a href='mailto:{0}'>{0}</a></li> ".format(*r) for r in LstUsers])
            return render_template('task/textexport_create.html',header=txt,data=self.param,TxtFiltres=TxtFiltres)



    def GetResultFile(self):
        return self.param.OutFile
