from appli.database import GetAll

FilterList = ("MapN", "MapW", "MapE", "MapS", "depthmin", "depthmax", "samples", "fromdate", "todate",
              "inverttime", "fromtime", "totime", "statusfilter", 'instrum', 'month', 'daytime', 'validfromdate',
              'validtodate', 'freenum', 'freenumst', 'freenumend', 'freetxt', 'freetxtval', 'filt_annot',
              'taxo', 'taxochild')


def GetSQLFilter(filtres, sqlparam, currentuserid):
    whereclause = ""
    if filtres.get("taxo", "") != "":
        if filtres.get("taxochild", "") == "Y":
            taxo_sql = """WITH RECURSIVE rq(id) 
                            as ( select id 
                                   from taxonomy 
                                  where id in(%s)
                                 union
                                 select t.id 
                                   from rq 
                                   join taxonomy t on rq.id = t.parent_id 
                                ) select id from rq """ % (filtres["taxo"],)
            sqlparam['taxo'] = [int(x[0]) for x in GetAll(taxo_sql)]
            whereclause += " and o.classif_id= any (%(taxo)s) "
            # optimisation qui provoque de faux résultats : and (t.nbrobjcum>0 or t.nbrobj>0)
        else:
            whereclause += " and o.classif_id=%(taxo)s "
            sqlparam['taxo'] = filtres["taxo"]
    if filtres.get("statusfilter", "") != "":
        whereclause += " and (o.classif_qual"
        if filtres["statusfilter"] == "NV":
            whereclause += "!= 'V' or o.classif_qual is null"
        elif filtres["statusfilter"] == "PV":
            whereclause += " in ('V','P')"
        elif filtres["statusfilter"] == "NVM":
            whereclause += "= 'V' and o.classif_who !=" + currentuserid
        elif filtres["statusfilter"] == "VM":
            whereclause += "= 'V' and o.classif_who =" + currentuserid
        elif filtres["statusfilter"] == "U":
            whereclause += " is null "
        else:
            whereclause += "='" + filtres["statusfilter"] + "'"
        whereclause += ")"
    if filtres.get("MapN", '') != "" and filtres.get("MapW", '') != "" \
            and filtres.get("MapE", '') != "" and filtres.get("MapS", '') != "":
        whereclause += " and o.latitude between %(MapS)s and %(MapN)s and o.longitude between %(MapW)s and %(MapE)s  "
        sqlparam['MapN'] = filtres["MapN"]
        sqlparam['MapW'] = filtres["MapW"]
        sqlparam['MapE'] = filtres["MapE"]
        sqlparam['MapS'] = filtres["MapS"]

    if filtres.get("depthmin", '') != "" and filtres.get("depthmax", '') != "":
        whereclause += " and o.depth_min between %(depthmin)s and %(depthmax)s" \
                       " and o.depth_max between %(depthmin)s and %(depthmax)s  "
        sqlparam['depthmin'] = filtres["depthmin"]
        sqlparam['depthmax'] = filtres["depthmax"]

    if filtres.get("samples", "") != "":
        whereclause += " and o.sampleid = any (%(samples)s) "
        sqlparam['samples'] = [int(x) for x in filtres["samples"].split(',')]

    if filtres.get("instrum", '') != "":
        whereclause += " and o.acquisid in (select acquisid " \
                       "                      from acquisitions " \
                       "                     where instrument ilike %(instrum)s " \
                       "                       and projid = %(projid)s )"
        sqlparam['instrum'] = '%' + filtres["instrum"] + '%'

    if filtres.get("daytime", "") != "":
        whereclause += " and o.sunpos= any (%(daytime)s) "
        sqlparam['daytime'] = [x for x in filtres["daytime"].split(',')]

    if filtres.get("month", "") != "":
        whereclause += " and extract(month from o.objdate) = any (%(month)s) "
        sqlparam['month'] = [int(x) for x in filtres["month"].split(',')]

    if filtres.get("fromdate", '') != "":
        whereclause += " and objdate >= to_date(%(fromdate)s,'YYYY-MM-DD') "
        sqlparam['fromdate'] = filtres["fromdate"]
    if filtres.get("todate", '') != "":
        whereclause += " and objdate <= to_date(%(todate)s,'YYYY-MM-DD') "
        sqlparam['todate'] = filtres["todate"]

    if filtres.get("inverttime", '') == "1":
        if filtres.get("fromtime", '') != "" and filtres.get("totime", '') != "":
            whereclause += " and (objtime <= time %(fromtime)s or objtime >= time %(totime)s)"
            sqlparam['fromtime'] = filtres["fromtime"]
            sqlparam['totime'] = filtres["totime"]
    else:
        if filtres.get("fromtime", '') != "":
            whereclause += " and objtime>= time %(fromtime)s "
            sqlparam['fromtime'] = filtres["fromtime"]
        if filtres.get("totime", '') != "":
            whereclause += " and objtime<= time %(totime)s "
            sqlparam['totime'] = filtres["totime"]

    if filtres.get("validfromdate", '') != "":
        whereclause += " and classif_when >= to_timestamp(%(validfromdate)s,'YYYY-MM-DD HH24:MI') "
        sqlparam['validfromdate'] = filtres["validfromdate"]
    if filtres.get("validtodate", '') != "":
        whereclause += " and classif_when <= to_timestamp(%(validtodate)s,'YYYY-MM-DD HH24:MI') "
        sqlparam['validtodate'] = filtres["validtodate"]

    if filtres.get("freenum", '') != "" and filtres.get("freenumst", '') != "":
        whereclause += " and o.n" + ("%02d" % int(filtres["freenum"][2:])) + " >=%(freenumst)s  "
        sqlparam['freenumst'] = filtres["freenumst"]
    if filtres.get("freenum", '') != "" and filtres.get("freenumend", '') != "":
        whereclause += " and o.n" + ("%02d" % int(filtres["freenum"][2:])) + " <=%(freenumend)s  "
        sqlparam['freenumend'] = filtres["freenumend"]
    if filtres.get("freetxt", '') != "" and filtres.get("freetxtval", "") != "":
        sqlparam['freetxtval'] = '%' + filtres["freetxtval"] + '%'
        if filtres.get("freetxt", '')[0] == 'o':
            whereclause += " and o.t" + ("%02d" % int(filtres["freetxt"][2:])) + " ilike %(freetxtval)s  "
        elif filtres.get("freetxt", '')[0] == 'a':
            whereclause += " and o.acquisid in (select acquisid from acquisitions s where t" + (
                    "%02d" % int(filtres["freetxt"][2:])) + " ilike %(freetxtval)s and projid=%(projid)s )"
        elif filtres.get("freetxt", '')[0] == 's':
            whereclause += " and o.sampleid in (select sampleid from samples s where t" + (
                    "%02d" % int(filtres["freetxt"][2:])) + " ilike %(freetxtval)s and projid=%(projid)s )"
        elif filtres.get("freetxt", '')[0] == 'p':
            whereclause += " and o.processid in (select processid from process s where t" + (
                    "%02d" % int(filtres["freetxt"][2:])) + " ilike %(freetxtval)s and projid=%(projid)s )"
    if filtres.get('filt_annot', '') != '':
        whereclause += " and (o.classif_who = any (%(filt_annot)s) " \
                       "  or exists (select classif_who " \
                       "               from objectsclassifhisto oh " \
                       "              where oh.objid=o.objid " \
                       "                and classif_who = any (%(filt_annot)s) ) )"
        sqlparam['filt_annot'] = [int(x) for x in filtres["filt_annot"].split(',')]
    return whereclause


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
