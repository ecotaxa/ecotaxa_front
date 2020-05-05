from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app, ObjectToStr, PrintInCharte, database, gvg, gvp, ntcv, DecodeEqualList, ScaleForDisplay, \
    ComputeLimitForImage, nonetoformat, CreateDirConcurrentlyIfNeeded, UtfDiag3
from pathlib import Path,PurePath
from PIL import  Image
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections,html,urllib.parse,zipfile,shutil
from appli.database import GetAll,GetClassifQualClass,db
import datetime

# Cache des Preset d'import simple, ayant la durée de vie de l'application (soit la journée en prod)
SimpleImportPreset={}

def PrintError(FlashMsg,BodyMsg):
    flash(FlashMsg, 'error')
    return PrintInCharte(BodyMsg)

def CreateObject(Prj,Metadata,ImageName,ImageFile):
    obj=database.Objects()
    obj.projid=Prj.projid
    obj.depth_min=Metadata['depthmin']
    obj.depth_max = Metadata['depthmax']
    obj.objdate=Metadata['imgdate']
    obj.objtime= Metadata['imgtime']
    obj.latitude= Metadata['latitude']
    obj.longitude = Metadata['longitude']
    obj.classif_id= Metadata['taxolb']
    if Metadata['taxolb']:
        obj.classif_who= Metadata['userlb']
        obj.classif_qual = Metadata['status']
    db.session.add(obj)
    db.session.commit()
    objf=database.ObjectsFields()
    objf.objfid=obj.objid
    objf.orig_id=obj.objid
    db.session.add(objf)
    db.session.commit()
    # Gestion de l'image, creation DB et fichier dans Vault
    Img=database.Images()
    Img.objid = obj.objid
    pgcur = db.engine.raw_connection().cursor()
    pgcur.execute("select nextval('seq_images')")
    Img.imgid=pgcur.fetchone()[0]
    VaultFolder = "%04d" % (Img.imgid // 10000)
    vaultroot = Path("vault")
    # creation du repertoire contenant les images si necessaire
    CreateDirConcurrentlyIfNeeded(vaultroot.joinpath(VaultFolder))
    vaultfilename = "%s/%04d%s" % (VaultFolder, Img.imgid % 10000, PurePath(ImageName).suffix)
    vaultfilenameThumb = "%s/%04d_mini%s" % (VaultFolder, Img.imgid % 10000, '.jpg')  # on Impose le format de la miniature
    Img.file_name = vaultfilename
    Img.orig_file_name=ImageName
    # copie du fichier image
    if isinstance(ImageFile,zipfile.ZipExtFile):
        with open(vaultroot.joinpath(vaultfilename).as_posix(), "wb") as target:
            shutil.copyfileobj(ImageFile, target)
    else:
        shutil.copyfile(ImageFile, vaultroot.joinpath(vaultfilename).as_posix())
    im = Image.open(vaultroot.joinpath(vaultfilename).as_posix())
    Img.width = im.size[0]
    Img.height = im.size[1]
    SizeLimit = app.config['THUMBSIZELIMIT']
    # génération d'une miniature si une image est trop grande.
    if (im.size[0] > SizeLimit) or (im.size[1] > SizeLimit):
        im.thumbnail((SizeLimit, SizeLimit))
        if im.mode == 'P':
            im = im.convert("RGB")
        im.save(vaultroot.joinpath(vaultfilenameThumb).as_posix())
        Img.thumb_file_name = vaultfilenameThumb
        Img.thumb_width = im.size[0]
        Img.thumb_height = im.size[1]
    # ajoute de l'image en DB
    Img.imgrank = 0  # valeur par defaut
    db.session.add(Img)
    db.session.commit()

def ConvDegTxtToDecimal(valdeg):
    """Convertie une valeur '12°25.358' en  25.42263 """
    splitted=valdeg.split("°")
    if len(splitted)==1:
        return splitted[0] # valeur passée en format numérique ou vide
    return round(float(splitted[0])+(float(splitted[1])/60),8)

@app.route('/prj/simpleimport/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prj_simpleimport(PrjId):
    Prj = database.Projects.query.filter_by(projid=PrjId).first()
    DefBodyMsg="<a href=//prj/simpleimport/%s>Simple Import Screen</a>"%(Prj.projid,)
    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid, Prj.title)
    if Prj is None:
        return PrintError("Project doesn't exists",DefBodyMsg)

    if not Prj.CheckRight(2):  # Level 0 = Read, 1 = Annotate, 2 = Admin
        return PrintError('You cannot edit settings for this project', DefBodyMsg)

    if gvp("doimport",'N')=='N':
        preset=SimpleImportPreset.get(current_user.id,{})
        # preset = {"imgdate": "20150327", "imgtime": "1447", "latitude": "-12.06398", "longitude": "-135.05325","depthmin": "50", "depthmax": "70","userlb":8,"status":'V'}
        if 'userlb' in preset and preset['userlb']:
            DbRes=GetAll("select name from users where id=(%s)", (preset['userlb'],))
            if DbRes:
                preset["annot_name"]=DbRes[0][0]
        # instrum=GetAll("select * from (SELECT DISTINCT  instrument  from acquisitions where instrument is not null) q order by upper(instrument)")
        # ,instrum=instrum
        return PrintInCharte(render_template("project/simpleimport.html",preset=preset))
    if gvp("doimport", 'N') == 'Y':
        txt=""
        ServerPath=z=None
        uploadfile = request.files.get("uploadfile")
        if uploadfile is not None and uploadfile.filename != '':  # import d'un fichier par HTTP
            txt = "Load file %s"%(uploadfile,)
            z=zipfile.ZipFile(uploadfile.stream)
        elif len(gvp("ServerPath")) < 2:
            return PrintError("Input Folder/File Too Short", DefBodyMsg)
        else:
            ServerRoot = Path(app.config['SERVERLOADAREA'])
            sp = ServerRoot.joinpath(Path(gvp("ServerPath")))
            if not sp.exists():  # verifie que le repertoire existe
                err = "Input Folder/File Invalid"
                err += UtfDiag3(str(sp))
                return PrintError(err, DefBodyMsg)
            else:
                ServerPath = sp.as_posix()
                if ServerPath.lower().endswith("zip"):
                    z = zipfile.ZipFile(ServerPath)
        fieldlist=("imgdate","imgtime","latitude","longitude","depthmin","depthmax","taxolb","userlb","status")
        Metadata={}
        for f in fieldlist:
            Metadata[f]=gvp(f)
            if Metadata[f]=="":
                Metadata[f]=None
        if Metadata["imgdate"]:
            if len(Metadata["imgdate"])!=8:
                return PrintError("Invalid Date size '%s' for Field Image date . Must be 8 digit YYYYMMDD" % (Metadata["imgdate"],),DefBodyMsg)
            try:
                datetime.date(int(Metadata["imgdate"][0:4]), int(Metadata["imgdate"][4:6]), int(Metadata["imgdate"][6:8]))
            except ValueError:
                return PrintError("Invalid Date value '%s' for Field Image date ." % (Metadata["imgdate"],),DefBodyMsg)
        if Metadata["imgtime"]:
            if len(Metadata["imgtime"])!=4:
                return PrintError("Invalid Time size '%s' for Field Image Time . Must be 4 digit HHMM" % (Metadata["imgtime"],),DefBodyMsg)
            try:
                datetime.time(int(Metadata["imgtime"][0:2]), int(Metadata["imgtime"][2:4]),0)
            except ValueError:
                return PrintError("Invalid Time value '%s' for Field Image time ." % (Metadata["imgtime"],),DefBodyMsg)
        if Metadata["taxolb"]:
            Metadata["taxolb"]=int(Metadata["taxolb"])
        if Metadata["latitude"]:
            Metadata["latitude"]=ConvDegTxtToDecimal(Metadata["latitude"])
        if Metadata["longitude"]:
            Metadata["longitude"]=ConvDegTxtToDecimal(Metadata["longitude"])
        SimpleImportPreset[current_user.id]=Metadata
        ObjCount=0
        if z: # Parcour d'un fichier zip uploadé ou sur le serveur
            Lst=z.infolist()
            for fichier in Lst:
                nomfichier=fichier.filename
                if nomfichier[0:8]=="__MACOSX":
                    continue
                nomfichierseul=os.path.basename(nomfichier)
                filename, file_extension = os.path.splitext(nomfichier)
                if file_extension.lower() in ('.jpg','.png','.gif'):
                    # txt+="<br>"+nomfichier
                    ObjCount+=1
                    with z.open(fichier) as source:
                        CreateObject(Prj,Metadata,nomfichierseul,source)
        elif ServerPath:
            sd = Path(ServerPath)
            for fichier in sd.glob('*'):
                nomfichier=fichier.as_posix()
                nomfichierseul=os.path.basename(nomfichier)
                filename, file_extension = os.path.splitext(nomfichier)
                if file_extension.lower() in ('.jpg','.png','.gif'):
                    # txt += "<br>" + nomfichier
                    ObjCount += 1
                    CreateObject(Prj, Metadata, nomfichierseul, nomfichier)
        else:
            return PrintError("File missing", DefBodyMsg)
        pgcur = db.engine.raw_connection().cursor()
        pgcur.execute("""update obj_head o
                            set imgcount=(select count(*) from images where objid=o.objid)
                            ,img0id=(select imgid from images where objid=o.objid order by imgrank asc limit 1 )
                            where projid="""+str(Prj.projid))
        pgcur.connection.commit()
        txt+="Imported %s images successfully<br><a href='/prj/%s' class='btn btn-primary'>Go to project</a>"%(ObjCount,Prj.projid)
        return PrintInCharte(txt)

    return PrintInCharte("Invalid state")
