# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,gvg,db,gvp
import psycopg2,psycopg2.extras


def GetAll(sql,params=None):
    cur = db.engine.raw_connection().cursor()
    cur.execute(sql,params)
    res = cur.fetchall()
    cur.close()  #TODO ajouter un Finaly
    return res


@app.route('/search/taxo')
def searchtaxo():
    term=gvg("q")
    if len(term)<=2:
        return "[]"
    term+=R"%"
    res = GetAll("SELECT id, nom FROM taxonomy WHERE  nom LIKE %s order by nom limit 1000", (term,))
    return json.dumps([dict(id=r[0],text=r[1]) for r in res])


@app.route('/search/taxotree')
def searchtaxotree():
    res = GetAll("SELECT id, nom FROM taxonomy WHERE  parent_id is null order by nom ")
    print(res)
    return render_template('search/taxopopup.html',root_elements=res)


@app.route('/search/taxotreejson')
def taxotreerootjson():
    parent=gvg("id")
    sql="SELECT id, nom,parent_id FROM taxonomy WHERE "
    if parent=='#': sql+="parent_id is null"
    else: sql+="parent_id ="+parent
    sql+=" order by nom "
    res = GetAll(sql)
    print(res)
    return json.dumps([dict(id=str(r[0]),text="<span class=v>"+r[1]+"</span> <span class='TaxoSel label label-default'>Select</span>",parent=r[2] or "#",children=True) for r in res])


@app.route('/search/taxofinal', methods=['GET', 'POST'])
def taxofinal():
    if gvp("taxo[]"):
        resin=",".join(request.form.getlist("taxo[]"))
        res = GetAll("SELECT id, nom FROM taxonomy WHERE  id in ("+resin+")  order by nom ")
        txt="Taxonomy = "+",".join((x[1] for x in res))
    else:txt="No Criteria"
    Imgs=GetAll("""SELECT o.objid, i.imgid, i.file_name, coalesce(i.thumb_file_name,i.file_name), coalesce(i.thumb_width,i.width), coalesce(i.thumb_height,i.height), taxo.nom
              FROM public.objects o, public.images i, public.taxonomy taxo
              WHERE o.objid = i.objid AND o.classif_id = taxo.id;""")
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
