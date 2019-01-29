# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json,jsonify
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,gvg,db,gvp,database,ntcv
from appli.database import GetAll,GetAssoc2Col
from psycopg2.extensions import QuotedString
import psycopg2,psycopg2.extras

SQLTreeExp="""concat(tf.name,'<'||t1.name,'<'||t2.name,'<'||t3.name,'<'||t4.name,'<'||t5.name,'<'||t6.name,'<'||t7.name
            ,'<'||t8.name,'<'||t9.name,'<'||t10.name,'<'||t11.name,'<'||t12.name,'<'||t13.name,'<'||t14.name)"""
SQLTreeJoin="""left join taxonomy t1 on tf.parent_id=t1.id
      left join taxonomy t2 on t1.parent_id=t2.id
      left join taxonomy t3 on t2.parent_id=t3.id
      left join taxonomy t4 on t3.parent_id=t4.id
      left join taxonomy t5 on t4.parent_id=t5.id
      left join taxonomy t6 on t5.parent_id=t6.id
      left join taxonomy t7 on t6.parent_id=t7.id
      left join taxonomy t8 on t7.parent_id=t8.id
      left join taxonomy t9 on t8.parent_id=t9.id
      left join taxonomy t10 on t9.parent_id=t10.id
      left join taxonomy t11 on t10.parent_id=t11.id
      left join taxonomy t12 on t11.parent_id=t12.id
      left join taxonomy t13 on t12.parent_id=t13.id
      left join taxonomy t14 on t13.parent_id=t14.id"""


@app.route('/search/taxo')
def searchtaxo():
    term=gvg("q")
    if len(term)<=2:
        # return "[]"
        if not current_user.is_authenticated:
            return "[]"
        # current_user.id
        with app.MRUClassif_lock:
            # app.MRUClassif[current_user.id]=[{"id": 2904, "pr": 0, "text": "Teranympha (Eucomonymphidae-Teranymphidae)"},
         # {"id": 12488, "pr": 0, "text": "Teranympha mirabilis "},
         # {"id": 76677, "pr": 0, "text": "Terasakiella (Methylocystaceae)"},
         # {"id": 82969, "pr": 0, "text": "Terasakiella pusilla "}]
            return json.dumps(app.MRUClassif.get(current_user.id,[])) # gère les MRU en utilisant les classif
    ltfound=term.find('<')>0
    SQLWith="""
    """
    # * et espace comme %
    terms=[x.lower().replace("*","%").replace(" ","%")+R"%" for x in term.split('<')]
    param={'term':terms[0]} # le premier term est toujours appliqué sur le display name
    ExtraWhere=ExtraFrom=""
    if len(terms)>1:
        ExtraFrom = SQLTreeJoin
        terms = ['%%<'+x.replace("%","%%").replace("*","%%").replace(" ","%%")  for x in terms[1:]]
        termsSQL=QuotedString("".join(terms)).getquoted().decode('iso-8859-15','strict')
        ExtraWhere= ' and '+SQLTreeExp+" ilike "+termsSQL
    sql="""SELECT tf.id, tf.display_name as name
          ,0 FROM taxonomy tf
          {0}
          WHERE  lower(tf.display_name) LIKE %(term)s  {1}
          order by lower(tf.display_name) limit 200""".format(ExtraFrom,ExtraWhere)

    PrjId=gvg("projid")
    if PrjId!="":
        PrjId=int(PrjId)
        Prj=database.Projects.query.filter_by(projid=PrjId).first()
        if ntcv(Prj.initclassiflist) != "":
            InitClassif=Prj.initclassiflist
            InitClassif=", ".join(["("+x.strip()+")" for x in InitClassif.split(",") if x.strip()!=""])
            #             ,tf.name||case when p1.name is not null and tf.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name

            sql="""
            SELECT tf.id
            ,tf.display_name as name
            , case when id2 is null then 0 else 1 end inpreset FROM taxonomy tf
            join (select t.id id1,c.id id2 FROM taxonomy t
            full JOIN (VALUES """+InitClassif+""") c(id) ON t.id = c.id
                 WHERE  lower(display_name) LIKE %(term)s) tl2
            on tf.id=coalesce(id1,id2)
            """+ExtraFrom+"""
              WHERE  lower(tf.display_name) LIKE %(term)s """+ExtraWhere+"""
            order by inpreset desc,lower(tf.display_name),name limit 200 """
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
    sql="""SELECT id, name,parent_id,coalesce(nbrobj,0)+coalesce(nbrobjcum,0)
          ,exists(select 1 from taxonomy te where te.parent_id=taxonomy.id)
          FROM taxonomy
          WHERE """
    if parent=='#': sql+="parent_id is null"
    else: sql+="parent_id =%d"%(int(parent))
    sql+=" order by name "
    res = GetAll(sql)
    # print(res)
    return json.dumps([dict(id=str(r[0]),text="<span class=v>"+r[1]+"</span> ("+str(r[3])+") <span class='TaxoSel label label-default'><span class='glyphicon glyphicon-ok'></span></span>",parent=r[2] or "#",children=r[4]) for r in res])

@app.route('/search/taxoresolve', methods=['POST'])
def taxoresolve():
    idlist=gvp('idlist','')
    lst = [int(x) for x in idlist.split(",") if x.isdigit()]
    taxomap=GetAssoc2Col("""select id,display_name from taxonomy where id = any(%s) order by lower(display_name)""",[ lst ])
    return jsonify(taxomap)

