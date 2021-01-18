import logging
import math
import re
from pathlib import Path

from flask import request, flash

from appli import gvp, app, UtfDiag
from appli.database import GetAll
# object_annotation_category_id
from appli.tasks.taskmanager import AsyncTask


# retourne le flottant image de la chaine en faisant la conversion ou None
def ToFloat(value):
    if value == '': return None
    try:
        return float(value)
    except ValueError:
        return None


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
