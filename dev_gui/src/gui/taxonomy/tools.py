from flask import request
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi

######################################################################################################################
# taxo names
def taxo_with_names(ids: list) -> list:
    from markupsafe import escape

    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(ids))
    taxo_names = [(r.id, escape(r.display_name)) for r in res]
    taxo_names.sort(key=lambda r: r[1])
    return taxo_names


######################################################################################################################
# taxo names, lineage
def taxo_with_lineage(ids: list) -> list:
    from markupsafe import escape
    from collections.abc import Iterable

    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(ids))
    taxo_data = [
        (r.id, escape(r.display_name), list([l for l in r.lineage])) for r in res
    ]
    taxo_data.sort(key=lambda r: ">".join(r[2]))
    return taxo_data
