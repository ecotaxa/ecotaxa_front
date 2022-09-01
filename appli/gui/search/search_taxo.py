from json import JSONEncoder
from flask import request, json
from appli.utils import ApiClient
from appli.search.taxo import BackEndJSONEncoder
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import TaxonModel

######################################################################################################################
# taxo by ids


def search_taxoset(ids: list) -> list:
    if len(ids) == 0:
        return None
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(ids))
    taxolist = [(r.id, r.display_name) for r in res]
    taxolist.sort(key=lambda r: r[1].lower())
    return json.dumps(taxolist, cls=BackEndJSONEncoder)
