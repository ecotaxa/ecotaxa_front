import math
import re


# retourne le flottant image de la chaine en faisant la conversion ou None
def _ToFloat(value):
    if value == '': return None
    try:
        return float(value)
    except ValueError:
        return None


def ConvTextDegreeDotMinuteToDecimalDegree(v):
    """
    Converti une lattitude ou longitude texte en version flottante degrés decimaux.
    Format possibles :
    DD°MM SS
    DD.MMMMM : MMMMM = Minutes /100 donc compris entre 0.0 et 0.6 format historique UVP
    DD.FFFFF : FFFFF = Fractions de dégrés
    :param v: Input text
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
        v = _ToFloat(v)
        # format historique la partie decimale etait exprimée en minutes
        f, i = math.modf(v)
        return round(i + (f / 0.6), 5)


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
