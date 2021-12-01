from flask import request


def gvg(varname, defvalue=''):
    """
    Permet de récuperer une variable dans la Chaine GET ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par default si elle n'existe pas
    """
    return request.args.get(varname, defvalue)


def gvp(varname, defvalue=''):
    """
    Permet de récuperer une variable dans la Chaine POST ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par default si elle n'existe pas
    """
    return request.form.get(varname, defvalue)
