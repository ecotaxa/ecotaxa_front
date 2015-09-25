# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,gvg,db,gvp,database
from appli.database import GetAll
import psycopg2,psycopg2.extras

@app.route('/search/taxo')
def searchtaxo():
    term=gvg("q")
    if len(term)<=2:
        return "[]"
    term+=R"%"
    param={'term':term.lower()}
    sql="SELECT id, name,0 FROM taxonomy WHERE  lower(name) LIKE %(term)s order by name limit 200"

    PrjId=gvg("projid")
    if PrjId!="":
        PrjId=int(PrjId)
        Prj=database.Projects.query.filter_by(projid=PrjId).first()
        if Prj.initclassiflist is not None:
            InitClassif=Prj.initclassiflist
            InitClassif=", ".join(["("+x.strip()+")" for x in InitClassif.split(",") if x.strip()!=""])
            sql="""
            SELECT tf.id, name, case when id2 is null then 0 else 1 end inpreset FROM taxonomy tf
            join (select t.id id1,c.id id2 FROM taxonomy t
            full JOIN (VALUES """+InitClassif+""") c(id) ON t.id = c.id
                 WHERE  lower(name) LIKE %(term)s) t2
            on tf.id=coalesce(id1,id2)
              WHERE  lower(name) LIKE %(term)s
            order by inpreset desc,name limit 200 """
    res = GetAll(sql, param,debug=False)
    return json.dumps([dict(id=r[0],text=r[1],pr=r[2]) for r in res])


@app.route('/search/taxotree')
def searchtaxotree():
    res = GetAll("SELECT id, name FROM taxonomy WHERE  parent_id is null order by name ")
    # print(res)
    return render_template('search/taxopopup.html',root_elements=res,targetid=gvg("target","taxolb"))


@app.route('/search/taxotreejson')
def taxotreerootjson():
    parent=gvg("id")
    sql="SELECT id, name,parent_id,coalesce(nbrobj,0)+coalesce(nbrobjcum,0) FROM taxonomy WHERE "
    if parent=='#': sql+="parent_id is null"
    else: sql+="parent_id ="+parent
    sql+=" order by name "
    res = GetAll(sql)
    # print(res)
    return json.dumps([dict(id=str(r[0]),text="<span class=v>"+r[1]+"</span> ("+str(r[3])+") <span class='TaxoSel label label-default'>Select</span>",parent=r[2] or "#",children=True) for r in res])


@app.route('/search/taxofinal', methods=['GET', 'POST'])
def taxofinal():
    sql="""SELECT o.objid, i.imgid, i.file_name, coalesce(i.thumb_file_name,i.file_name), coalesce(i.thumb_width,i.width), coalesce(i.thumb_height,i.height), taxo.name
              FROM objects o
              join taxonomy taxo on o.classif_id = taxo.id
              join images i on o.img0id=i.imgid
              WHERE  1=1 """
    if gvp("taxo[]"):
        resin=",".join(request.form.getlist("taxo[]"))
        res = GetAll("SELECT id, name FROM taxonomy WHERE  id in ("+resin+")  order by name ")
        txt="Taxonomy = "+",".join((x[1] for x in res))
        sql+=" and o.classif_id in ("+",".join(request.form.getlist("taxo[]"))+")"
    else:txt="No Criteria"
    sql+=" limit 100"
    Imgs=GetAll(sql)
    txt+=" (%d response)"%(len(Imgs))
    txt+="\n<table><tr>"
    try:
        NbrCol=int(gvp("resultwidth"))//160
    except:
        NbrCol=4;
    for Img,i in zip(Imgs,range(0,9999999)):
        if i>0 and (i%NbrCol)==0:
            txt+="\n</tr><tr>"
        # txt+="\n<td valign=bottom witdth=160px><img class='lazy' src='' data-src='/vault/%s?3' width=%s height=%s data-zoom-image='/vault/%s'><br>%s</td>"%(Img[3],Img[4],Img[5],Img[2],Img[6])
        txt+="\n<td valign=bottom witdth=160px><img class='lazy' id=I%d src='' data-src='/vault/%s?3' width=%s height=%s data-zoom-image='%s'><br>%s</td>"%(i,Img[3],Img[4],Img[5],Img[2],Img[6])
#        txt+="\n<td valign=bottom witdth=160px><img class='bttrlazyloading' data-bttrlazyloading-sm-src='vault/%s?1' width=%s height=%s><br>%s</td>"%(Img[3],Img[4],Img[5],Img[6])

    txt+="\n</tr></table>"
    txt+="\n<script>jQuery('div#column-right img.lazy').Lazy({bind: 'event',afterLoad: function(element) {AddZoom(element);}});</script>"
#   txt+="\n<script>jQuery('div#column-right img.lazy').Lazy({bind: 'event'}); $('img.lazy').elevateZoom({scrollZoom : true});</script>"
#    txt+="\n<script>$('.bttrlazyloading').bttrlazyloading();</script>"
#     txt+="""
# <script>
# function AddZoom2(id,big,index)
# {
# var pos='right'
# if((index%5)>=3) pos='left'
#
# $('#'+id).addimagezoom({ // single image zoom
# 		zoomrange: [3, 10],
# 		magnifiersize: [300,300],
# 		magnifierpos: pos,
# 		cursorshade: true,
# 		largeimage: '/vault/'+big
# 	});
# }
#
#
#     $(document).ready(function() {
#
# $( "li" ).each(function( index ) {
#   console.log( index + ": " + $( this ).text() );
# });
#         //AddZoom('IMG1','0000/41201.JPG?1',0)
#         //AddZoom('IMG2','0000/41200.JPG?1',3)
#
# });
# </script>
# """
    return txt
