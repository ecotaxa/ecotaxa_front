# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,gvg,db,gvp,database,ntcv
from appli.database import GetAll
from psycopg2.extensions import QuotedString
import psycopg2,psycopg2.extras

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
    terms=[x.strip().lower()+R"%" for x in term.split('*')]
    # psycopg2.extensions.QuotedString("""c'est ok "ici" à  """).getquoted()
    param={'term':terms[-1]} # le dernier term est toujours dans la requete
    terms=[QuotedString(x).getquoted().decode('iso-8859-15','strict').replace("%","%%") for x in terms[0:-1]]
    ExtraWhere=ExtraFrom=""
    if terms:
        for t in terms:
            ExtraWhere +="\n and ("
            # SQLI insensible, protégé par quotedstring
            ExtraWhere +=' or '.join(("lower(p{0}.name) like {1}".format(i,t) for i in range(1,6)))+")"
        ExtraFrom="\n".join(["left join taxonomy p{0} on p{1}.parent_id=p{0}.id".format(i,i-1) for i in range(2,6)])

    sql="""SELECT tf.id, tf.name||case when p1.name is not null and tf.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name
          ,0 FROM taxonomy tf
          left join taxonomy p1 on tf.parent_id=p1.id
          {0}
          WHERE  lower(tf.name) LIKE %(term)s  {1}
          order by tf.name limit 200""".format(ExtraFrom,ExtraWhere)

    PrjId=gvg("projid")
    if PrjId!="":
        PrjId=int(PrjId)
        Prj=database.Projects.query.filter_by(projid=PrjId).first()
        if ntcv(Prj.initclassiflist) != "":
            InitClassif=Prj.initclassiflist
            InitClassif=", ".join(["("+x.strip()+")" for x in InitClassif.split(",") if x.strip()!=""])
            sql="""
            SELECT tf.id
            ,tf.name||case when p1.name is not null and tf.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name
            , case when id2 is null then 0 else 1 end inpreset FROM taxonomy tf
            join (select t.id id1,c.id id2 FROM taxonomy t
            full JOIN (VALUES """+InitClassif+""") c(id) ON t.id = c.id
                 WHERE  lower(name) LIKE %(term)s) t2
            on tf.id=coalesce(id1,id2)
            left join taxonomy p1 on tf.parent_id=p1.id
            """+ExtraFrom+"""
              WHERE  lower(tf.name) LIKE %(term)s """+ExtraWhere+"""
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


