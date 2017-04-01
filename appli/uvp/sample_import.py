from appli import db,app, database , ObjectToStr,PrintInCharte,gvp,gvg,EncodeEqualList,DecodeEqualList,ntcv,GetAppManagerMailto,CreateDirConcurrentlyIfNeeded
from pathlib import Path
import appli.uvp.database as uvpdatabase, logging

# Purge les espace et converti le Nan en vide
def CleanValue(v):
    v=v.strip()
    if v.lower()=='nan':
        v=''
    if v.lower().find('inf')>=0:
        v=''
    return v;
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
    Sample=uvpdatabase.uvp_samples.query.filter_by(profileid=headerdata['profileid']).first()
    if Sample is None:
        logging.info("Create sample for %s %s"%(headerdata['profileid'],headerdata['filename']))
        Sample = uvpdatabase.uvp_samples()
        Sample.profileid=headerdata['profileid']
        Sample.uprojid=uprojid
        db.session.add(Sample)
    else:
        logging.info("Update sample %s for %s %s" % (Sample.usampleid,headerdata['profileid'], headerdata['filename']))
    Sample.filename=headerdata['filename']
    Sample.latitude = ToFloat(headerdata['latitude'])
    Sample.longitude = ToFloat(headerdata['longitude'])
    Sample.organizedbydeepth = True
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
    Sample.yoyo = headerdata['yoyo']
    Sample.firstimage = int(headerdata['firstimage'])
    Sample.lastimg = int(headerdata['endimg'])

    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / Prj.rawfolder
    uvp5_configuration_data =  DossierUVPPath / "config"/"uvp5_settings"/"uvp5_configuration_data.txt"
    if not uvp5_configuration_data.exists():
        logging.warning("file %s is missing"%(uvp5_configuration_data.as_posix()))
    else:
        with uvp5_configuration_data.open('r') as F:
            Lines=F.readlines()
            print("%s"%(Lines))
            # TODO traiter ce fichier

    HDRFolder =  DossierUVPPath / "raw"/("HDR"+Sample.filename)
    HDRFile = HDRFolder/("HDR"+Sample.filename+".hdr")
    if not HDRFile.exists():
        raise Exception("File %s is missing "%(HDRFile.as_posix()))
    else:
        with HDRFile.open('r') as F:
            # Lines=F.readlines()
            Lines = F.readline()
            Ligne2=Lines = F.readline()
            Sample.acq_filedescription = Ligne2.strip('; \r\n')
            print("Ligne2= %s" % (Ligne2))
            Lines = F.read()
            HdrParam=DecodeEqualList(Lines)
            print("%s" % (HdrParam))
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

    # TODO TRAITER YOYO, instrumsn, sampledate
    # TODO pixel à supprimer ?
    # {'yoyo': 'N', 'firstimage': '2276',   'endimg': '16207'
    # 'ctdrosettefilename': 'skq201605s-007avg',
    # ,
    # ,  }
    db.session.commit()

    return None