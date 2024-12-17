FilterList = ("MapN", "MapW", "MapE", "MapS",
              "depthmin", "depthmax",
              "samples",
              "fromdate", "todate", "inverttime",
              "fromtime", "totime",
              'instrum', 'month', 'daytime',
              'validfromdate', 'validtodate',
              'freetxt', 'freetxtval', 'filt_annot',
              'freenum', 'freenumst', 'freenumend',
              "statusfilter",
              'taxo', 'taxochild')


def GetTextFilter(filtres):
    """
    Retourne le texte décrivant un filtre
    :param filtres: Dictionnaires des filtres
    :return:  chaine du filtre ou chaine vide si pas de filtres
    """
    filtresremplis = {}
    for k in FilterList:
        if filtres.get(k, "") != "":
            filtresremplis[k] = filtres[k]
    if len(filtresremplis) > 0:
        TxtFiltres = ",".join([k + "=" + v for k, v in filtresremplis.items() if v != ""])
    else:
        TxtFiltres = ""
    return TxtFiltres
