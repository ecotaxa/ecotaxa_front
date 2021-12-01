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


def ErrorFormat(txt):
    return """
<div class='cell panel ' style='background-color: #f2dede; margin: 15px;'><div class='body' >
				<table style='background-color: #f2dede'><tr><td width='50px' style='color: red;font-size: larger'> <span class='glyphicon glyphicon-exclamation-sign'></span></td>
				<td style='color: red;font-size: larger;vertical-align: middle;'><B>%s</B></td>
				</tr></table></div></div>
    """ % (txt)


def GetAppManagerMailto(part_app):
    if 'APPMANAGER_EMAIL' in part_app.config and 'APPMANAGER_NAME' in part_app.config:
        return "<a href='mailto:{APPMANAGER_EMAIL}'>{APPMANAGER_NAME} ({APPMANAGER_EMAIL})</a>".format(**part_app.config)
    return ""

