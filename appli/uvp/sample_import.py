from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,VaultRootDir,DecodeEqualList,ntcv,EncodeEqualList,CreateDirConcurrentlyIfNeeded
from pathlib import Path
import appli.uvp.database as uvpdatabase, logging,re,datetime,csv,math
import numpy as np
import matplotlib.pyplot as plt
from appli import database
from appli.uvp import PartDetClassLimit
from flask_login import current_user

# Purge les espace et converti le Nan en vide
def CleanValue(v):
    if type(v) != str:
        return v
    v=v.strip()
    if v.lower()=='nan':
        v=''
    if v.lower().find('inf')>=0:
        v=''
    return v
# retourne le flottant image de la chaine en faisant la conversion ou None
def ToFloat(value):
    if value=='': return None
    try:
        return float(value)
    except ValueError:
        return None


def CreateOrUpdateSample(uprojid,headerdata):
    """
    Crée ou met à jour le sample
    :param uprojid:
    :param headerdata:
    :return: Objet BD sample
    """
    Prj = uvpdatabase.uvp_projects.query.filter_by(uprojid=uprojid).first()
    for k,v in headerdata.items():
        headerdata[k]=CleanValue(v)
    Sample=uvpdatabase.uvp_samples.query.filter_by(profileid=headerdata['profileid'],uprojid=uprojid).first()
    if Sample is None:
        logging.info("Create sample for %s %s"%(headerdata['profileid'],headerdata['filename']))
        Sample = uvpdatabase.uvp_samples()
        Sample.profileid=headerdata['profileid']
        Sample.uprojid=uprojid
        db.session.add(Sample)
    else:
        logging.info("Update sample %s for %s %s" % (Sample.usampleid,headerdata['profileid'], headerdata['filename']))
    Sample.filename=headerdata['filename']
    Sample.sampledate=datetime.datetime(int(headerdata['filename'][0:4]),int(headerdata['filename'][4:6]),int(headerdata['filename'][6:8])
                                       ,int(headerdata['filename'][8:10]), int(headerdata['filename'][10:12]), int(headerdata['filename'][12:14])
                                        )
    Sample.latitude = ToFloat(headerdata['latitude'])
    Sample.longitude = ToFloat(headerdata['longitude'])
    Sample.organizedbydeepth = True
    Sample.acq_descent_filter=True
    Sample.winddir = int(headerdata['winddir'])
    Sample.winspeed = int(headerdata['windspeed'])
    Sample.seastate = int(headerdata['seastate'])
    Sample.nebuloussness = int(headerdata['nebuloussness'])
    Sample.comment = headerdata['comment']
    Sample.stationid = headerdata['stationid']
    Sample.acq_volimage = ToFloat(headerdata['volimage'])
    Sample.acq_aa = ToFloat(headerdata['aa'])
    Sample.acq_exp = ToFloat(headerdata['exp'])
    Sample.bottomdepth = int(headerdata['bottomdepth'])//10
    Sample.yoyo = headerdata['yoyo']=="Y"
    Sample.firstimage = int(headerdata['firstimage'])
    Sample.lastimg = int(headerdata['endimg'])

    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    uvp5_configuration_data =  DossierUVPPath / "config"/"uvp5_settings"/"uvp5_configuration_data.txt"
    if not uvp5_configuration_data.exists():
        logging.warning("file %s is missing, pixel data will miss (required for Taxo histogram esd/biovolume)"%(uvp5_configuration_data.as_posix()))
    else:
        with uvp5_configuration_data.open('r') as F:
            Lines=F.read()
            ConfigParam = DecodeEqualList(Lines)
            if 'pixel' not in ConfigParam:
                app.logger.warning("pixel parameter missing in file %s "%(uvp5_configuration_data.as_posix()))
            else:
                Sample.acq_pixel=float(ConfigParam['pixel'])

    HDRFolder =  DossierUVPPath / "raw"/("HDR"+Sample.filename)
    HDRFile = HDRFolder/("HDR"+Sample.filename+".hdr")
    if not HDRFile.exists():
        raise Exception("File %s is missing "%(HDRFile.as_posix()))
    else:
        with HDRFile.open('r') as F:
            F.readline() # on saute la ligne 1
            Ligne2=F.readline().strip('; \r\n')
            # print("Ligne2= '%s'" % (Ligne2))
            Sample.acq_filedescription = Ligne2
            m = re.search(R"\w+ (\w+)", Ligne2)
            if m.lastindex == 1:
                Sample.instrumsn=m.group(1)
            Lines = F.read()
            HdrParam=DecodeEqualList(Lines)
            # print("%s" % (HdrParam))
            Sample.acq_shutterspeed=ToFloat(HdrParam.get('shutterspeed',''))
            Sample.acq_smzoo = int(HdrParam['smzoo'])
            Sample.acq_smbase = int(HdrParam['smbase'])
            Sample.acq_exposure = ToFloat(HdrParam.get('exposure',''))
            Sample.acq_gain = ToFloat(HdrParam.get('gain', ''))
            Sample.acq_eraseborder = ToFloat(HdrParam.get('eraseborderblobs', ''))
            Sample.acq_tasktype = ToFloat(HdrParam.get('tasktype', ''))
            Sample.acq_threshold = ToFloat(HdrParam.get('thresh', ''))
            Sample.acq_choice = ToFloat(HdrParam.get('choice', ''))
            Sample.acq_disktype = ToFloat(HdrParam.get('disktype', ''))
            Sample.acq_ratio = ToFloat(HdrParam.get('ratio', ''))

    # TODO pixel à prendre dans uvp5_configuration_data.txt s'il existe ?
    db.session.commit()
    return Sample.usampleid

def GetPathForRawHistoFile(usampleid):
    VaultFolder = "partraw%04d" % (usampleid // 10000)
    vaultroot = Path(VaultRootDir)
    # creation du repertoire contenant les histogramme brut si necessaire
    CreateDirConcurrentlyIfNeeded(vaultroot / VaultFolder)
    return (vaultroot /VaultFolder/("%04d.tsv.bz2" %(usampleid % 10000))).as_posix()


def GenerateRawHistogram(usampleid):
    """
    Génération de l'histogramme particulaire brut stocké dans un fichier tsv bzippé stocké dans le vault.
    :param usampleid:
    :return:
    """
    UvpSample= uvpdatabase.uvp_samples.query.filter_by(usampleid=usampleid).first()
    if UvpSample is None:
        raise Exception("GenerateRawHistogram: Sample %d missing"%usampleid)
    Prj = uvpdatabase.uvp_projects.query.filter_by(uprojid=UvpSample.uprojid).first()

    FirstImage = int(UvpSample.firstimage)
    LastImage = int(UvpSample.lastimg)
    if LastImage>=999999:
        LastImage=None
    DepthOffset=UvpSample.acq_depthoffset
    if DepthOffset is None:
        DepthOffset = Prj.default_depthoffset
    if DepthOffset is None:
        DepthOffset=1.20 # valeur par défaut, 1.20 m
    DescentFilter=UvpSample.acq_descent_filter

    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    LstFichiers = list((DossierUVPPath / 'raw' / ('HDR' + UvpSample.filename)).glob('HDR' + UvpSample.filename + "*.dat"))
    # print(LstFichiers)
    RawImgDepth={} # version non filtrée utilisée pour générer le graphique
    ImgDepth={} # version filtrée
    ImgTime={} # heure des images
    LastImageIdx=LastImageDepth=None
    for Fichier in LstFichiers:
        logging.info("Processing file "+Fichier.as_posix())
        with Fichier.open() as csvfile:
            Rdr = csv.reader(csvfile, delimiter=';')
            next(Rdr) # au saute la ligne de titre
            for row in Rdr:
                idx = row[0].strip("\t ")
                instrumdata = row[2].strip("\t ")
                if idx == "" or instrumdata == "": continue
                idx = int(idx)
                instrumdata = instrumdata.split('*')
                depth = float(instrumdata[0])*0.1+DepthOffset
                RawImgDepth[idx] = depth
                if idx<FirstImage : continue
                ImgTime[idx]=row[1][0:14]
                if LastImage is None: # On détermine la dernière image si elle n'est pas determinée
                    if DescentFilter==False and (LastImageIdx is None or idx>LastImageIdx): # si le filtre de descente n'est pas actif on considère toujour la derniere image
                        LastImageIdx = idx
                    elif LastImageDepth is None or depth>LastImageDepth:
                        LastImageDepth=depth
                        LastImageIdx=idx
    if LastImage is None:
        LastImage=LastImageIdx
    if len(RawImgDepth)==0:
        raise Exception("No data in dat file %s " % (Fichier.as_posix()))
    PrevDepth=0
    # Application du filtre en descente
    for i in range(FirstImage,LastImage+1):
        if i not in RawImgDepth: continue
        KeepLine=True
        if DescentFilter:
            if RawImgDepth[i]<PrevDepth:
                KeepLine = False
            else:
                PrevDepth=RawImgDepth[i]
        if KeepLine:
            ImgDepth[i] = RawImgDepth[i]
    logging.info("Raw image count = {0} , Filtered image count = {1} , LastIndex= {2},LastIndex-First+1= {4}, DescentFiltered images={3}"
          .format(len(RawImgDepth),len(ImgDepth),LastImage,LastImage-FirstImage-len(ImgDepth)+1,LastImage-FirstImage+1))
    if len(ImgDepth)==0:
        raise Exception("No remaining filtered data in dat file")

    font = {'family' : 'arial','weight' : 'normal','size'   : 10}
    plt.rc('font', **font)
    plt.rcParams['lines.linewidth'] = 0.5
    Fig=plt.figure(figsize=(8,10), dpi=100)
    # 2 lignes, 3 colonnes, graphique en haut à gauche trace de la courbe de descente
    # ax = Fig.add_subplot(231)
    ax = plt.axes()
    aRawImgDepth=np.empty([len(RawImgDepth),2])
    for i,(idx,dept) in enumerate(RawImgDepth.items()):
        aRawImgDepth[i]=idx,dept
    # Courbe bleu des données brutes
    ax.plot(aRawImgDepth[:,0] , -aRawImgDepth[:,1])
    ax.set_xlabel('Image nb')
    ax.set_ylabel('Depth(m)')
    ax.set_xticks(np.arange(0,aRawImgDepth[:,0].max(),5000))
    aRawImgDepth=RawImgDepth=None # libère la mémoire des données brutes, elle ne sont plus utile une fois le graphe tracé
    # courbe rouge des données réduites à first==>Last et filtrées
    aFilteredImgDepth=np.empty([len(ImgDepth),2])
    for i,(idx,dept) in enumerate(ImgDepth.items()):
        aFilteredImgDepth[i]=idx,dept
    ax.plot(aFilteredImgDepth[:,0] , -aFilteredImgDepth[:,1],'r')
    MinDepth=aFilteredImgDepth[:,1].min()
    MaxDepth=aFilteredImgDepth[:,1].max()
    # Calcule le nombre d'image par mettre à partir de 0m
    DepthBinCount=np.bincount(np.floor(aFilteredImgDepth[:,1]).astype('int'))
    aFilteredImgDepth=None # version nparray plus necessaire.
    logging.info("Depth range= {0}->{1}".format(MinDepth,MaxDepth))
    Fig.savefig((DossierUVPPath / 'results' / ('ecotaxa_depth_' + UvpSample.filename+'.png')).as_posix())

    # chargement des données particulaires
    logging.info("Processing BRU Files:")
    LstFichiers= list((DossierUVPPath / 'raw' / ('HDR'+UvpSample.filename)).glob('HDR'+UvpSample.filename+"*.bru"))+list((DossierUVPPath / 'raw' / ('HDR'+UvpSample.filename)).glob('HDR'+UvpSample.filename+"*.bru1"))
    # logging.info(LstFichiers)
    SegmentedData={} # version filtrée
    for Fichier in LstFichiers:
        logging.info("Processing file "+Fichier.as_posix())
        with Fichier.open() as csvfile:
            Rdr = csv.reader(csvfile, delimiter=';')
            next(Rdr) # au saute la ligne de titre
            for row in Rdr:
                idx = int(row[0].strip("\t "))
                if idx not in ImgDepth : continue # c'est sur une image filtrée, on ignore
                if Fichier.suffix=='.bru':
                    area= int(row[3].strip("\t "))
                    grey= int(row[4].strip("\t "))
                elif Fichier.suffix=='.bru1':
                    area = int(row[2].strip("\t "))
                    grey = int(row[3].strip("\t "))
                else: raise Exception("Invalid file extension")
                # calcule la parition en section de 5m depuis le minimum
                Depth=math.floor(ImgDepth[idx])
                Partition =Depth
                if Partition not in SegmentedData:
                    SegmentedData[Partition]={'depth':Depth,'time':ImgTime[idx],'imgcount':DepthBinCount[Partition],'area':{}}
                if area not in SegmentedData[Partition]['area']:
                    SegmentedData[Partition]['area'][area] = [] # tableau=liste des niveaux de gris
                SegmentedData[Partition]['area'][area].append(grey)


    DetHistoFile =GetPathForRawHistoFile(usampleid)
    import bz2
    with bz2.open(DetHistoFile, 'wt', newline='') as f:
        cf=csv.writer(f,delimiter='\t')
        cf.writerow(["depth","imgcount","area","nbr","greylimit1","greylimit2","greylimit3"])
        for Partition,PartitionContent in SegmentedData.items():
            for area,greydata in PartitionContent['area'].items():
                # if area in ('depth', 'time'): continue  # ces clés sont au même niveau que les area
                agreydata=np.asarray(greydata)
                # ça ne gère pas l'organisation temporelle des données
                cf.writerow([PartitionContent['depth'],PartitionContent['imgcount'],area,len(agreydata)
                    ,np.percentile(agreydata,25,interpolation='lower')
                    , np.percentile(agreydata, 50, interpolation='lower')
                    , np.percentile(agreydata, 75, interpolation='higher')]
                )
    UvpSample.histobrutavailable=True
    UvpSample.lastimgused=LastImage
    db.session.commit()

def GetTicks(MaxVal):
    Step=math.pow(10,math.floor(math.log10(MaxVal)))
    if(MaxVal/Step)<3:
        Step=Step/2
    return np.arange(0,MaxVal,Step)

def GenerateParticleHistogram(usampleid):
    """
    Génération de l'histogramme particulaire détaillé (45 classes) et réduit (15 classes) à partir de l'histogramme détaillé
    :param usampleid:
    :return:
    """
    UvpSample= uvpdatabase.uvp_samples.query.filter_by(usampleid=usampleid).first()
    if UvpSample is None:
        raise Exception("GenerateRawHistogram: Sample %d missing"%usampleid)
    Prj = uvpdatabase.uvp_projects.query.filter_by(uprojid=UvpSample.uprojid).first()
    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    FirstImage = UvpSample.firstimage
    LastImage = UvpSample.lastimgused
    if LastImage is None: # Si aucune determinée lors de la génération de l'histogramme brut, on prend celle spécifiée dans le sample.
        LastImage = UvpSample.lastimg
    if FirstImage is None or LastImage is None:
        raise Exception("GenerateParticuleHistogram sample %s first or last image undefined %s-%s"%(UvpSample.profileid,FirstImage,LastImage))

    DetHistoFile=GetPathForRawHistoFile(usampleid)
    logging.info("GenerateParticleHistogram processing raw histogram file  %s" % DetHistoFile)
    Part=np.loadtxt(DetHistoFile,delimiter='\t',skiprows=1)
    # format de raw 0:depth,1:imgcount,2:area,3:nbr,4:greylimit1,greylimit2,greylimit3
    # 1 Ligne par mètre et area, ne contient les données entre fist et last
    MinDepth=Part[:,0].min()
    # ajout d'attributs calculés pour chaque ligne du fichier.
    PartCalc=np.empty([Part.shape[0],2]) # col0 = tranche, Col1=ESD
    PartCalc[:,0]=Part[:,0]//5  #calcul de la tranche 0 pour [0m..5m[,1 pour [5m..10m[
    PartCalc[:,1]=2*np.sqrt((pow(Part[:,2],UvpSample.acq_exp)*UvpSample.acq_aa)/np.pi)
    LastTranche=PartCalc[:,0].max()
    # on récupere les 1ère ligne de chaque mètre afin de calculer le volume d'eau
    FirstLigByDepth = Part[np.unique(Part[:, 0], return_index=True)[1]]
    # on calcule le volume de chaque tranche (y compris celle qui n'existent pas en 0 et la profondeur maxi)
    VolumeParTranche=np.bincount((FirstLigByDepth[:, 0]  // 5).astype(int), FirstLigByDepth[:, 1])*UvpSample.acq_volimage  # Bin par tranche de tranche 5m partant de 0m
    MetreParTranche=np.bincount((FirstLigByDepth[:, 0]  // 5).astype(int))  # Bin par tranche de tranche 5m partant de 0m

    (PartByClassAndTranche, bins, binsdept) = np.histogram2d(PartCalc[:,1], PartCalc[:,0], bins=(
        PartDetClassLimit, np.arange(0, VolumeParTranche.shape[0]+1 ))
            , weights=Part[:, 3])


    font = {'family' : 'arial',
            'weight' : 'normal',
            'size'   : 10}
    plt.rc('font', **font)
    plt.rcParams['lines.linewidth'] = 0.5

    Fig=plt.figure(figsize=(16,12), dpi=100)
    # calcul volume par metre moyen de chaque tranche
    ax = Fig.add_subplot(241)
    # si une tranche n'as pas été entierement explorée la /5 est un calcul éronné
    ax.plot(VolumeParTranche/MetreParTranche , np.arange(len(VolumeParTranche))*-5-2.5)
    ax.set_xticks(GetTicks((VolumeParTranche/5).max()))
    ax.set_xlabel('Volume/M')
    ax.set_ylabel('Depth(m)')

    # Calcul Particle <=0.53
    Filtre=np.argwhere(PartCalc[:,1]<=0.53)
    ax = Fig.add_subplot(242)
    (n,bins)=np.histogram(PartCalc[Filtre,0],np.arange(len(VolumeParTranche)+1),weights=Part[Filtre,3])
    n=n/VolumeParTranche
    ax.plot(n , bins[:-1]*-5-MinDepth-2.5)
    ax.set_xticks(GetTicks(n.max()))

    ax.set_xlabel('Part 0.06-0.53 mm esd #/L')
    ax.set_ylabel('Depth(m)')


    # Calcul Particle 0.53->1.06
    Filtre=np.argwhere((PartCalc[:,1]>=0.53)&(PartCalc[:,1]<=1.06))
    ax = Fig.add_subplot(243)
    (n,bins)=np.histogram(PartCalc[Filtre,0],np.arange(len(VolumeParTranche)+1),weights=Part[Filtre,3])
    n=n/VolumeParTranche
    ax.plot(n , bins[:-1]*-5-MinDepth-2.5)
    ax.set_xticks(GetTicks(n.max()))
    ax.set_xlabel('Part 0.53-1.06 mm esd #/L')
    ax.set_ylabel('Depth(m)')

    # Calcul Particle 1.06->2.66
    Filtre=np.argwhere((PartCalc[:,1]>=1.06)&(PartCalc[:,1]<=2.66))
    ax = Fig.add_subplot(244)
    (n,bins)=np.histogram(PartCalc[Filtre,0],np.arange(len(VolumeParTranche)+1),weights=Part[Filtre,3])
    n=n/VolumeParTranche
    ax.plot(n , bins[:-1]*-5-MinDepth-2.5)
    ax.set_xticks(GetTicks(n.max()))
    ax.set_xlabel('Part 1.06-2.66 mm esd #/L')
    ax.set_ylabel('Depth(m)')


    # Calcul Particle <=0.512 mm via histograme
    n=np.sum(PartByClassAndTranche[0:28,:],axis=0)
    ax = Fig.add_subplot(246)
    n=n/VolumeParTranche
    ax.plot(n , np.arange(0, LastTranche+1 )*-5 -2.5)
    ax.set_xticks(GetTicks(n.max()))
    ax.set_xlabel('Part <0.512 mm esd #/L from det histo')
    ax.set_ylabel('Depth(m)')

    # Calcul Particle >0.512-<=1.02 mm via histograme
    n=np.sum(PartByClassAndTranche[28:30,:],axis=0)
    ax = Fig.add_subplot(247)
    n=n/VolumeParTranche
    ax.plot(n , np.arange(0, LastTranche+1 )*-5 -2.5)
    ax.set_xticks(GetTicks(n.max()))
    ax.set_xlabel('Part >=0.512-<1.02 mm esd #/L from det histo')
    ax.set_ylabel('Depth(m)')

    # Calcul Particle >0.512-<=1.02 mm via histograme
    n=np.sum(PartByClassAndTranche[30:34,:],axis=0)
    ax = Fig.add_subplot(248)
    n=n/VolumeParTranche
    ax.plot(n , np.arange(0, LastTranche+1 )*-5 -2.5)
    ax.set_xticks(GetTicks(n.max()))
    ax.set_xlabel('Part >=1.02-<2.58 mm esd #/L from det histo')
    ax.set_ylabel('Depth(m)')

    Fig.savefig((DossierUVPPath / 'results' / ('ecotaxa_particle_' + UvpSample.filename+'.png')).as_posix())

    database.ExecSQL("delete from uvp_histopart_det where usampleid="+str(usampleid))
    sql="""insert into uvp_histopart_det(usampleid, lineno, depth,  watervolume
        , class01, class02, class03, class04, class05, class06, class07, class08, class09, class10, class11, class12, class13, class14
        , class15, class16, class17, class18, class19, class20, class21, class22, class23, class24, class25, class26, class27, class28, class29
        , class30, class31, class32, class33, class34, class35, class36, class37, class38, class39, class40, class41, class42, class43, class44, class45)
    values(%(usampleid)s,%(lineno)s,%(depth)s,%(watervolume)s,%(class01)s,%(class02)s,%(class03)s,%(class04)s,%(class05)s,%(class06)s
    ,%(class07)s,%(class08)s,%(class09)s,%(class10)s,%(class11)s,%(class12)s,%(class13)s,%(class14)s,%(class15)s,%(class16)s,%(class17)s
    ,%(class18)s,%(class19)s,%(class20)s,%(class21)s,%(class22)s,%(class23)s,%(class24)s,%(class25)s,%(class26)s,%(class27)s,%(class28)s
    ,%(class29)s,%(class30)s,%(class31)s,%(class32)s,%(class33)s,%(class34)s,%(class35)s,%(class36)s,%(class37)s,%(class38)s,%(class39)s
    ,%(class40)s,%(class41)s,%(class42)s,%(class43)s,%(class44)s,%(class45)s)"""
    sqlparam={'usampleid':usampleid}
    for i,r in enumerate(VolumeParTranche):
        sqlparam['lineno']=i
        sqlparam['depth'] = (i*5+2.5)
        sqlparam['watervolume'] = VolumeParTranche[i]
        for k in range(0,45):
            sqlparam['class%02d'%(k+1)] = PartByClassAndTranche[k,i]
        database.ExecSQL(sql,sqlparam)
    GenerateReducedParticleHistogram(usampleid)

def GenerateReducedParticleHistogram(usampleid):
    """
    Génération de l'histogramme particulaire détaillé (45 classes) et réduit (15 classes) à partir de l'histogramme détaillé
    :param usampleid:
    :return:
    """
    database.ExecSQL("delete from uvp_histopart_reduit where usampleid=" + str(usampleid))
    sql = """insert into uvp_histopart_reduit(usampleid, lineno, depth,datetime,  watervolume
    , class01, class02, class03, class04, class05, class06, class07, class08, class09, class10, class11, class12, class13, class14
    , class15)
    select usampleid, lineno, depth,datetime,  watervolume,
      class01+ class02+class03 as c1, class04+class05+class06 as c2, class07+class08+class09 as c3, class10+class11+class12 as c4
      , class13+class14+class15 as c5, class16+class17+class18 as c6, class19+class20+class21 as c7, class22+class23+class24 as c8
      , class25+class26+class27 c9, class28+class29+class30 as c10, class31+class32+class33 as c11, class34+class35+class36 as c12
      , class37+class38+class39 as c13, class40+class41+class42 as c14, class43+class44+class45 as c15
    from uvp_histopart_det where usampleid="""+str(usampleid)
    database.ExecSQL(sql)

def GenerateTaxonomyHistogram(usampleid):
    """
    Génération de l'histogramme Taxonomique 
    :param usampleid:
    :return:
    """
    UvpSample= uvpdatabase.uvp_samples.query.filter_by(usampleid=usampleid).first()
    if UvpSample is None:
        raise Exception("GenerateTaxonomyHistogram: Sample %d missing"%usampleid)
    Prj = uvpdatabase.uvp_projects.query.filter_by(uprojid=UvpSample.uprojid).first()
    if UvpSample.sampleid is None:
        raise Exception("GenerateTaxonomyHistogram: Ecotaxa sampleid required in Sample %d " % usampleid)
    pixel=UvpSample.acq_pixel
    EcoPrj = database.Projects.query.filter_by(projid=Prj.projid).first()
    if EcoPrj is None:
        raise Exception("GenerateTaxonomyHistogram: Ecotaxa project %d missing"%Prj.projid)
    objmap = DecodeEqualList(EcoPrj.mappingobj)
    areacol=None
    for k,v in objmap.items():
        if v.lower()=='area':
            areacol=k
            break
    if areacol is None:
        raise Exception("GenerateTaxonomyHistogram: esd attribute required in Ecotaxa project %d"%Prj.projid)
    app.logger.info("Esd col is %s",areacol)
    LstTaxo=database.GetAll("""select classif_id,floor(depth_min/5) tranche,avg({areacol}) as avgarea,count(*) nbr
                from objects
                WHERE sampleid={sampleid} and classif_id is not NULL and depth_min is not NULL and {areacol} is not NULL
                group by classif_id,floor(depth_min/5)"""
                            .format(sampleid=UvpSample.sampleid,areacol=areacol))
    LstVol=database.GetAssoc("""select cast(round((depth-2.5)/5) as INT) tranche,watervolume from uvp_histopart_reduit where usampleid=%s"""%usampleid)
    # 0 Taxoid, tranche
    # TblTaxo=np.empty([len(LstTaxo),4])
    database.ExecSQL("delete from uvp_histocat_lst where usampleid=%s"%usampleid)
    database.ExecSQL("delete from uvp_histocat where usampleid=%s"%usampleid)
    sql="""insert into uvp_histocat(usampleid, classif_id, lineno, depth, watervolume, nbr, avgesd, totalbiovolume)
            values({usampleid},{classif_id},{lineno},{depth},{watervolume},{nbr},{avgesd},{totalbiovolume})"""
    for r in LstTaxo:
        watervolume=LstVol.get(r['tranche'])
        esd=r['avgarea']*pixel*pixel  # todo finir
        biovolume=r['nbr']*pow(esd/2,3)*4*math.pi/3
        watervolume='NULL'
        if r['tranche'] in LstVol:
            watervolume =LstVol[r['tranche']]['watervolume']
        database.ExecSQL(sql.format(
        usampleid=usampleid, classif_id=r['classif_id'], lineno=r['tranche'], depth=r['tranche']*5+2.5, watervolume=watervolume
            , nbr=r['nbr'], avgesd=esd, totalbiovolume=biovolume ))
    database.ExecSQL("""insert into uvp_histocat_lst(usampleid, classif_id) 
            select distinct usampleid,classif_id from uvp_histocat where usampleid=%s""" % usampleid)

    database.ExecSQL("""update uvp_samples set daterecalculhistotaxo=current_timestamp  
            where usampleid=%s""" % usampleid)

        # TblTaxo[i,0:2]=r['avgarea'],r['nbr']
    # TblTaxo[:,2]=

def ImportCTD(usampleid):
    """
    Importe les données CTD 
    :param usampleid:
    :return:
    """
    FixedCol={
        "chloro fluo [mg chl/m3]": "chloro_fluo",
        "conductivity [ms/cm]": "conductivity",
        "cpar [%]": "cpar",
        "depth [salt water, m]": "fcdom_factory",
        "fcdom factory [ppb qse]": "in_situ_density_anomaly",
        "in situ density anomaly [kg/m3]": "neutral_density",
        "neutral density [kg/m3]": "nitrate",
        "nitrate [µmol/l]": "oxygen_mass",
        "oxygen [µmol/kg]": "oxygen_vol",
        "oxygen [ml/l]": "par",
        "par [µmol m-2 s-1]": "part_backscattering_coef_470_nm",
        "part backscattering coef 470 nm [m-1]": "pot_temperature",
        "pot. temperature [degc] (any ref.)": "potential_density_anomaly",
        "potential density anomaly [kg/m3]": "potential_temperature",
        "potential temperature [degc]": "practical_salinity",
        "practical salinity [psu]": "practical_salinity__from_conductivity",
        "practical salinity from conductivity": "uvp_ctd_pkey",
        "pressure in water column [db]": "pressure_in_water_column",
        "qc flag": "qc_flag",
        "sound speed c [m/s]": "sound_speed_c",
        "spar [µmol m-2 s-1]": "spar",
        "temperature [degc]": "temperature"
    }
    UvpSample= uvpdatabase.uvp_samples.query.filter_by(usampleid=usampleid).first()
    if UvpSample is None:
        raise Exception("ImportCTD: Sample %d missing"%usampleid)
    Prj = uvpdatabase.uvp_projects.query.filter_by(uprojid=UvpSample.uprojid).first()
    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    CtdFile =  DossierUVPPath / "ctd_data_cnv"/(UvpSample.profileid+".ctd")
    if not CtdFile.exists():
        app.logger.info("CTD file %s missing", CtdFile.as_posix())
        return False
    app.logger.info("Import CTD file %s", CtdFile.as_posix())
    with CtdFile.open('r') as tsvfile:
        Rdr = csv.reader(tsvfile, delimiter='\t')
        HeadRow=Rdr.__next__()
        # Analyser la ligne de titre et assigner à chaque ID l'attribut
        # Construire la table d'association des attributs complémentaires.
        ExtramesID=0
        Mapping=[]
        ExtraMapping ={}
        for ic,c in enumerate(HeadRow):
            clow=c.lower().strip()
            if clow in FixedCol:
                Target=FixedCol[clow]
            else:
                ExtramesID += 1
                Target ='extrames%02d'%ExtramesID
                ExtraMapping['%02d'%ExtramesID]=c
                if ExtramesID>20:
                    raise Exception("ImportCTD: Too much CTD data, column %s skipped" % c)
            Mapping.append(Target)
        app.logger.info("Mapping = %s",Mapping)
        database.ExecSQL("delete from uvp_ctd where usampleid=%s"%usampleid)
        for i,r in enumerate(Rdr):
            cl=uvpdatabase.uvp_ctd()
            cl.usampleid=usampleid
            cl.lineno=i
            for i,c in enumerate(Mapping):
                v=CleanValue(r[i])
                if v!='':
                    setattr(cl,c,v)
            db.session.add(cl)
            db.session.commit()
        UvpSample.ctd_desc=EncodeEqualList(ExtraMapping)
        UvpSample.ctd_import_datetime=datetime.datetime.now()
        UvpSample.ctd_import_name=current_user.name
        UvpSample.ctd_import_email = current_user.email
        db.session.commit()
        return True
