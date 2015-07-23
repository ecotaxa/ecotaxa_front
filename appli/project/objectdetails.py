from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections
from appli.database import GetAll,GetClassifQualClass,db



@app.route('/objectdetails/<int:objid>')
@login_required
def objectdetails(objid):
    #récuperation et ajustement des dimensions de la zone d'affichage
    try:
        PageWidth=int(gvg("w"))-40 # on laisse un peu de marge à droite et la scroolbar
        if PageWidth<200 : PageWidth=20000
        WindowHeight=int(gvg("h"))-40 # on laisse un peu de marge en haut
        if WindowHeight<200 : WindowHeight=20000
    except:
        PageWidth=20000;
        WindowHeight=20000;

    obj=database.Objects.query.filter_by(objid=objid).first()
    t=[]
    t.append("Object #{0} , Original Object ID : {1}".format(objid,obj.orig_id))
    Prj=obj.project
    if not Prj.CheckRight(0): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot view this project','error')
        return PrintInCharte("<a href=/>Back to home</a>")
    t.append("<br>Part of project %s"%(Prj.title))
    t.append("<br>Classification : %s (%s)"%(obj.classif.name,database.ClassifQual.get(obj.classif_qual,"???")))
    if obj.classiffier is not None:
        t.append(" by %s (%s) "%(obj.classiffier.name,obj.classiffier.email))
        if obj.classif_when is not None:
            t.append(" on %s "%(obj.classif_when.strftime("%Y-%m-%d %H:%M")))

    obj.images.sort(key=lambda x: x.imgrank)
    t.append('<div id=DetailsImgTabs><ul class="nav nav-tabs" role="tablist">')
    for img in obj.images:
        t.append('<li role="presentation" class="{1}"><a href="#tab{0}" aria-controls="tab{0}" role="tab" data-toggle="tab">Rank {0}</a></li>'.format(img.imgrank+1,"active" if img.imgrank==0 else ""))
    t.append("</ul><div class='tab-content'>")
    for img in obj.images:
        # On limite les images pour qu'elles tiennent toujours dans l'écran
        width=img.width
        height=img.height
        if width>PageWidth:
            width=PageWidth
            height=math.trunc(img.height*width/img.width)
            if height==0: height=1
        if height>WindowHeight:
            height=WindowHeight
            width=math.trunc(img.width*height/img.height)
            if width==0: width=1
        t.append('<br><div role="tabpanel" class="tab-pane {2}" id="tab{0}"><img class=lazy id=img{0} src=/vault/{1} data-zoom-image={1} width={3} height={4} pos=right></div>'
                 .format(img.imgrank+1,img.file_name,"active" if img.imgrank==0 else "",width,height))
    t.append("""</div></div>
    """)
    # <script>
    # // Marche pas car les images sont superposés dans le tab et du coup c'est tout le temps la derniere image
    # $(document).ready(function() {
    #     jQuery('#DetailsImgTabs a').on('shown.bs.tab', function (e) {
    #         console.log(e);
    #          jQuery(jQuery(e.target).attr('href')).find('img.lazy').Lazy({bind: 'event',afterLoad: function(element) {
    #                     AddZoom(element);}});
    #     });
    #     // Add Zoom , ne marche pas car pas encore posisionné dans les tab
    #     //jQuery('#DetailsImgTabs img').each(function(element) {AddZoom($(this));});
    # });
    # </script>


    t.append("""<div><ul class="nav nav-tabs" role="tablist">
    <li role="presentation" class="active"><a href="#tabdobj" aria-controls="tabdobj" role="tab" data-toggle="tab"> Object details</a></li>
    <li role="presentation" ><a href="#tabdsample" aria-controls="tabdsample" role="tab" data-toggle="tab"> Sample details</a></li>
    <li role="presentation" ><a href="#tabdacquis" aria-controls="tabdacquis" role="tab" data-toggle="tab"> Acquisition details</a></li>
    <li role="presentation" ><a href="#tabdprocess" aria-controls="tabdprocess" role="tab" data-toggle="tab"> Processing details</a></li>
    </ul>
    <div class="tab-content">
    <div role="tabpanel" class="tab-pane active" id="tabdobj">
    <table class='table table-bordered'><tr>""")
    cpt=0
    for k,v in  collections.OrderedDict(sorted(DecodeEqualList(Prj.mappingobj).items())).items():
        if cpt>0 and cpt%4==0:
            t.append("</tr><tr>")
        cpt+=1
        t.append("<td>{0}</td><td>{1}</td>".format(v,ScaleForDisplay(getattr(obj,k,"???"))))
    t.append("</tr></table></div>")

    for r in (("Sample","mappingsample","sample") ,("Acquisition","mappingacq","acquis"),("Processing","mappingprocess","process") ):
        t.append('<div role="tabpanel" class="tab-pane" id="tabd'+r[2]+'">'+r[0]+" details :<table class='table table-bordered'><tr>")
        cpt=0
        for k,v in  collections.OrderedDict(sorted(DecodeEqualList(getattr(Prj,r[1])).items())).items():
            if cpt>0 and cpt%4==0:
                t.append("</tr><tr>")
            cpt+=1
            t.append("<td>{0}</td><td>{1}</td>".format(v,ScaleForDisplay(getattr(getattr(obj,r[2]),k,"???"))))
        t.append("</tr></table></div>")
    t.append("</div></div>")

    return PrintInCharte("\n".join(t))