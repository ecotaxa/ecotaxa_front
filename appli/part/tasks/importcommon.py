import math
import re


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
