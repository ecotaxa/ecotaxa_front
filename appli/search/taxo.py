# -*- coding: utf-8 -*-
from json import JSONEncoder
from typing import List

from flask import render_template, json, jsonify, request

from appli import app, gvg, gvp
from appli.database import GetAll, GetAssoc2Col
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import TaxonomyTreeApi, TaxaSearchRsp


# Specialize an encoder for serializing directly the back-end response
class BackEndJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, TaxaSearchRsp):
            return o.to_dict()
        return JSONEncoder.default(self, o)


@app.route('/search/taxo')
def searchtaxo():
    term = gvg("q")
    prj_id = gvg("projid")
    if not prj_id:
        prj_id = -1

    # Relay to back-end
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxaSearchRsp] = api.search_taxa_taxa_search_get(query=term,
                                                                   project_id=prj_id)

    # TODO: temporary until the HTML goes to /api directly
    return json.dumps(res, cls=BackEndJSONEncoder)


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
