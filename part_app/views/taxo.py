import json
from typing import List

from flask import request

from to_back.ecotaxa_cli_py import TaxaSearchRsp
from ..app import part_app
from ..http_utils import gvg
from ..remote import EcoTaxaInstance


@part_app.route('/search/taxo')
def search_taxo():
    term = gvg("q")
    ecotaxa_if = EcoTaxaInstance(request)
    # Relay to back-end and reformat
    rsp: List[TaxaSearchRsp] = ecotaxa_if.search_taxa(term)
    res = [{'id': a_taxon.id, 'text': a_taxon.text}
           for a_taxon in rsp
           if a_taxon.renm_id is None]
    return json.dumps(res)


@part_app.route('/search/taxotreejson')
def taxo_tree():
    parent = gvg("id")
    ecotaxa_if = EcoTaxaInstance(request)
    if parent == '#':
        # Root nodes
        roots = ecotaxa_if.get_taxo_roots()
        res = [(r.id, r.name, None, r.nb_objects + r.nb_children_objects, len(r.children) > 0)
               for r in roots]
    else:
        # Children of the requested parent_id, when opening the tree
        # Fetch the parent for getting its children
        parents = ecotaxa_if.query_taxa_set([parent])
        # Fetch children, for their names and to know if they have children
        children = ecotaxa_if.query_taxa_set(parents[0].children)
        res = [(r.id, r.name, parent, r.nb_objects + r.nb_children_objects, len(r.children) > 0)
               for r in children]
    res.sort(key=lambda r: r[1])

    def span_for_node(rec):
        return "<span class=v>" + rec[1] + "</span> (" + str(rec[3]) + ") " + \
               "<span class='TaxoSel label label-default'><span class='glyphicon glyphicon-ok'></span></span>"

    return json.dumps([dict(id=str(r[0]),
                            text=span_for_node(r),
                            parent=r[2] or "#",
                            children=r[4]) for r in res])
