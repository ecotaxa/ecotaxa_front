from flask import request
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi, ProjectsApi
from to_back.ecotaxa_cli_py.models import ProjectModel, ProjectTaxoStatsModel

######################################################################################################################
# taxo names
def taxo_with_names(ids: list) -> list:

    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(ids))
    taxo_names = [(r.id, r.display_name) for r in res]
    taxo_names.sort(key=lambda r: r[1])
    return taxo_names


######################################################################################################################
# taxo names, lineage
def taxo_with_lineage(ids: list) -> list:
    from collections.abc import Iterable

    ids = list(filter(lambda i: i != "-1", ids))
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=",".join(ids))
    taxo_data = [(r.id, r.display_name, list([l for l in r.lineage])) for r in res]
    taxo_data.sort(key=lambda r: ">".join(r[2]))
    return taxo_data


#######################################################################################################################
# project used taxa
def project_used_taxa(projid: int, req_taxa: str = "all") -> list:
    with ApiClient(ProjectsApi, request) as api:
        taxo_stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(
            ids=str(projid), taxa_ids=req_taxa
        )
        # easier format to display stats by taxon id
        used_taxa = list([])
        if len(taxo_stats):
            used_taxa.extend([str(t.used_taxa[0]) for t in taxo_stats])

            return taxo_with_names(used_taxa)
        return []
