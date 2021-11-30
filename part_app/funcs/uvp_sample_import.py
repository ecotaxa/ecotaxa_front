import csv
import datetime
import logging
import math
import re
from pathlib import Path

import bz2
import configparser
import io
import matplotlib.pyplot as plt
import numpy as np
import sys
import zipfile

from appli import VaultRootDir, DecodeEqualList, CreateDirConcurrentlyIfNeeded
from .. import database as partdatabase
from ..app import part_app, db
from ..constants import PartDetClassLimit
from ..db_utils import ExecSQL, GetAssoc
from ..funcs.common_sample_import import CleanValue, ToFloat, GetTicks, GenerateReducedParticleHistogram
from ..remote import EcoTaxaInstance
from ..tasks.importcommon import ConvTextDegreeDotMinuteToDecimalDegree, calcpixelfromesd_aa_exp


def CreateOrUpdateSample(pprojid, headerdata):
    """
    Crée ou met à jour le sample
    :param pprojid:
    :param headerdata:
    :return: Objet BD sample
    """
    Prj = partdatabase.part_projects.query.filter_by(pprojid=pprojid).first()
    for k, v in headerdata.items():
        headerdata[k] = CleanValue(v)
    Sample = partdatabase.part_samples.query.filter_by(profileid=headerdata['profileid'], pprojid=pprojid).first()
    if Sample is None:
        logging.info("Create UVP sample for %s %s" % (headerdata['profileid'], headerdata['filename']))
        Sample = partdatabase.part_samples()
        Sample.profileid = headerdata['profileid']
        Sample.pprojid = pprojid
        db.session.add(Sample)
    else:
        logging.info(
            "Update UVP sample %s for %s %s" % (Sample.psampleid, headerdata['profileid'], headerdata['filename']))
    Sample.filename = headerdata['filename']
    if 'sampledatetime' in headerdata and headerdata['sampledatetime']:
        sampledatetxt = headerdata['sampledatetime']  # format uvpapp
    else:
        sampledatetxt = headerdata['filename']  # format historique uvp5
    m = re.search("(\d{4})(\d{2})(\d{2})-?(\d{2})(\d{2})(\d{2})?",
                  sampledatetxt)  # YYYYMMDD-HHMMSS avec tiret central et secondes optionnelles
    Sample.sampledate = datetime.datetime(*[int(x) if x else 0 for x in m.group(1, 2, 3, 4, 5, 6)])
    Sample.latitude = ConvTextDegreeDotMinuteToDecimalDegree(
        headerdata['latitude'])  # dans les fichiers UVP historique c'est la notation degree.minute
    Sample.longitude = ConvTextDegreeDotMinuteToDecimalDegree(headerdata['longitude'])
    Sample.organizedbydeepth = headerdata.get('sampletype',
                                              'P') == 'P'  # Nouvelle colonne optionnel, par défaut organisé par (P)ression
    # 2020-05-01 : ce champ est à present actualisé lors du traitement du sample
    # Sample.acq_descent_filter=Sample.organizedbydeepth # Si sample vertical alors filtrage en descente activé par défaut.
    Sample.ctd_origfilename = headerdata['ctdrosettefilename']
    if headerdata['winddir']:
        Sample.winddir = int(round(ToFloat(headerdata['winddir'])))
    if headerdata['windspeed']:
        Sample.winspeed = int(round(ToFloat(headerdata['windspeed'])))
    if headerdata['seastate']:
        Sample.seastate = int(headerdata['seastate'])
    if headerdata['nebuloussness']:
        Sample.nebuloussness = int(headerdata['nebuloussness'])
    if headerdata.get('integrationtime'):
        Sample.integrationtime = int(headerdata['integrationtime'])
    Sample.comment = headerdata['comment']
    Sample.stationid = headerdata['stationid']
    Sample.acq_volimage = ToFloat(headerdata['volimage'])
    Sample.acq_aa = ToFloat(headerdata['aa'])
    Sample.acq_exp = ToFloat(headerdata['exp'])
    if headerdata.get('bottomdepth'):
        Sample.bottomdepth = int(headerdata['bottomdepth']) // 10
    Sample.yoyo = headerdata['yoyo'] == "Y"
    Sample.firstimage = int(float(headerdata['firstimage']))
    Sample.lastimg = int(float(headerdata['endimg']))
    Sample.proc_soft = "Zooprocess"
    if headerdata.get("pixelsize"):
        Sample.acq_pixel = float(headerdata['pixelsize'])

    ServerRoot = Path(part_app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    uvp5_configuration_data = DossierUVPPath / "config" / "uvp5_settings" / "uvp5_configuration_data.txt"
    if not uvp5_configuration_data.exists():
        if Sample.acq_pixel is None:  # warning sauf si déjà rempli grace à la colonne ajoutée au fichier header version uvpapp
            logging.warning("file %s is missing, pixel data will miss (required for Taxo histogram esd/biovolume)" % (
                uvp5_configuration_data.as_posix()))
    else:
        with uvp5_configuration_data.open('r', encoding='latin_1') as F:
            Lines = F.read()
            ConfigParam = DecodeEqualList(Lines)
            if 'pixel' not in ConfigParam:
                part_app.logger.warning("pixel parameter missing in file %s " % (uvp5_configuration_data.as_posix()))
            else:
                Sample.acq_pixel = float(ConfigParam['pixel'])
            if 'xsize' in ConfigParam:
                Sample.acq_xsize = int(ConfigParam['xsize'])
            if 'ysize' in ConfigParam:
                Sample.acq_ysize = int(ConfigParam['ysize'])

    HDRFolder = DossierUVPPath / "raw" / ("HDR" + Sample.filename)
    HDRFile = HDRFolder / ("HDR" + Sample.filename + ".hdr")
    if not HDRFile.exists():
        HDRFolder = DossierUVPPath / "work" / Sample.profileid
        HDRFile = HDRFolder / ("HDR" + Sample.filename + ".txt")
        if not HDRFile.exists():
            EcodataPartFile = DossierUVPPath / "ecodata" / Sample.profileid / (Sample.profileid + "_Particule.zip")
            if EcodataPartFile.exists():
                HDRFile = None  # pas un fichier HDR donc on lira le fichier zip
            else:
                raise Exception("File %s or %s are  missing, and in raw folder too" % (
                    HDRFile.as_posix(), EcodataPartFile.as_posix()))
    if HDRFile:
        with HDRFile.open('r', encoding='latin_1') as F:
            F.readline()  # on saute la ligne 1
            Ligne2 = F.readline().strip('; \r\n')
            # print("Ligne2= '%s'" % (Ligne2))
            Sample.acq_filedescription = Ligne2
            m = re.search(R"\w+ (\w+)", Ligne2)
            if m is not None and m.lastindex == 1:
                Sample.instrumsn = m.group(1)
            Lines = F.read()
            HdrParam = DecodeEqualList(Lines)
            # print("%s" % (HdrParam))
            Sample.acq_shutterspeed = ToFloat(HdrParam.get('shutterspeed', ''))
            Sample.acq_smzoo = int(HdrParam['smzoo'])
            Sample.acq_smbase = int(HdrParam['smbase'])
            Sample.acq_exposure = ToFloat(HdrParam.get('exposure', ''))
            Sample.acq_gain = ToFloat(HdrParam.get('gain', ''))
            Sample.acq_eraseborder = ToFloat(HdrParam.get('eraseborderblobs', ''))
            Sample.acq_tasktype = ToFloat(HdrParam.get('tasktype', ''))
            Sample.acq_threshold = ToFloat(HdrParam.get('thresh', ''))
            Sample.acq_choice = ToFloat(HdrParam.get('choice', ''))
            Sample.acq_disktype = ToFloat(HdrParam.get('disktype', ''))
            Sample.acq_ratio = ToFloat(HdrParam.get('ratio', ''))
    else:
        z = zipfile.ZipFile(EcodataPartFile.as_posix())
        with z.open("metadata.ini", "r") as metadata_ini_raw:
            metadata_ini = io.TextIOWrapper(io.BytesIO(metadata_ini_raw.read()), encoding="latin_1")
            # with open(metadata_ini_raw, encoding='latin_1') as metadata_ini:
            ini = configparser.ConfigParser()
            ini.read_file(metadata_ini)
            hw_conf = ini['HW_CONF']
            acq_conf = ini['ACQ_CONF']
            Sample.acq_shutterspeed = ToFloat(hw_conf.get('Shutter', ''))
            Sample.acq_gain = ToFloat(hw_conf.get('Gain', ''))
            Sample.acq_threshold = ToFloat(hw_conf.get('Threshold', ''))
            Sample.acq_smzoo = calcpixelfromesd_aa_exp(
                ToFloat(acq_conf.get('Vignetting_lower_limit_size', '')) / 1000.0, Sample.acq_aa, Sample.acq_exp)
            Sample.acq_smbase = calcpixelfromesd_aa_exp(ToFloat(acq_conf.get('Limit_lpm_detection_size', '')) / 1000.0,
                                                        Sample.acq_aa, Sample.acq_exp)
            if (hw_conf.get('Pressure_offset', '') != ''):
                if 0 <= ToFloat(hw_conf.get('Pressure_offset', '')) < 100:
                    Sample.acq_depthoffset = ToFloat(hw_conf.get('Pressure_offset', ''))
    db.session.commit()
    return Sample.psampleid


def GetPathForRawHistoFile(psampleid, flash='1'):
    VaultFolder = "partraw%04d" % (psampleid // 10000)
    vaultroot = Path(VaultRootDir)
    # creation du repertoire contenant les histogramme brut si necessaire
    CreateDirConcurrentlyIfNeeded(vaultroot / VaultFolder)
    # si flash est à 0 on ajoute .black dans le nom du fichier
    return (vaultroot / VaultFolder / (
            "%04d%s.tsv.bz2" % (psampleid % 10000, '.black' if flash == '0' else ''))).as_posix()


def GetPathForImportGraph(psampleid, suffix, RelativeToVault=False):
    """
    Retourne le chemin vers l'image associée en gérant l'éventuelle création du répertoire  
    :param psampleid: 
    :param suffix: suffixe mis à la fin du nom de l'image
    :param RelativeToVault: 
    :return: chemin posix de l'image 
    """
    VaultFolder = "pargraph%04d" % (psampleid // 10000)
    vaultroot = Path(VaultRootDir)
    # creation du repertoire contenant les graphe d'importation si necessaire
    if not RelativeToVault:  # Si Relatif c'est pour avoir l'url inutile de regarder si le repertoire existe.
        CreateDirConcurrentlyIfNeeded(vaultroot / VaultFolder)
    NomFichier = "%06d_%s.png" % (psampleid % 10000, suffix)
    if RelativeToVault:
        return VaultFolder + "/" + NomFichier
    else:
        return (vaultroot / VaultFolder / NomFichier).as_posix()


def ExplodeGreyLevel(Nbr, Avg, ET):
    """
    ventile les particule de façon lineaire sur +/- l'ecart type
    :param Nbr: # de particule
    :param Avg: # Gris moyen
    :param ET:  # ecart type
    :return: Liste de paire Nbr, Niveau de gris
    """
    if ET < 1 or Nbr < ET:
        return [[Nbr, Avg]]
    mini = Avg - ET
    if mini < 1:
        mini = 1
    maxi = Avg + ET
    if maxi > 255:
        maxi = 255
    res = []
    Tot = 0
    for i in range(mini, maxi + 1):
        n = round(Nbr / (2 * ET + 1))
        res.append([n, i])
        Tot += n
    res[len(res) // 2][0] += Nbr - Tot  # On ajoute ce qu'il manque sur la moyenne
    return res


def GenerateRawHistogramUVPAPP(UvpSample, Prj, DepthOffset, organizedbydepth, DescentFilter, EcodataPartFile):
    """
    Génération de l'histogramme particulaire à partir d'un fichier généré par UVPApp
    """
    RawImgDepth = {}  # version non filtrée utilisée pour générer le graphique
    ImgDepth = {}  # version filtrée
    ImgTime = {}  # heure des images
    SegmentedData = {'0': {}, '1': {}}  # version filtrée black&flash
    PrevDepth = 0
    DescentFilterRemovedCount = 0
    organizedbytime = not organizedbydepth
    if organizedbytime:
        DescentFilter = False  # sur les profile temporel le filtrage en descente ne peux pas être utilisé.
    z = zipfile.ZipFile(EcodataPartFile.as_posix())
    with z.open("particules.csv", "r") as csvfile:
        logging.info("Processing file " + EcodataPartFile.as_posix() + "/particules.csv")
        idx = -1  # Les index d'image sont en base 0
        for rownum, row in enumerate(csvfile):
            row = row.decode('latin-1')
            rowpart = row.split(":")
            if len(rowpart) != 2:  # Pas une ligne data
                continue
            if rowpart[0][0:2] != "20":
                continue  # les lignes de données commencent toutes par la date 2019-MM-DD ...
            idx += 1
            header = rowpart[0].split(",")
            dateheuretxt = header[0]
            depth = float(header[1]) + DepthOffset
            if math.isnan(depth):
                if organizedbydepth:
                    continue  # si on a pas de profondeur on ne peut pas traiter la donnée
                else:
                    depth = float(0)
            else:
                if depth < 0:
                    depth = 0  # les profondeur négatives sont forcées à 0
            RawImgDepth[idx] = depth
            ImgTime[idx] = dateheuretxt
            flash = header[3]
            # Application du filtre en descente
            KeepLine = True
            if DescentFilter:
                if depth < PrevDepth:
                    KeepLine = False
                else:
                    PrevDepth = depth
            if KeepLine:
                ImgDepth[idx] = depth
            else:
                DescentFilterRemovedCount += 1
            if KeepLine == False:
                continue

            data = [p.split(',') for p in rowpart[1].split(";") if len(p.split(',')) == 4]
            if rowpart[1].find("OVER_EXPOSED") >= 0:
                pass
            elif rowpart[1].find("EMPTY_IMAGE") >= 0:
                pass
            elif int(data[0][0]) == 0:  # taille de particule non valide
                pass
            else:  # Données normale

                if organizedbydepth:
                    Partition = math.floor(depth)
                else:
                    integrationtime = int(UvpSample.integrationtime)
                    if integrationtime <= 0:
                        raise Exception(
                            "GenerateRawHistogramUVPAPP: Sample %d : integrationtime must be a positive value for horizontal profile" % [
                                UvpSample.psampleid])
                    dateheure = datetime.datetime.strptime(dateheuretxt, "%Y%m%d-%H%M%S")
                    partts = (
                                     dateheure.timestamp() // integrationtime) * integrationtime  # Conversion en TimeStamp, regroupement par integration time
                    Partition = int(datetime.datetime.fromtimestamp(partts).strftime(
                        "%Y%m%d%H%M%S"))  # conversion en numerique YYYYMMDDHHMISS

                if flash in ('0', '1'):
                    if Partition not in SegmentedData[flash]:
                        if organizedbydepth:
                            SegmentedData[flash][Partition] = {'depth': Partition, 'imgcount': 0,
                                                               'area': {}}  # 'time':dateheuretxt,
                        else:
                            SegmentedData[flash][Partition] = {'depth': 0, 'time': Partition, 'imgcount': 0, 'area': {}}
                    SegmentedData[flash][Partition]['imgcount'] += 1
                    if organizedbytime:
                        SegmentedData[flash][Partition][
                            'depth'] += depth  # on va calculer la profondeur moyenne, donc on fait la somme
                    for data1taille in data:
                        area = int(data1taille[0])
                        if area not in SegmentedData[flash][Partition]['area']:
                            SegmentedData[flash][Partition]['area'][area] = []  # tableau=liste des niveaux de gris
                        try:
                            SegmentedData[flash][Partition]['area'][area].extend(
                                ExplodeGreyLevel(int(data1taille[1]), round(float(data1taille[2])),
                                                 round(float(data1taille[3]))))  # nbr, moyenne,ecarttype
                        except:
                            raise Exception(
                                "{} at row {} data=[{},{},{},{}]".format(sys.exc_info(), rownum, data1taille[0],
                                                                         data1taille[1], data1taille[2],
                                                                         data1taille[3]))

            # logging.info("rowpart={}",rowpart)

        if len(RawImgDepth) == 0:
            raise Exception("No data in particlefile for sample %s " % [UvpSample.profileid])

        logging.info(
            "Raw image count = {0} , Filtered image count = {1} ,  DescentFiltered images={2}"
                .format(len(RawImgDepth), len(ImgDepth), len(RawImgDepth) - len(ImgDepth) + 1))
        if len(ImgDepth) == 0:
            raise Exception("No remaining filtered data in dat file")

        DepthBinCount = GenerateDepthChart(Prj, UvpSample, RawImgDepth, ImgDepth)
        for flash in ('0', '1'):
            DetHistoFile = GetPathForRawHistoFile(UvpSample.psampleid, flash)
            with bz2.open(DetHistoFile, 'wt', newline='') as f:
                cf = csv.writer(f, delimiter='\t')
                HeaderColsName = ["depth", "imgcount", "area", "nbr", "greylimit1", "greylimit2", "greylimit3"]
                if organizedbytime:
                    HeaderColsName.append("datetime")
                cf.writerow(HeaderColsName)
                PartitionCles = list(SegmentedData[flash].keys())
                PartitionCles.sort()
                for Partition in PartitionCles:
                    if organizedbytime:  # calcule la profondeur moyenne de la partition si profil temporel
                        SegmentedData[flash][Partition]['depth'] = round(
                            SegmentedData[flash][Partition]['depth'] / SegmentedData[flash][Partition]['imgcount'], 1)
                    for area in SegmentedData[flash][Partition]['area']:
                        a = np.array(SegmentedData[flash][Partition]['area'][area])
                        (histo, limits) = np.histogram(a[:, 1], bins=4, weights=a[:, 0])
                        DataRow = [SegmentedData[flash][Partition]['depth'],
                                   SegmentedData[flash][Partition]['imgcount'], area, histo.sum(), limits[1], limits[2],
                                   limits[3]]
                        if organizedbytime:  # ajout de l'heure de la partition
                            DataRow.append(Partition)
                        cf.writerow(DataRow)

        UvpSample.histobrutavailable = True
        UvpSample.imp_descent_filtered_row = DescentFilterRemovedCount
        db.session.commit()


def GenerateRawHistogram(psampleid):
    """
    Génération de l'histogramme particulaire brut stocké dans un fichier tsv bzippé stocké dans le vault.
    :param psampleid:
    :return: None    
    """
    UvpSample = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if UvpSample is None:
        raise Exception("GenerateRawHistogram: Sample %d missing" % psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=UvpSample.pprojid).first()

    FirstImage = int(UvpSample.firstimage)
    LastImage = int(UvpSample.lastimg)
    if LastImage >= 999999:
        LastImage = None
    DepthOffset = Prj.default_depthoffset
    if DepthOffset is None:
        DepthOffset = UvpSample.acq_depthoffset
    if DepthOffset is None:
        DepthOffset = 0
    if UvpSample.organizedbydeepth:
        if Prj.enable_descent_filter == 'Y':
            UvpSample.acq_descent_filter = True
        elif Prj.enable_descent_filter == 'N':
            UvpSample.acq_descent_filter = False
        else:  # si pas explicitement positionné au niveau du projet, on utilise des valeurs par defaut en fonction de l'instrument.
            if Prj.instrumtype == 'uvp5':
                UvpSample.acq_descent_filter = True
            else:
                UvpSample.acq_descent_filter = False
    else:  # si pas organisé par temps, pas de filtre de descente.
        UvpSample.acq_descent_filter = False
    DescentFilter = UvpSample.acq_descent_filter
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
    ServerRoot = Path(part_app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    PathDat = DossierUVPPath / 'results' / (UvpSample.profileid + "_datfile.txt")
    EcodataPartFile = DossierUVPPath / "ecodata" / UvpSample.profileid / (UvpSample.profileid + "_Particule.zip")
    if EcodataPartFile.exists():
        GenerateRawHistogramUVPAPP(UvpSample, Prj, DepthOffset, UvpSample.organizedbydeepth, DescentFilter,
                                   EcodataPartFile)
        return

    if PathDat.exists():
        LstFichiers = [PathDat]
    else:
        PathDat = DossierUVPPath / 'work' / UvpSample.profileid / ('HDR' + UvpSample.filename + ".dat")
        if PathDat.exists():
            LstFichiers = [PathDat]
        else:
            # Le sorted n'as pas l'air necessaire d'après les essais sous windows, mais glob ne garanti pas l'ordre
            LstFichiers = sorted(list(
                (DossierUVPPath / 'raw' / ('HDR' + UvpSample.filename)).glob('HDR' + UvpSample.filename + "*.dat")))
    # print(LstFichiers)
    RawImgDepth = {}  # version non filtrée utilisée pour générer le graphique
    ImgDepth = {}  # version filtrée
    ImgTime = {}  # heure des images
    LastImageIdx = LastImageDepth = None
    for Fichier in LstFichiers:
        logging.info("Processing file " + Fichier.as_posix())
        with Fichier.open(encoding='latin_1') as csvfile:
            Rdr = csv.reader(csvfile, delimiter=';')
            next(Rdr)  # au saute la ligne de titre
            for row in Rdr:
                idx = row[0].strip("\t ")
                instrumdata = row[2].strip("\t ")
                if idx == "" or instrumdata == "": continue
                idx = int(idx)
                instrumdata = instrumdata.split('*')
                depth = float(instrumdata[0]) * 0.1 + DepthOffset
                if (not math.isnan(depth)) and (depth < 0):
                    depth = 0  # les profondeur négatives sont forcées à 0
                RawImgDepth[idx] = depth
                if idx < FirstImage: continue
                ImgTime[idx] = row[1][0:14]
                if LastImage is None:  # On détermine la dernière image si elle n'est pas determinée
                    if DescentFilter == False and (
                            LastImageIdx is None or idx > LastImageIdx):  # si le filtre de descente n'est pas actif on considère toujour la derniere image
                        LastImageIdx = idx
                    elif LastImageDepth is None or depth > LastImageDepth:
                        LastImageDepth = depth
                        LastImageIdx = idx
    if LastImage is None:
        LastImage = LastImageIdx
    if len(RawImgDepth) == 0:
        raise Exception("No data in dat file %s " % (Fichier.as_posix()))
    PrevDepth = 0
    DescentFilterRemovedCount = 0
    # Application du filtre en descente
    for i in range(FirstImage, LastImage + 1):
        if i not in RawImgDepth: continue
        KeepLine = True
        if DescentFilter:
            if RawImgDepth[i] < PrevDepth:
                KeepLine = False
            else:
                PrevDepth = RawImgDepth[i]
        if KeepLine:
            ImgDepth[i] = RawImgDepth[i]
        else:
            DescentFilterRemovedCount += 1
    logging.info(
        "Raw image count = {0} , Filtered image count = {1} , LastIndex= {2},LastIndex-First+1= {4}, DescentFiltered images={3}"
            .format(len(RawImgDepth), len(ImgDepth), LastImage, LastImage - FirstImage - len(ImgDepth) + 1,
                    LastImage - FirstImage + 1))
    if len(ImgDepth) == 0:
        raise Exception("No remaining filtered data in dat file")

    DepthBinCount = GenerateDepthChart(Prj, UvpSample, RawImgDepth, ImgDepth)
    # Ecart format suivant l'endroit
    # Dans results nom = p1604_13.bru toujours au format bru1 malgré l'extension bru fichier unique
    # dans work p1604_13/p1604_13.bru toujours au format bru1 malgré l'extension bru fichier unique
    # dans raw HDR20160429180115/HDR20160429180115_000.bru ou bru1
    # chargement des données particulaires
    logging.info("Processing BRU Files:")
    PathBru = DossierUVPPath / 'results' / (UvpSample.profileid + ".bru")
    if PathBru.exists():
        BRUFormat = "bru1"
        LstFichiers = [PathBru]
    else:
        PathBru = DossierUVPPath / 'work' / UvpSample.profileid / (UvpSample.profileid + ".bru")
        if PathBru.exists():
            BRUFormat = "bru1"
            LstFichiers = [PathBru]
        else:
            LstFichiers = list(
                (DossierUVPPath / 'raw' / ('HDR' + UvpSample.filename)).glob('HDR' + UvpSample.filename + "*.bru"))
            if len(LstFichiers) > 0:
                BRUFormat = "bru"
            else:
                LstFichiers = list(
                    (DossierUVPPath / 'raw' / ('HDR' + UvpSample.filename)).glob('HDR' + UvpSample.filename + "*.bru1"))
                BRUFormat = "bru1"
    # logging.info(LstFichiers)
    SegmentedData = {}  # version filtrée
    for Fichier in LstFichiers:
        logging.info("Processing file " + Fichier.as_posix())
        with Fichier.open(encoding='latin_1') as csvfile:
            Rdr = csv.reader(csvfile, delimiter=';')
            next(Rdr)  # au saute la ligne de titre
            for row in Rdr:
                idx = int(row[0].strip("\t "))
                if idx not in ImgDepth: continue  # c'est sur une image filtrée, on ignore
                if BRUFormat == 'bru':
                    area = int(row[3].strip("\t "))
                    grey = int(row[4].strip("\t "))
                elif BRUFormat == 'bru1':
                    area = int(row[2].strip("\t "))
                    grey = int(row[3].strip("\t "))
                else:
                    raise Exception("Invalid file extension")
                # calcule la parition en section de 5m depuis le minimum
                Depth = math.floor(ImgDepth[idx])
                Partition = Depth
                if Partition not in SegmentedData:
                    SegmentedData[Partition] = {'depth': Depth, 'time': ImgTime[idx],
                                                'imgcount': DepthBinCount[Partition], 'area': {}}
                if area not in SegmentedData[Partition]['area']:
                    SegmentedData[Partition]['area'][area] = []  # tableau=liste des niveaux de gris
                SegmentedData[Partition]['area'][area].append(grey)

    DetHistoFile = GetPathForRawHistoFile(psampleid)
    import bz2
    with bz2.open(DetHistoFile, 'wt', newline='') as f:
        cf = csv.writer(f, delimiter='\t')
        cf.writerow(["depth", "imgcount", "area", "nbr", "greylimit1", "greylimit2", "greylimit3"])
        for Partition, PartitionContent in SegmentedData.items():
            for area, greydata in PartitionContent['area'].items():
                # if area in ('depth', 'time'): continue  # ces clés sont au même niveau que les area
                agreydata = np.asarray(greydata)
                # ça ne gère pas l'organisation temporelle des données
                cf.writerow([PartitionContent['depth'], PartitionContent['imgcount'], area, len(agreydata)
                                , np.percentile(agreydata, 25, interpolation='lower')
                                , np.percentile(agreydata, 50, interpolation='lower')
                                , np.percentile(agreydata, 75, interpolation='higher')]
                            )
    UvpSample.histobrutavailable = True
    UvpSample.lastimgused = LastImage
    UvpSample.imp_descent_filtered_row = DescentFilterRemovedCount
    db.session.commit()


def GenerateDepthChart(Prj, UvpSample, RawImgDepth, ImgDepth):
    font = {'family': 'arial', 'weight': 'normal', 'size': 10}
    plt.rc('font', **font)
    plt.rcParams['lines.linewidth'] = 0.5
    Fig = plt.figure(figsize=(8, 10), dpi=100)
    # 2 lignes, 3 colonnes, graphique en haut à gauche trace de la courbe de descente
    # ax = Fig.add_subplot(231)
    ax = plt.axes()
    aRawImgDepth = np.empty([len(RawImgDepth), 2])
    for i, (idx, dept) in enumerate(sorted(RawImgDepth.items(), key=lambda r: r[0])):
        aRawImgDepth[i] = idx, dept
    # Courbe bleu des données brutes
    ax.plot(aRawImgDepth[:, 0], -aRawImgDepth[:, 1])
    ax.set_xlabel('Image nb')
    ax.set_ylabel('Depth(m)')
    ax.set_xticks(np.arange(0, aRawImgDepth[:, 0].max(), 5000))
    aRawImgDepth = RawImgDepth = None  # libère la mémoire des données brutes, elle ne sont plus utile une fois le graphe tracé
    # courbe rouge des données réduites à first==>Last et filtrées
    aFilteredImgDepth = np.empty([len(ImgDepth), 2])
    for i, (idx, dept) in enumerate(sorted(ImgDepth.items(), key=lambda r: r[0])):
        aFilteredImgDepth[i] = idx, dept
    ax.plot(aFilteredImgDepth[:, 0], -aFilteredImgDepth[:, 1], 'r')
    MinDepth = aFilteredImgDepth[:, 1].min()
    MaxDepth = aFilteredImgDepth[:, 1].max()
    # Calcule le nombre d'image par mettre à partir de 0m
    DepthBinCount = np.bincount(np.floor(aFilteredImgDepth[:, 1]).astype('int'))
    aFilteredImgDepth = None  # version nparray plus necessaire.
    logging.info("Depth range= {0}->{1}".format(MinDepth, MaxDepth))
    # Fig.savefig((DossierUVPPath / 'results' / ('ecotaxa_depth_' + UvpSample.profileid+'.png')).as_posix())
    Fig.text(0.05, 0.98,
             "Project : %s , Profile %s , Filename : %s" % (Prj.ptitle, UvpSample.profileid, UvpSample.filename),
             ha='left')
    Fig.tight_layout(rect=(0, 0, 1, 0.98))  # permet de laisser un peu de blanc en haut pour le titre
    Fig.savefig(GetPathForImportGraph(UvpSample.psampleid, 'depth'))
    Fig.clf()
    return DepthBinCount


def GenerateParticleHistogram(psampleid):
    """
    Génération de l'histogramme particulaire détaillé (45 classes) et réduit (15 classes) à partir de l'histogramme détaillé
    :param psampleid:
    :return:
    """
    UvpSample = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if UvpSample is None:
        raise Exception("GenerateParticleHistogram: Sample %d missing" % psampleid)
    if not UvpSample.histobrutavailable:
        raise Exception(
            "GenerateParticleHistogram: Sample %d Particle Histogram can't be computed without Raw histogram" % psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=UvpSample.pprojid).first()
    ServerRoot = Path(part_app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    FirstImage = UvpSample.firstimage
    LastImage = UvpSample.lastimgused
    if LastImage is None:  # Si aucune determinée lors de la génération de l'histogramme brut, on prend celle spécifiée dans le sample.
        LastImage = UvpSample.lastimg
    if FirstImage is None or LastImage is None:
        raise Exception("GenerateParticuleHistogram sample %s first or last image undefined %s-%s" % (
            UvpSample.profileid, FirstImage, LastImage))

    DetHistoFile = GetPathForRawHistoFile(psampleid)
    logging.info("GenerateParticleHistogram processing raw histogram file  %s" % DetHistoFile)
    Part = np.loadtxt(DetHistoFile, delimiter='\t', skiprows=1)
    if UvpSample.organizedbydeepth:
        # format de raw 0:depth,1:imgcount,2:area,3:nbr,4:greylimit1,greylimit2,greylimit3
        # 1 Ligne par mètre et area, ne contient les données entre fist et last
        MinDepth = Part[:, 0].min()
        # ajout d'attributs calculés pour chaque ligne du fichier.
        PartCalc = np.empty([Part.shape[0], 3])  # col0 = tranche, Col1=ESD, Col2=Biovolume en µl=mm3
        PartCalc[:, 0] = Part[:, 0] // 5  # calcul de la tranche 0 pour [0m..5m[,1 pour [5m..10m[
        PartCalc[:, 1] = 2 * np.sqrt((pow(Part[:, 2], UvpSample.acq_exp) * UvpSample.acq_aa) / np.pi)
        PartCalc[:, 2] = Part[:, 3] * pow(PartCalc[:, 1] / 2, 3) * 4 * math.pi / 3
        LastTranche = PartCalc[:, 0].max()
        # on récupere les 1ère ligne de chaque mètre afin de calculer le volume d'eau
        FirstLigByDepth = Part[np.unique(Part[:, 0], return_index=True)[1]]
        # on calcule le volume de chaque tranche (y compris celle qui n'existent pas en 0 et la profondeur maxi)
        VolumeParTranche = np.bincount((FirstLigByDepth[:, 0] // 5).astype(int), FirstLigByDepth[:,
                                                                                 1]) * UvpSample.acq_volimage  # Bin par tranche de tranche 5m partant de 0m
        MetreParTranche = np.bincount(
            (FirstLigByDepth[:, 0] // 5).astype(int))  # Bin par tranche de tranche 5m partant de 0m
        # On supprime les tranches vides, mais ça fait planter les graphes suivants
        # VolumeParTranche=VolumeParTranche[np.nonzero(VolumeParTranche)]
        # MetreParTranche = MetreParTranche[np.nonzero(VolumeParTranche)]
    else:  # calcul des histogramme temporels
        # format de raw 0:depth,1:imgcount,2:area,3:nbr,4:greylimit1,5:greylimit2,6:greylimit3,7:YYYYMMDDHHMISS en decimal arrondi à la resolution integrationtime
        # 1 Ligne par mètre et area, ne contient les données entre fist et last
        MinDepth = Part[:, 0].min()
        # ajout d'attributs calculés pour chaque ligne du fichier.
        PartCalc = np.empty([Part.shape[0], 3])  # col0 = tranche, Col1=ESD, Col2=Biovolume en µl=mm3
        DateConvDict = {}
        for i in range(Part.shape[0]):
            dateint = int(Part[i, 7])
            if dateint not in DateConvDict:
                DateConvDict[dateint] = datetime.datetime.strptime(str(dateint), "%Y%m%d%H%M%S").timestamp() // 3600
            PartCalc[i, 0] = DateConvDict[dateint]
        TSHeureDebut = np.min(PartCalc[:, 0])
        HeureDebut = datetime.datetime.fromtimestamp(TSHeureDebut * 3600)
        PartCalc[:, 0] -= TSHeureDebut  # contient Le N° de tranche temporelle relatif 0= 1ère tranche, 1=1h plus tard
        PartCalc[:, 1] = 2 * np.sqrt((pow(Part[:, 2], UvpSample.acq_exp) * UvpSample.acq_aa) / np.pi)
        PartCalc[:, 2] = Part[:, 3] * pow(PartCalc[:, 1] / 2, 3) * 4 * math.pi / 3
        # on récupere les 1ère ligne de chaque tranche temporelle originale
        FirstLigIDByImage = np.unique(Part[:, 7], return_index=True)[1]
        # MaxTrancheId=np.max(PartCalc[:, 0])
        # on calcule le volume de chaque tranche (y compris celle qui n'existent (bincount génère touts les pas entre 0 et la MaxTrancheId
        VolumeParTranche = np.bincount((PartCalc[FirstLigIDByImage, 0]).astype(np.int32),
                                       Part[FirstLigIDByImage, 1]) * UvpSample.acq_volimage  # Bin par tranche de 1h
        DepthParTranche = np.bincount((PartCalc[FirstLigIDByImage, 0]).astype(np.int32),
                                      Part[FirstLigIDByImage, 0]) / np.bincount(
            (PartCalc[FirstLigIDByImage, 0]).astype(np.int32))
    # les calculs de concentration sont commun au 2 types de profils
    (PartByClassAndTranche, bins, binsdept) = np.histogram2d(PartCalc[:, 1], PartCalc[:, 0], bins=(
        PartDetClassLimit, np.arange(0, VolumeParTranche.shape[0] + 1))
                                                             , weights=Part[:, 3])
    (BioVolByClassAndTranche, bins, binsdept) = np.histogram2d(PartCalc[:, 1], PartCalc[:, 0], bins=(
        PartDetClassLimit, np.arange(0, VolumeParTranche.shape[0] + 1))
                                                               , weights=PartCalc[:, 2])
    with np.errstate(divide='ignore',
                     invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
        BioVolByClassAndTranche /= VolumeParTranche

    font = {'family': 'arial',
            'weight': 'normal',
            'size': 10}
    plt.rc('font', **font)
    plt.rcParams['lines.linewidth'] = 0.5

    Fig = plt.figure(figsize=(16, 12), dpi=100, )
    if UvpSample.organizedbydeepth:
        # calcul volume par metre moyen de chaque tranche
        ax = Fig.add_subplot(241)
        # si une tranche n'as pas été entierement explorée la /5 est un calcul éronné
        with np.errstate(divide='ignore',
                         invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
            ax.plot(VolumeParTranche / MetreParTranche, np.arange(len(VolumeParTranche)) * -5 - 2.5)
        ax.set_xticks(GetTicks((VolumeParTranche / 5).max()))
        ax.set_xlabel('Volume/M')
        ax.set_ylabel('Depth(m)')

        # Calcul Particle <=0.53
        Filtre = np.argwhere(PartCalc[:, 1] <= 0.53)
        ax = Fig.add_subplot(242)
        (n, bins) = np.histogram(PartCalc[Filtre, 0], np.arange(len(VolumeParTranche) + 1), weights=Part[Filtre, 3])
        with np.errstate(divide='ignore',
                         invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
            n = n / VolumeParTranche
        ax.plot(n, bins[:-1] * -5 - MinDepth - 2.5)
        ax.set_xticks(GetTicks(n.max()))

        ax.set_xlabel('Part 0.06-0.53 mm esd # l-1')
        ax.set_ylabel('Depth(m)')

        # Calcul Particle 0.53->1.06
        Filtre = np.argwhere((PartCalc[:, 1] >= 0.53) & (PartCalc[:, 1] <= 1.06))
        ax = Fig.add_subplot(243)
        (n, bins) = np.histogram(PartCalc[Filtre, 0], np.arange(len(VolumeParTranche) + 1), weights=Part[Filtre, 3])
        with np.errstate(divide='ignore',
                         invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
            n = n / VolumeParTranche
        ax.plot(n, bins[:-1] * -5 - MinDepth - 2.5)
        ax.set_xticks(GetTicks(n.max()))
        ax.set_xlabel('Part 0.53-1.06 mm esd # l-1')
        ax.set_ylabel('Depth(m)')

        # Calcul Particle 1.06->2.66
        Filtre = np.argwhere((PartCalc[:, 1] >= 1.06) & (PartCalc[:, 1] <= 2.66))
        ax = Fig.add_subplot(244)
        (n, bins) = np.histogram(PartCalc[Filtre, 0], np.arange(len(VolumeParTranche) + 1), weights=Part[Filtre, 3])
        with np.errstate(divide='ignore',
                         invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
            n = n / VolumeParTranche
        ax.plot(n, bins[:-1] * -5 - MinDepth - 2.5)
        ax.set_xticks(GetTicks(n.max()))
        ax.set_xlabel('Part 1.06-2.66 mm esd # l-1')
        ax.set_ylabel('Depth(m)')

        # Calcul Biovolume Particle >0.512-<=1.02 mm via histograme
        n = np.sum(BioVolByClassAndTranche[28:30, :], axis=0)
        ax = Fig.add_subplot(245)
        ax.plot(n, np.arange(0, LastTranche + 1) * -5 - 2.5)
        ax.set_xticks(GetTicks(n.max()))
        ax.set_xlabel('Part >=0.512-<1.02 mm esd mm3 l-1 from det histo')
        ax.set_ylabel('Depth(m)')

        # Calcul Particle <=0.512 mm via histograme
        n = np.sum(PartByClassAndTranche[0:28, :], axis=0)
        ax = Fig.add_subplot(246)
        with np.errstate(divide='ignore',
                         invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
            n = n / VolumeParTranche
        ax.plot(n, np.arange(0, LastTranche + 1) * -5 - 2.5)
        ax.set_xticks(GetTicks(n.max()))
        ax.set_xlabel('Part <0.512 mm esd # l-1 from det histo')
        ax.set_ylabel('Depth(m)')

        # Calcul Particle >0.512-<=1.02 mm via histograme
        n = np.sum(PartByClassAndTranche[28:30, :], axis=0)
        ax = Fig.add_subplot(247)
        with np.errstate(divide='ignore',
                         invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
            n = n / VolumeParTranche
        ax.plot(n, np.arange(0, LastTranche + 1) * -5 - 2.5)
        ax.set_xticks(GetTicks(n.max()))
        ax.set_xlabel('Part >=0.512-<1.02 mm esd # l-1 from det histo')
        ax.set_ylabel('Depth(m)')

        # Calcul Particle >0.512-<=1.02 mm via histograme
        n = np.sum(PartByClassAndTranche[30:34, :], axis=0)
        ax = Fig.add_subplot(248)
        with np.errstate(divide='ignore',
                         invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
            n = n / VolumeParTranche
        ax.plot(n, np.arange(0, LastTranche + 1) * -5 - 2.5)
        ax.set_xticks(GetTicks(n.max()))
        ax.set_xlabel('Part >=1.02-<2.58 mm esd # l-1 from det histo')
        ax.set_ylabel('Depth(m)')
    else:
        # calcul volume par metre moyen de chaque tranche
        ax = Fig.add_subplot(421)
        # si une tranche n'as pas été entierement explorée la /5 est un calcul éronné
        ax.plot(np.arange(len(VolumeParTranche)) + 0.5, VolumeParTranche)
        ax.set_yticks(GetTicks(VolumeParTranche.max()))
        ax.set_ylabel('Volume')

        # Calcul Particle <=0.53
        Graphes = [
            {'filtre': np.argwhere(PartCalc[:, 1] <= 0.53), "label": 'Part 0.06-0.53 mm esd # l-1', 'pos': 422},
            {'filtre': np.argwhere((PartCalc[:, 1] >= 0.53) & (PartCalc[:, 1] <= 1.06)),
             "label": 'Part 0.53-1.06 mm esd # l-1', 'pos': 423},
            {'filtre': np.argwhere((PartCalc[:, 1] >= 1.06) & (PartCalc[:, 1] <= 2.66)),
             "label": 'Part 1.06-2.66 mm esd # l-1', 'pos': 424},
        ]
        for G in Graphes:
            ax = Fig.add_subplot(G['pos'])
            (n, bins) = np.histogram(PartCalc[G['filtre'], 0], np.arange(len(VolumeParTranche) + 1),
                                     weights=Part[G['filtre'], 3])
            with np.errstate(divide='ignore',
                             invalid='ignore'):  # masque les warning provoquées par les divisions par 0 des tranches vides.
                n = n / VolumeParTranche
            ax.plot(np.arange(len(VolumeParTranche)) + 0.5, n)
            ax.set_yticks(GetTicks(n.max()))
            ax.set_ylabel(G['label'])

        # Calcul Biovolume Particle >0.512-<=1.02 mm via histograme
        Graphes = [
            {'data': np.sum(BioVolByClassAndTranche[28:30, :], axis=0), "label": 'Part >=0.512-<1.02 mm esd mm3 l-1',
             'pos': 425},
            {'data': np.sum(PartByClassAndTranche[0:28, :], axis=0) / VolumeParTranche,
             "label": 'Part <0.512 mm esd # l-1', 'pos': 426},
            {'data': np.sum(PartByClassAndTranche[28:30, :], axis=0) / VolumeParTranche,
             "label": 'Part >=0.512-<1.02 mm esd # l-1', 'pos': 427},
            {'data': np.sum(PartByClassAndTranche[30:34, :], axis=0) / VolumeParTranche,
             "label": 'Part >=1.02-<2.58 mm esd # l-1', 'pos': 428},
        ]
        for G in Graphes:
            ax = Fig.add_subplot(G['pos'])
            ax.plot(np.arange(len(VolumeParTranche)) + 0.5, G['data'])
            ax.set_yticks(GetTicks(G['data'].max()))
            ax.set_xlabel('Time(h) from det histo')
            ax.set_ylabel(G['label'])

    # Fig.savefig((DossierUVPPath / 'results' / ('ecotaxa_particle_' + UvpSample.profileid+'.png')).as_posix())
    Fig.text(0.05, 0.99,
             "Project : %s , Profile %s , Filename : %s" % (Prj.ptitle, UvpSample.profileid, UvpSample.filename),
             ha='left')
    # Fig.suptitle("Project %s : Profile %s"%(Prj.ptitle,UvpSample.profileid), ha='center')
    Fig.tight_layout(rect=(0, 0, 1, 0.99))  # permet de laisser un peu de blanc en haut pour le titre
    Fig.savefig(GetPathForImportGraph(psampleid, 'particle'))
    Fig.clf()

    ExecSQL("delete from part_histopart_det where psampleid=" + str(psampleid))
    sql = """insert into part_histopart_det(psampleid, lineno, depth,  watervolume,datetime
        , class01, class02, class03, class04, class05, class06, class07, class08, class09, class10, class11, class12, class13, class14
        , class15, class16, class17, class18, class19, class20, class21, class22, class23, class24, class25, class26, class27, class28, class29
        , class30, class31, class32, class33, class34, class35, class36, class37, class38, class39, class40, class41, class42, class43, class44, class45
        , biovol01, biovol02, biovol03, biovol04, biovol05, biovol06, biovol07, biovol08, biovol09, biovol10, biovol11, biovol12, biovol13, biovol14
        , biovol15, biovol16, biovol17, biovol18, biovol19, biovol20, biovol21, biovol22, biovol23, biovol24, biovol25, biovol26, biovol27, biovol28, biovol29
        , biovol30, biovol31, biovol32, biovol33, biovol34, biovol35, biovol36, biovol37, biovol38, biovol39, biovol40, biovol41, biovol42, biovol43, biovol44, biovol45
        )
    values(%(psampleid)s,%(lineno)s,%(depth)s,%(watervolume)s,%(datetime)s
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
    sqlparam = {'psampleid': psampleid}
    for i, r in enumerate(VolumeParTranche):
        sqlparam['lineno'] = i
        if UvpSample.organizedbydeepth:
            sqlparam['depth'] = (i * 5 + 2.5)
            sqlparam['datetime'] = None
        else:
            sqlparam['depth'] = round(DepthParTranche[i], 1)
            sqlparam['datetime'] = HeureDebut + datetime.timedelta(hours=i, minutes=30)
        if VolumeParTranche[
            i] == 0:  # On ne charge pas les lignes sans volume d'eau car ça signifie qu'l n'y a pas eu d'échantillon
            continue
        sqlparam['watervolume'] = VolumeParTranche[i]
        for k in range(0, 45):
            sqlparam['class%02d' % (k + 1)] = PartByClassAndTranche[k, i]
        for k in range(0, 45):
            sqlparam['biovol%02d' % (k + 1)] = BioVolByClassAndTranche[k, i]
        ExecSQL(sql, sqlparam)

    GenerateReducedParticleHistogram(psampleid)


def GenerateTaxonomyHistogram(ecotaxa_if: EcoTaxaInstance, psampleid):
    """
    Génération de l'histogramme Taxonomique 
    :param psampleid:
    :return:
    """
    UvpSample = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if UvpSample is None:
        raise Exception("GenerateTaxonomyHistogram: Sample %d missing" % psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=UvpSample.pprojid).first()
    if UvpSample.sampleid is None:
        raise Exception("GenerateTaxonomyHistogram: EcoTaxa sampleid is required in Sample %d " % psampleid)
    pixel = UvpSample.acq_pixel

    # Lire le projet EcoTaxa correspondant
    zoo_proj = ecotaxa_if.get_project(Prj.projid)
    if zoo_proj is None:
        raise Exception("GenerateTaxonomyHistogram: EcoTaxa project %s could not be read in EcoPart project %s"
                        % (Prj.projid, Prj.pprojid))
    areacol = zoo_proj.obj_free_cols.get("area")
    if areacol is None:
        raise Exception("GenerateTaxonomyHistogram: area attribute is required in EcoTaxa project %d" % Prj.projid)
    # part_app.logger.info("Esd col is %s",areacol)

    DepthOffset = Prj.default_depthoffset
    if DepthOffset is None:
        DepthOffset = UvpSample.acq_depthoffset
    if DepthOffset is None:
        DepthOffset = 0

    queried_columns = ["obj.classif_id", "obj.classif_qual", "obj.depth_min", "fre.area"]
    api_res = ecotaxa_if.get_objects_for_sample(zoo_proj.projid, UvpSample.sampleid, queried_columns,
                                                only_validated=True)
    # Do some calculations/filtering for returned data
    res = []
    for an_obj in api_res:
        if an_obj["classif_id"] is None or an_obj["depth_min"] is None or an_obj["area"] is None:
            continue
        an_obj["tranche"] = int((an_obj["depth_min"] + DepthOffset) / 5)
        res.append(an_obj)

    LstTaxo = {}
    for r in res:
        # On aggrège par catégorie+tranche d'eau
        cle = "{}/{}".format(r['classif_id'], r['tranche'])
        if cle not in LstTaxo:
            LstTaxo[cle] = {'nbr': 0, 'esdsum': 0, 'bvsum': 0, 'classif_id': r['classif_id'], 'tranche': r['tranche']}
        LstTaxo[cle]['nbr'] += 1
        esd = 2 * math.sqrt(r['area'] * (pixel ** 2) / math.pi)
        LstTaxo[cle]['esdsum'] += esd
        biovolume = pow(esd / 2, 3) * 4 * math.pi / 3
        LstTaxo[cle]['bvsum'] += biovolume

    LstVol = GetAssoc("""select cast(round((depth-2.5)/5) as INT) tranche, watervolume 
    from part_histopart_reduit 
    where psampleid=%s""" % psampleid)
    # 0 Taxoid, tranche
    # TblTaxo=np.empty([len(LstTaxo),4])
    ExecSQL("delete from part_histocat_lst where psampleid=%s" % psampleid)
    ExecSQL("delete from part_histocat where psampleid=%s" % psampleid)
    sql = """insert into part_histocat(psampleid, classif_id, lineno, depth, watervolume, nbr, avgesd, totalbiovolume)
            values({psampleid},{classif_id},{lineno},{depth},{watervolume},{nbr},{avgesd},{totalbiovolume})"""
    for r in LstTaxo.values():
        avgesd = r['esdsum'] / r['nbr']
        biovolume = r['bvsum']
        watervolume = 'NULL'
        if r['tranche'] in LstVol:
            watervolume = LstVol[r['tranche']]['watervolume']
        ExecSQL(sql.format(
            psampleid=psampleid, classif_id=r['classif_id'], lineno=r['tranche'], depth=r['tranche'] * 5 + 2.5,
            watervolume=watervolume
            , nbr=r['nbr'], avgesd=avgesd, totalbiovolume=biovolume))
    ExecSQL("""insert into part_histocat_lst(psampleid, classif_id) 
            select distinct psampleid,classif_id from part_histocat where psampleid=%s""" % psampleid)

    ExecSQL("""update part_samples set daterecalculhistotaxo=current_timestamp  
            where psampleid=%s""" % psampleid)
