import collections
import datetime
import html
import math
import urllib.parse
from typing import List

import psycopg2.extras
from flask import render_template, g, flash, json, session, request, Markup, url_for
from flask_login import current_user
from flask_security import login_required

import appli
import appli.project.sharedfilter as sharedfilter
from appli import app, PrintInCharte, database, gvg, gvp, user_datastore, DecodeEqualList, ScaleForDisplay, ntcv, \
    XSSEscape
from appli.database import GetAll, GetClassifQualClass, ExecSQL, GetAssoc
from appli.search.leftfilters import getcommonfilters
######################################################################################################################
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectSearchResult, CreateProjectReq, ProjectsApi, Project, ApiException, ObjectsApi


@app.route('/prj/')
@login_required
def indexProjects(Others=False):
    filt_title = gvg('filt_title', session.get('prjfilt_title', ''))
    session['prjfilt_title'] = filt_title

    filt_instrum = gvg('filt_instrum', session.get('prjfilt_instrum', ''))
    session['prjfilt_instrum'] = filt_instrum

    # Les checkbox ne sont pas transmises si elle ne sont pas coché,
    if 'filt_title' in request.args:  # donc si le filtre du titre est transmis on utilise le get
        filt_subset = gvg('filt_subset', "")
        session['prjfilt_subset'] = filt_subset
    else:  # Sinon on prend la valeur de la session.
        filt_subset = session.get('prjfilt_subset', '')

    with ApiClient(ProjectsApi, request.cookies.get('session')) as api:
        rsp: List[ProjectSearchResult] = api.search_projects_projects_search_get(also_others=Others,
                                                                                 title_filter=filt_title,
                                                                                 instrument_filter=filt_instrum,
                                                                                 filter_subset=(filt_subset == 'Y'))

    CanCreate = False
    if not Others:
        if current_user.has_role(database.AdministratorLabel) or current_user.has_role(database.ProjectCreatorLabel):
            CanCreate = True

    PDT = database.PersistantDataTable.query.first()
    if PDT is None or PDT.lastserverversioncheck_datetime is None or (
            datetime.datetime.now() - PDT.lastserverversioncheck_datetime).days > 7:
        fashtxt = "Taxonomy synchronization and Ecotaxa version check wasn’t done during the last 7 days, " \
                  "Ask application administrator to do it."  # +str(PDT.lastserverversioncheck_datetime)
        fashtxt += "  <a href='/taxo/browse/' class='btn btn-primary btn-xs'>Synchronize to check Ecotaxa version</a>"
        flash(Markup(fashtxt), 'warning')

    return PrintInCharte(
        render_template('project/list.html', PrjList=rsp, CanCreate=CanCreate,
                        AppManagerMailto=appli.GetAppManagerMailto(),
                        filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum, Others=Others,
                        isadmin=current_user.has_role(database.AdministratorLabel),
                        _manager_mail=_manager_mail))


######################################################################################################################
@app.route('/prjothers/')
@login_required
def ProjectsOthers():
    return indexProjects(Others=True)


######################################################################################################################
def UpdateProjectStat(PrjId):
    ExecSQL("""UPDATE projects
         SET  objcount=q.nbr,pctclassified=100.0*nbrclassified/q.nbr,pctvalidated=100.0*nbrvalidated/q.nbr
         from projects p
         left join
         (SELECT  projid,sum(nbr) nbr,sum(case when id>0 then nbr end) nbrclassified,sum(nbr_v) nbrvalidated
              from projects_taxo_stat
              where projid=%(projid)s
              group by projid )q on p.projid=q.projid
         where projects.projid=%(projid)s and p.projid=%(projid)s""", {'projid': PrjId})


######################################################################################################################
def RecalcProjectTaxoStat(PrjId):
    ExecSQL("""begin;
        delete from projects_taxo_stat WHERE projid=%(projid)s;
        insert into projects_taxo_stat(projid, id, nbr, nbr_v, nbr_d, nbr_p) 
          select projid,coalesce(classif_id,-1) id,count(*) nbr,count(case when classif_qual='V' then 1 end) nbr_v
          ,count(case when classif_qual='D' then 1 end) nbr_d,count(case when classif_qual='P' then 1 end) nbr_p
          from obj_head
          where projid=%(projid)s
          GROUP BY projid,classif_id;
          commit;""", {'projid': PrjId})


######################################################################################################################
def GetFieldList(Prj, champ='classiffieldlist'):
    fieldlist = collections.OrderedDict()
    fieldlist["orig_id"] = "Image Name"
    fieldlist["classif_auto_score"] = "Score"
    objmap = DecodeEqualList(Prj.mappingobj)
    for v in ('objtime', 'objdate', 'latitude', 'longitude', 'depth_min', 'depth_max'):
        objmap[v] = v
    # fieldlist fait le mapping entre le nom fonctionnel et le nom à affiche
    # cette boucle permet de faire le lien avec le nom de la colonne (si elle existe.
    fieldlist2 = {}
    for field, dispname in DecodeEqualList(getattr(Prj, champ)).items():
        for ok, on in objmap.items():
            if field == on:
                fieldlist2[ok] = dispname
    for k, v in sorted(fieldlist2.items(), key=lambda t: t[1]):
        fieldlist[k] = v
    return fieldlist


# Contient la liste des filtres & parametres de cet écran avec les valeurs par défaut
# noinspection SpellCheckingInspection
FilterList = {"MapN": "", "MapW": "", "MapE": "", "MapS": "", "depthmin": "", "depthmax": "", "samples": "",
              "fromdate": "", "todate": "", "inverttime": "", "fromtime": "", "totime": "", "sortby": "",
              "sortorder": "", "dispfield": "", "statusfilter": "", 'ipp': 100, 'zoom': 100, 'magenabled': 0,
              'popupenabled': 0, 'instrum': '', 'month': '', 'daytime': '', 'freenum': '', 'freenumst': '',
              'freenumend': '', 'freetxt': '', 'freetxtval': '', 'filt_annot': ''}
FilterListAutoSave = ("sortby", "sortorder", "dispfield", "statusfilter", 'ipp', 'zoom', 'magenabled', 'popupenabled')


######################################################################################################################
@app.route('/prj/<int:PrjId>')
# @login_required
def indexPrj(PrjId):
    data = {'pageoffset': gvg("pageoffset", "0")}
    for k, v in FilterList.items():
        data[k] = gvg(k, str(current_user.GetPref(PrjId, k, v)) if current_user.is_authenticated else "")
    # print('%s',data)
    if data.get("samples", None):
        data["sample_for_select"] = ""
        for r in GetAll(
                "select sampleid,orig_id from samples where projid=%d and sampleid in(%s)" % (PrjId, data["samples"])):
            data["sample_for_select"] += "\n<option value='{0}' selected>{1}</option> ".format(*r)
    data["month_for_select"] = ""
    # print("%s",data['month'])
    for (k, v) in enumerate(('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                             'October', 'November', 'December'), start=1):
        data["month_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format(
            'selected' if str(k) in data.get('month', '').split(',') else '', k, v)
    data["daytime_for_select"] = ""
    for (k, v) in database.DayTimeList.items():
        data["daytime_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format(
            'selected' if str(k) in data.get('daytime', '').split(',') else '', k, v)
    Prj = database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        flash("Project doesn't exists", 'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(-1) and not Prj.CheckRight(0):
        # Level -1=Read Anonymous, 0 = Read, 1 = Annotate, 2 = Admin
        MainContact = GetAll("""select u.email,u.name
                        from projectspriv pp join users u on pp.member=u.id
                        where pp.privilege='Manage' and u.active=true and pp.projid=%s""", (PrjId,))
        # flash("",'error')
        html_mail_body = _manager_mail(ntcv(Prj.title), Prj.projid)
        msg = """
        <div class="alert alert-danger alert-dismissible" role="alert"> You cannot view this project : {1} [{2}] 
        <a class='btn btn-primary' href='mailto:{3}?{0}' style='margin-left:15px;'>REQUEST ACCESS to {4}</a>
        </div>""".format(html_mail_body, Prj.title, Prj.projid, MainContact[0]['email'], MainContact[0]['name'])
        return PrintInCharte(msg + "<a href=/prj/>Select another project</a>")
    g.Projid = Prj.projid
    # Ces 2 listes sont ajax mais si on passe le filtre dans l'URL il faut ajouter l'entrée en statique pour l'affichage
    data["filt_freenum_for_select"] = ""
    if data.get('freenum', '') != "":
        for r in PrjGetFieldList(Prj, 'n', ''):  # type: dict
            if r['id'] == data['freenum']:
                data["filt_freenum_for_select"] = "\n<option value='{0}' selected>{1}</option> ".format(r['id'],
                                                                                                        r['text'])
    data["filt_freetxt_for_select"] = ""
    if data.get('freetxt', '') != "":
        for r in PrjGetFieldList(Prj, 't', ''):  # type: dict
            if r['id'] == data['freetxt']:
                data["filt_freetxt_for_select"] = "\n<option value='{0}' selected>{1}</option> ".format(r['id'],
                                                                                                        r['text'])
    data["filt_annot_for_select"] = ""
    if data.get('filt_annot', '') != "":
        for r in GetAll("select id,name from users where id =any (%s)",
                        ([int(x) for x in data["filt_annot"].split(',')],)):
            data["filt_annot_for_select"] += "\n<option value='{0}' selected>{1}</option> ".format(r['id'], r['name'])
    fieldlist = GetFieldList(Prj)
    fieldlist["classif_when"] = "Validation date"
    data["fieldlist"] = fieldlist
    data["sortlist"] = collections.OrderedDict({"": ""})
    data["sortlist"]["classifname"] = "Category Name"
    data["sortlist"]["random_value"] = "Random"
    data["sortlist"]["classif_when"] = "Validation date"
    for k, v in fieldlist.items():
        data["sortlist"][k] = v
    data["statuslist"] = collections.OrderedDict({"": "All"})
    data["statuslist"]["U"] = "Unclassified"
    data["statuslist"]["P"] = "Predicted"
    data["statuslist"]["NV"] = "Not Validated"
    data["statuslist"]["V"] = "Validated"
    data["statuslist"]["PV"] = "Predicted or Validated"
    data["statuslist"]["NVM"] = "Validated by others"
    data["statuslist"]["VM"] = "Validated by me"
    data["statuslist"]["D"] = "Dubious"
    g.PrjAnnotate = g.PrjManager = Prj.CheckRight(2)
    if not g.PrjManager:
        g.PrjAnnotate = Prj.CheckRight(1)
    g.PublicViewMode = not Prj.CheckRight(0)
    right = 'dodefault'
    if gvg("taxo") != "":
        g.taxofilter = gvg("taxo")
        g.taxochild = gvg("taxochild")
        g.taxofilterlabel = GetAll("select name from taxonomy where id=%s ", (gvg("taxo"),))[0][0]
    else:
        g.taxofilter = g.taxofilter = g.taxofilterlabel = ""

    classiftab = GetClassifTab(Prj)
    g.ProjectTitle = Prj.title
    g.headmenu = []  # Menu project
    g.headmenuF = []  # Menu Filtered
    g.headmenu.append(("/prjcm/%d" % (PrjId,), "Show confusion matrix"))
    if g.PrjAnnotate:
        g.headmenu.append(("", "SEP"))
        if Prj.status == "Annotate":
            g.headmenu.append(
                ("/Task/Create/TaskClassifAuto2?projid=%d" % (PrjId,), "Train and Predict identifications V2"))
            g.headmenuF.append(
                ("javascript:GotoWithFilter('/Task/Create/TaskClassifAuto2')", "Train and Predict identifications V2"))
            g.headmenu.append(("/Task/Create/TaskClassifAuto2?projid=%d&frommodel=Y" % (PrjId,),
                               "Predict identifications from trained model"))
            g.headmenuF.append(("javascript:GotoWithFilter('/Task/Create/TaskClassifAuto2?frommodel=Y')",
                                "Predict identifications from trained model"))
            g.headmenu.append(("/Task/Create/TaskImport?p=%d" % (PrjId,), "Import images and metadata"))

        g.headmenu.append(("/Task/Create/TaskExportTxt?projid=%d" % PrjId, "Export"))
        g.headmenuF.append(("javascript:GotoWithFilter('/Task/Create/TaskExportTxt')", "Export"))
    if g.PrjManager:
        g.headmenu.append(("", "SEP"))
        g.headmenuF.append(("", "SEP"))
        g.headmenu.append(("/prj/edit/%d" % (PrjId,), "Edit project settings"))
        g.headmenu.append(("/Task/Create/TaskSubset?p=%d" % (PrjId,), "Extract Subset"))
        g.headmenuF.append(("javascript:GotoWithFilter('/Task/Create/TaskSubset?p=%d')" % (PrjId,),
                            "Extract Subset"))
        g.headmenu.append(("/prj/merge/%d" % (PrjId,), "Merge another project in this project"))
        g.headmenu.append(("/prj/EditAnnot/%d" % (PrjId,), "Edit or erase annotations massively"))
        g.headmenu.append(("/prj/editdatamass/%d" % (PrjId,), "Batch edit metadata"))
        g.headmenuF.append(("javascript:GotoWithFilter('/prj/editdatamass/%d')" % (PrjId,), "Batch edit metadata"))
        g.headmenu.append(("/prj/resettopredicted/%d" % (PrjId,), "Reset status to Predicted"))
        g.headmenuF.append(
            ("javascript:GotoWithFilter('/prj/resettopredicted/%d')" % (PrjId,), "Reset status to Predicted"))
        g.headmenu.append(("/prjPurge/%d" % (PrjId,), "Delete objects or project"))
        g.headmenuF.append(("javascript:GotoWithFilter('/prjPurge/%d')" % (PrjId,), "Delete objects"))

    appli.AddTaskSummaryForTemplate()
    filtertab = getcommonfilters(data)
    g.useselect4 = True
    return render_template('project/projectmain.html', top="", lefta=classiftab, leftb=filtertab,
                           right=right, data=data, title='EcoTaxa ' + ntcv(Prj.title))


def _manager_mail(prj_title, prj_id):
    base_url = request.host_url[:-1]
    mail_body = "Please provide me privileges to project : '%s' at this address : %s " % (
        prj_title, base_url+url_for('indexPrj', PrjId=int(prj_id)))
    mail_link = urllib.parse.urlencode({'body': mail_body,
                                        'subject': 'EcoTaxa project access request'},
                                       quote_via=urllib.parse.quote)
    return mail_link


######################################################################################################################
# noinspection SpellCheckingInspection
@app.route('/prj/LoadRightPane', methods=['GET', 'POST'])
# @login_required
def LoadRightPane():
    # Fetch project are check rights
    PrjId = gvp("projid")
    Prj = database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        return "Invalid project"
    if not Prj.CheckRight(-1):
        return "Access Denied"

    # copie des valeurs de filtres connues
    Filt = {}
    for k, v in FilterList.items():
        Filt[k] = gvp(k, v)

    # on sauvegarde les parametres dans le profil utilisateur
    if current_user.is_authenticated:
        PrefToSave = 0
        save_all = gvp("saveinprofile") == "Y"
        for k, v in Filt.items():
            if save_all or (k in FilterListAutoSave):
                PrefToSave += current_user.SetPref(Prj.projid, k, v)
        if PrefToSave > 0:
            database.ExecSQL("update users set preferences=%s where id=%s", (current_user.preferences, current_user.id),
                             True)
            user_datastore.ClearCache()

    # récupération des parametres d'affichage
    filtres = {}
    for k in sharedfilter.FilterList:
        filtres[k] = gvp(k, "")
    pageoffset = int(gvp("pageoffset", "0"))
    sortby = Filt["sortby"]
    sortorder = Filt["sortorder"]
    dispfield = Filt["dispfield"]
    ipp = int(Filt["ipp"])
    # Fit to page envoi un ipp de 0 donc on se comporte comme du 200 d'un point de vue DB
    ippdb = ipp if ipp > 0 else 200
    zoom = int(Filt["zoom"])
    popupenabled = Filt["popupenabled"]
    g.PublicViewMode = not Prj.CheckRight(0)
    fieldlist = GetFieldList(Prj)
    fieldlist.pop('orig_id', '')
    fieldlist.pop('objtime', '')
    whereclause = " where o.projid=%(projid)s "
    sqlparam = {'projid': Prj.projid}
    sql = """select o.objid,t.name taxoname,t2.name taxoparent,o.classif_qual,
    u.name classifwhoname,i.file_name,t.display_name
  ,i.height,i.width,i.thumb_file_name,i.thumb_height,i.thumb_width
  ,o.depth_min,o.depth_max,s.orig_id samplename,o.objdate
  ,to_char(o.objtime,'HH24:MI') objtime,to_char(classif_when,'YYYY-MM-DD HH24:MI') classif_when
  ,case when o.complement_info is not null and o.complement_info!='' then 1 else 0 end commentaires
  ,o.latitude,o.orig_id,o.imgcount"""
    for k in fieldlist.keys():
        sql += ",o." + k + " as extra_" + k
    sql += """ from objects o
left Join images i on o.img0id=i.imgid
left JOIN taxonomy t on o.classif_id=t.id
left JOIN taxonomy t2 on t.parent_id=t2.id
LEFT JOIN users u on o.classif_who=u.id
LEFT JOIN  samples s on o.sampleid=s.sampleid
"""
    whereclause += sharedfilter.GetSQLFilter(filtres, sqlparam,
                                             str(current_user.id if current_user.is_authenticated else "999999"))
    if g.PublicViewMode:  # Si c'est une lecture publique
        whereclause += " and o.classif_qual='V' "  # Les anonymes ne peuvent voir que les objets validés
    sql += whereclause

    sqlcount = """select count(*)
        ,count(case when classif_qual='V' then 1 end) NbValidated
        ,count(case when classif_qual='D' then 1 end) NbDubious
        ,count(case when classif_qual='P' then 1 end) NbPredicted
        from objects o
        LEFT JOIN  acquisitions acq on o.acquisid=acq.acquisid
        """ + whereclause
    # Optimisation pour des cas simples et fréquents
    if whereclause == ' where o.projid=%(projid)s ':
        sqlcount = """select sum(nbr),sum(nbr_v) NbValidated,sum(nbr_d) NbDubious,sum(nbr_p) NbPredicted 
                    from projects_taxo_stat 
                    where projid=%(projid)s """
    if whereclause == ' where o.projid=%(projid)s  and o.classif_id=%(taxo)s ':
        sqlcount = """select sum(nbr),sum(nbr_v) NbValidated,sum(nbr_d) NbDubious,sum(nbr_p) NbPredicted 
                from projects_taxo_stat 
                where projid=%(projid)s and id=%(taxo)s"""
    if whereclause == " where o.projid=%(projid)s  and o.classif_id=%(taxo)s  and o.classif_qual!='V'":
        sqlcount = """select sum(nbr-nbr_v),0 NbValidated,sum(nbr_d) NbDubious,sum(nbr_p) NbPredicted 
                from projects_taxo_stat 
                where projid=%(projid)s and id=%(taxo)s"""
    # ' where o.projid=%(projid)s '
    # ' where o.projid=%(projid)s  and o.classif_id=%(taxo)s '
    (nbrtotal, nbrvalid, nbrdubious, nbrpredict) = GetAll(sqlcount, sqlparam, debug=False)[0]
    if nbrtotal is None:  # si table vide
        nbrtotal = nbrvalid = nbrdubious = nbrpredict = 0
        RecalcProjectTaxoStat(Prj.projid)
    pagecount = math.ceil(int(nbrtotal) / ippdb)
    if sortby == "classifname":
        sql += " order by t.name " + sortorder + " ,objid " + sortorder
    elif sortby != "":
        sql += " order by o." + sortby + " " + sortorder + " ,objid " + sortorder
    # else:  # pas de tri par defaut pour améliorer les performances sur les gros projets
    #     sql+=" order by o.orig_id"
    # app.logger.info("pageoffset/pagecount %s / %s",pageoffset,pagecount)
    if pageoffset >= pagecount:
        pageoffset = pagecount - 1
        if pageoffset < 0:
            pageoffset = 0
    sql += " Limit %d offset %d " % (ippdb, pageoffset * ippdb)
    res = GetAll(sql, sqlparam, False)

    # Produce page lines using request output
    # print("%s\n%s\n%s"%(sql,sqlparam,res))
    html = ["<a name='toppage'/>"]
    trcount = 1
    fitlastclosedtr = 0  # index de t de la derniere création de ligne qu'il faudrat effacer quand la page sera pleine
    fitheight = 100  # hauteur déjà occupé dans la page plus les header footer (hors premier header)
    fitcurrentlinemaxheight = 0
    LineStart = ""
    if Prj.CheckRight(1):  # si annotateur on peut sauver les changements.
        LineStart = "<td class='linestart'></td>"
    html.append("<table class=imgtab><tr id=tr1>" + LineStart)
    WidthOnRow = 0
    # récuperation et ajustement des dimensions de la zone d'affichage
    # noinspection PyBroadException
    try:
        PageWidth = int(gvp("resultwidth")) - 40  # on laisse un peu de marge à droite et la scrollbar
        if PageWidth < 200:
            PageWidth = 200
    except Exception:
        PageWidth = 200
    # noinspection PyBroadException
    try:
        WindowHeight = int(gvp("windowheight")) - 100  # on enleve le bandeau du haut
        if WindowHeight < 200:
            WindowHeight = 200
    except Exception:
        WindowHeight = 200
    # print("PageWidth=%s, WindowHeight=%s"%(PageWidth,WindowHeight))
    # Calcul des dimmensions et affichage des images
    for r in res:
        filename = r['file_name']
        origwidth = r['width']
        origheight = r['height']
        thumbfilename = r['thumb_file_name']
        thumbwidth = r['thumb_width']
        if origwidth is None:  # pas d'image associé, pas trés normal mais arrive pour les subset sans images
            width = 80
            height = 40
        else:
            width = origwidth * zoom // 100
            height = origheight * zoom // 100
        if max(width, height) < 75:  # en dessous de 75 px de coté on ne fait plus le scaling
            if max(origwidth, origheight) < 75:
                width = origwidth  # si l'image originale est petite on l'affiche telle quelle
                height = origheight
            elif max(origwidth, origheight) == origwidth:
                width = 75
                height = origheight * 75 // origwidth
                if height < 1:
                    height = 1
            else:
                height = 75
                width = origwidth * 75 // origheight
                if width < 1:
                    width = 1

        # On limite les images pour qu'elles tiennent toujours dans l'écran
        if width > PageWidth:
            width = PageWidth
            height = math.trunc(r['height'] * width / r['width'])
            if height == 0:
                height = 1
        if height > WindowHeight:
            height = WindowHeight
            width = math.trunc(r['width'] * height / r['height'])
            if width == 0:
                width = 1
        if WidthOnRow != 0 and (WidthOnRow + width) > PageWidth:
            trcount += 1
            fitheight += fitcurrentlinemaxheight
            if (ipp == 0) and (fitheight > WindowHeight):  # en mode fit quand la page est pleine
                if fitlastclosedtr > 0:  # dans tous les cas on laisse une ligne
                    del html[fitlastclosedtr:]
                break
            fitlastclosedtr = len(html)
            fitcurrentlinemaxheight = 0
            html.append("</tr></table><table class=imgtab><tr id=tr%d>%s" % (trcount, LineStart))
            WidthOnRow = 0
        cellwidth = width + 22
        fitcurrentlinemaxheight = max(fitcurrentlinemaxheight, height + 45 + 14 * len(
            dispfield.split()))  # 45 espace sur le dessus et le dessous de l'image + 14px par info affichée
        if cellwidth < 80:
            cellwidth = 80  # on considère au moins 80 car avec les label c'est rarement moins
        # Met la fenetre de zoon la ou il y a plus de place, sachant qu'elle fait 400px
        #  et ne peut donc pas être calée à gauche des premieres images.
        if (WidthOnRow + cellwidth) > (PageWidth / 2):
            pos = 'left'
        else:
            pos = 'right'
        # Si l'image affiché est plus petite que la miniature, afficher la miniature.
        if thumbwidth is None or thumbwidth < width or thumbfilename is None:
            # sinon (si la miniature est plus petite que l'image à afficher )
            thumbfilename = filename  # la miniature est l'image elle même
        txt = "<td width={0}>".format(cellwidth)
        if filename:
            txt += "<img class='lazy' id=I{3} data-src='/vault/{5}' " \
                   "data-zoom-image='{0}' width={1} height={2} pos={4}>" \
                .format(filename, width, height, r['objid'], pos, thumbfilename)
        else:
            txt += "No Image"
        # Génération de la popover qui apparait pour donner quelques détails sur l'image
        if popupenabled == "1":
            popoverfieldlist = GetFieldList(Prj, champ='popoverfieldlist')
            popoverfieldlist.pop('orig_id', '')
            popoverfieldlist.pop('objtime', '')
            poptitletxt = "%s" % (r['orig_id'],)
            poptxt = ""
            # poptxt="<p style='white-space: nowrap;color:black;'>cat. %s"%(r['taxoname'],)
            if ntcv(r['classifwhoname']) != "":
                poptxt += "<em>by</em> %s<br>" % (r['classifwhoname'])
            poptxt += "<em>parent</em> " + ntcv(r['taxoparent'])
            poptxt += "<br><em>in</em> " + ntcv(r['samplename'])
            for k, v in popoverfieldlist.items():
                if k == 'classif_auto_score' and r["classif_qual"] == 'V':
                    poptxt += "<br>%s : %s" % (v, "-")
                else:
                    poptxt += "<br>%s : %s" % (v, ScaleForDisplay(r["extra_" + k]))
            if r['classif_when']:
                poptxt += "<br>Validation date : %s" % (ntcv(r['classif_when']),)
            popattribute = "data-title=\"{0}\" data-content=\"{1}\" data-placement='{2}'". \
                format(poptitletxt, poptxt, 'left' if WidthOnRow > 500 else 'right')
        else:
            popattribute = ""
        # Génération du texte sous l'image qui contient la taxo + les champs à afficher
        bottomtxt = ""
        if 'objtime' in dispfield:
            bottomtxt += "<br>Time %s" % (r['objtime'],)
        if 'classif_when' in dispfield and r['classif_when']:
            bottomtxt += "<br>Validation date : %s" % (r['classif_when'],)
        for k, v in fieldlist.items():
            if k in dispfield:
                if k == 'classif_auto_score' and r["classif_qual"] == 'V':
                    bottomtxt += "<br>%s : -" % v
                else:
                    bottomtxt += "<br>%s : %s" % (v, ScaleForDisplay(r["extra_" + k]))
        if bottomtxt != "":
            bottomtxt = bottomtxt[4::]  # [4::] supprime le premier <BR>
        if 'orig_id' in dispfield:
            bottomtxt = "<div style='word-break: break-all;'>%s</div>" % (r['orig_id'],) + bottomtxt

        def FormatNameForVignetteDisplay(CategName):
            Parts = ntcv(CategName).split('<')
            restxt = "<span class='cat_name'>{}</span>".format(Parts[0])
            if len(Parts) > 1:
                restxt += "<span class='cat_ancestor'> &lt;&nbsp;{}</span>".format(" &lt;&nbsp;".join(Parts[1:]))
            else:
                restxt += ""
            return restxt

        txt += """<div class='subimg {1}' {2}>
<div class='taxo'>{0}</div>
<div class='displayedFields'>{3}</div></div>
<div class='ddet'><span class='ddets'><span class='glyphicon glyphicon-eye-open'></span> {4} {5}</div>""" \
            .format(FormatNameForVignetteDisplay(r['display_name']), GetClassifQualClass(r['classif_qual']),
                    popattribute, bottomtxt,
                    "(%d)" % (r['imgcount'],) if r['imgcount'] is not None and r['imgcount'] > 1 else "",
                    "<b>!</b> " if r['commentaires'] > 0 else "")
        txt += "</td>"

        # WidthOnRow+=max(cellwidth,80) # on ajoute au moins 80 car avec les label c'est rarement moins
        WidthOnRow += cellwidth + 5  # 5 = border-spacing = espace inter image
        html.append(txt)

    html.append("</tr></table>")
    if len(res) == 0:
        html.append("<b>No Result</b><br>")
    if Prj.CheckRight(1):  # si annotateur on peut sauver les changements.
        html.append("""
        <div id='PendingChanges' class='PendingChangesClass text-danger'></div>
        <button class='btn btn-default' onclick="$(window).scrollTop(0);">
            <span class='glyphicon glyphicon-arrow-up ' ></span></button>
        <button class='btn btn-primary' onclick='SavePendingChanges();' title='CTRL+S' id=BtnSave disabled>
            <span class='glyphicon glyphicon-save' /> Save pending changes [CTRL+S]</button>
        <button class='btn btn-success' onclick='ValidateAll(0);'><span class='glyphicon glyphicon-ok' /> 
            <span class='glyphicon glyphicon-arrow-right' /> 
                <span id=TxtBtnValidateAll>Validate all and move to next page</span></button>
        <!--<button class='btn btn-success' onclick='ValidateAll(1);' title="Save changed annotations , 
        Validate all objects in page &amp; Go to Next Page"><span class='glyphicon glyphicon-arrow-right' /> 
        Save, Validate all &amp; Go to Next Page</button>-->
        <button class='btn btn-success' onclick="ValidateSelection('V');">
            <span class='glyphicon glyphicon-ok' />  Validate Selection [CTRL+L]</button>
        <button class='btn btn-warning' onclick="ValidateSelection('D');">Set Selection Dubious</button>
        <button class='btn btn-default' onclick="$('#bottomhelp').toggle()" >
            <span class='glyphicon glyphicon-question-sign' /> Undo</button>
        <div id="bottomhelp" class="panel panel-default" style="margin:10px 0 0 40px;width:500px;display:none;">
            To correct validation mistakes (no UNDO button in Ecotaxa):
<br>1.	Select Validated Status
<br>2.	Sort by : Validation date
<br>3.	Move the most recent (erroneous) validated objects into the suitable category
</div><script>$("#PendingChanges2").html('');</script>
        """)
    # Gestion de la navigation entre les pages
    if ipp == 0:
        html.append("<p class='inliner'> Page management not available on Fit mode</p>")
    elif pagecount > 1 or pageoffset > 0:
        html.append("<p class='inliner'> Page %d / %d</p>" % (pageoffset + 1, pagecount))
        html.append("<nav><ul class='pagination'>")
        if pageoffset > 0:
            html.append("<li><a href='javascript:gotopage(%d);' >&laquo;</a></li>" % (pageoffset - 1))
        for i in range(0, pagecount - 1, math.ceil(pagecount / 20)):
            if i == pageoffset:
                html.append("<li class='active'><a href='javascript:gotopage(%d);'>%d</a></li>" % (i, i + 1))
            else:
                html.append("<li><a href='javascript:gotopage(%d);'>%d</a></li>" % (i, i + 1))
        html.append("<li><a href='javascript:gotopage(%d);'>%d</a></li>" % (pagecount - 1, pagecount))
        if pageoffset < pagecount - 1:
            html.append("<li><a href='javascript:gotopage(%d);' >&raquo;</a></li>" % (pageoffset + 1))
        html.append("</ul></nav>")
    if nbrtotal > 0:
        pctvalid = 100 * nbrvalid / nbrtotal
        pctpredict = 100 * nbrpredict / nbrtotal
        pctdubious = 100 * nbrdubious / nbrtotal
        nbrothers = nbrtotal - nbrvalid - nbrpredict - nbrdubious
        txtpctvalid = "<span style=\"color:#0A0\">%0d </span>, " \
                      "<span style=\"color:#5bc0de\">%0d </span>, " \
                      "<span style=\"color:#F0AD4E\">%0d</span>, " \
                      "<span style=\"color:#888\">%0d </span>" % (nbrvalid, nbrpredict, nbrdubious, nbrothers)
    else:
        txtpctvalid = "-"
        pctdubious = pctpredict = pctvalid = 0
    html.append("""
    <script>
        PostAddImages();
        $('#objcount').html('{0} / {1} ');
        $('#progress-bar-validated').css('width','{2}%');
        $('#progress-bar-predicted').css('width','{3}%');
        $('#progress-bar-dubious').css('width','{4}%');
    </script>""".format(txtpctvalid, nbrtotal, pctvalid, pctpredict, pctdubious))
    return "\n".join(html)


######################################################################################################################
def GetClassifTab(Prj):
    if Prj.initclassiflist is None:
        InitClassif = "0"  # pour être sur qu'il y a toujours au moins une valeur
    else:
        InitClassif = [x for x in Prj.initclassiflist.split(",") if x.isdigit()]
        if len(InitClassif):
            InitClassif = ",".join(InitClassif)
        else:
            InitClassif = "0"  # pour être sur qu'il y a toujours au moins une valeur
    ColForNbr = "nbr"
    if g.PublicViewMode:
        ColForNbr = " nbr_v "
    InitClassif = ", ".join(["(" + x.strip() + ")" for x in InitClassif.split(",") if x.strip() != ""])
    sql = """select t.id,coalesce(t.display_name,'') display_name
        ,t.name as taxoname
        ,case when tp.name is not null and t.name not like '%% %%' and t.display_name not like '%%<%%'  
         then ' ('||tp.name||')' 
         else ' ' end as  taxoparent
        ,nbr,nbr_p,nbr_d,nbr_v,nbrothers
    from (SELECT o.classif_id, c.id,coalesce(sum(nbr),0) Nbr,
                 coalesce(sum(nbr_d),0) nbr_d,coalesce(sum(nbr_p),0) nbr_p,
                 coalesce(sum(nbr-nbr_v-nbr_p-nbr_d),0) NbrOthers,
                 coalesce(sum(nbr_v),0) nbr_v
            FROM (select id classif_id,{0} nbr,nbr_v,nbr_d,nbr_p 
                  from projects_taxo_stat where 
                  id>0 and projid=%(projid)s ) o
       FULL JOIN (VALUES {1}) c(id) ON o.classif_id = c.id
                   GROUP BY classif_id, c.id) o
    JOIN taxonomy t on coalesce(o.classif_id,o.id)=t.id
    left JOIN taxonomy tp ON t.parent_id = tp.id
    order by t.name       """.format(ColForNbr, InitClassif)
    param = {'projid': Prj.projid}
    res = GetAll(sql, param, debug=False, cursor_factory=psycopg2.extras.RealDictCursor)
    ids = [x['id'] for x in res]
    # print(ids)
    sql = """WITH RECURSIVE rq as (
                SELECT DISTINCT t.id,t.name,t.parent_id
                FROM taxonomy t where t.id = any (%s)
              union
                SELECT t.id,t.name,t.parent_id
                FROM rq JOIN taxonomy t ON rq.parent_id = t.id
            )
            select * from rq  """
    taxotree = GetAssoc(sql, (ids,))
    for k, v in enumerate(res):
        res[k]['cp'] = None  # cp = Closest parent
        res[k]['cpdist'] = 0
        taxoid = v["id"]
        for i in range(50):  # 50 pour arreter en cas de boucle
            if taxoid in taxotree:
                taxoid = taxotree[taxoid]['parent_id']
            else:
                taxoid = None
            if taxoid is None:
                break
            if taxoid in ids:
                res[k]['cp'] = taxoid
                res[k]['cpdist'] = i + 1
                break
    # noinspection PyUnresolvedReferences
    restree = []  # type:list[dict]

    def AddChild(Src, Parent, Res, Deep, ParentClasses):
        for rec in Src:
            if rec['cp'] == Parent:
                # r['dist']=Deep+r['cpdist']
                rec['dist'] = Deep
                rec['parentclasses'] = ParentClasses
                rec["haschild"] = False
                for prnt, ndx in zip(Res, range(10000)):
                    if prnt['id'] == Parent:
                        Res[ndx]["haschild"] = True
                Res.append(rec)
                AddChild(Src, rec['id'], Res, rec['dist'] + 1, ParentClasses + (" visib%s" % (rec['id'],)))

    AddChild(res, None, restree, 0, "")
    # Cette section de code à pour but de trier le niveau final (qui n'as pas d'enfant) par parent
    # s'il un parent apparait plus d'une fois sinon par enfant
    # on isole d'abord les branches
    parents = set([x['parentclasses'] for x in restree])
    # on ne garde que les branches sans enfants
    parentsnochild = parents.copy()
    for p in parents:
        for r in restree:
            if r['parentclasses'] == p and r['haschild']:
                parentsnochild.discard(p)
    for p in parentsnochild:
        # on recherche dans le tableau à plats les bornes de chaques branche et on met la branche dans subset
        d = f = 0
        for (r, i) in zip(restree, range(0, 1000)):
            if r['parentclasses'] == p:
                f = i
                if d == 0:
                    d = i
        subset = restree[d:f + 1]
        # on cherche les parents presents plus d'une fois
        NbrParent = {x['taxoparent']: 0 for x in subset}
        for r in subset:
            NbrParent[r['taxoparent']] += 1
        # on calcule une clause de tri en fonction du fait que le parent est present plusieurs fois ou pas
        for (r, i) in zip(subset, range(0, 1000)):
            if NbrParent[r['taxoparent']] > 1:
                subset[i]['sortclause'] = r['taxoparent'][1:99] + r['taxoname']
            else:
                subset[i]['sortclause'] = r['taxoname']
        # on tri le subset et on le remet dans le tableau original.
        restree[d:f + 1] = sorted(subset, key=lambda t: t['sortclause'])
    for k, v in enumerate(restree):
        if v['display_name'].find('<') > 0:
            parts = v['display_name'].split('<')
            restree[k]['htmldisplayname'] = parts[0]
            restree[k]['taxoparent'] = ''.join((' &lt;&nbsp;' + XSSEscape(x) for x in parts[1:]))
        else:
            restree[k]['htmldisplayname'] = v['display_name']
            restree[k]['taxoparent'] = XSSEscape(v['taxoparent'])
            restree[k]['taxoparent'] = ""
    return render_template('project/classiftab.html', res=restree, taxotree=json.dumps(taxotree))


######################################################################################################################
@app.route('/prjGetClassifTab/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prjGetClassifTab(PrjId):
    Prj = database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        return "Project doesn't exists"
    g.PrjAnnotate = g.PrjManager = Prj.CheckRight(2)
    if not g.PrjManager:
        g.PrjAnnotate = Prj.CheckRight(1)
    g.PublicViewMode = not Prj.CheckRight(0)
    if gvp('ForceRecalc') == 'Y':
        RecalcProjectTaxoStat(Prj.projid)
    UpdateProjectStat(Prj.projid)
    g.Projid = Prj.projid
    return GetClassifTab(Prj)


######################################################################################################################
@app.route('/prjPurge/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prjPurge(PrjId):
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: Project = api.project_query_projects_project_id_query_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status == 403:
                flash('You cannot Purge this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    txt = ObjListTxt = ""
    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    txt += "<div style='margin-left: 5px;'><h3>ERASE OBJECTS TOOL </h3>"

    if gvp("objlist") == "":

        # Extract filter values
        filtres = {}
        for k in sharedfilter.FilterList:
            if gvg(k):
                filtres[k] = gvg(k, "")
        if len(filtres):
            # QUERY objects in project
            with ApiClient(ObjectsApi, request) as api:
                # noinspection PyTypeChecker
                object_ids: List[int] = api.get_object_set_object_set_project_id_query_post(PrjId, filtres)
            ObjListTxt = "\n".join((str(r) for r in object_ids))

            txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
                   "USING Active Project Filters, {0} objects</span>".format(len(object_ids))
        else:
            txt += """Enter the list of internal object id you want to delete. 
            <br>Or type in <span style='cursor:pointer;color:#337ab7;' onclick="$('#objlist').val('DELETEALL')">
            "DELETEALL"</span> to remove all object from this project.
            <br>(<b>Around 10000 objects are deleted per second, so on a big project it can be long, 
            a NGinx Error may happen, but erase process is still working in background. 
            <br/>Statistics are not updated during erase project. </b>)
            <br>You can retrieve object id from a TSV export file using export data from project action menu<br>"""
        txt += """
        <form action=? method=post>
        <textarea name=objlist id=objlist cols=15 rows=20 autocomplete=off>{1}</textarea><br>
        <input type=checkbox name=destroyproject value=Y> DELETE project after DELETEALL action.<br>
        <input type="submit" class="btn btn-danger" value='ERASE THESE OBJECTS !!! IRREVERSIBLE !!!!!'>
        <a href ="/prj/{0}" class="btn btn-success">Cancel, Back to project home</a>
        </form></div>
        """.format(PrjId, ObjListTxt)
    else:
        if gvp("objlist") == "DELETEALL":
            # DELETE all objects
            with ApiClient(ProjectsApi, request) as api:
                no, noh, ni, nbrfile = api.erase_project_projects_project_id_delete(project_id=PrjId,
                                                                                    only_objects=
                                                                                    gvp("destroyproject") != "Y")
        else:
            # DELETE some objects in project
            objs = [int(x.strip()) for x in gvp("objlist").splitlines() if x.strip() != ""]
            with ApiClient(ObjectsApi, request) as api:
                no, noh, ni, nbrfile = api.erase_object_set_object_set_delete(objs)

        txt += "Deleted %d Objects, %d ObjectHisto, %d Images in Database and %d files" % (no, noh, ni, nbrfile)

        if gvp("objlist") == "DELETEALL" and gvp("destroyproject") == "Y":
            txt += "<br>Project and associated privileges, destroyed"
            return PrintInCharte(txt + "<br><br><a href ='/prj/'>Back to project list</a>")

    return PrintInCharte(txt + "<br><br><a href ='/prj/{0}'>Back to project home</a>".format(PrjId))


def PrjGetFieldList(Prj, typefield, term):
    fieldlist = []
    MapList = {'o': 'mappingobj', 's': 'mappingsample', 'a': 'mappingacq', 'p': 'mappingprocess'}
    MapPrefix = {'o': '', 's': 'sample ', 'a': 'acquis. ', 'p': 'process. '}
    for mapk, mapv in MapList.items():
        for k, v in sorted(DecodeEqualList(getattr(Prj, mapv, "")).items(), key=lambda t: t[1]):
            if (k[0] == typefield or typefield == '') and v != "" and (term == '' or term in v):
                fieldlist.append({'id': mapk + k, 'text': MapPrefix[mapk] + v})
    return fieldlist


@app.route('/prj/GetFieldList/<int:PrjId>/<string:typefield>')
@login_required
def PrjGetFieldListAjax(PrjId, typefield):
    Prj = database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        return "Project doesn't exists"
    term = gvg("q")
    fieldlist = PrjGetFieldList(Prj, typefield, term)
    return json.dumps(fieldlist)


@app.route('/prj/simplecreate/', methods=['GET', 'POST'])
@login_required
def SimpleCreate():
    with ApiClient(ProjectsApi, request.cookies.get('session')) as api:
        req = CreateProjectReq(title=gvp("projtitle"))
        rsp: int = api.create_project_projects_create_post(req)

    # return "<a href='/prj/{0}' class='btn btn-primary'>Project Created ! Open IT</a>".format(Prj.projid)
    return "<script>window.location='/prj/{0}';</script>".format(rsp)
