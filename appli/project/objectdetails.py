from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,ntcv,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections,html
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
    t=list()
    # Dans cet écran on utilise ElevateZoom car sinon en mode popup il y a conflit avec les images sous la popup
    t.append("<script src='/static/jquery.elevatezoom.js'></script>")
    t.append("Object #{0} , Original Object ID : {1}".format(objid,obj.orig_id))
    Prj=obj.project
    if not Prj.CheckRight(0): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot view this project','error')
        return PrintInCharte("<a href=/>Back to home</a>")
    g.Projid=Prj.projid
    t.append("<br>Part of project %s"%(Prj.title,))
    t.append("<br>Classification : %s (%s)"%(obj.classif.name if obj.classif else "Unknown",database.ClassifQual.get(obj.classif_qual,"To be classified")))
    if obj.classiffier is not None:
        t.append(" by %s (%s) "%(obj.classiffier.name,obj.classiffier.email))
        if obj.classif_when is not None:
            t.append(" on %s "%(obj.classif_when.strftime("%Y-%m-%d %H:%M")))
    if obj.object_link is not None:
        t.append("<br>External link :<a href='{0}' target=_blank> {0}</a>".format(obj.object_link))
    # On affiche la liste des images, en selectionnant une image on changera le contenu de l'image Img1 + Redim
    # l'approche avec des onglets de marchait pas car les images sont superposées
    obj.images.sort(key=lambda x: x.imgrank)
    t.append("""<BR>Image list : """)
    for img in obj.images:
        (width,height)=ComputeLimitForImage(img.width,img.height,PageWidth,WindowHeight)
        t.append("""<a href="javascript:SwapImg1('{1}',{2},{3});" >Miniature {0}</a> """
                 .format(img.imgrank+1,img.file_name,width,height))
    # Ajout de la 1ère image
    (width,height)=ComputeLimitForImage(obj.images[0].width,obj.images[0].height,PageWidth,WindowHeight)
    t.append("<br><img id=img1 src=/vault/{1} data-zoom-image=/vault/{1} width={2} height={0}><br>"
             .format(height,obj.images[0].file_name,width))
    t.append("""<script>
    $("#img1").elevateZoom({scrollZoom : true});
    function SwapImg1(filename,width,height)    {
        $('#img1').attr("width",width);
        $('#img1').attr("height",height);
        $('#img1').data('elevateZoom').swaptheimage('/vault/'+filename, '/vault/'+filename);
    }
    </script>
    """)
    # Affichage de l'onglet de classification
    if Prj.CheckRight(1):
        t.append("""<script>
function Save1Object(classqual) {
    var classid=$("#taxolbpop").val();
    var objid='"""+str(objid)+"""';
    if(classid=='') {
        alert('Select a new category first');
        return;
    }
    req={changes:{},qual:classqual}
    req['changes'][objid]=classid;
    $("#PendingChangesPop").html('<span class="label label-info">Server update in progress...</span>');
    $("#PendingChangesPop").load("/prj/ManualClassif/"""+str(Prj.projid)+"""",req,function(){
        if ($("#PendingChangesPop").html().indexOf("Successfull")>0) {
            PendingChanges={}; // After successfull update no pending changes.
            if(classqual=='V')
                $('#I'+objid).parents('td').find('.subimg').attr('class','subimg status-validated');
            else
                $('#I'+objid).parents('td').find('.subimg').attr('class','subimg status-dubious');
            if($("#taxolbpop").text().trim()!="")
                $('#I'+objid).parents('td').find('.taxo').text($("#taxolbpop").text());
            $('#PopupDetails').modal('hide');
        }
    });
}
$(document).ready(function() {
    $("#taxolbpop").select2({
        ajax: {
            url: "/search/taxo",
            dataType: 'json',
            delay: 250,
            data: function (params) {  return { q: params.term, page: params.page };  },
            processResults: function (data, page) { return { results: data};  },
            cache: true
        },
        minimumInputLength: 3
    }); // Select2 Ajax
});
 </script>
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
    <button type="button" class="btn btn-success" onclick="Save1Object('V');">Save as Validated</button>
    <button type="button" class="btn btn-danger" onclick="Save1Object('D');">Save as dubious</button>
    <button type="button" class="btn btn-default"  onclick="$('#PopupDetails').modal('hide');">Close</button>
    </td></tr></table>
    """)
    # Ajout des Onglets sous l'image
    t.append("""<br><div><ul class="nav nav-tabs" role="tablist">
    <li role="presentation" class="active"><a href="#tabdobj" aria-controls="tabdobj" role="tab" data-toggle="tab"> Object details</a></li>
    <li role="presentation" ><a href="#tabdsample" aria-controls="tabdsample" role="tab" data-toggle="tab"> Sample details</a></li>
    <li role="presentation" ><a href="#tabdacquis" aria-controls="tabdacquis" role="tab" data-toggle="tab"> Acquisition details</a></li>
    <li role="presentation" ><a href="#tabdprocess" aria-controls="tabdprocess" role="tab" data-toggle="tab"> Processing details</a></li>
    <li role="presentation" ><a href="#tabdclassiflog" aria-controls="tabdclassiflog" role="tab" data-toggle="tab">Classification change log</a></li>""")
    t.append("""</ul>
    <div class="tab-content">
    <div role="tabpanel" class="tab-pane active" id="tabdobj">
    <table class='table table-bordered'><tr>
    <td><b>longitude</td><td>{0:.5f}</td><td><b>latitude</td><td>{1:.5f}</td><td><b>Date</td><td>{2}</td><td><b>Time</td><td>{3}</td>
    </tr><tr><td><b>Depth min</td><td>{4}</td><td><b>Depth max</td><td>{5}</td><td><b>Classif auto</td><td>{6}</td><td><b>Classif auto when</td><td>{7}</td>
    </tr><tr>""".format(obj.longitude,obj.latitude,obj.objdate,obj.objtime
                        ,obj.depth_min,obj.depth_max
                        ,obj.classif_auto.name+" (%0.3f)"%obj.classif_auto_score if obj.classif_auto else "",obj.classif_auto_when))
    cpt=0
    # Insertion des champs object
    for k,v in  collections.OrderedDict(sorted(DecodeEqualList(Prj.mappingobj).items())).items():
        if cpt>0 and cpt%4==0:
            t.append("</tr><tr>")
        cpt+=1
        t.append("<td><b>{0}</td><td>{1}</td>".format(v,ScaleForDisplay(getattr(obj,k,"???"))))
    t.append("</tr></table></div>")
    # insertion des champs Sample, Acquisition & Processing dans leurs onglets respectifs
    for r in (("Sample","mappingsample","sample") ,("Acquisition","mappingacq","acquis"),("Processing","mappingprocess","processrel") ):
        t.append('<div role="tabpanel" class="tab-pane" id="tabd'+r[2]+'">'+r[0]+" details :<table class='table table-bordered'><tr>")
        cpt=0
        if r[2]=="sample":
            t.append("<td><b>{0}</td><td>{1}</td><td><b>{2}</td><td>{3}</td><td><b>{4}</td><td>{5}</td></tr><tr>"
                     .format("Original ID",ScaleForDisplay(obj.sample.orig_id),
                             "longitude",ScaleForDisplay(obj.sample.longitude),
                             "latitude",ScaleForDisplay(obj.sample.latitude),))
            t.append("<td><b>{0}</td><td colspan=7>{1}</td></tr><tr>"
                     .format("Dataportal Desc.",ScaleForDisplay(html.escape(ntcv(obj.sample.dataportal_descriptor)))))
        else:
            t.append("<td><b>{0}</td><td>{1}</td></tr><tr>"
                     .format("Original ID.",ScaleForDisplay(getattr(getattr(obj,r[2]),"orig_id","???"))))
        for k,v in  collections.OrderedDict(sorted(DecodeEqualList(getattr(Prj,r[1])).items())).items():
            if cpt>0 and cpt%4==0:
                t.append("</tr><tr>")
            cpt+=1
            t.append("<td><b>{0}</td><td>{1}</td>".format(v,ScaleForDisplay(getattr(getattr(obj,r[2]),k,"???"))))
        t.append("</tr></table></div>")

    # Affichage de l'historique des classification
    t.append("""<div role="tabpanel" class="tab-pane" id="tabdclassiflog">
    <table class='table table-bordered'><tr>
    <td>Date</td><td>Type</td><td>Taxo</td><td>Author</td><td>Quality</td></tr>""")
    Histo=GetAll("""SELECT to_char(classif_date,'YYYY-MM-DD HH24:MI:SS') datetxt,classif_type ,t.name,u.name username,classif_qual
  from objectsclassifhisto h
  left join taxonomy t on h.classif_id=t.id
  LEFT JOIN users u on u.id = h.classif_who
WHERE objid=%(objid)s
order by classif_date desc""",{"objid":objid})
    for r in Histo:
        t.append("<tr><td>"+("</td><td>".join([str(x) if x else "-" for x in r])) +"</td></tr>")
    t.append("</table></div>")

    # En mode popup ajout en haut de l'écran d'un hyperlien pour ouvrir en fenete isolée
    # Sinon affichage sans lien dans la charte.
    if gvg("ajax","0")=="1":
        return """<table width=100%><tr><td><a href='/objectdetails/{0}?w={1}&h={2}' target=_blank><b>Open in a separate window</b> (right click to copy link)</a>
        </td><td align='right'><button type="button" class="btn btn-default"  onclick="$('#PopupDetails').modal('hide');">Close</button>&nbsp;&nbsp;
        </td></tr></table>""".format(objid,gvg("w"),gvg("h"))+"\n".join(t)
    return PrintInCharte("\n".join(t)+render_template('common/taxopopup.html'))