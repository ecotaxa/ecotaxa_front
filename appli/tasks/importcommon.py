import logging
import math
import re
from pathlib import Path

from flask import request, flash

from appli import gvp, app, UtfDiag
from appli.database import GetAll
# object_annotation_category_id
from appli.tasks.taskmanager import AsyncTask

PredefinedTables = ['obj_field', 'sample', 'process', 'acq']
# PredefinedTypes={'[float]':'n','[int]':'n','[text]':'t'}
PredefinedTypes = {'[f]': 'n', '[t]': 't'}
PredefinedFields = {
    'object_id': {'table': 'obj_field', 'field': 'orig_id', 'type': 't'},
    'sample_id': {'table': 'sample', 'field': 'orig_id', 'type': 't'},
    'acq_id': {'table': 'acq', 'field': 'orig_id', 'type': 't'},
    'process_id': {'table': 'process', 'field': 'orig_id', 'type': 't'},
    'object_lat': {'table': 'obj_head', 'field': 'latitude', 'type': 'n'},
    'object_lon': {'table': 'obj_head', 'field': 'longitude', 'type': 'n'},
    'object_date': {'table': 'obj_head', 'field': 'objdate', 'type': 't'},
    'object_time': {'table': 'obj_head', 'field': 'objtime', 'type': 't'},
    'object_link': {'table': 'obj_head', 'field': 'object_link', 'type': 't'},
    'object_depth_min': {'table': 'obj_head', 'field': 'depth_min', 'type': 'n'},
    'object_depth_max': {'table': 'obj_head', 'field': 'depth_max', 'type': 'n'},
    'object_annotation_category': {'table': 'obj_head', 'field': 'classif_id', 'type': 't'},
    'object_annotation_category_id': {'table': 'obj_head', 'field': 'classif_id', 'type': 'n'},
    'object_annotation_person_email': {'table': 'obj_head', 'field': 'tmp_annotemail', 'type': 't'},
    'object_annotation_date': {'table': 'obj_head', 'field': 'classif_when', 'type': 't'},
    'object_annotation_time': {'table': 'obj_head', 'field': 'tmp_annottime', 'type': 't'},
    'object_annotation_person_name': {'table': 'obj_head', 'field': 'classif_who', 'type': 't'},
    'object_annotation_status': {'table': 'obj_head', 'field': 'classif_qual', 'type': 't'},
    'img_rank': {'table': 'image', 'field': 'imgrank', 'type': 'n'},
    'img_file_name': {'table': 'image', 'field': 'orig_file_name', 'type': 't'},
    'annotation_person_first_name': {'table': 'obj_head', 'field': 'tmp_todelete1', 'type': 't'},
    'sample_dataportal_descriptor': {'table': 'sample', 'field': 'dataportal_descriptor', 'type': 't'},
    'acq_instrument': {'table': 'acq', 'field': 'instrument', 'type': 't'},
}


# Purge les espace et converti le Nan en vide
def CleanValue(v):
    if v is None:
        return ''
    v = v.strip()
    if (v.lower() == 'nan') or (v.lower() == 'na'):
        v = ''
    return v


# retourne le flottant image de la chaine en faisant la conversion ou None
def ToFloat(value):
    if value == '': return None
    try:
        return float(value)
    except ValueError:
        return None


def ResolveTaxoFound(TaxoFound, o_NotFoundTaxo):
    lowertaxonlist = []
    regexsearchparenthese = re.compile('(.+) \((.+)\)$')
    for lowertaxon in TaxoFound.keys():
        TaxoFound[lowertaxon] = {'nbr': 0, 'id': None}
        lowertaxonlist.append(lowertaxon)
        resregex = regexsearchparenthese.match(lowertaxon)
        if resregex:  # Si on trouve des parenthèse à la fin
            lowertaxonLT = resregex.group(1) + '<' + resregex.group(2)
            TaxoFound[lowertaxon]['alterdisplayname'] = lowertaxonLT
            lowertaxonlist.append(lowertaxonLT)

    TaxonsFromDB = GetAll(
        """SELECT t.id,lower(t.name) AS name,lower(t.display_name) display_name,lower(t.name)||'<'||lower(p.name) AS computedchevronname 
            FROM taxonomy t
            LEFT JOIN taxonomy p on t.parent_id=p.id
            WHERE lower(t.name) = ANY(%s) OR lower(t.display_name) = ANY(%s) or lower(t.name)||'<'||lower(p.name) = ANY(%s) """
        , [lowertaxonlist, lowertaxonlist, lowertaxonlist])
    for recTaxon in TaxonsFromDB:
        for FoundK, FoundV in TaxoFound.items():
            if (FoundK == recTaxon['name']) or (FoundK == recTaxon['display_name']) or (
                    FoundK == recTaxon['computedchevronname']) \
                    or (('alterdisplayname' in FoundV) and (FoundV['alterdisplayname'] == recTaxon['display_name'])):
                TaxoFound[FoundK]['nbr'] += 1
                TaxoFound[FoundK]['id'] = recTaxon['id']
    logging.info("Taxo Found = %s", TaxoFound)
    for FoundK, FoundV in TaxoFound.items():
        if FoundV['nbr'] == 0:
            logging.info("Taxo '%s' Not Found", FoundK)
            o_NotFoundTaxo.append(FoundK)
        elif FoundV['nbr'] > 1:
            logging.info("Taxo '%s' Found more than once", FoundK)  # traité comme si pas trouvé
            o_NotFoundTaxo.append(FoundK)
            TaxoFound[FoundK]['id'] = None
    for FoundK, FoundV in TaxoFound.items():
        TaxoFound[FoundK] = FoundV['id']  # in fine on ne garde que l'id, les autres champs etaient temporaires.


def ConvTextDegreeToDecimalDegree(v, FloatAsDecimalDegree=True):
    """
    Converti une lattitude ou longitude texte en version floattante degrés decimaux.
    Format possibles :
    DD°MM SS
    DD.MMMMM : MMMMM = Minutes /100 donc compris entre 0.0 et 0.6 format historique UVP
    DD.FFFFF : FFFFF = Fractions de dégrés
    :param v: Input text
    :param FloatAsDecimalDegree: Si False notation historique, si True degrés décimaux
    :return:
    """
    m = re.search("(-?\d+)°(\d+) (\d+)", v)
    if m:  # donnée au format DDD°MM SSS
        parties = [float(x) for x in m.group(1, 2, 3)]
        parties[1] += parties[2] / 60  # on ajoute les secondes en fraction des minutes
        parties[0] += math.copysign(parties[1] / 60, parties[
            0])  # on ajoute les minutes en fraction des degrés avec le même signe que la partie dégrés
        return round(parties[0], 5)
    else:
        v = ToFloat(v)
        if FloatAsDecimalDegree:  # format degrée decimal, il faut juste convertir le texte en float.
            return v
        else:  # format historique la partie decimale etait exprimée en minutes
            f, i = math.modf(v)
            return round(i + (f / 0.6), 5)


def calcesdFrom_aa_exp(nbr, aa, exp):
    """
    Calcule l'ESD en utilisant aa & exp
    :param nbr: surface en pixel
    :param aa: en pseudo mm²/px unité UVP5 ou UVP6*1E-6
    :param exp:
    :return: ESD en mm
    """
    return 2 * math.sqrt((math.pow(nbr, exp) * aa) / math.pi)


#     PartCalc[:,1]=2*np.sqrt((pow(Part[:,2],UvpSample.acq_exp)*UvpSample.acq_aa)/np.pi)

def calcpixelfromesd_aa_exp(esd, aa, exp):
    """
    Calcule une surface à partir d'un ESD
    :param esd: en mm
    :param aa: en pseudo mm²/px unité UVP5 ou UVP6*1E-6
    :param exp:
    :return: Nbr pixel
    """
    pxfloat = pow((math.pi / (aa)) * ((esd / 2) ** 2), 1 / exp)
    return math.floor(round(pxfloat, 3))


def get_file_from_form(a_task: AsyncTask, errors):
    """
        Common treatment of "file" fields in several tasks.
    """
    FileToSave = None
    FileToSaveFileName = None
    uploadfile = request.files.get("uploadfile")
    if uploadfile is not None and uploadfile.filename != '':  # import d'un fichier par HTTP
        FileToSave = uploadfile  # La copie est faite plus tard, car à ce moment là, le repertoire
        # de la tache n'est pas encore créé
        FileToSaveFileName = "uploaded.zip"
        # noinspection PyUnresolvedReferences
        a_task.param.InData = "uploaded.zip"
    elif len(gvp("ServerPath")) < 2:
        errors.append("Input Folder/File Too Short")
    else:
        ServerRoot = Path(app.config['SERVERLOADAREA'])
        sp = ServerRoot.joinpath(Path(gvp("ServerPath")))
        if not sp.exists():  # verifie que le repertoire existe
            errors.append("Input Folder/File Invalid")
            UtfDiag(errors, str(sp))
        else:
            # noinspection PyUnresolvedReferences
            a_task.param.InData = sp.as_posix()
    return FileToSave, FileToSaveFileName


def flash_any_error(errors):
    if len(errors) > 0:
        for e in errors:
            flash(e, "error")
        return True
    else:
        return False
