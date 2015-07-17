#TODO Ajouter colonne InitClassif
#TODO Ajouter colonne Champs affichable du projet
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections
from appli.database import GetAll,GetClassifQualClass,db

@app.route('/prj/')
@login_required
def indexProjects():
    txt = "<h3>Select your Project</h3>"
    sql="select p.projid,title,status,pctvalidated from projects p"
    if not current_user.has_role(database.AdministratorLabel):
        sql+=" Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id)
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

def GetFieldList(Prj):
    fieldlist=collections.OrderedDict()
    fieldlist["orig_id"]="Image Name"
    objmap=DecodeEqualList(Prj.mappingobj)
    #fieldlist fait le mapping entre le nom fonctionnel et le nom à affiche
    # cette boucle permet de faire le lien avec le nom de la colonne (si elle existe.
    for field,dispname in DecodeEqualList(Prj.classiffieldlist).items():
        for ok,on in objmap.items():
            if field==on :
                fieldlist[ok]=dispname
    return fieldlist

@app.route('/prj/<int:PrjId>')
def indexPrj(PrjId):
    data={ 'ipp':str(current_user.GetPref('ipp',100))
          ,'zoom':str(current_user.GetPref('zoom',100))
          ,'sortby':current_user.GetPref('sortby',"")
          ,'dispfield':current_user.GetPref('dispfield',"")
          ,'sortorder':current_user.GetPref('sortorder',"")
          ,'magenabled':str(current_user.GetPref('magenabled',1))
          }
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    fieldlist=GetFieldList(Prj)
    data["fieldlist"]=fieldlist
    data["sortlist"]=collections.OrderedDict({"":""})
    for k,v in fieldlist.items():data["sortlist"][k]=v
    data["sortlist"]["random_value"]="Random"

    right='dodefault'
    classiftab=GetClassifTab(PrjId)
    g.headmenu = []
    g.headmenu.append(("/prj/%d"%(PrjId,),"Project home/Annotation"))
    g.headmenu.append(("","SEP"))
    if Prj.CheckRight(2):
        g.headmenu.append(("/Task/Create/TaskImport?p=%d"%(PrjId,),"Import data"))


    return render_template('project/projectmain.html',top="",lefta=classiftab
                           ,right=right,data=data,projid=PrjId)

@app.route('/prj/LoadRightPane', methods=['GET', 'POST'])
def LoadRightPane():
    # récupération des parametres d'affichage
    ipp=int(gvp("ipp","10"))
    zoom=int(gvp("zoom","100"))
    sortby=gvp("sortby","")
    sortorder=gvp("sortorder","")
    dispfield=gvp("dispfield","")
    PrjId=gvp("projid")
    # dispfield=" dispfield_orig_id dispfield_n07"
    # on sauvegarde les parametres dans le profil utilisateur
    if current_user.SetPref("ipp",ipp) + current_user.SetPref("zoom",zoom)+ current_user.SetPref("sortby",sortby)\
            + current_user.SetPref("sortorder",sortorder)+ current_user.SetPref("dispfield",dispfield) >0:
        database.ExecSQL("update users set preferences=%s where id=%s",(current_user.preferences,current_user.id),True)
        user_datastore.ClearCache()
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    fieldlist=GetFieldList(Prj)
    fieldlist.pop('orig_id','')
    t=[]
    sqlparam={'projid':gvp("projid")}
    sql="""select o.objid,t.name taxoname,o.classif_qual,u.name classifwhoname,i.file_name
  ,i.height,i.width,i.thumb_file_name,i.thumb_height,i.thumb_width
  ,o.depth_min,o.depth_max,s.orig_id samplename,o.objdate,o.objtime
  ,o.latitude,o.orig_id"""
    for k in fieldlist.keys():
        sql+=",o."+k+" as extra_"+k
    sql+=""" from objects o
Join images i on o.img0id=i.imgid
left JOIN taxonomy t on o.classif_id=t.id
LEFT JOIN users u on o.classif_who=u.id
LEFT JOIN  samples s on o.sampleid=s.sampleid
where o.projid=%(projid)s
"""
    if(gvp("taxo")!=""):
        sql+=" and o.classif_id=%(taxo)s "
        sqlparam['taxo']=gvp("taxo")
    sqlcount="select count(*) from ("+sql+") q"
    nbrtotal=GetAll(sqlcount,sqlparam,False)[0][0]
    # TODO affiche le total
    if sortby!="":
        sql+=" order by o."+sortby+" "+sortorder
    sql+=" Limit %d offset 0 "%(ipp,)
    res=GetAll(sql,sqlparam,True)
    trcount=1
    t.append("<table class=imgtab><tr id=tr1>")
    WidthOnRow=0
    #récuperation et ajustement des dimensions de la zone d'affichage
    try:
        PageWidth=int(gvp("resultwidth"))-40 # on laisse un peu de marge à droite et la scroolbar
        if PageWidth<200 : PageWidth=200
    except:
        PageWidth=200;
    try:
        WindowHeight=int(gvp("windowheight"))-100 # on enleve le bandeau du haut
        if WindowHeight<200 : WindowHeight=200
    except:
        WindowHeight=200;
    #print("PageWidth=%s, WindowHeight=%s"%(PageWidth,WindowHeight))
    # Calcul des dimmensions et affichage des images
    for r in res:
        filename=r[4]
        origwidth=r[6]
        origheight=r[5]
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
            height=math.trunc(r[5]*width/r[6])
            if height==0: height=1
        if height>WindowHeight:
            height=WindowHeight
            width=math.trunc(r[6]*height/r[5])
            if width==0: width=1
        if WidthOnRow!=0 and (WidthOnRow+width)>PageWidth:
            trcount+=1
            t.append("</tr></table><table class=imgtab><tr id=tr%d>"%(trcount,))
            WidthOnRow=0
        cellwidth=width+22
        # Met la fenetre de zoon la ou il y plus de place, sachant qu'elle fait 400px et ne peut donc pas être callée à gauche des premieres images.
        if (WidthOnRow+cellwidth)>(PageWidth/2):
            pos='left'
        else: pos='right'
        #TODO Si l'image affiché est plus petite que la miniature, afficher la miniature.
        # txt="<td width={3}><div class='divtodrag'><img class='lazy' id=I{4} data-src='/vault/{0}' data-zoom-image='{0}' width={1} height={2}></div>"\
        txt="<td width={3}><img class='lazy' id=I{4} data-src='/vault/{0}' data-zoom-image='{0}' width={1} height={2} pos={5}>"\
            .format(filename,width,height,cellwidth,r[0],pos)
        poptxt=("<p style='white-space: nowrap;'>cat. %s")%(r[1],)
        if r[3]!="":
            poptxt+="<br>Identified by %s"%(r[3])
        colid=17
        for k,v in fieldlist.items():
            if isinstance(r[colid], (float)):
                if(abs(r[colid])<100):
                    poptxt+="<br>%s : %0.2f"%(v,r[colid])
                else: poptxt+="<br>%s : %0.f"%(v,r[colid])
            else:
                poptxt+="<br>%s : %s"%(v,r[colid])
            colid+=1
        txt+="<div class='subimg {1}'><span class=taxo data-title=\"{2}\" data-content=\"{3}\">{0}</span></div>".format(r[1],GetClassifQualClass(r[2]),r[12],poptxt)
        txt+="</td>"
        WidthOnRow+=max(cellwidth,80) # on ajoute au moins 80 car avec les label c'est rarement moins
        t.append(txt)

    t.append("</tr></table>")
    t.append("""
        <style>
        .lazy {margin: 10 5 10 0;}
        </style>
        <script>
        // Add Zoom
        jQuery('div#column-right img.lazy').Lazy({bind: 'event',afterLoad: function(element) {
            if($('#magenabled').prop("checked")==false)
                return; // Si il y a une checkbox magenabled et qu'elle est decochée on ne met pas le zoom
            AddZoom(element);}});
        // Make sub image draggable
        jQuery('.imgtab td .subimg').draggable({revert:true,revertDuration:0});
        // Make the cell clickable for selection
        jQuery('.imgtab td').click(function(e){
            if (!e.ctrlKey)
                $('.ui-selected').toggleClass('ui-selected');
            $(e.target).closest('td').toggleClass('ui-selected');
            //alert('test');
            });
        // Make ZoomTracker Clickable for selection
        jQuery('body').delegate('.zoomtracker','click',function(e){
            if (!e.ctrlKey)
                $('.ui-selected').toggleClass('ui-selected');
            $($(e.target).data("specs").origImg.parents("td")[0]).toggleClass('ui-selected')
            });
        // setup zoomtracker creation tracking to make them draggable
        var target = $( "body" )[0];
        var observer = new MutationObserver(function( mutations ) {
          mutations.forEach(function( mutation ) {
            var newNodes = mutation.addedNodes; // DOM NodeList
            if( newNodes !== null ) { // If there are new nodes added
                var $nodes = $( newNodes ); // jQuery set
                $nodes.each(function() {
                    var $node = $( this );
                    if( $node.hasClass( "zoomtracker" ) ) {
                        //console.log("zoomtracker");
                        jQuery($node).draggable({revert:true,revertDuration:0});
                    }
                });
            }
          });
        });
        var config = {attributes: true,childList: true,characterData: true};
        observer.observe(target, config);
        // Enable the popover
        var option={'placement':'bottom','trigger':'hover','html':true};
        $('span.taxo').popover(option);
        </script>""")
    return "\n".join(t)

def GetClassifTab(PrjId):
    sql="""select t.id,t.name taxoname,Nbr,NbrNotV
    from (  SELECT    o.classif_id,   c.id,count(classif_id) Nbr,count(case when classif_qual='V' then NULL else o.classif_id end) NbrNotV
        FROM (select * from objects where projid=%(projid)s) o
        FULL JOIN (VALUES (6), (8), (12), (21), (23), (17059011)) c(id) ON o.classif_id = c.id
        GROUP BY classif_id, c.id
      ) o
    left JOIN taxonomy t on coalesce(o.classif_id,o.id)=t.id
    order by t.name       """
    param={'projid':PrjId} #TODO InitClassif="6,8,12,21,23"
    res=GetAll(sql,param)
    return render_template('project/classiftab.html',res=res)