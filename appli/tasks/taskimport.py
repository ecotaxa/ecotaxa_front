# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp
from PIL import Image
from flask import Blueprint, render_template, g, flash
from io import StringIO
import html,functools,logging,json,time,os
import datetime,shutil,random
from appli.tasks.taskmanager import AsyncTask,LoadTask
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class TaskImport(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            super().__init__(InitStr)
            if InitStr==None: # Valeurs par defaut ou vide pour init
                self.InData='My In Data'

    def __init__(self,task=None):
        super().__init__(task)
        if task==None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon")


    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__))
        logging.info("Start Step 1")
        progress=0
        for i in range(10):
            time.sleep(0.5)
            progress+=2
            self.UpdateProgress(progress,"My Message %d"%(progress))
        logging.info("End Step 1")
        self.task.taskstate="Question"
        db.session.commit()


    def SPStep2(self):
        logging.info("Start Step 2")
        for i in range(20,102,2):
            time.sleep(0.1)
            self.UpdateProgress(i,"My Step 2 Message %d"%(i))
        logging.info("End Step 2")


    def QuestionProcess(self):
        txt="<h1>Test Task</h1>"
        if self.task.taskstep==0:
            txt+="<h3>Task Creation</h3>"
            if gvp('starttask')=="Y":
                for k,v  in self.param.__dict__.items():
                    setattr(self.param,k,gvp(k))
                # Verifier la coherence des données
                if(len(self.param.InData)<5):
                    flash("Champ In Data trop court","error")
                else:
                    return self.StartTask(self.param)
            return render_template('task/testcreate.html',header=txt,data=self.param)
        if self.task.taskstep==1:
            txt+="<h3>Task Question 1</h3>"
            if gvp('starttask')=="Y":
                self.param.InData2=gvp("InData2")
                # Verifier la coherence des données
                if(len(self.param.InData2)<5):
                    flash("Champ In Data 2 trop court","error")
                else:
                    return self.StartTask(self.param,step=2)
            return render_template('task/testquestion1.html',header=txt,data=self.param)


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
    # t=LoadTask(1)
    # t.Process()
    # LoadHeader()
    LoadFile()