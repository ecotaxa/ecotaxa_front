from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,time
from appli.database import GetAll

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

@app.route('/prj/<int:PrjId>')
def indexPrj(PrjId):
    txt = "<h3>Welcome to project %d<h3>"%(PrjId,)
    ipp=100 #TODO récupérer la valeur d'ailleurs
    data={'ipp':str(ipp)}
    right='dodefault'
    InitClassif="6,8,12,21,23"
    classiftab=GetClassifTab(PrjId)
    return render_template('project/projectmain.html',top="Contenu du Haut",lefta=classiftab,right=right,data=data)
    return PrintInCharte(txt)

@app.route('/prj/LoadRightPane', methods=['GET', 'POST'])
def LoadRightPane():
    t=[]
    sql="""select o.objid,t.name taxoname,o.classif_qual,u.name classifwhoname,i.file_name
  ,i.height,i.width,i.thumb_file_name,i.thumb_height,i.thumb_width
  ,o.depth_min,o.depth_max,s.orig_id samplename,o.objdate,o.objtime
  ,o.latitude,o.orig_id
from objects o
Join images i on o.img0id=i.imgid
left JOIN taxonomy t on o.classif_id=t.id
LEFT JOIN users u on o.classif_who=u.id
LEFT JOIN  samples s on o.sampleid=s.sampleid
"""
    sql+=" order by objid "
    sql+=" Limit 1000 offset 80 "
    res=GetAll(sql)
    t.append("<table class=imgtab><tr>")
    ImgOnRow=0
    WidthOnRow=0
    try:
        PageWidth=int(gvp("resultwidth"))
    except:
        PageWidth=200;

    for r in res:
        filename=r[4] # Todo traiter le scaling
        width=r[6]
        height=r[5]
        if WidthOnRow!=0 and (WidthOnRow+width)>PageWidth:
            t.append("</tr></table><table class=imgtab><tr>")
            WidthOnRow=0
        cellwidth=width+20
        txt="<td width={3}><div class='divtodrag'><img class='lazy' id=I{4} data-src='/vault/{0}' data-zoom-image='{0}' width={1} height={2}></div>"\
            .format(filename,width,height,cellwidth,r[0])
        txt+="<div class='subimg'>{0}</div>".format(r[1])
        txt+="</td>"
        WidthOnRow+=cellwidth
        t.append(txt)

    t.append("</tr></table>")
    t.append("""<script>
        jQuery('div#column-right img.lazy').Lazy({bind: 'event',afterLoad: function(element) {AddZoom(element);}});
        //jQuery('#column-right ').selectable({ filter: ".subimg"});
        //jQuery('.imgtab td .divtodrag').draggable({revert:true,revertDuration:0});
        jQuery('#column-right ').selectable({ filter: "td"});
        jQuery('.imgtab td .subimg').draggable({revert:true,revertDuration:0});
        // $('document').ready(function(){
        // jQuery('.divtodrag').multiDraggable({revert:true,revertDuration:0});
        // });
        </script>""")
    return "\n".join(t)

def GetClassifTab(PrjId):
    sql="""select t.id,t.name taxoname,Nbr
    from (  SELECT    o.classif_id,   c.id,   count(classif_id) Nbr
        FROM objects o
        FULL JOIN (VALUES (6), (8), (12), (21), (23), (17059011)) c(id) ON o.classif_id = c.id
        GROUP BY classif_id, c.id
      ) o
    left JOIN taxonomy t on coalesce(o.classif_id,o.id)=t.id
    order by t.name       """
    res=GetAll(sql)
    return render_template('project/classiftab.html',res=res)