import csv
import datetime
import io
import math
import zipfile
from pathlib import Path

import numpy as np

from .. import database as partdatabase
from ..app import part_app, db
from ..constants import CTDFixedCol
from ..db_utils import ExecSQL, GetAll
from ..txt_utils import EncodeEqualList


# Purge les espace et converti le Nan en vide
def CleanValue(v):
    if type(v) != str:
        return v
    v = v.strip()
    if (v.lower() == 'nan') or (v.lower() == 'na'):
        v = ''
    if v.lower().find('inf') >= 0:
        v = ''
    return v


# retourne le flottant image de la chaine en faisant la conversion ou None
def ToFloat(value):
    if value == '': return None
    try:
        return float(value)
    except ValueError:
        return None


def GetTicks(MaxVal):
    if np.isnan(MaxVal):
        MaxVal = 100  # Arbitraire si MaxVal n'est pas valide
    if MaxVal < 1:
        MaxVal = 1
    Step = math.pow(10, math.floor(math.log10(MaxVal)))
    if (MaxVal / Step) < 3:
        Step = Step / 2
    return np.arange(0, MaxVal, Step)


def GenerateReducedParticleHistogram(psampleid):
    """
    Génération de l'histogramme particulaire détaillé (45 classes) et réduit (15 classes) à partir de l'histogramme détaillé
    :param psampleid:
    :return:
    """
    if GetAll("select count(*) from part_histopart_det where psampleid=" + str(psampleid))[0][0] <= 0:
        return "<span style='color: red;'>Reduced Histogram can't be computer without Detailed histogram</span>"
    ExecSQL("delete from part_histopart_reduit where psampleid=" + str(psampleid))
    sql = """insert into part_histopart_reduit(psampleid, lineno, depth,datetime,  watervolume
    , class01, class02, class03, class04, class05, class06, class07, class08, class09, class10, class11, class12, class13, class14, class15
    , biovol01, biovol02, biovol03, biovol04, biovol05, biovol06, biovol07, biovol08, biovol09, biovol10, biovol11, biovol12, biovol13, biovol14, biovol15
    )
    select psampleid, lineno, depth,datetime,  watervolume,
      coalesce(class01,0)+coalesce(class02,0)+coalesce(class03,0) as c1, 
      coalesce(class04,0)+coalesce(class05,0)+coalesce(class06,0) as c2, 
      coalesce(class07,0)+coalesce(class08,0)+coalesce(class09,0) as c3,
      coalesce(class10,0)+coalesce(class11,0)+coalesce(class12,0) as c4,
      coalesce(class13,0)+coalesce(class14,0)+coalesce(class15,0) as c5,
      coalesce(class16,0)+coalesce(class17,0)+coalesce(class18,0) as c6,
      coalesce(class19,0)+coalesce(class20,0)+coalesce(class21,0) as c7,
      coalesce(class22,0)+coalesce(class23,0)+coalesce(class24,0) as c8,
      coalesce(class25,0)+coalesce(class26,0)+coalesce(class27,0) as c9,
      coalesce(class28,0)+coalesce(class29,0)+coalesce(class30,0) as c10,
      coalesce(class31,0)+coalesce(class32,0)+coalesce(class33,0) as c11,
      coalesce(class34,0)+coalesce(class35,0)+coalesce(class36,0) as c12,
      coalesce(class37,0)+coalesce(class38,0)+coalesce(class39,0) as c13,
      coalesce(class40,0)+coalesce(class41,0)+coalesce(class42,0) as c14, 
      coalesce(class43,0)+coalesce(class44,0)+coalesce(class45,0) as c15,
      coalesce(biovol01,0)+coalesce(biovol02,0)+coalesce(biovol03,0) as bv1, 
      coalesce(biovol04,0)+coalesce(biovol05,0)+coalesce(biovol06,0) as bv2, 
      coalesce(biovol07,0)+coalesce(biovol08,0)+coalesce(biovol09,0) as bv3,
      coalesce(biovol10,0)+coalesce(biovol11,0)+coalesce(biovol12,0) as bv4,
      coalesce(biovol13,0)+coalesce(biovol14,0)+coalesce(biovol15,0) as bv5,
      coalesce(biovol16,0)+coalesce(biovol17,0)+coalesce(biovol18,0) as bv6,
      coalesce(biovol19,0)+coalesce(biovol20,0)+coalesce(biovol21,0) as bv7,
      coalesce(biovol22,0)+coalesce(biovol23,0)+coalesce(biovol24,0) as bv8,
      coalesce(biovol25,0)+coalesce(biovol26,0)+coalesce(biovol27,0) as bv9,
      coalesce(biovol28,0)+coalesce(biovol29,0)+coalesce(biovol30,0) as bv10,
      coalesce(biovol31,0)+coalesce(biovol32,0)+coalesce(biovol33,0) as bv11,
      coalesce(biovol34,0)+coalesce(biovol35,0)+coalesce(biovol36,0) as bv12,
      coalesce(biovol37,0)+coalesce(biovol38,0)+coalesce(biovol39,0) as bv13,
      coalesce(biovol40,0)+coalesce(biovol41,0)+coalesce(biovol42,0) as bv14, 
      coalesce(biovol43,0)+coalesce(biovol44,0)+coalesce(biovol45,0) as bv15
    from part_histopart_det where psampleid=""" + str(psampleid)
    ExecSQL(sql)
    return " reduced Histogram computed"


def ImportCTD(psampleid, user_name, user_email):
    """
    Importe les données CTD 
    :param psampleid:
    :return:
    """

    UvpSample = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if UvpSample is None:
        raise Exception("ImportCTD: Sample %d missing" % psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=UvpSample.pprojid).first()
    if Prj.instrumtype == 'uvp6remote':
        import part_app.funcs.uvp_sample_import as uvp_sample_import
        rawfileinvault = uvp_sample_import.GetPathForRawHistoFile(UvpSample.psampleid)
        zf = zipfile.ZipFile(rawfileinvault, "r")
        if 'CTD.txt' not in zf.namelist():
            part_app.logger.info("CTD.txt file missing")
            return False
        fctb = zf.open('CTD.txt', 'r')
        tsvfile = io.TextIOWrapper(fctb, encoding='latin_1')
    else:  # process normal par traitement du repertoire des données
        ServerRoot = Path(part_app.config['SERVERLOADAREA'])
        DossierUVPPath = ServerRoot / Prj.rawfolder
        CtdFile = DossierUVPPath / "ctd_data_cnv" / (UvpSample.profileid + ".ctd")
        if not CtdFile.exists():
            part_app.logger.info("CTD file %s missing", CtdFile.as_posix())
            return False
        part_app.logger.info("Import CTD file %s", CtdFile.as_posix())
        tsvfile = CtdFile.open('r', encoding='latin_1')

    Rdr = csv.reader(tsvfile, delimiter='\t')
    HeadRow = Rdr.__next__()
    # Analyser la ligne de titre et assigner à chaque ID l'attribut
    # Construire la table d'association des attributs complémentaires.
    ExtramesID = 0
    Mapping = []
    ExtraMapping = {}
    for ic, c in enumerate(HeadRow):
        clow = c.lower().strip()
        if clow == "chloro fluo [mg chl/m3]": clow = "chloro fluo [mg chl m-3]"
        if clow == "conductivity [ms/cm]": clow = "conductivity [ms cm-1]"
        if clow == "depth [salt water, m]": clow = "depth [m]"
        if clow == "fcdom factory [ppb qse]": clow = "fcdom [ppb qse]"
        if clow == "in situ density anomaly [kg/m3]": clow = "in situ density anomaly [kg m-3]"
        if clow == "nitrate [µmol/l]": clow = "nitrate [umol l-1]"
        if clow == "oxygen [µmol/kg]": clow = "oxygen [umol kg-1]"
        if clow == "oxygen [ml/l]": clow = "oxygen [ml l-1]"
        if clow == "par [µmol m-2 s-1]": clow = "par [umol m-2 s-1]"
        if clow == "potential density anomaly [kg/m3]": clow = "potential density anomaly [kg m-3]"
        if clow == "pressure in water column [db]": clow = "pressure [db]"
        if clow == "spar [µmol m-2 s-1]": clow = "spar [umol m-2 s-1]"
        if clow in CTDFixedCol:
            Target = CTDFixedCol[clow]
        else:
            # print (clow)
            ExtramesID += 1
            Target = 'extrames%02d' % ExtramesID
            ExtraMapping['%02d' % ExtramesID] = c
            if ExtramesID > 20:
                raise Exception("ImportCTD: Too much CTD data, column %s skipped" % c)
        Mapping.append(Target)
    part_app.logger.info("Mapping = %s", Mapping)
    ExecSQL("delete from part_ctd where psampleid=%s" % psampleid)
    for i, r in enumerate(Rdr):
        cl = partdatabase.part_ctd()
        cl.psampleid = psampleid
        cl.lineno = i
        for i, c in enumerate(Mapping):
            v = CleanValue(r[i])
            if v != '':
                if c == 'qc_flag':
                    setattr(cl, c, int(float(v)))
                elif c == 'datetime':
                    setattr(cl, c, datetime.datetime(int(v[0:4]), int(v[4:6]), int(v[6:8]), int(v[8:10]), int(v[10:12]),
                                                     int(v[12:14]), int(v[14:17]) * 1000))
                else:
                    setattr(cl, c, v)
        db.session.add(cl)
        db.session.commit()
    UvpSample.ctd_desc = EncodeEqualList(ExtraMapping)
    UvpSample.ctd_import_datetime = datetime.datetime.now()
    UvpSample.ctd_import_name = user_name
    UvpSample.ctd_import_email = user_email
    db.session.commit()
    return True
