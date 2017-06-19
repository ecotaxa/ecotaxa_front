from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,VaultRootDir,DecodeEqualList,ntcv,EncodeEqualList,CreateDirConcurrentlyIfNeeded
from pathlib import Path
import appli.part.database as partdatabase, logging,re,datetime,csv,math
import numpy as np
import matplotlib.pyplot as plt
from appli import database
from appli.part import PartDetClassLimit,CTDFixedCol
from flask_login import current_user
from appli.part.common_sample_import import CleanValue,ToFloat,GetTicks,GenerateReducedParticleHistogram

def ConvDegreeMinuteFloatToDecimaldegre(v):
    f,i=math.modf(v)
    return i+(f/0.6)


def CreateOrUpdateSample(pprojid,headerdata):
    """
    Crée ou met à jour le sample
    :param pprojid:
    :param headerdata:
    :return: Objet BD sample
    """
    Prj = partdatabase.part_projects.query.filter_by(pprojid=pprojid).first()
    for k,v in headerdata.items():
        headerdata[k]=CleanValue(v)
    Sample=partdatabase.part_samples.query.filter_by(profileid=headerdata['profileid'],pprojid=pprojid).first()
    if Sample is None:
        logging.info("Create UVP sample for %s %s"%(headerdata['profileid'],headerdata['filename']))
        Sample = partdatabase.part_samples()
        Sample.profileid=headerdata['profileid']
        Sample.pprojid=pprojid
        db.session.add(Sample)
    else:
        logging.info("Update UVP sample %s for %s %s" % (Sample.psampleid,headerdata['profileid'], headerdata['filename']))
    Sample.filename=headerdata['filename']
    Sample.sampledate=datetime.datetime(int(headerdata['filename'][0:4]),int(headerdata['filename'][4:6]),int(headerdata['filename'][6:8])
                                       ,int(headerdata['filename'][8:10]), int(headerdata['filename'][10:12]), int(headerdata['filename'][12:14])
                                        )
    Sample.latitude = ConvDegreeMinuteFloatToDecimaldegre(ToFloat(headerdata['latitude']))
    Sample.longitude = ConvDegreeMinuteFloatToDecimaldegre(ToFloat(headerdata['longitude']))
    Sample.organizedbydeepth = True
    Sample.acq_descent_filter=True
    Sample.ctd_origfilename=headerdata['ctdrosettefilename']
    Sample.winddir = int(round(ToFloat(headerdata['winddir'])))
    Sample.winspeed = int(round(ToFloat(headerdata['windspeed'])))
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
    Sample.proc_soft="Zooprocess"

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
            if 'xsize' in ConfigParam:
                Sample.acq_xsize = int(ConfigParam['xsize'])
            if 'ysize' in ConfigParam:
                Sample.acq_ysize = int(ConfigParam['ysize'])

    HDRFolder =  DossierUVPPath / "raw"/("HDR"+Sample.filename)
    HDRFile = HDRFolder/("HDR"+Sample.filename+".hdr")
    if not HDRFile.exists():
        HDRFolder = DossierUVPPath / "work" / Sample.profileid
        HDRFile = HDRFolder / ("HDR" + Sample.filename + ".txt")
        if not HDRFile.exists():
            raise Exception("File %s is missing, and in raw folder too" % (HDRFile.as_posix()))

    with HDRFile.open('r') as F:
        F.readline() # on saute la ligne 1
        Ligne2=F.readline().strip('; \r\n')
        # print("Ligne2= '%s'" % (Ligne2))
        Sample.acq_filedescription = Ligne2
        m = re.search(R"\w+ (\w+)", Ligne2)
        if m is not None and m.lastindex == 1:
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


    db.session.commit()
    return Sample.psampleid

def GetPathForRawHistoFile(psampleid):
    VaultFolder = "partraw%04d" % (psampleid // 10000)
    vaultroot = Path(VaultRootDir)
    # creation du repertoire contenant les histogramme brut si necessaire
    CreateDirConcurrentlyIfNeeded(vaultroot / VaultFolder)
    return (vaultroot /VaultFolder/("%04d.tsv.bz2" %(psampleid % 10000))).as_posix()


def GenerateRawHistogram(psampleid):
    """
    Génération de l'histogramme particulaire brut stocké dans un fichier tsv bzippé stocké dans le vault.
    :param psampleid:
    :return: None    
    """
    UvpSample= partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if UvpSample is None:
        raise Exception("GenerateRawHistogram: Sample %d missing"%psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=UvpSample.pprojid).first()

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
    # Ecart format suivant l'endroit
    # dans result on a comme dans work
    #      1;	20160710164151_998;	00203;00181;00181;00009;02761;02683;00612;01051;00828;00396;00588;00692!;	542;	1;	4;	2;	5;
    # dans work on a ;	00208;00175;00175;00019;02828;02055;00732;01049;00756;00712;00705;00682!;
    #      1;	20160710164151_998;	00203;00181;00181;00009;02761;02683;00612;01051;00828;00396;00588;00692!;	542;	1;	4;	2;	5;
    # 12 colonnes au lieu de 1
    # alors que dans RAW on a ;	00208*00175*00175*00019*02828*02055*00732*01049*00756*00712*00705*00682!;
    #      1;	20160628160507_071;	00203*00180*00180*00012*02611*02766*01125*00898*00655*00752*00786*00791!;	1289;	1;	7;	1;	10;
    # Nom du fichier dans raw : HDR20160710164150/HDR20160710164150_000.dat
    # Nom du fichier dans work ge_2016_202/HDR20160710164150.dat , un fichier unique
    # Nom du fichier dans result ge_2016_202_datfile.txt, un fichier unique
    # le changement de format n'as pas d'impact car seule les 3 premières colonnes sont utilisées et c'est le format de la 3eme qui change
    # dans l'instrument on ne se sert que de la première valeurs donc le découpage suivant * et la prise de la première valeur donne le même résultat.
    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    PathDat = DossierUVPPath / 'results' / ( UvpSample.profileid + "_datfile.txt")
    if PathDat.exists():
        LstFichiers = [PathDat]
    else:
        PathDat = DossierUVPPath / 'work' / UvpSample.profileid / ('HDR' + UvpSample.filename + ".dat")
        if PathDat.exists():
            LstFichiers = [PathDat]
        else:
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
    DescentFilterRemovedCount=0
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
        else:
            DescentFilterRemovedCount+=1
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
    Fig.savefig((DossierUVPPath / 'results' / ('ecotaxa_depth_' + UvpSample.profileid+'.png')).as_posix())
    Fig.clf()
    # Ecart format suivant l'endroit
    # Dans results nom = p1604_13.bru toujours au format bru1 malgré l'extension bru fichier unique
    # dans work p1604_13/p1604_13.bru toujours au format bru1 malgré l'extension bru fichier unique
    # dans raw HDR20160429180115/HDR20160429180115_000.bru ou bru1
    # chargement des données particulaires
    logging.info("Processing BRU Files:")
    PathBru=DossierUVPPath / 'results' /(UvpSample.profileid+".bru")
    if PathBru.exists():
        BRUFormat="bru1"
        LstFichiers = [PathBru ]
    else:
        PathBru=DossierUVPPath / 'work' /UvpSample.profileid/(UvpSample.profileid+".bru")
        if PathBru.exists():
            BRUFormat="bru1"
            LstFichiers = [PathBru ]
        else:
            LstFichiers= list((DossierUVPPath / 'raw' / ('HDR'+UvpSample.filename)).glob('HDR'+UvpSample.filename+"*.bru"))
            if len(LstFichiers)>0:
                BRUFormat = "bru"
            else:
                LstFichiers = list((DossierUVPPath / 'raw' / ('HDR'+UvpSample.filename)).glob('HDR'+UvpSample.filename+"*.bru1"))
                BRUFormat = "bru1"
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
                if BRUFormat=='bru':
                    area= int(row[3].strip("\t "))
                    grey= int(row[4].strip("\t "))
                elif BRUFormat=='bru1':
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


    DetHistoFile =GetPathForRawHistoFile(psampleid)
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
    UvpSample.imp_descent_filtered_row=DescentFilterRemovedCount
    db.session.commit()

def GenerateParticleHistogram(psampleid):
    """
    Génération de l'histogramme particulaire détaillé (45 classes) et réduit (15 classes) à partir de l'histogramme détaillé
    :param psampleid:
    :return:
    """
    UvpSample= partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if UvpSample is None:
        raise Exception("GenerateRawHistogram: Sample %d missing"%psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=UvpSample.pprojid).first()
    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    FirstImage = UvpSample.firstimage
    LastImage = UvpSample.lastimgused
    if LastImage is None: # Si aucune determinée lors de la génération de l'histogramme brut, on prend celle spécifiée dans le sample.
        LastImage = UvpSample.lastimg
    if FirstImage is None or LastImage is None:
        raise Exception("GenerateParticuleHistogram sample %s first or last image undefined %s-%s"%(UvpSample.profileid,FirstImage,LastImage))

    DetHistoFile=GetPathForRawHistoFile(psampleid)
    logging.info("GenerateParticleHistogram processing raw histogram file  %s" % DetHistoFile)
    Part=np.loadtxt(DetHistoFile,delimiter='\t',skiprows=1)
    # format de raw 0:depth,1:imgcount,2:area,3:nbr,4:greylimit1,greylimit2,greylimit3
    # 1 Ligne par mètre et area, ne contient les données entre fist et last
    MinDepth=Part[:,0].min()
    # ajout d'attributs calculés pour chaque ligne du fichier.
    PartCalc=np.empty([Part.shape[0],3]) # col0 = tranche, Col1=ESD, Col2=Biovolume en µl
    PartCalc[:,0]=Part[:,0]//5  #calcul de la tranche 0 pour [0m..5m[,1 pour [5m..10m[
    PartCalc[:,1]=2*np.sqrt((pow(Part[:,2],UvpSample.acq_exp)*UvpSample.acq_aa)/np.pi)
    PartCalc[:, 2] = Part[:,3]*pow(PartCalc[:, 1] / 2, 3) * 4 * math.pi / 3
    LastTranche=PartCalc[:,0].max()
    # on récupere les 1ère ligne de chaque mètre afin de calculer le volume d'eau
    FirstLigByDepth = Part[np.unique(Part[:, 0], return_index=True)[1]]
    # on calcule le volume de chaque tranche (y compris celle qui n'existent pas en 0 et la profondeur maxi)
    VolumeParTranche=np.bincount((FirstLigByDepth[:, 0]  // 5).astype(int), FirstLigByDepth[:, 1])*UvpSample.acq_volimage  # Bin par tranche de tranche 5m partant de 0m
    MetreParTranche=np.bincount((FirstLigByDepth[:, 0]  // 5).astype(int))  # Bin par tranche de tranche 5m partant de 0m
    # On supprime les tranches vides, mais ça fait planter les graphes suivants
    # VolumeParTranche=VolumeParTranche[np.nonzero(VolumeParTranche)]
    # MetreParTranche = MetreParTranche[np.nonzero(VolumeParTranche)]

    (PartByClassAndTranche, bins, binsdept) = np.histogram2d(PartCalc[:,1], PartCalc[:,0], bins=(
        PartDetClassLimit, np.arange(0, VolumeParTranche.shape[0]+1 ))
            , weights=Part[:, 3])
    (BioVolByClassAndTranche, bins, binsdept) = np.histogram2d(PartCalc[:,1], PartCalc[:,0], bins=(
        PartDetClassLimit, np.arange(0, VolumeParTranche.shape[0]+1 ))
            , weights=PartCalc[:, 2])
    with np.errstate(divide='ignore', invalid='ignore'): # masque les warning provoquées par les divisions par 0 des tranches vides.
        BioVolByClassAndTranche/=VolumeParTranche


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

        # Calcul Biovolume Particle >0.512-<=1.02 mm via histograme
        n=np.sum(BioVolByClassAndTranche[28:30,:],axis=0)
        ax = Fig.add_subplot(245)

        ax.plot(n , np.arange(0, LastTranche+1 )*-5 -2.5)
        ax.set_xticks(GetTicks(n.max()))
        ax.set_xlabel('Part >=0.512-<1.02 mm esd µl/l from det histo')
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

        Fig.savefig((DossierUVPPath / 'results' / ('ecotaxa_particle_' + UvpSample.profileid+'.png')).as_posix())
        Fig.clf()

    database.ExecSQL("delete from part_histopart_det where psampleid="+str(psampleid))
    sql="""insert into part_histopart_det(psampleid, lineno, depth,  watervolume
        , class01, class02, class03, class04, class05, class06, class07, class08, class09, class10, class11, class12, class13, class14
        , class15, class16, class17, class18, class19, class20, class21, class22, class23, class24, class25, class26, class27, class28, class29
        , class30, class31, class32, class33, class34, class35, class36, class37, class38, class39, class40, class41, class42, class43, class44, class45
        , biovol01, biovol02, biovol03, biovol04, biovol05, biovol06, biovol07, biovol08, biovol09, biovol10, biovol11, biovol12, biovol13, biovol14
        , biovol15, biovol16, biovol17, biovol18, biovol19, biovol20, biovol21, biovol22, biovol23, biovol24, biovol25, biovol26, biovol27, biovol28, biovol29
        , biovol30, biovol31, biovol32, biovol33, biovol34, biovol35, biovol36, biovol37, biovol38, biovol39, biovol40, biovol41, biovol42, biovol43, biovol44, biovol45
        )
    values(%(psampleid)s,%(lineno)s,%(depth)s,%(watervolume)s
    ,%(class01)s,%(class02)s,%(class03)s,%(class04)s,%(class05)s,%(class06)s
    ,%(class07)s,%(class08)s,%(class09)s,%(class10)s,%(class11)s,%(class12)s,%(class13)s,%(class14)s,%(class15)s,%(class16)s,%(class17)s
    ,%(class18)s,%(class19)s,%(class20)s,%(class21)s,%(class22)s,%(class23)s,%(class24)s,%(class25)s,%(class26)s,%(class27)s,%(class28)s
    ,%(class29)s,%(class30)s,%(class31)s,%(class32)s,%(class33)s,%(class34)s,%(class35)s,%(class36)s,%(class37)s,%(class38)s,%(class39)s
    ,%(class40)s,%(class41)s,%(class42)s,%(class43)s,%(class44)s,%(class45)s
    ,%(biovol01)s,%(biovol02)s,%(biovol03)s,%(biovol04)s,%(biovol05)s,%(biovol06)s
    ,%(biovol07)s,%(biovol08)s,%(biovol09)s,%(biovol10)s,%(biovol11)s,%(biovol12)s,%(biovol13)s,%(biovol14)s,%(biovol15)s,%(biovol16)s,%(biovol17)s
    ,%(biovol18)s,%(biovol19)s,%(biovol20)s,%(biovol21)s,%(biovol22)s,%(biovol23)s,%(biovol24)s,%(biovol25)s,%(biovol26)s,%(biovol27)s,%(biovol28)s
    ,%(biovol29)s,%(biovol30)s,%(biovol31)s,%(biovol32)s,%(biovol33)s,%(biovol34)s,%(biovol35)s,%(biovol36)s,%(biovol37)s,%(biovol38)s,%(biovol39)s
    ,%(biovol40)s,%(biovol41)s,%(biovol42)s,%(biovol43)s,%(biovol44)s,%(biovol45)s
    )"""
    sqlparam={'psampleid':psampleid}
    for i,r in enumerate(VolumeParTranche):
        sqlparam['lineno']=i
        sqlparam['depth'] = (i*5+2.5)
        if VolumeParTranche[i]==0: # On ne charge pas les lignes sans volume d'eau car ça signifie qu'l n'y a pas eu d'échantillon
            continue
        sqlparam['watervolume'] = VolumeParTranche[i]
        for k in range(0,45):
            sqlparam['class%02d'%(k+1)] = PartByClassAndTranche[k,i]
        for k in range(0,45):
            sqlparam['biovol%02d'%(k+1)] = BioVolByClassAndTranche[k,i]
        database.ExecSQL(sql,sqlparam)

    GenerateReducedParticleHistogram(psampleid)


def GenerateTaxonomyHistogram(psampleid):
    """
    Génération de l'histogramme Taxonomique 
    :param psampleid:
    :return:
    """
    UvpSample= partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if UvpSample is None:
        raise Exception("GenerateTaxonomyHistogram: Sample %d missing"%psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=UvpSample.pprojid).first()
    if UvpSample.sampleid is None:
        raise Exception("GenerateTaxonomyHistogram: Ecotaxa sampleid required in Sample %d " % psampleid)
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
    LstVol=database.GetAssoc("""select cast(round((depth-2.5)/5) as INT) tranche,watervolume from part_histopart_reduit where psampleid=%s"""%psampleid)
    # 0 Taxoid, tranche
    # TblTaxo=np.empty([len(LstTaxo),4])
    database.ExecSQL("delete from part_histocat_lst where psampleid=%s"%psampleid)
    database.ExecSQL("delete from part_histocat where psampleid=%s"%psampleid)
    sql="""insert into part_histocat(psampleid, classif_id, lineno, depth, watervolume, nbr, avgesd, totalbiovolume)
            values({psampleid},{classif_id},{lineno},{depth},{watervolume},{nbr},{avgesd},{totalbiovolume})"""
    for r in LstTaxo:
        watervolume=LstVol.get(r['tranche'])
        esd=r['avgarea']*pixel*pixel
        biovolume=r['nbr']*pow(esd/2,3)*4*math.pi/3
        watervolume='NULL'
        if r['tranche'] in LstVol:
            watervolume =LstVol[r['tranche']]['watervolume']
        database.ExecSQL(sql.format(
        psampleid=psampleid, classif_id=r['classif_id'], lineno=r['tranche'], depth=r['tranche']*5+2.5, watervolume=watervolume
            , nbr=r['nbr'], avgesd=esd, totalbiovolume=biovolume ))
    database.ExecSQL("""insert into part_histocat_lst(psampleid, classif_id) 
            select distinct psampleid,classif_id from part_histocat where psampleid=%s""" % psampleid)

    database.ExecSQL("""update part_samples set daterecalculhistotaxo=current_timestamp  
            where psampleid=%s""" % psampleid)

        # TblTaxo[i,0:2]=r['avgarea'],r['nbr']
    # TblTaxo[:,2]=

