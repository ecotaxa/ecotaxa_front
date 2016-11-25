from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage,ntcv
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli,psycopg2.extras,urllib
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
import appli.project.sharedfilter as sharedfilter

######################################################################################################################
@app.route('/prj/')
@login_required
def indexProjects():
    txt = "<h3>Select a project</h3>" #,pp.member
    sql="select p.projid,title,status,coalesce(objcount,0),coalesce(pctvalidated,0),coalesce(pctclassified,0) from projects p"
    if not current_user.has_role(database.AdministratorLabel):
        sql+="  Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
    sql+=" order by lower(title)" #pp.member nulls last,
    res = GetAll(sql) #,debug=True
    txt+="""
    <p>To create a new project and upload images in it, please contact the application manager(s): {0}</p>
    """.format(appli.GetAppManagerMailto())

    txt+="""
    <table class='table table-hover table-verycondensed projectsList'>
        <thead><tr>
                <th></th>
                <th>Title [ID]</th>
                <th>Status</th>
                <th>Nb objects</th>
                <th>%&nbsp;validated</th>
                <th>%&nbsp;classified</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in res:
        # if r[6] is None:
        #     txt+="<tr><td><a class='btn btn-primary' href='/prj/{0}'>Request !</a> {0}</td>".format(*r)
        # else:
        txt+="<tr><td><a class='btn btn-primary' href='/prj/{0}'>Select</a></td>".format(*r)
        txt+="""<td>{1} [{0}]</td>
        <td>{2}</td>
        <td>{3:0.0f}</td>
        <td>{4:0.2f}</td>
        <td>{5:0.2f}</td>
        </tr>""".format(*r)
    txt+="</tbody></table>"
    txt+="""<div class="col-sm-6 col-sm-offset-3">
			<a href="/prjothers/" class="btn  btn-block btn-primary">Show projectspriv in which you are not registered</a>
        </div>"""
    return PrintInCharte(txt)
######################################################################################################################
@app.route('/prjothers/')
@login_required
def ProjectsOthers():
    txt = "<h3>Other projects</h3>" #,pp.member
    sql="""select p.projid,title,status,coalesce(objcount,0),coalesce(pctvalidated,0),coalesce(pctclassified,0),qpp.email,qpp.name
           from projects p
           left Join projectspriv pp on p.projid = pp.projid and pp.member=%d
           left join ( select * from (
                        select u.email,u.name,pp.projid,rank() OVER (PARTITION BY pp.projid ORDER BY pp.id) rang
                        from projectspriv pp join users u on pp.member=u.id
                        where pp.privilege='Manage' and u.active=true ) q where rang=1
                      ) qpp on qpp.projid=p.projid
           where pp.member is null
           order by lower(title)"""%(current_user.id,)
    res = GetAll(sql) #,debug=True
    txt+="""
    <p>To have acces to theses projects, request access to the project manager.</p>
    <table class='table table-hover table-verycondensed projectsList'>
        <thead><tr>
                <th></th>
                <th>Title [ID]</th>
                <th>Status</th>
                <th>Nb objects</th>
                <th>%&nbsp;validated</th>
                <th>%&nbsp;classified</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in res:
        if r[6] is None:
            txt+="<tr><td> </td>"
        else:
            txt+="<tr><td><a class='btn btn-primary' href='mailto:{7}?{0}'>REQUEST ACCESS</a></td>".format(
                urllib.parse.urlencode({'body':"Please provide me privileges to project : "+ntcv(r[1])
                                           ,'subject':'Project access request'}
                                       ).replace('+','%20') # replace car urlencode mais des + pour les espaces qui sont mal traitrés par le navigateur
                ,*r)
        txt+="<td>{1} [{0}]".format(*r)
        if r['name']: txt+="<br>"+r['name']
        txt+="""</td><td>{2}</td>
        <td>{3:0.0f}</td>
        <td>{4:0.2f}</td>
        <td>{5:0.2f}</td>
        </tr>""".format(*r)
    txt+="</tbody></table>"
    txt+="""<div class="col-sm-6 col-sm-offset-3">
			<a href="/prj/" class="btn  btn-block btn-primary">Back to projects list</a>
        </div>"""
    return PrintInCharte(txt)



######################################################################################################################
def UpdateProjectStat(PrjId):
    ExecSQL("""UPDATE projects
         SET  objcount=q.nbr,pctclassified=100.0*nbrclassified/q.nbr,pctvalidated=100.0*nbrvalidated/q.nbr
         from projects p
         left join
         (select projid, count(*) nbr,count(classif_id) nbrclassified,count(case when classif_qual='V' then 1 end) nbrvalidated
              from objects o
              where projid=%(projid)s
              group by projid )q on p.projid=q.projid
         where projects.projid=%(projid)s and p.projid=%(projid)s""",{'projid':PrjId})
######################################################################################################################
def GetFieldList(Prj,champ='classiffieldlist'):
    fieldlist=collections.OrderedDict()
    fieldlist["orig_id"]="Image Name"
    fieldlist["classif_auto_score"]="Score"
    objmap=DecodeEqualList(Prj.mappingobj)
    for v in ('objtime','depth_min','depth_max'):
        objmap[v]=v
    #fieldlist fait le mapping entre le nom fonctionnel et le nom à affiche
    # cette boucle permet de faire le lien avec le nom de la colonne (si elle existe.
    fieldlist2={}
    for field,dispname in DecodeEqualList(getattr(Prj,champ)).items():
        for ok,on in objmap.items():
            if field==on :
                fieldlist2[ok]=dispname
    for k,v in sorted(fieldlist2.items(), key=lambda t: t[1]):
        fieldlist[k]=v
    return fieldlist
# Contient la liste des filtre & parametres de cet écrans avec les valeurs par degaut
FilterList={"MapN":"","MapW":"","MapE":"","MapS":"","depthmin":"","depthmax":"","samples":"","fromdate":"","todate":""
               ,"inverttime":"","fromtime":"","totime":"","sortby":"","sortorder":"","dispfield":"","statusfilter":""
            ,'ipp':100,'zoom':100,'magenabled':1,'popupenabled':1,'instrum':'','month':'','daytime':''
            ,'freenum':'','freenumst':'','freenumend':'','freetxt':'','freetxtval':'','filt_annot':''}
FilterListAutoSave=("sortby","sortorder","dispfield","statusfilter",'ipp','zoom','magenabled','popupenabled')
######################################################################################################################
@app.route('/prj/<int:PrjId>')
@login_required
def indexPrj(PrjId):
    data={'pageoffset':gvg("pageoffset","0")}
    for k,v in FilterList.items():
        data[k]=gvg(k,str(current_user.GetPref(k,v)))
    # print('%s',data)
    if data["samples"]:
        data["sample_for_select"]=""
        for r in GetAll("select sampleid,orig_id from samples where projid=%d and sampleid in(%s)"%(PrjId,data["samples"])):
            data["sample_for_select"]+="\n<option value='{0}' selected>{1}</option> ".format(*r)
    data["month_for_select"] = ""
    # print("%s",data['month'])
    for (k,v) in enumerate(('January','February','March','April','May','June','July','August','September','October','November','December'),start=1):
        data["month_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format('selected' if str(k) in data['month'].split(',') else '',k,v)
    data["daytime_for_select"] = ""
    for (k,v) in database.DayTimeList.items():
        data["daytime_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format('selected' if str(k) in data['daytime'].split(',') else '',k,v)
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        flash("Project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(0): # Level 0 = Read, 1 = Annotate, 2 = Admin
        MainContact=GetAll("""select u.email,u.name
                        from projectspriv pp join users u on pp.member=u.id
                        where pp.privilege='Manage' and u.active=true and pp.projid=%s""",(PrjId,))
        # flash("",'error')
        msg="""<div class="alert alert-danger alert-dismissible" role="alert">
        You cannot view this project : {1} [{2}] <a class='btn btn-primary' href='mailto:{3}?{0}' style='margin-left:15px;'>REQUEST ACCESS to {4}</a>
        </div>""".format(
                urllib.parse.urlencode({'body':"Please provide me privileges to project : "+ntcv(Prj.title)
                                           ,'subject':'Project access request'}
                                       ).replace('+','%20') # replace car urlencode mais des + pour les espaces qui sont mal traitrés par le navigateur
                ,Prj.title,Prj.projid,MainContact[0]['email'],MainContact[0]['name'])
        return PrintInCharte(msg+"<a href=/prj/>Select another project</a>")
    g.Projid=Prj.projid
    # Ces 2 listes sont ajax mais si on passe le filtre dans l'URL il faut ajouter l'entrée en statique pour l'affichage
    data["filt_freenum_for_select"] = ""
    if data['freenum']!="":
        for r in PrjGetFieldList(Prj,'n',''):
            if r['id']==data['freenum']:
                data["filt_freenum_for_select"] = "\n<option value='{0}' selected>{1}</option> ".format(r['id'],r['text'])
    data["filt_freetxt_for_select"] = ""
    if data['freetxt']!="":
        for r in PrjGetFieldList(Prj,'t',''):
            if r['id']==data['freetxt']:
                data["filt_freetxt_for_select"] = "\n<option value='{0}' selected>{1}</option> ".format(r['id'],r['text'])
    data["filt_annot_for_select"] = ""
    if data['filt_annot']!="":
        for r in GetAll("select id,name from users where id =any (%s)",([int(x) for x in data["filt_annot"].split(',')],)):
                data["filt_annot_for_select"] += "\n<option value='{0}' selected>{1}</option> ".format(r['id'],r['name'])
    fieldlist=GetFieldList(Prj)
    data["fieldlist"]=fieldlist
    data["sortlist"]=collections.OrderedDict({"":""})
    data["sortlist"]["classifname"]="Category Name"
    data["sortlist"]["random_value"]="Random"
    data["sortlist"]["classif_when"]="Validation date"
    for k,v in fieldlist.items():data["sortlist"][k]=v
    data["statuslist"]=collections.OrderedDict({"":"All"})
    data["statuslist"]["U"]="Unclassified"
    data["statuslist"]["P"]="Predicted"
    data["statuslist"]["NV"]="Not Validated"
    data["statuslist"]["V"]="Validated"
    data["statuslist"]["NVM"]="Validated by others"
    data["statuslist"]["VM"]="Validated by me"
    data["statuslist"]["D"]="Dubious"
    g.PrjAnnotate=g.PrjManager=Prj.CheckRight(2)
    if not g.PrjManager: g.PrjAnnotate=Prj.CheckRight(1)
    right='dodefault'
    if gvg("taxo")!="":
        g.taxofilter=gvg("taxo")
        g.taxofilterlabel= GetAll("select name from taxonomy where id=%s ",(gvg("taxo"),))[0][0]
    else:
        g.taxofilter=""
        g.taxofilterlabel=""

    classiftab=GetClassifTab(Prj)
    g.ProjectTitle=Prj.title
    g.headmenu = []
    g.headmenu.append(("/prjcm/%d"%(PrjId,),"Show confusion matrix"))
    if g.PrjAnnotate:
        g.headmenu.append(("","SEP"))
        g.headmenu.append(("/Task/Create/TaskClassifAuto?p=%d"%(PrjId,),"Predict identifications"))
        g.headmenu.append(("javascript:GotoWithFilter('/Task/Create/TaskExportTxt')" , "Export data with active filters"))
        g.headmenu.append(("/Task/Create/TaskExportTxt?projid=%d"%(PrjId,),"Export all data"))
    if g.PrjManager:
        g.headmenu.append(("","SEP"))
        g.headmenu.append(("/Task/Create/TaskImport?p=%d"%(PrjId,),"Import images and metadata"))
        g.headmenu.append(("/Task/Create/TaskImportUpdate?p=%d" % (PrjId,), "Re-import and update metadata"))
        g.headmenu.append(("/prj/edit/%d"%(PrjId,),"Edit project settings"))
        g.headmenu.append(("/Task/Create/TaskSubset?p=%d"%(PrjId,),"Extract subset"))
        g.headmenu.append(("/prj/merge/%d"%(PrjId,),"Merge another project in this project"))
        g.headmenu.append(("/prj/EditAnnot/%d"%(PrjId,),"Edit or erase annotations massively"))
        g.headmenu.append(("/prjPurge/%d"%(PrjId,),"Delete objects and project"))
        g.headmenu.append(("javascript:GotoWithFilter('/prjPurge/%d')"%(PrjId,), "Erase objects with active filter"))
        g.headmenu.append(("javascript:GotoWithFilter('/Task/Create/TaskSubset?p=%d&eps=y')"%(PrjId,), "Extract Subset with active filter"))

    appli.AddTaskSummaryForTemplate()
    filtertab=getcommonfilters(data)
    return render_template('project/projectmain.html',top="",lefta=classiftab,leftb=filtertab
                           ,right=right,data=data)

######################################################################################################################
@app.route('/prj/LoadRightPane', methods=['GET', 'POST'])
@login_required
def LoadRightPane():
    # récupération des parametres d'affichage
    pageoffset=int(gvp("pageoffset","0"))
    filtres={}
    for k in sharedfilter.FilterList:
        filtres[k]=gvp(k,"")

    PrjId=gvp("projid")
    Filt={}
    PrefToSave=0
    for k,v in FilterList.items():
        Filt[k]=gvp(k,v)
        if k in FilterListAutoSave or gvp("saveinprofile")=="Y":
            PrefToSave+=current_user.SetPref(k,Filt[k])

    # on sauvegarde les parametres dans le profil utilisateur
    if PrefToSave>0 :
        database.ExecSQL("update users set preferences=%s where id=%s",(current_user.preferences,current_user.id),True)
        user_datastore.ClearCache()
    sortby=Filt["sortby"]
    sortorder=Filt["sortorder"]
    dispfield=Filt["dispfield"]
    ipp=int(Filt["ipp"])
    ippdb=ipp if ipp>0 else 200 # Fit to page envoi un ipp de 0 donc on se comporte comme du 200 d'un point de vue DB
    zoom=int(Filt["zoom"])
    popupenabled=Filt["popupenabled"]
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    fieldlist=GetFieldList(Prj)
    fieldlist.pop('orig_id','')
    fieldlist.pop('objtime','')
    t=["<a name='toppage'/>"]
    whereclause=" where o.projid=%(projid)s "
    sqlparam={'projid':gvp("projid")}
    sql="""select o.objid,t.name taxoname,o.classif_qual,u.name classifwhoname,i.file_name
  ,i.height,i.width,i.thumb_file_name,i.thumb_height,i.thumb_width
  ,o.depth_min,o.depth_max,s.orig_id samplename,o.objdate,to_char(o.objtime,'HH24:MI') objtime
  ,case when o.complement_info is not null and o.complement_info!='' then 1 else 0 end commentaires
  ,o.latitude,o.orig_id,o.imgcount"""
    for k in fieldlist.keys():
        sql+=",o."+k+" as extra_"+k
    sql+=""" from objects o
left Join images i on o.img0id=i.imgid
left JOIN taxonomy t on o.classif_id=t.id
LEFT JOIN users u on o.classif_who=u.id
LEFT JOIN  samples s on o.sampleid=s.sampleid
"""
    whereclause += sharedfilter.GetSQLFilter(filtres,sqlparam,str(current_user.id))
    sql+=whereclause

    sqlcount="""select count(*)
        ,count(case when classif_qual='V' then 1 end) NbValidated
        ,count(case when classif_qual='D' then 1 end) NbDubious
        ,count(case when classif_qual='P' then 1 end) NbPredicted
        from objects o
        LEFT JOIN  acquisitions acq on o.acquisid=acq.acquisid
        """+whereclause
    (nbrtotal,nbrvalid,nbrdubious,nbrpredict)=GetAll(sqlcount,sqlparam,debug=False)[0]
    pagecount=math.ceil(nbrtotal/ippdb)
    if sortby=="classifname":
        sql+=" order by t.name "+sortorder
    elif sortby!="":
        sql+=" order by o."+sortby+" "+sortorder
    # else:  # pas de tri par defaut pour améliorer les performances sur les gros projets
    #     sql+=" order by o.orig_id"
    # app.logger.info("pageoffset/pagecount %s / %s",pageoffset,pagecount)
    if pageoffset>=pagecount:
        pageoffset=pagecount-1
        if pageoffset<0:
            pageoffset=0
    sql+=" Limit %d offset %d "%(ippdb,pageoffset*ippdb)
    res=GetAll(sql,sqlparam,False)
    trcount=1
    fitlastclosedtr=0 # index de t de la derniere création de ligne qu'il faudrat effacer quand la page sera pleine
    fitheight=100 # hauteur déjà occupé dans la page plus les header footer (hors premier header)
    fitcurrentlinemaxheight=0
    LineStart=""
    if Prj.CheckRight(1): # si annotateur on peut sauver les changements.
        LineStart="<td class='linestart'></td>"
    t.append("<table class=imgtab><tr id=tr1>"+LineStart)
    WidthOnRow=0
    #récuperation et ajustement des dimensions de la zone d'affichage
    try:
        PageWidth=int(gvp("resultwidth"))-40 # on laisse un peu de marge à droite et la scroolbar
        if PageWidth<200 : PageWidth=200
    except:
        PageWidth=200
    try:
        WindowHeight=int(gvp("windowheight"))-100 # on enleve le bandeau du haut
        if WindowHeight<200 : WindowHeight=200
    except:
        WindowHeight=200
    #print("PageWidth=%s, WindowHeight=%s"%(PageWidth,WindowHeight))
    # Calcul des dimmensions et affichage des images
    for r in res:
        filename=r['file_name']
        origwidth=r['width']
        origheight=r['height']
        thumbfilename=r['thumb_file_name']
        thumbwidth=r['thumb_width']
        if origwidth is None: # pas d'image associé, pas trés normal mais arrive pour les subset sans images
            width=80
            height=40
        else:
            width=origwidth*zoom//100
            height=origheight*zoom//100
        if max(width,height)<75: # en dessous de 75 px de coté on ne fait plus le scaling
            if max(origwidth,origheight)<75:
                width=origwidth   # si l'image originale est petite on l'affiche telle quelle
                height=origheight
            elif max(origwidth,origheight)==origwidth:
                width=75
                height=origheight*75//origwidth
                if height<1 : height=1
            else:
                height=75
                width=origwidth*75//origheight
                if width<1 : width=1

        # On limite les images pour qu'elles tiennent toujours dans l'écran
        if width>PageWidth:
            width=PageWidth
            height=math.trunc(r['height']*width/r['width'])
            if height==0: height=1
        if height>WindowHeight:
            height=WindowHeight
            width=math.trunc(r['width']*height/r['height'])
            if width==0: width=1
        if WidthOnRow!=0 and (WidthOnRow+width)>PageWidth:
            trcount+=1
            fitheight+=fitcurrentlinemaxheight
            if(ipp==0) and (fitheight>WindowHeight): # en mode fit quand la page est pleine
                if fitlastclosedtr>0 : #dans tous les cas on laisse une ligne
                    del t[fitlastclosedtr:]
                break;
            fitlastclosedtr=len(t)
            fitcurrentlinemaxheight=0
            t.append("</tr></table><table class=imgtab><tr id=tr%d>%s"%(trcount,LineStart))
            WidthOnRow=0
        cellwidth=width+22
        fitcurrentlinemaxheight=max(fitcurrentlinemaxheight,height+45+14*len(dispfield.split())) #45 espace sur le dessus et le dessous de l'image + 14px par info affichée
        if cellwidth<80: cellwidth=80 # on considère au moins 80 car avec les label c'est rarement moins
        # Met la fenetre de zoon la ou il y plus de place, sachant qu'elle fait 400px et ne peut donc pas être callée à gauche des premieres images.
        if (WidthOnRow+cellwidth)>(PageWidth/2):
            pos='left'
        else: pos='right'
        #Si l'image affiché est plus petite que la miniature, afficher la miniature.
        if thumbwidth is None or thumbwidth<width or thumbfilename is None: # sinon (si la miniature est plus petite que l'image à afficher )
            thumbfilename=filename # la miniature est l'image elle même
        txt="<td width={0}>".format(cellwidth)
        if filename:
            txt+="<img class='lazy' id=I{3} data-src='/vault/{5}' data-zoom-image='{0}' width={1} height={2} pos={4}>"\
                .format(filename,width,height,r['objid'],pos,thumbfilename)
        else:
            txt+="No Image"
        # Génération de la popover qui apparait pour donner quelques détails sur l'image
        if popupenabled=="1":
            popoverfieldlist=GetFieldList(Prj,champ='popoverfieldlist')
            popoverfieldlist.pop('orig_id','')
            popoverfieldlist.pop('objtime','')
            poptitletxt="%s"%(r['orig_id'],)
            poptxt=""
            #poptxt="<p style='white-space: nowrap;color:black;'>cat. %s"%(r['taxoname'],)
            if r[3]!="":
                poptxt+="<em>by</em> %s"%(r[3])
            poptxt+="<br><em>in</em> "+ntcv(r['samplename'])
            for k,v in popoverfieldlist.items():
                if k=='classif_auto_score' and r["classif_qual"]=='V':
                    poptxt+="<br>%s : %s"%(v,"-")
                else:
                    poptxt+="<br>%s : %s"%(v,ScaleForDisplay(r["extra_"+k]))
            popattribute="data-title=\"{0}\" data-content=\"{1}\" data-placement='{2}'".format(poptitletxt,poptxt,'left' if WidthOnRow>500 else 'right')
        else: popattribute=""
        # Génération du texte sous l'image qui contient la taxo + les champs à afficher
        bottomtxt=""
        if 'objtime' in dispfield:
            bottomtxt+="<br>Time %s"%(r['objtime'],)
        for k,v in fieldlist.items():
            if k in dispfield:
                if k=='classif_auto_score' and r["classif_qual"]=='V':
                    bottomtxt+="<br>%s : -"%v
                else:
                    bottomtxt+="<br>%s : %s"%(v,ScaleForDisplay(r["extra_"+k]))
        if bottomtxt!="":
            bottomtxt=bottomtxt[4::] #[4::] supprime le premier <BR>
        if 'orig_id' in dispfield:
            bottomtxt="<div style='word-break: break-all;'>%s</div>"%(r['orig_id'],)+bottomtxt
        txt+="""<div class='subimg {1}' {2}>
<div class='taxo'>{0}</div>
<div class='displayedFields'>{3}</div></div>
<div class='ddet'><span class='ddets'><span class='glyphicon glyphicon-eye-open'></span> {4} {5}</div>"""\
            .format(r['taxoname'],GetClassifQualClass(r['classif_qual']),popattribute,bottomtxt
                    ,"(%d)"%(r['imgcount'],) if r['imgcount'] is not None and r['imgcount']>1 else ""
                    ,"<b>!</b> "if r['commentaires'] >0 else "" )
        txt+="</td>"

        # WidthOnRow+=max(cellwidth,80) # on ajoute au moins 80 car avec les label c'est rarement moins
        WidthOnRow+=cellwidth+5 # 5 = border-spacing = espace inter image
        t.append(txt)

    t.append("</tr></table>")
    if len(res)==0:
        t.append("<b>No Result</b><br>")
    if Prj.CheckRight(1): # si annotateur on peut sauver les changements.
        t.append("""
		<div id='PendingChanges' class='PendingChangesClass text-danger'></div>
		<button class='btn btn-default' onclick="$(window).scrollTop(0);"><span class='glyphicon glyphicon-arrow-up ' ></span></button>
        <button class='btn btn-primary' onclick='SavePendingChanges();' title='CTRL+S' id=BtnSave disabled><span class='glyphicon glyphicon-save' /> Save pending changes [CTRL+S]</button>
        <button class='btn btn-success' onclick='ValidateAll();'><span class='glyphicon glyphicon-ok' /> <span class='glyphicon glyphicon-arrow-right' /> <span id=TxtBtnValidateAll>Validate all and move to next page</span></button>
        <!--<button class='btn btn-success' onclick='ValidateAll(1);' title="Save changed annotations , Validate all objects in page &amp; Go to Next Page"><span class='glyphicon glyphicon-arrow-right' /> Save, Validate all &amp; Go to Next Page</button>-->
        <button class='btn btn-success' onclick='ValidateSelection();'><span class='glyphicon glyphicon-ok' />  Validate Selection</button>
        <button class='btn btn-default' onclick="$('#bottomhelp').toggle()" ><span class='glyphicon glyphicon-question-sign' /> Undo</button>
        <div id="bottomhelp" class="panel panel-default" style="margin:10px 0px 0px 40px;width:500px;display:none;">To correct validation mistakes (no UNDO button in Ecotaxa):
<br>1.	Select Validated Status
<br>2.	Sort by : Validation date
<br>3.	Move the most recent (erroneous) validated objects into the suitable category
</div>
        """)
    # Gestion de la navigation entre les pages
    if pagecount>1 or pageoffset>0:
        t.append("<p class='inliner'> Page %d / %d</p>"%(pageoffset+1,pagecount))
        t.append("<nav><ul class='pagination'>")
        if pageoffset>0:
            t.append("<li><a href='javascript:gotopage(%d);' >&laquo;</a></li>"%(pageoffset-1))
        for i in range(0,pagecount-1,math.ceil(pagecount/20)):
            if i == pageoffset:
                t.append("<li class='active'><a href='javascript:gotopage(%d);'>%d</a></li>"%(i,i+1))
            else:
                t.append("<li><a href='javascript:gotopage(%d);'>%d</a></li>"%(i,i+1))
        t.append("<li><a href='javascript:gotopage(%d);'>%d</a></li>"%(pagecount-1,pagecount))
        if pageoffset<pagecount-1:
            t.append("<li><a href='javascript:gotopage(%d);' >&raquo;</a></li>"%(pageoffset+1))
        t.append("</ul></nav>")
    if nbrtotal>0:
        pctvalid="<font color=#0A0>%0.1f %%</font>, <font color=#5bc0de>%0.1f %%</font>, <font color=#F0AD4E>%0.1f %%</font>"%(100*nbrvalid/nbrtotal,100*nbrpredict/nbrtotal,100*nbrdubious/nbrtotal)
    else: pctvalid="-"
    t.append("""
    <script>
        PostAddImages();
        $('#objcount').html('%s / %d ');
    </script>"""%(pctvalid,nbrtotal))
    return "\n".join(t)

######################################################################################################################
def GetClassifTab(Prj):
    if Prj.initclassiflist is None:
        InitClassif="0" # pour être sur qu'il y a toujours au moins une valeur
    else:
        InitClassif=[x for x in Prj.initclassiflist.split(",") if x.isdigit()]
        if len(InitClassif):
            InitClassif=",".join(InitClassif)
        else:
            InitClassif="0" # pour être sur qu'il y a toujours au moins une valeur

    InitClassif=", ".join(["("+x.strip()+")" for x in InitClassif.split(",") if x.strip()!=""])
    sql="""select t.id,t.name as taxoname,case when tp.name is not null and t.name not like '%% %%'  then ' ('||tp.name||')' else ' ' end as  taxoparent,nbr,nbrnotv
    from (  SELECT    o.classif_id,   c.id,count(classif_id) Nbr,count(case when classif_qual='V' then NULL else o.classif_id end) NbrNotV
        FROM (select * from objects where projid=%(projid)s) o
        FULL JOIN (VALUES """+InitClassif+""") c(id) ON o.classif_id = c.id
        GROUP BY classif_id, c.id
      ) o
    JOIN taxonomy t on coalesce(o.classif_id,o.id)=t.id
    left JOIN taxonomy tp ON t.parent_id = tp.id
    order by t.name       """
    param={'projid':Prj.projid}
    res=GetAll(sql,param,debug=False,cursor_factory=psycopg2.extras.RealDictCursor)
    ids=[x['id'] for x in res]
    # print(ids)
    sql="""WITH RECURSIVE rq as (
                SELECT DISTINCT t.id,t.name,t.parent_id
                FROM taxonomy t where t.id = any (%s)
              union
                SELECT t.id,t.name,t.parent_id
                FROM rq JOIN taxonomy t ON rq.parent_id = t.id
            )
            select * from rq  """
    taxotree=GetAssoc(sql,(ids,))
    for k,v in enumerate(res):
        res[k]['cp']=None  #cp = Closest parent
        res[k]['cpdist']=0
        id=v["id"]
        for i in range(50): # 50 pour arreter en cas de boucle
            if id in taxotree:
                id=taxotree[id]['parent_id']
            else:
                id=None
            if id is None:
                break
            if id in ids:
                res[k]['cp']=id
                res[k]['cpdist']=i+1
                break
    restree=[]
    def AddChild(Src,Parent,Res,Deep,ParentClasses):
        for r in Src:
            if r['cp'] ==Parent:
                # r['dist']=Deep+r['cpdist']
                r['dist']=Deep
                r['parentclasses']=ParentClasses
                r["haschild"]=False
                for p,i in zip(Res,range(10000)):
                    if p['id']==Parent:
                        Res[i]["haschild"]=True
                Res.append(r)
                AddChild(Src,r['id'],Res,r['dist']+1,ParentClasses+(" visib%s"%(r['id'],)))
    AddChild(res,None,restree,0,"")
    # Cette section de code à pour but de trier le niveau final (qui n'as pas d'enfant) par parent s'il un parent apparait plus d'une fois sinon par enfant
    # on isole d'abord les branche
    parents=set([x['parentclasses'] for x in restree])
    # on ne garde que les branches sans enfants
    parentsnochild=parents.copy()
    for p in parents:
        for r in restree:
            if r['parentclasses']==p and r['haschild'] :
                parentsnochild.discard(p)
    for p in parentsnochild:
        # on recherche dans le tableau à plats les bornes de chaques branche et on met la branche dans subset
        d=f=0
        for (r,i) in zip(restree,range(0,1000)):
            if r['parentclasses']==p :
                f=i
                if d==0: d=i
        subset=restree[d:f+1]
        # on cherche les parents presents plus d'une fois
        NbrParent={x['taxoparent']:0 for x in subset}
        for r in subset:
            NbrParent[r['taxoparent']]+=1
        # on calcule une clause de tri en fonction du fait que le parent est present plusieurs fois ou pas
        for (r,i) in zip(subset,range(0,1000)):
            if NbrParent[r['taxoparent']]>1:
                subset[i]['sortclause']=r['taxoparent'][1:99]+r['taxoname']
            else:
                subset[i]['sortclause']=r['taxoname']
        # on tri le subset et on le remet dans le tableau original.
        restree[d:f+1]=sorted(subset,key=lambda t:t['sortclause'])
    return render_template('project/classiftab.html',res=restree,taxotree=json.dumps(taxotree))

######################################################################################################################
@app.route('/prjGetClassifTab/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prjGetClassifTab(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        return "Project doesn't exists"
    g.PrjAnnotate=g.PrjManager=Prj.CheckRight(2)
    UpdateProjectStat(Prj.projid)
    g.Projid=Prj.projid
    if gvp("taxo")!="":
        g.taxoclearspan="<span class='label label-default' onclick='SetTaxoFilter(false,-1)'>Clear "+gvp("taxofilterlabel")+"</span>"
    return GetClassifTab(Prj)

######################################################################################################################
@app.route('/prjPurge/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prjPurge(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        return "Project doesn't exists"
    if not Prj.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot Purge this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    txt=ObjListTxt=""
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title)
    txt += "<h3>ERASE OBJECTS TOOL </h3>";
    if gvp("objlist")=="":
        sql="select objid FROM objects o where projid="+str(Prj.projid)
        sqlparam={}
        filtres = {}
        for k in sharedfilter.FilterList:
            if gvg(k):
                filtres[k] = gvg(k, "")
        if len(filtres):
            sql+= sharedfilter.GetSQLFilter(filtres, sqlparam, str(current_user.id))
            ObjList=GetAll(sql,sqlparam)
            ObjListTxt="\n".join((str(r['objid']) for r in ObjList))
            txt+="<span style='color:red;weight:bold;font-size:large;'>USING Active Project Filters</span>"
        else:
            txt += """Enter the list of internal object id you want to delete. <br>Or type in ‘’DELETEALL’’ to remove all object from this project.<br>
        You can retrieve object id from a TSV export file using export data from project action menu<br>""";
        txt+="""
        <form action=? method=post>
        <textarea name=objlist cols=15 rows=20 autocomplete=off>{1}</textarea><br>
        <input type=checkbox name=destroyproject value=Y> DELETE project after DELETEALL action.<br>
        <input type="submit" class="btn btn-danger" value='ERASE THESES OBJECTS !!! IRREVERSIBLE !!!!!'>
        <a href ="/prj/{0}" class="btn btn-success">Cancel, Back to project home</a>
        </form>
        """.format(PrjId,ObjListTxt)
    else:
        if gvp("objlist")=="DELETEALL":
            sqlsi="select file_name,thumb_file_name from images i,objects o where o.objid=i.objid and o.projid={0}".format(PrjId)
            sqldi="delete from images i using objects o where o.objid=i.objid and o.projid={0}".format(PrjId)
            sqldoh="delete from objectsclassifhisto i using objects o where o.objid=i.objid and o.projid={0}".format(PrjId)
            sqldo="delete from obj_head where projid={0}".format(PrjId)
            objs=()
            SqlParam={}
        else:
            sqlsi="select file_name,thumb_file_name from images i,objects o where o.objid=i.objid and o.projid={0} and o.objid = any(%(objs)s)".format(PrjId)
            sqldi="delete from images i using objects o where o.objid=i.objid and o.projid={0} and o.objid = any(%(objs)s)".format(PrjId)
            sqldoh="delete from objectsclassifhisto i using objects o where o.objid=i.objid and o.projid={0} and o.objid = any(%(objs)s)".format(PrjId)
            sqldo="delete from obj_head where projid={0} and objid = any(%(objs)s)".format(PrjId)
            objs=[int(x.strip()) for x in gvp("objlist").splitlines() if x.strip()!=""]
            if len(objs)==0:
                raise Exception("No Objects ID specified")
            SqlParam={"objs":objs}
            app.logger.info("Erase %s"%(objs,))
        cur = db.engine.raw_connection().cursor()
        try:
            app.logger.info("Erase SQL=%s"%(sqlsi,))
            cur.execute(sqlsi,SqlParam)
            vaultroot=Path("./vault")
            nbrfile=0
            for r in cur:  # chaque enregistrement
                for f in r: # chacun des 2 champs
                    if f:  # si pas null
                        img=vaultroot.joinpath(f)
                        if img.exists():
                            os.remove(img.as_posix())
                            nbrfile+=1
        finally:
            cur.close()

        ni=ExecSQL(sqldi,SqlParam)
        noh=ExecSQL(sqldoh,SqlParam)
        no=ExecSQL(sqldo,SqlParam)
        if gvp("objlist")=="DELETEALL":
            ExecSQL("delete from samples where projid={0}".format(PrjId))
            ExecSQL("delete from acquisitions where projid={0}".format(PrjId))
            ExecSQL("delete from process where projid={0}".format(PrjId))
        txt+="Deleted %d Objects, %d ObjectHisto, %d Images in Database and %d files"%(no,noh,ni,nbrfile)
        if gvp("objlist")=="DELETEALL" and gvp("destroyproject")=="Y" :
            ExecSQL("delete from projectspriv where projid={0}".format(PrjId))
            ExecSQL("delete from projects where projid={0}".format(PrjId))
            txt+="<br>Project and associated privileges, destroyed"
            return PrintInCharte(txt+ ("<br><br><a href ='/prj/'>Back to project list</a>"))
        UpdateProjectStat(Prj.projid)
    return PrintInCharte(txt+ ("<br><br><a href ='/prj/{0}'>Back to project home</a>".format(PrjId)))

def PrjGetFieldList(Prj,typefield,term):
    fieldlist = []
    MapList = {'o': 'mappingobj', 's': 'mappingsample', 'a': 'mappingacq', 'p': 'mappingprocess'}
    MapPrefix = {'o': '', 's': 'sample ', 'a': 'acquis. ', 'p': 'process. '}
    for mapk, mapv in MapList.items():
        for k, v in sorted(DecodeEqualList(getattr(Prj, mapv, "")).items(), key=lambda t: t[1]):
            if k[0] == typefield and v != "" and (term=='' or term in v):
                fieldlist.append({'id': mapk + k, 'text': MapPrefix[mapk] + v})
    return fieldlist

@app.route('/prj/GetFieldList/<int:PrjId>/<string:typefield>')
@login_required
def PrjGetFieldListAjax(PrjId,typefield):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        return "Project doesn't exists"
    term=gvg("q")
    fieldlist=PrjGetFieldList(Prj, typefield, term)
    return json.dumps(fieldlist)

