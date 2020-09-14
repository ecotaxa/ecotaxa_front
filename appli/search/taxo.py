# -*- coding: utf-8 -*-
import re
from typing import List, Dict

from flask import render_template, json, jsonify
from flask_login import current_user
from psycopg2.extensions import QuotedString

from appli import app, gvg, gvp, database, ntcv
from appli.database import GetAll, GetAssoc2Col

sql_tree_exp = """concat(tf.name,'<'||t1.name,'<'||t2.name,'<'||t3.name,'<'||t4.name,'<'||t5.name,'<'||t6.name,
            '<'||t7.name,'<'||t8.name,'<'||t9.name,'<'||t10.name,'<'||t11.name,'<'||t12.name,
            '<'||t13.name,'<'||t14.name)"""
SQLTreeJoin = """left join taxonomy t1 on tf.parent_id=t1.id
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


def _filter_mru(raw_mru: List[Dict], query: str) -> List[Dict]:
    """
        Apply filtering to the MRU so that it complies with the query.
    """
    query = query.lower()
    # OK we have only 2 letters so below is a bit of overkill
    if not ("*" in query or " " in query or "%" in query):
        # Simple search
        filter_func = lambda txt: txt.lower().startswith(query)
    else:
        # Regexp match
        query = query.replace(" ", "*").replace("%", "*").replace("*", ".*")
        filter_func = lambda txt: re.match(query, txt.lower())
    try:
        return [itm for itm in raw_mru if filter_func(itm["text"])]
    except (KeyError, ValueError):
        # Better nothing than a faulty value
        return []


@app.route('/search/taxo')
def searchtaxo():
    term = gvg("q")
    if len(term) <= 2:
        # return "[]"
        if not current_user.is_authenticated:
            return "[]"
        # current_user.id
        with app.MRUClassif_lock:
            # app.MRUClassif[current_user.id]=[{"id": 2904, "pr": 0, "text": "Teranympha (Eucomonymphidae
            #  -Teranymphidae)"},
            # {"id": 12488, "pr": 0, "text": "Teranympha mirabilis "},
            # {"id": 76677, "pr": 0, "text": "Terasakiella (Methylocystaceae)"},
            # {"id": 82969, "pr": 0, "text": "Terasakiella pusilla "}]
            mru = app.MRUClassif.get(current_user.id, [])
            # filter inside the MRU list
            mru = _filter_mru(mru, term)
            return json.dumps(mru)
    # Proceed to 3+ letters
    # * et espace comme %
    terms = [x.lower().replace("*", "%").replace(" ", "%") + R"%" for x in term.split('<')]
    param = {'term': terms[0]}  # le premier term est toujours appliqué sur le display name
    extra_where = extra_from = ""

    if len(terms) > 1:
        extra_from = SQLTreeJoin
        terms = ['%%<' + x.replace("%", "%%").replace("*", "%%").replace(" ", "%%") for x in terms[1:]]
        terms_sql = QuotedString("".join(terms)).getquoted().decode('iso-8859-15', 'strict')
        extra_where = ' and ' + sql_tree_exp + " ilike " + terms_sql

    # By default, simple select from taxonomy and return alphabetical matches
    sql = """SELECT tf.id, tf.display_name as name, 0 
               FROM taxonomy tf
                 {0}
              WHERE LOWER(tf.display_name) LIKE %(term)s  {1}
           ORDER BY LOWER(tf.display_name) LIMIT 200""".format(extra_from, extra_where)

    prj_id = gvg("projid")
    if prj_id != "":
        prj_id = int(prj_id)
        prj = database.Projects.query.filter_by(projid=prj_id).first()
        if ntcv(prj.initclassiflist) != "":
            # e.g. 14532,16789,165778
            db_init_classif = prj.initclassiflist
            # => (14532),(16789),(165778)
            init_classif = ", ".join(["(" + x.strip() + ")" for x in db_init_classif.split(",") if x.strip() != ""])
            # We're inside a project, with presets, so favor the presets in the search output order
            sql = """
            SELECT tf.id, tf.display_name as name, case when id2 is null then 0 else 1 end inpreset 
              FROM taxonomy tf
              JOIN (SELECT t.id id1, c.id id2 
                      FROM taxonomy t
                      FULL JOIN (VALUES """ + init_classif + """) c(id) ON t.id = c.id
                     WHERE LOWER(display_name) LIKE %(term)s ) tl2 ON tf.id = COALESCE(id1, id2)
            """ + extra_from + """
             WHERE LOWER(tf.display_name) LIKE %(term)s """ + extra_where + """
          ORDER BY inpreset DESC, LOWER(tf.display_name), name LIMIT 200 """

    res = GetAll(sql, param, debug=False)
    return json.dumps([dict(id=r[0], text=r[1], pr=r[2]) for r in res])


@app.route('/search/taxotree')
def searchtaxotree():
    res = GetAll("SELECT id, name FROM taxonomy WHERE  parent_id is null order by name ")
    # print(res)
    return render_template('search/taxopopup.html', root_elements=res, targetid=gvg("target", "taxolb"))


@app.route('/search/taxotreejson')
def taxotreerootjson():
    parent = gvg("id")
    sql = """SELECT id, name,parent_id,coalesce(nbrobj,0)+coalesce(nbrobjcum,0)
          ,exists(select 1 from taxonomy te where te.parent_id=taxonomy.id)
          FROM taxonomy
          WHERE """
    if parent == '#':
        sql += "parent_id is null"
    else:
        sql += "parent_id =%d" % (int(parent))
    sql += " order by name "
    res = GetAll(sql)
    # print(res)
    return json.dumps([dict(id=str(r[0]), text="<span class=v>" + r[1] + "</span> (" + str(
        r[3]) + ") <span class='TaxoSel label label-default'><span class='glyphicon glyphicon-ok'></span></span>",
                            parent=r[2] or "#", children=r[4]) for r in res])


@app.route('/search/taxoresolve', methods=['POST'])
def taxoresolve():
    idlist = gvp('idlist', '')
    lst = [int(x) for x in idlist.split(",") if x.isdigit()]
    taxomap = GetAssoc2Col("""select id,display_name from taxonomy where id = any(%s) order by lower(display_name)""",
                           [lst])
    return jsonify(taxomap)
