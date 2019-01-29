from flask import Blueprint, render_template, g, flash,request,url_for,json,Response
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,ntcv,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage,nonetoformat,XSSEscape
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections,html,urllib.parse,datetime
from appli.database import GetAll,GetClassifQualClass,db



@app.route('/objectdetails/<int:objid>')
def objectdetails(objid):
    #récuperation et ajustement des dimensions de la zone d'affichage
    try:
        PageWidth=int(gvg("w"))-40 # on laisse un peu de marge à droite et la scroolbar
        if PageWidth<200 : PageWidth=20000
        WindowHeight=int(gvg("h"))-40 # on laisse un peu de marge en haut
        if WindowHeight<200 : WindowHeight=20000
    except:
        PageWidth=20000
        WindowHeight=20000

    obj=database.Objects.query.filter_by(objid=objid).first()
    t=list()
    # Dans cet écran on utilise ElevateZoom car sinon en mode popup il y a conflit avec les images sous la popup
    t.append("<script src='/static/jquery.elevatezoom.js'></script>")
    Prj=obj.project
    if Prj.visible==False and  not Prj.CheckRight(0): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot view this project','error')
        return PrintInCharte("<a href=/>Back to home</a>")
    g.Projid=Prj.projid
    PrjManager=[(m.memberrel.email,m.memberrel.name) for m in Prj.projmembers  if m.privilege=='Manage']
    t.append("<p>Project: <b><a href='/prj/%d'>%s</a></b> (managed by : %s)"%(Prj.projid,XSSEscape(Prj.title)
                     ,",".join(("<a href ='mailto:%s'>%s</a>"%m for m in PrjManager))))
    if len(PrjManager)>0:
        t.append("<br>To report a mistake, contact <a href ='mailto:{0}?subject=Ecotaxa%20mistake%20notification&body={2}'>{1}</a>".format(
            PrjManager[0][0],PrjManager[0][1],urllib.parse.quote("Hello,\n\nI have discovered a mistake on this page "+request.base_url+"\n")))
# //window.location="mailto:?subject=Ecotaxa%20page%20share&body="+encodeURIComponent("Hello,\n\nAn Ecotaxa user want share this page with you \n"+url);
    t.append("</p><p>Classification :")
    if obj.classif:
        t.append("<br>&emsp;<b>%s</b>"%XSSEscape(obj.classif.display_name))
        TaxoHierarchie=(r[0] for r in GetAll("""WITH RECURSIVE rq(id,name,parent_id) as ( select id,name,parent_id FROM taxonomy where id =%(taxoid)s
                        union
                        SELECT t.id,t.name,t.parent_id FROM rq JOIN taxonomy t ON t.id = rq.parent_id )
                        select name from rq""",{"taxoid":obj.classif.id}))
        t.append("<br>&emsp;"+ (" &lt; ".join(TaxoHierarchie))+" (id=%s)"%obj.classif_id )
    else:
        t.append("<br>&emsp;<b>Unknown</b>")
    if obj.classiffier is not None:
        t.append("<br>&emsp;%s "%(database.ClassifQual.get(obj.classif_qual,"To be classified")))
        t.append(" by %s (%s) "%(obj.classiffier.name,obj.classiffier.email))
        if obj.classif_when is not None:
            t.append(" on %s "%(obj.classif_when.strftime("%Y-%m-%d %H:%M")))
    t.append("</p>")
    if obj.objfrel.object_link is not None:
        t.append("<p>External link :<a href='{0}' target=_blank> {0}</a></p>".format(obj.objfrel.object_link))
    t.append("<table><tr><td valign=top>Complementaty information <a href='javascript:gotocommenttab();' > ( edit )</a>: </td><td> <span id=spancomplinfo> {0}</span></td></tr></table>".format(ntcv( obj.complement_info).replace('\n','<br>\n')))
    # On affiche la liste des images, en selectionnant une image on changera le contenu de l'image Img1 + Redim
    # l'approche avec des onglets de marchait pas car les images sont superposées
    obj.images.sort(key=lambda x: x.imgrank)
    t.append("""<p>Image list : """)
    for img in obj.images:
        (width,height)=ComputeLimitForImage(img.width,img.height,PageWidth,WindowHeight)
        if img.thumb_file_name:
            minifile=img.thumb_file_name
            (miniwidth,miniheight)=ComputeLimitForImage(img.thumb_width,img.thumb_height,30,30)
        else:
            minifile=img.file_name
            (miniwidth,miniheight)=ComputeLimitForImage(img.width,img.height,30,30)
        t.append("""<a href="javascript:SwapImg1('{1}',{2},{3});" >{0} <img src=/vault/{4} width={5} height={6}></a> """
                 .format(img.imgrank+1,img.file_name,width,height,minifile,miniwidth,miniheight))
    # Ajout de la 1ère image
    (width,height)=ComputeLimitForImage(obj.images[0].width,obj.images[0].height,PageWidth,WindowHeight)
    t.append("</p><p><img id=img1 src=/vault/{1} data-zoom-image=/vault/{1} width={2} height={0}></p>"
             .format(height,obj.images[0].file_name,width))
    # Affichage de l'onglet de classification
    if Prj.CheckRight(1):
        t.append("""
<table><tr><td>Set a new classification :</td>
 <td style="width: 230px;">
     <div class="input-group">
       <select id="taxolbpop" name="taxolbpop" style="width: 200px" class='taxolb' > </select>""")
        if gvg("ajax","0")=="0":
            t.append("""<span class="input-group-btn">
                    <button class="btn btn-default btn-sm" type="button"  data-toggle="modal" data-target="#TaxoModal" data-mytargetid="taxolbpop" title="Search on Taxonomy Tree">
                        <span id=OpenTaxoLB class="glyphicon glyphicon-th-list" aria-hidden="true"/></button>
                    </span>""")
        else: t.append("<br>")
        t.append("""</div><!-- /input-group -->
 <span id=PendingChangesPop></span></td><td width=30px></td><td valign=top>
    <button type="button" class="btn btn-success btn-xs" onclick="Save1Object('V');">Save as Validated</button>
    <button type="button" class="btn btn-warning btn-xs" onclick="Save1Object('D');">Save as dubious</button>
    <button id=btenableedit type="button" class="btn btn-gris btn-xs" onclick="EnableEdit();">Enable Editing</button>
    <button type="button" class="btn btn-default btn-xs"  onclick="$('#PopupDetails').modal('hide');">Close</button>
    </td></tr></table>
    """)
    # Ajout des Onglets sous l'image
    t.append("""<br><div><ul class="nav nav-tabs" role="tablist">
    <li role="presentation" class="active"><a href="#tabdobj" aria-controls="tabdobj" role="tab" data-toggle="tab"> Object details</a></li>
    <li role="presentation" ><a href="#tabdsample" aria-controls="tabdsample" role="tab" data-toggle="tab"> Sample details</a></li>
    <li role="presentation" ><a href="#tabdacquis" aria-controls="tabdacquis" role="tab" data-toggle="tab"> Acquisition details</a></li>
    <li role="presentation" ><a href="#tabdprocessrel" aria-controls="tabdprocess" role="tab" data-toggle="tab"> Processing details</a></li>
    <li role="presentation" ><a href="#tabdclassiflog" aria-controls="tabdclassiflog" role="tab" data-toggle="tab">Classification change log</a></li>
    <li role="presentation" ><a href="#tabdmap" aria-controls="tabdmap" role="tab" data-toggle="tab" id=atabdmap style="background: #5CB85C;color:white;">Map</a></li>
    """)
    if Prj.CheckRight(1):
        t.append("""<li role="presentation" ><a id=linktabdaddcomments href="#tabdaddcomments" aria-controls="tabdaddcomments" role="tab" data-toggle="tab">Edit complementary informations</a></li>""")
    if obj.classif_auto:
        classif_auto_name=obj.classif_auto.name
        if obj.classif_auto_score:
            classif_auto_name+= " (%0.3f)"%(obj.classif_auto_score,)
    else: classif_auto_name=''
    t.append("""</ul>
    <div class="tab-content">
    <div role="tabpanel" class="tab-pane active" id="tabdobj">
    <table class='table table-bordered table-condensed' data-table='object'><tr>
    <td style=' background-color: #f2f2f2;' data-edit='longitude'><b>longitude</td><td>{0}</td>
    <td style=' background-color: #f2f2f2;' data-edit='latitude'><b>latitude</td><td>{1}</td>
    <td style=' background-color: #f2f2f2;' data-edit='objdate'><b>Date</td><td>{2}</td>
    <td style=' background-color: #f2f2f2;'><b>Time (daytime)</td><td>{3} ({10})</td>
    </tr><tr><td style=' background-color: #f2f2f2;' data-edit='depth_min'><b>Depth min</td><td>{4}</td>
    <td style=' background-color: #f2f2f2;' data-edit='depth_max'><b>Depth max</td><td>{5}</td>
    <td><b>Classif auto</td><td>{6}</td><td><b>Classif auto when</td><td>{7}</td>
    </tr><tr><td><b>Object #</td><td>{8}</td>
    <td data-edit='orig_id'><b>Original Object ID</td><td colspan=5>{9}</td></tr><tr>""".format(nonetoformat(obj.longitude,'.5f'),nonetoformat(obj.latitude,'.5f'),obj.objdate,obj.objtime
                        ,obj.depth_min,obj.depth_max
                        ,classif_auto_name,obj.classif_auto_when,objid,obj.objfrel.orig_id,database.DayTimeList.get(obj.sunpos,'?') ))
    cpt=0
    # Insertion des champs object
    for k,v in  collections.OrderedDict(sorted(DecodeEqualList(Prj.mappingobj).items())).items():
        if cpt>0 and cpt%4==0:
            t.append("</tr><tr>")
        cpt+=1
        t.append("<td data-edit='{2}'><b>{0}</td><td>{1}</td>".format(v,ScaleForDisplay(getattr(obj.objfrel,k,"???")),k))
    t.append("</tr></table></div>")
    # insertion des champs Sample, Acquisition & Processing dans leurs onglets respectifs
    for r in (("Sample","mappingsample","sample") ,("Acquisition","mappingacq","acquis"),("Processing","mappingprocess","processrel") ):
        t.append('<div role="tabpanel" class="tab-pane" id="tabd'+r[2]+'">'+r[0]+" details :<table class='table table-bordered table-condensed'  data-table='"+r[2]+"'><tr>")
        cpt=0
        if getattr(obj,r[2]):
            if r[2]=="sample":
                t.append("<td data-edit='orig_id'><b>{0}</td><td colspan=3>{1}</td><td data-edit='longitude'><b>{2}</td><td>{3}</td><td data-edit='latitude'><b>{4}</td><td>{5}</td></tr><tr>"
                         .format("Original ID",ScaleForDisplay(obj.sample.orig_id),
                                 "longitude",ScaleForDisplay(obj.sample.longitude),
                                 "latitude",ScaleForDisplay(obj.sample.latitude),))
            elif r[2] == "acquis":
                t.append(
                    "<td data-edit='orig_id'><b>{0}</td><td colspan=3>{1}</td><td data-edit='instrument'><b>{2}</td><td>{3}</td></tr><tr>"
                    .format("Original ID", ScaleForDisplay(obj.acquis.orig_id),
                            "Instrument", ScaleForDisplay(obj.acquis.instrument),
                             ))
            else:
                t.append("<td data-edit='orig_id'><b>{0}</td><td>{1}</td></tr><tr>"
                         .format("Original ID.",ScaleForDisplay(getattr(getattr(obj,r[2]),"orig_id","???"))))
            for k,v in  collections.OrderedDict(sorted(DecodeEqualList(getattr(Prj,r[1])).items())).items():
                if cpt>0 and cpt%4==0:
                    t.append("</tr><tr>")
                cpt+=1
                t.append("<td data-edit='{2}'><b>{0}</td><td>{1}</td>".format(v,ScaleForDisplay(getattr(getattr(obj,r[2]),k,"???")),k))
            if r[2]=="sample":
                t.append("</tr><tr><td><b>{0}</td><td colspan=7>{1}</td></tr><tr>"
                         .format("Dataportal Desc.",ScaleForDisplay(html.escape(ntcv(obj.sample.dataportal_descriptor)))))
        else:
            t.append("<td>No {0}</td>".format(r[0]))
        t.append("</tr></table></div>")

    # Affichage de l'historique des classification
    t.append("""<div role="tabpanel" class="tab-pane" id="tabdclassiflog">
Current Classification : Quality={} , date={}    
    <table class='table table-bordered table-condensed'><tr>
    <td>Date</td><td>Type</td><td>Taxo</td><td>Author</td><td>Quality</td></tr>""".format(obj.classif_qual,obj.classif_when))
    Histo=GetAll("""SELECT to_char(classif_date,'YYYY-MM-DD HH24:MI:SS') datetxt,classif_type ,t.display_name as name,u.name username,classif_qual
  from objectsclassifhisto h
  left join taxonomy t on h.classif_id=t.id
  LEFT JOIN users u on u.id = h.classif_who
WHERE objid=%(objid)s
order by classif_date desc""",{"objid":objid},doXSSEscape=True)
    for r in Histo:
        t.append("<tr><td>"+("</td><td>".join([str(r[x]) if r[x] else "-" for x in ("datetxt","classif_type","name","username","classif_qual")])) +"</td></tr>")
    t.append("</table></div>")
    if Prj.CheckRight(1):
        t.append("""<div role="tabpanel" class="tab-pane" id="tabdaddcomments">
        <textarea id=compinfo rows=5 cols=120 autocomplete=off>%s</textarea><br>
        <button type="button" class='btn btn-primary' onclick="UpdateComment();">Save additional comment</button>
        <span id=ajaxresultcomment></span>
        """%(ntcv( obj.complement_info),))
        t.append("</div>")
    # Affichage de la carte
    t.append("""
    <div role="tabpanel" class="tab-pane" id="tabdmap">
<div id="map2" class="map2" style="width: 100%; height: 450px;">
  Displaying Map requires Internet Access to load map from https://server.arcgisonline.com
</div>""")

    t.append("</table></div>")
    t.append(render_template("common/objectdetailsscripts.html", Prj=Prj,
                             objid=objid,obj=obj))

    # En mode popup ajout en haut de l'écran d'un hyperlien pour ouvrir en fenete isolée
    # Sinon affichage sans lien dans la charte.
    if gvg("ajax","0")=="1":
        return """<table width=100% style='margin: 3px'><tr><td><a href='/objectdetails/{0}?w={1}&h={2}' target=_blank><b>Open in a separate window</b> (right click to copy link)</a>
        </td><td align='right'><button type="button" class="btn btn-default"  onclick="$('#PopupDetails').modal('hide');">Close</button>&nbsp;&nbsp;
        </td></tr></table><div style='margin: 0 5px;'>""".format(objid,gvg("w"),gvg("h"))+"\n".join(t)
    return PrintInCharte("<div style='margin-left:10px;'>"+"\n".join(t)+render_template('common/taxopopup.html'))

@app.route('/objectdetailsupdate/<int:objid>',  methods=['GET', 'POST'])
@login_required
def objectdetailsupdate(objid):
    request.form  # Force la lecture des données POST sinon il y a une erreur 504
    obj=database.Objects.query.filter_by(objid=objid).first()
    Prj=obj.project
    if not Prj.CheckRight(2): # Level 0 = Read, 1 = Annotate, 2 = Admin
        return '<span class="label label-danger">You cannot edit data on this project</span>'

    table=gvp("table")
    field= gvp("field")
    if table=="object":
        if hasattr(obj,field):
            target=obj
        elif hasattr(obj.objfrel, field):
            target = obj.objfrel
        else:
            return '<span class="label label-danger">Invalid field %s.%s</span>'%(table,field)
    elif table=="sample":
        target=obj.sample
    elif table=="acquis":
        target=obj.acquis
    elif table=="processrel":
        target=obj.processrel

    else:
        return '<span class="label label-danger">Invalid table %s</span>' % (table, )

    oldval=getattr(target, field)
    newval=gvp("newval")
    try:
        dbval=newval
        if field=="objdate":
            dbval=datetime.date(int(newval[0:4]), int(newval[5:7]), int(newval[8:10]))
        if dbval=="": dbval=None
        setattr(target, field,dbval)
        db.session.commit()
    except Exception as E:
        return '<span class="label label-danger">Data update error %s</span>' % (str(E)[0:100],)

    return "<span class='label label-success'>changed value '%s' by '%s'"%(oldval,newval)