from pathlib import Path

import numpy as np

from .. import database as partdatabase
import csv
import logging
from ..constants import PartDetClassLimit
from ..app import part_app, db
from ..db_utils import ExecSQL
from ..funcs.common_sample_import import CleanValue, ToFloat, GenerateReducedParticleHistogram


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
        logging.info("Create LISST sample for %s %s" % (headerdata['profileid'], headerdata['filename']))
        Sample = partdatabase.part_samples()
        Sample.profileid = headerdata['profileid']
        Sample.pprojid = pprojid
        db.session.add(Sample)
    else:
        logging.info(
            "Update LISST sample %s for %s %s" % (Sample.psampleid, headerdata['profileid'], headerdata['filename']))
    Sample.filename = headerdata['filename']
    # TODO le calcule à partir de la première ligne
    # Sample.sampledate=datetime.datetime(int(headerdata['filename'][0:4]),int(headerdata['filename'][4:6]),int(headerdata['filename'][6:8])
    #                                    ,int(headerdata['filename'][8:10]), int(headerdata['filename'][10:12]), int(headerdata['filename'][12:14])
    #                                     )
    Sample.latitude = ToFloat(headerdata['latitude'])
    Sample.longitude = ToFloat(headerdata['longitude'])
    Sample.organizedbydeepth = True
    Sample.stationid = headerdata['stationid']
    Sample.comment = headerdata['comment']
    Sample.lisst_zscat_filename = headerdata['zscat_filename']
    Sample.lisst_kernel = headerdata['kernel']
    Sample.lisst_year = headerdata['year']
    db.session.commit()
    return Sample.psampleid


def BuildLISSTClass(kerneltype):
    if kerneltype == 'spherical':
        X = 1.25
    elif kerneltype == 'random':
        X = 1.00
    else:
        raise Exception("Invalide LISST kernel type '%s'" % kerneltype)
    LISSTClass = np.ndarray((32, 3))
    rho = np.power(200.0, 1 / 32.0)
    LISSTClass[:, 0] = 1.25 * (np.power(rho, np.arange(0, 32))) / 1000
    LISSTClass[:, 1] = 1.25 * (np.power(rho, np.arange(1, 33))) / 1000
    LISSTClass[:, 2] = np.sqrt(LISSTClass[:, 0] * LISSTClass[:, 1])
    return LISSTClass


def MapClasses(L, LISSTClass):
    # print (L)
    Res = np.zeros(45)
    for i, q in enumerate(L):
        # print ("%d %0.06f-%0.06f %g"%(i,LISSTClass[i,0],LISSTClass[i,1],q))
        if q != 0:  # on ne passe pas du temps à essayer de ventiler 0
            # recherche des limites dans PartDetClassLimit
            FirstClass = -1
            for ipd, pdl in enumerate(PartDetClassLimit):
                if FirstClass < 0 and pdl > LISSTClass[i, 0]:
                    FirstClass = ipd - 1
                if pdl > LISSTClass[i, 1]:
                    LastClass = ipd - 1
                    break
            if FirstClass == LastClass:  # ventilé dans une classe unique
                Res[FirstClass] += q
            else:  # ventillé dans 2 classes (il n'y a jamais plus de 2 classes
                Limite = PartDetClassLimit[LastClass]
                Gauche = q * (Limite - LISSTClass[i, 0]) / (LISSTClass[i, 1] - LISSTClass[i, 0])
                Droite = q - Gauche
                # print("        %0.06f-%0.06f" % (Gauche,Droite))
                Res[FirstClass] += Gauche
                Res[FirstClass + 1] += Droite

            # print("   %d-%d %0.06f-%0.06f q=%0.06f"%(FirstClass,LastClass,PartDetClassLimit[FirstClass],PartDetClassLimit[LastClass+1],Res[FirstClass]))
    # print (Res)
    # print(np.sum(L),np.sum(Res),np.sum(L)-np.sum(Res))
    return Res


def GenerateParticleHistogram(psampleid):
    """
    Génération de l'histogramme particulaire détaillé (45 classes) et réduit (15 classes) à partir du fichier ASC
    :param psampleid:
    :return:
    """
    PartSample = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if PartSample is None:
        raise Exception("GenerateRawHistogram: Sample %d missing" % psampleid)
    LISSTClass = BuildLISSTClass(PartSample.lisst_kernel)

    Prj = partdatabase.part_projects.query.filter_by(pprojid=PartSample.pprojid).first()
    ServerRoot = Path(part_app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    Fichier = DossierUVPPath / "work" / (PartSample.filename + '.asc')
    logging.info("Processing file " + Fichier.as_posix())
    NbrLine = 0
    with Fichier.open() as csvfile:
        for L in csvfile:
            NbrLine += 1
    logging.info("Line count %d" % NbrLine)
    # Col0=Nbr Data pour calculer la moyenne , 1->45 Biovol cumulé puis moyénné
    HistoByTranche = np.zeros((1, 46))
    with Fichier.open() as csvfile:
        Rdr = csv.reader(csvfile, delimiter=' ')
        for i, row in enumerate(Rdr):
            Depth = float(row[36])
            if PartSample.organizedbydeepth:
                Tranche = Depth // 5
            else:
                Tranche = i // 50
            Part = np.empty(32)
            for k in range(0, 32):
                Part[k] = float(row[k])
            # Mappe les 32 classes et retourne les 45 classes
            Part = MapClasses(Part, LISSTClass)
            # Todo gérer l'horodatage des tranche en profil horizontal
            if Tranche >= HistoByTranche.shape[0]:
                NewArray = np.zeros((Tranche + 1, 46))
                NewArray[0:HistoByTranche.shape[0], :] = HistoByTranche
                HistoByTranche = NewArray

            HistoByTranche[Tranche, 1:46] += Part
            HistoByTranche[Tranche, 0] += 1
    HistoByTranche[:, 1:46] /= HistoByTranche[:, 0, np.newaxis]

    ExecSQL("delete from part_histopart_det where psampleid=" + str(psampleid))
    sql = """insert into part_histopart_det(psampleid, lineno, depth,  watervolume
        , biovol01, biovol02, biovol03, biovol04, biovol05, biovol06, biovol07, biovol08, biovol09, biovol10, biovol11, biovol12, biovol13, biovol14
        , biovol15, biovol16, biovol17, biovol18, biovol19, biovol20, biovol21, biovol22, biovol23, biovol24, biovol25, biovol26, biovol27, biovol28, biovol29
        , biovol30, biovol31, biovol32, biovol33, biovol34, biovol35, biovol36, biovol37, biovol38, biovol39, biovol40, biovol41, biovol42, biovol43, biovol44, biovol45)
    values(%(psampleid)s,%(lineno)s,%(depth)s,%(watervolume)s,%(biovol01)s,%(biovol02)s,%(biovol03)s,%(biovol04)s,%(biovol05)s,%(biovol06)s
    ,%(biovol07)s,%(biovol08)s,%(biovol09)s,%(biovol10)s,%(biovol11)s,%(biovol12)s,%(biovol13)s,%(biovol14)s,%(biovol15)s,%(biovol16)s,%(biovol17)s
    ,%(biovol18)s,%(biovol19)s,%(biovol20)s,%(biovol21)s,%(biovol22)s,%(biovol23)s,%(biovol24)s,%(biovol25)s,%(biovol26)s,%(biovol27)s,%(biovol28)s
    ,%(biovol29)s,%(biovol30)s,%(biovol31)s,%(biovol32)s,%(biovol33)s,%(biovol34)s,%(biovol35)s,%(biovol36)s,%(biovol37)s,%(biovol38)s,%(biovol39)s
    ,%(biovol40)s,%(biovol41)s,%(biovol42)s,%(biovol43)s,%(biovol44)s,%(biovol45)s)"""
    sqlparam = {'psampleid': psampleid}
    for i, r in enumerate(HistoByTranche):
        sqlparam['lineno'] = i
        # Todo ajuste au type
        sqlparam['depth'] = (i * 5 + 2.5)
        sqlparam['watervolume'] = None
        # sqlparam['watervolume'] = VolumeParTranche[i]
        for k in range(0, 45):
            sqlparam['biovol%02d' % (k + 1)] = r[k + 1]
        ExecSQL(sql, sqlparam)

    GenerateReducedParticleHistogram(psampleid)
