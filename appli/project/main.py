#Todo filtres

from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db

######################################################################################################################
@app.route('/prj/')
@login_required
def indexProjects():
    txt = "<h3>Select your Project</h3>"
    sql="select p.projid,title,status,pctvalidated from projects p"
    if not current_user.has_role(database.AdministratorLabel):
        sql+=" Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id,)
    sql+=" order by title"
    res = GetAll(sql) #,debug=True
    txt+="""<table class='table table-bordered table-hover'>
            <tr><th width=100>ID</td><th>Title</td><th width=100>Status</td><th width=100>Progress</td></tr>"""
    for r in res:
        txt+="""<tr><td><a class="btn btn-primary" href='/prj/{0}'>Go !</a> {0}</td>
        <td>{1}</td>
        <td>{2}</td>
        <td>{3}</td>
        </tr>""".format(*r)
    txt+="</table>"

    return PrintInCharte(txt)

######################################################################################################################
def GetFieldList(Prj):
    fieldlist=collections.OrderedDict()
    fieldlist["orig_id"]="Image Name"
    objmap=DecodeEqualList(Prj.mappingobj)
    for v in ('objtime','depth_min','depth_max'):
        objmap[v]=v
    #fieldlist fait le mapping entre le nom fonctionnel et le nom à affiche
    # cette boucle permet de faire le lien avec le nom de la colonne (si elle existe.
    for field,dispname in DecodeEqualList(Prj.classiffieldlist).items():
        for ok,on in objmap.items():
            if field==on :
                fieldlist[ok]=dispname
    fieldlist["classif_auto_score"]="Score"
    return fieldlist

######################################################################################################################
@app.route('/prj/<int:PrjId>')
@login_required
def indexPrj(PrjId):
    data={ 'ipp':str(current_user.GetPref('ipp',100))
          ,'zoom':str(current_user.GetPref('zoom',100))
          ,'sortby':current_user.GetPref('sortby',"")
          ,'dispfield':current_user.GetPref('dispfield',"")
          ,'sortorder':current_user.GetPref('sortorder',"")
          ,'statusfilter':current_user.GetPref('statusfilter',"")
          ,'magenabled':str(current_user.GetPref('magenabled',1))
          ,'popupenabled':str(current_user.GetPref('popupenabled',1))
          }
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        flash("Project doesn't exists",'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(0): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot view this project','error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    g.Projid=Prj.projid
    fieldlist=GetFieldList(Prj)
    data["fieldlist"]=fieldlist
    data["sortlist"]=collections.OrderedDict({"":""})
    for k,v in fieldlist.items():data["sortlist"][k]=v
    data["sortlist"]["classifname"]="Category Name"
    data["sortlist"]["random_value"]="Random"
    data["sortlist"]["classif_when"]="Validation date"
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
    classiftab=GetClassifTab(Prj)
    g.ProjectTitle=Prj.title
    g.headmenu = []
    g.headmenu.append(("/prj/%d"%(PrjId,),"Project home/Annotation"))
    g.headmenu.append(("/prjcm/%d"%(PrjId,),"Show Confusion Matrix"))
    g.headmenu.append(("","SEP"))
    if g.PrjManager:
        g.headmenu.append(("/Task/Create/TaskImport?p=%d"%(PrjId,),"Import data"))
        g.headmenu.append(("/Task/Create/TaskClassifAuto?p=%d"%(PrjId,),"Automatic classification"))
        g.headmenu.append(("/prjPurge/%d"%(PrjId,),"Erase Objects"))
    appli.AddTaskSummaryForTemplate()
    filtertab=getcommonfilters()
    return render_template('project/projectmain.html',top="",lefta=classiftab,leftb=filtertab
                           ,right=right,data=data,projid=PrjId)

######################################################################################################################
@app.route('/prj/LoadRightPane', methods=['GET', 'POST'])
@login_required
def LoadRightPane():
    # récupération des parametres d'affichage
    ipp=int(gvp("ipp","10"))
    zoom=int(gvp("zoom","100"))
    pageoffset=int(gvp("pageoffset","0"))
    sortby=gvp("sortby","")
    sortorder=gvp("sortorder","")
    dispfield=gvp("dispfield","")
    statusfilter=gvp("statusfilter","")
    magenabled=gvp("magenabled","0")
    popupenabled=gvp("popupenabled","0")
    PrjId=gvp("projid")
    # dispfield=" dispfield_orig_id dispfield_n07"
    # on sauvegarde les parametres dans le profil utilisateur
    if current_user.SetPref("ipp",ipp) + current_user.SetPref("zoom",zoom)+ current_user.SetPref("sortby",sortby)\
            + current_user.SetPref("sortorder",sortorder)+ current_user.SetPref("dispfield",dispfield) \
            + current_user.SetPref("statusfilter",statusfilter)+ current_user.SetPref("magenabled",magenabled)\
            + current_user.SetPref("popupenabled",popupenabled)>0:
        database.ExecSQL("update users set preferences=%s where id=%s",(current_user.preferences,current_user.id),True)
        user_datastore.ClearCache()
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    fieldlist=GetFieldList(Prj)
    fieldlist.pop('orig_id','')
    t=["<a name='toppage'/>"]
    sqlparam={'projid':gvp("projid")}
    sql="""select o.objid,t.name taxoname,o.classif_qual,u.name classifwhoname,i.file_name
  ,i.height,i.width,i.thumb_file_name,i.thumb_height,i.thumb_width
  ,o.depth_min,o.depth_max,s.orig_id samplename,o.objdate,o.objtime
  ,o.latitude,o.orig_id,o.imgcount"""
    for k in fieldlist.keys():
        sql+=",o."+k+" as extra_"+k
    sql+=""" from objects o
Join images i on o.img0id=i.imgid
left JOIN taxonomy t on o.classif_id=t.id
LEFT JOIN users u on o.classif_who=u.id
LEFT JOIN  samples s on o.sampleid=s.sampleid
where o.projid=%(projid)s
"""
    if gvp("taxo")!="":
        sql+=" and o.classif_id=%(taxo)s "
        sqlparam['taxo']=gvp("taxo")
    if gvp("statusfilter")!="":
        sql+=" and classif_qual"
        if gvp("statusfilter")=="NV":
            sql+="!='V'"
        elif gvp("statusfilter")=="NVM":
            sql+="='V' and classif_who!="+str(current_user.id)
        elif gvp("statusfilter")=="VM":
            sql+="='V' and classif_who="+str(current_user.id)
        elif gvp("statusfilter")=="U":
            sql+=" is null "
        else:
            sql+="='"+gvp("statusfilter")+"'"

    if gvp("MapN")!="" and gvp("MapW")!="" and gvp("MapE")!="" and gvp("MapS")!="":
        sql+=" and o.latitude between %(MapS)s and %(MapN)s and o.longitude between %(MapW)s and %(MapE)s  "
        sqlparam['MapN']=gvp("MapN")
        sqlparam['MapW']=gvp("MapW")
        sqlparam['MapE']=gvp("MapE")
        sqlparam['MapS']=gvp("MapS")

    if gvp("depthmin")!="" and gvp("depthmax")!="" :
        sql+=" and o.depth_min between %(depthmin)s and %(depthmax)s and o.depth_max between %(depthmin)s and %(depthmax)s  "
        sqlparam['depthmin']=gvp("depthmin")
        sqlparam['depthmax']=gvp("depthmax")

    sqlcount="select count(*) from ("+sql+") q"
    nbrtotal=GetAll(sqlcount,sqlparam,False)[0][0]
    pagecount=math.ceil(nbrtotal/ipp)
    if sortby=="classifname":
        sql+=" order by t.name "+sortorder
    elif sortby!="":
        sql+=" order by o."+sortby+" "+sortorder
    else:
        sql+=" order by o.orig_id"
    sql+=" Limit %d offset %d "%(ipp,pageoffset*ipp)
    res=GetAll(sql,sqlparam,False)
    trcount=1
    LineStart=""
    if Prj.CheckRight(1): # si annotateur on peut sauver les changements.
        t.append("""<span id=SpanSelectAll style="background:#FFFF00;">[Select All]</span> <button class='btn btn-primary btn-xs' onclick='SavePendingChanges();'><span class='glyphicon glyphicon-floppy-open' /> Save changed annotations </button>
        <span id=PendingChanges2 class=PendingChangesClass style="font-size:12px;"></span>""")
        LineStart="<td class=linestart>&gt;<br>&gt;<br>&gt;<br></td>"
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
        width=origwidth*zoom//100
        height=origheight*zoom//100
        if max(width,height)<20: # en dessous de 20 px de coté on ne fait plus le scaling
            if max(origwidth,origheight)<20:
                width=origwidth   # si l'image originale est petite on l'affiche telle quelle
                height=origheight
            elif max(origwidth,origheight)==origwidth:
                width=20
                height=origheight*20//origwidth
                if height<1 : height=1
            else:
                height=20
                width=origwidth*20//origheight
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
            t.append("</tr></table><table class=imgtab><tr id=tr%d>%s"%(trcount,LineStart))
            WidthOnRow=0
        cellwidth=width+22
        # Met la fenetre de zoon la ou il y plus de place, sachant qu'elle fait 400px et ne peut donc pas être callée à gauche des premieres images.
        if (WidthOnRow+cellwidth)>(PageWidth/2):
            pos='left'
        else: pos='right'
        #Si l'image affiché est plus petite que la miniature, afficher la miniature.
        if thumbwidth is None or thumbwidth<width or thumbfilename is None: # sinon (si la miniature est plus petite que l'image à afficher )
            thumbfilename=filename # la miniature est l'image elle même

        txt="<td width={3}><img class='lazy' id=I{4} data-src='/vault/{6}' data-zoom-image='{0}' width={1} height={2} pos={5}>"\
            .format(filename,width,height,cellwidth,r['objid'],pos,thumbfilename)
        # Génération de la popover qui apparait pour donner quelques détails sur l'image
        if popupenabled=="1":
            poptitletxt="<p style='color:black;'>%s"%(r['orig_id'],)
            poptxt="<p style='white-space: nowrap;color:black;'>cat. %s"%(r['taxoname'],)
            if r[3]!="":
                poptxt+="<br>By %s"%(r[3])
            for k,v in fieldlist.items():
                poptxt+="<br>%s : %s"%(v,ScaleForDisplay(r["extra_"+k]))
            poptxt+="<br>Sample : "+r['samplename']
            popattribute="data-title=\"{0}\" data-content=\"{1}\"".format(poptitletxt,poptxt)
        else: popattribute=""
        # Génération du texte sous l'image qui contient la taxo + les champs à afficher
        bottomtxt=""
        if 'orig_id' in dispfield:
            bottomtxt+="<br>%s"%(r['orig_id'],)
        for k,v in fieldlist.items():
            if k in dispfield:
                bottomtxt+="<br>%s : %s"%(v,ScaleForDisplay(r["extra_"+k]))
        txt+="<div class='subimg {1}' {2}><span class=taxo >{0}</span>{3}<div class=ddet><span class=ddets>View {4}</div></div>"\
            .format(r['taxoname'],GetClassifQualClass(r['classif_qual']),popattribute,bottomtxt
                    ,"(%d)"%(r['imgcount'],) if r['imgcount'] is not None and r['imgcount']>1 else "")
        txt+="</td>"

        WidthOnRow+=max(cellwidth,80) # on ajoute au moins 80 car avec les label c'est rarement moins
        t.append(txt)

    t.append("</tr></table>")
    if Prj.CheckRight(1): # si annotateur on peut sauver les changements.
        t.append("""<span id=PendingChanges class=PendingChangesClass></span><br>
        <button class='btn btn-primary btn-sm' onclick='SavePendingChanges();'><span class='glyphicon glyphicon-floppy-open' /> Save changed annotations </button>
        <button class='btn btn-success btn-sm' onclick='ValidateAll();'><span class='glyphicon glyphicon-ok' /> Save changed annotations &amp; Validate all objects in page</button>
        <button class='btn btn-success btn-sm' onclick='ValidateAll(1);' title="Save changed annotations , Validate all objects in page &amp; Go to Next Page"><span class='glyphicon glyphicon-arrow-right' /> Save, Validate all &amp; Go to Next Page</button>
        """)
    # Gestion de la navigation entre les pages
    if pagecount>1 or pageoffset>0:
        t.append("<p align=center> Page %d/%d - Go to page : "%(pageoffset+1,pagecount))
        if pageoffset>0:
            t.append("<a href='#toppage' onclick='gotopage(%d);'>&lt;</a>"%(pageoffset-1))
        for i in range(0,pagecount-1,math.ceil(pagecount/20)):
            t.append("<a href='#toppage' onclick='gotopage(%d);'>%d</a> "%(i,i+1))
        t.append("<a href='#toppage' onclick='gotopage(%d);'>%d</a>"%(pagecount-1,pagecount))
        if pageoffset<pagecount-1:
            t.append("<a href='#toppage' onclick='gotopage(%d);'>&gt;</a>"%(pageoffset+1))
        t.append("</p>")
    t.append("""
    <script>
        PostAddImages();
    </script>""")
    return "\n".join(t)

######################################################################################################################
def GetClassifTab(Prj):
    if Prj.initclassiflist is None:
        InitClassif="0" # pour être sur qu'il y a toujours au moins une valeur
    else:
        InitClassif=Prj.initclassiflist
    InitClassif=", ".join(["("+x.strip()+")" for x in InitClassif.split(",") if x.strip()!=""])
    sql="""select t.id,t.name taxoname,Nbr,NbrNotV
    from (  SELECT    o.classif_id,   c.id,count(classif_id) Nbr,count(case when classif_qual='V' then NULL else o.classif_id end) NbrNotV
        FROM (select * from objects where projid=%(projid)s) o
        FULL JOIN (VALUES """+InitClassif+""") c(id) ON o.classif_id = c.id
        GROUP BY classif_id, c.id
      ) o
    JOIN taxonomy t on coalesce(o.classif_id,o.id)=t.id
    order by t.name       """
    param={'projid':Prj.projid}
    res=GetAll(sql,param,False)
    return render_template('project/classiftab.html',res=res)

######################################################################################################################
@app.route('/prjGetClassifTab/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prjGetClassifTab(PrjId):
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        return "Project doesn't exists"
    g.PrjAnnotate=g.PrjManager=Prj.CheckRight(2)
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
    txt=""
    if gvp("objlist")=="":
        txt+="""<form action=? method=post>
        Enter the list of internal object id you want to delete. Or DELETEALL to erase all object of this project.<br>
        <textarea name=objlist cols=15 rows=20></textarea><br>
        <input type="submit" class="btn btn-danger" value='ERASE THESES OBJECTS !!! IRREVERSIBLE !!!!!'>
        <a href ="/prj/{0}" class="btn btn-success">Cancel, Back to project home</a>
        </form>
        """.format(PrjId)
    else:
        if gvp("objlist")=="DELETEALL":
            sqlsi="select file_name,thumb_file_name from images i,objects o where o.objid=i.objid and o.projid={0}".format(PrjId)
            sqldi="delete from images i using objects o where o.objid=i.objid and o.projid={0}".format(PrjId)
            sqldoh="delete from objectsclassifhisto i using objects o where o.objid=i.objid and o.projid={0}".format(PrjId)
            sqldo="delete from objects where projid={0}".format(PrjId)
            objs=()
            SqlParam={}
        else:
            sqlsi="select file_name,thumb_file_name from images i,objects o where o.objid=i.objid and o.projid={0} and o.objid = any(%(objs)s)".format(PrjId)
            sqldi="delete from images i using objects o where o.objid=i.objid and o.projid={0} and o.objid = any(%(objs)s)".format(PrjId)
            sqldoh="delete from objectsclassifhisto i using objects o where o.objid=i.objid and o.projid={0} and o.objid = any(%(objs)s)".format(PrjId)
            sqldo="delete from objects where projid={0} and objid = any(%(objs)s)".format(PrjId)
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
        txt+="Deleted %d Objects, %d ObjectHisto, %d Images in Database and %d files"%(no,noh,ni,nbrfile)

    return PrintInCharte(txt+ ("<br><br><a href ='/prj/{0}'>Back to project home</a>".format(PrjId)))