import json
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
    project_ids = ""
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
    # sort taxalist on lineage
    taxalist.sort(
        key=lambda t: (",".join(t.lineage[::-1]) if t.lineage is not None else ""),
        reverse=False,
    )
    recastres = get_taxo_recast(target_id, operation, is_collection)
    if recastres is not None:
        recastids = {str(k): str(v) for k, v in recastres.from_to.items()}
        taxo_doc = recastres.doc
    else:
        recastids = {}
        taxo_doc = {}

    def taxa_populate(
        _ids: Dict[str, str], _keys: List[str], _recastitems: Dict[str, TaxonModel]
    ):
        taxos = {}
        for k, vk in _ids.items():
            if vk != "0" and vk in _keys:
                v = _recastitems[vk]
                if v != "0":
                    taxos.update({str(k): v})
        return taxos

    recast_operation = get_back_constants("RECAST_OPERATION")
    if operation == recast_operation["dwca_export_emof"]:
        taxo_doc = {}
        # get automatic worms taxo
        with ApiClient(TaxonomyTreeApi, request) as api:
            ids = api.get_taxonomy_worms(taxaids=",".join(taxaids))
        autoids = {str(k): str(v) for k, v in ids.items()}
        # get modified automatic worms taxo
        res = get_taxo_recast(
            target_id, recast_operation["dwca_export_occurrence"], is_collection
        )
        if res is not None:
            wormsids = {str(k): str(v) for k, v in res.from_to.items()}
            if taxo_doc == {}:
                taxo_doc = res.doc
        else:
            wormsids = autoids
        if recastres is None:
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
        taxo_worms = taxa_populate(wormsids, keys, recastitems)
        taxo_auto = taxa_populate(autoids, keys, recastitems)
        taxo_recast = taxa_populate(recastids, keys, recastitems)
        print("taxalist----", taxalist)
        return render_template(
            "v2/taxonomy/_dwca_taxo_recast.html",
            taxo_auto=taxo_auto,
            taxo_recast=taxo_recast,
            taxalist=taxalist,
            taxo_worms=taxo_worms,
            taxo_doc=taxo_doc,
            operation=operation,
        )
    else:
        taxo_auto = {str(t.id): t for t in taxalist}
        recastvals = recastids.values()
        reqids = ",".join(list(recastvals))
        if len(recastvals) > 0:
            with ApiClient(TaxonomyTreeApi, request) as api:
                recasts = api.query_taxa_set(reqids)
            taxo_recast = {str(t.id): t for t in recasts}
        else:
            taxo_recast = taxo_auto
        return render_template(
            "v2/taxonomy/_taxo_recast.html",
            taxo_auto=taxo_auto,
            taxo_recast=taxo_recast,
            taxalist=taxalist,
            taxo_doc=taxo_doc,
            operation=operation,
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


def posted_dwca_taxo_recast(
    recast_operation: Dict[str, str],
) -> Dict[str, TaxoRecastRsp]:
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
        if toworms == "":
            toworms = "0"
        if tofinal == "":
            tofinal = "0"
        from_to_worms[frm] = int(toworms)
        doc_worms[frm] = todoc
        from_to_final[frm] = int(tofinal)
        doc_final[frm] = todoc
        idx += 1
    return dict(
        {
            recast_operation["dwca_export_occurrence"]: TaxoRecastRsp(
                from_to=from_to_worms, doc=doc_worms
            ),
            recast_operation["dwca_export_emof"]: TaxoRecastRsp(
                from_to=from_to_final, doc=doc_final
            ),
        }
    )


def posted_taxo_recast() -> TaxoRecastRsp:
    taxanum = gvp("simple-taxanum", "0")
    from_to_final = {}
    doc_final = {}
    idx = 1
    while idx <= int(taxanum):
        frm = gvp("simple-item-from-" + str(idx))
        tofinal = gvp("simple-item-recast-" + str(idx), "")
        todoc = gvp("simple-item-doc-" + str(idx), "")
        if tofinal == "":
            tofinal = "0"
        from_to_final[frm] = int(tofinal)
        doc_final[frm] = todoc
        idx += 1
    return TaxoRecastRsp(from_to=from_to_final, doc=doc_final)


def posted_modified_recast(dwca: bool) -> bool:
    modified = 0
    if dwca:
        taxanum = gvp("taxanum", "0")
        histo_worms = gvp("histo-worms", "{}")
        histo_recast = gvp("histo-recast", "{}")
        histo_doc = gvp("histo-doc", {})
        prefix = ""
        histo = {"worms": histo_worms, "recast": histo_recast, "doc": histo_doc}
    else:
        removerecast = gvp("remove-recast", "")
        taxanum = gvp("simple-taxanum", "0")
        histo_recast = gvp("simple-histo-recast", "{}")
        histo_doc = gvp("simple-histo-doc", "{}")
        prefix = "simple-"
        histo = {"recast": histo_recast, "doc": histo_doc}
    if taxanum != "0" or removerecast == "remove":
        return True
    for k, v in histo.items():
        idx = 1
        data = json.loads(v)
        while idx <= int(taxanum):
            to = gvp(prefix + "item-" + k + "-" + str(idx))
            frm = gvp(prefix + "item-from-" + str(idx))
            print(" to=" + to + " from=", frm)
            if frm in data:
                keep = data[frm]
                if str(to) != str(keep):
                    modified += 1
            else:
                modified += 1
            idx += 1
    return modified > 0
