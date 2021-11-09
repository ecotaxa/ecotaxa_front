#
# Holder for interface with 'remote' system, namely EcoTaxa
#
from typing import List, Tuple, Dict, Any

from flask import Request

from to_back.ecotaxa_cli_py import ApiClient, TaxonModel
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi


class EcoTaxaInstance(object):
    """
        Access to a remote EcoTaxa instance via API calls.
    """

    def __init__(self, base_url: str, request: Request):
        self.base_url = base_url + "api"
        self.token = request.cookies.get('session')

    def _get_client(self):
        ret = ApiClient()
        ret.configuration.access_token = self.token
        ret.configuration.host = self.base_url
        return ret

    def get_taxo(self, classif_ids: List[int]) -> List[Tuple[int, str]]:
        """
            Return taxonomy information for given list of IDs
        """
        tta = TaxonomyTreeApi(self._get_client())
        param = ','.join([str(an_id) for an_id in classif_ids])
        res: List[TaxonModel] = tta.query_taxa_set(param)
        return [(r.id, r.display_name) for r in res]

    @staticmethod
    def lt_tree(names: List[str]):
        return ">".join(reversed(names))

    def get_taxo2(self, classif_ids: List[int]) -> List[Dict[str, Any]]:
        """
            Return taxonomy information for given list of IDs, another format...
        """
        tta = TaxonomyTreeApi(self._get_client())
        param = ','.join([str(an_id) for an_id in classif_ids])
        res: List[TaxonModel] = tta.query_taxa_set(param)
        # TODO toto
        return [{"classid_id": r.id, "nom": r.display_name, "tree": self.lt_tree(r.lineage)} for r in res]
