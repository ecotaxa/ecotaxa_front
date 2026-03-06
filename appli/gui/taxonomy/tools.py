from typing import List, Dict, Optional
from flask import request, render_template
from appli.back_config import get_back_constants

from appli import gvp
from appli.utils import ApiClient
from appli.gui.commontools import new_ui_error
from werkzeug.exceptions import NotFound
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi, ProjectsApi, CollectionsApi
from to_back.ecotaxa_cli_py.models import (
    TaxoRecastRsp,
    TaxonomyRecastReq,
    ProjectTaxoStatsModel,
    TaxonModel,
)


######################################################################################################################
# taxo names
def taxo_with_names(ids: list) -> list:

    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(ids))
    taxo_names = [(r.id, r.display_name, r.status) for r in res]
    taxo_names.sort(key=lambda r: r[1])
    return taxo_names


######################################################################################################################
# taxo names, lineage
def taxo_with_lineage(ids: list) -> list:

    ids = list(filter(lambda i: i != "-1", ids))
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=",".join(ids))
    taxo_data = [
        (
            r.id,
            r.display_name,
            list([l for l in r.lineage]),
            list([l for l in r.lineage_status]),
        )
        for r in res
    ]
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


#######################################################################################################################
# taxonomy recast for projects and collections


def get_taxo_recast(
    target_id: int, operation: str, is_collection: bool
) -> Optional[TaxoRecastRsp]:
    try:
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxo_recast = api.get_taxonomy_recast(
                target_id=target_id, operation=operation, is_collection=is_collection
            )
        return taxo_recast

    except ApiException as ae:
        new_ui_error(ae)


def read_taxo_recast(target_id: int, operation: str, is_collection: bool):
    project_ids = []
    if is_collection:
        try:
            with ApiClient(CollectionsApi, request) as api:
                collection = api.get_collection(collection_id=target_id)
            project_ids = ",".join([str(pid) for pid in collection.project_ids])
        except ApiException as ae:
            new_ui_error(ae)
    else:
        project_ids = str(target_id)
    taxalist, taxaids = get_taxostats(project_ids)
    taxo_doc = {}
    # get automatic worms taxo
    with ApiClient(TaxonomyTreeApi, request) as api:
        ids = api.get_taxonomy_worms(taxa_ids=",".join(taxaids))
    autoids = {str(k): str(v) for k, v in ids.items()}
    # get modified automatic worms taxo
    recast_operation = get_back_constants("RECAST_OPERATION")
    res = get_taxo_recast(
        target_id, recast_operation["dwca_export_occurrence"], is_collection
    )
    if res is not None:
        wormsids = {str(k): str(v) for k, v in res.from_to.items()}
        taxo_doc = res.doc
    else:
        wormsids = autoids
    res = get_taxo_recast(target_id, operation, is_collection)
    if res is not None:
        recastids = {str(k): str(v) for k, v in res.from_to.items()}
        if taxo_doc == {}:
            taxo_doc = res.doc
    else:
        recastids = wormsids
    # search worms ids and recast ids in one request
    reqids = ",".join(
        list(
            set(
                list(wormsids.values())
                + list(recastids.values())
                + list(autoids.values())
            )
        )
    )
    with ApiClient(TaxonomyTreeApi, request) as api:
        recastitems = api.wormsification_taxa_set(reqids)
    keys = recastitems.keys()

    def taxa_wormsification(ids: List[str]):
        taxos = {}
        for k, vk in ids.items():
            if vk != "0" and vk in keys:
                v = recastitems[vk]
                if v != "0":
                    taxos.update({str(k): v})
        return taxos

    taxo_worms = taxa_wormsification(wormsids)
    taxo_auto = taxa_wormsification(autoids)
    taxo_recast = taxa_wormsification(recastids)
    # sort taxalist on lineage
    taxalist.sort(
        key=lambda t: (",".join(t.lineage[::-1]) if t.lineage is not None else ""),
        reverse=False,
    )

    return render_template(
        "v2/taxonomy/_taxo_recast.html",
        taxo_auto=taxo_auto,
        taxo_recast=taxo_recast,
        taxalist=taxalist,
        taxo_worms=taxo_worms,
        taxo_doc=taxo_doc,
    )


def update_taxo_recast(
    target_id: int,
    taxonomy_recast: TaxoRecastRsp,
    operation: str,
    is_collection: bool = False,
):
    from_to = {k: int(v) if v != "" else 0 for k, v in taxonomy_recast.from_to.items()}
    taxonomy_recast.from_to = from_to
    recast = TaxonomyRecastReq(
        target_id=target_id,
        operation=operation,
        recast=taxonomy_recast,
        is_collection=is_collection,
    )
    try:
        with ApiClient(TaxonomyTreeApi, request) as api:
            api.update_taxonomy_recast(recast)
    except ApiException as ae:
        if ae.status != NotFound.code:
            new_ui_error(ae)
    return read_taxo_recast(target_id, operation=operation, is_collection=is_collection)


def get_taxostats(project_ids: str):
    with ApiClient(ProjectsApi, request) as api:
        taxa = api.project_set_get_stats(ids=project_ids)
    used_taxa = []
    for res in taxa:
        used_taxa.extend([str(r) for r in res.used_taxa])
    taxaids = list(set(used_taxa))
    with ApiClient(TaxonomyTreeApi, request) as api:
        taxalist = api.query_taxa_set(",".join(taxaids))
    return taxalist, taxaids


def posted_taxo_recast() -> Dict[str, TaxoRecastRsp]:

    taxanum = gvp("taxanum", "0")

    from_to_worms = {}
    from_to_final = {}
    doc_worms = {}
    doc_final = {}
    idx = 1
    while idx <= int(taxanum):
        frm = gvp("item-from-" + str(idx))
        toworms = gvp("item-worms-" + str(idx), "")
        tofinal = gvp("item-to-" + str(idx), "")
        todoc = gvp("item-doc-" + str(idx), "")
        if toworms == "" or toworms == "0":
            toworms = "0"
            tofinal = "0"
        if tofinal == "" or tofinal == "0":
            tofinal = "0"
        if tofinal != "0" or toworms != "0":
            from_to_worms[frm] = int(toworms)
            doc_worms[frm] = todoc
            from_to_final[frm] = int(tofinal)
            doc_final[frm] = todoc
        idx += 1
    return dict(
        {
            "occurrence": TaxoRecastRsp(from_to=from_to_worms, doc=doc_worms),
            "emof": TaxoRecastRsp(from_to=from_to_final, doc=doc_final),
        }
    )
