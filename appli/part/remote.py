#
# Holder for interface with 'remote' system, namely EcoTaxa
#
from typing import List, Tuple, Dict, Any, Union

from flask import Request
from werkzeug.local import LocalProxy

from to_back.ecotaxa_cli_py import ApiClient, TaxonModel
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi


class EcoTaxaInstance(object):
    """
        Access to a remote EcoTaxa instance via API calls.
    """

    def __init__(self, base_url: str, request_or_cookie: Union[str, LocalProxy, Request]):
        self.base_url = base_url + "api"
        if isinstance(request_or_cookie, LocalProxy):
            request_or_cookie = request_or_cookie.cookies.get('session')
        self.token = request_or_cookie

    def _get_client(self):
        ret = ApiClient()
        ret.configuration.access_token = self.token
        ret.configuration.host = self.base_url
        return ret

    def query_taxa_set(self, classif_ids: List[int]) -> List[TaxonModel]:
        tta = TaxonomyTreeApi(self._get_client())
        ret = []
        # This ends up in a '%2C'-separated list in the URL, as it's a GET.
        # So we have to take care about the query length -> split in manageable parts.
        params_char_len = 0
        params = []
        for an_id in classif_ids:
            an_id_str = str(an_id)
            params.append(an_id_str)
            params_char_len += 3 + len(an_id_str)
            if params_char_len > 32768:
                ret.extend(tta.query_taxa_set(",".join(params)))
                params_char_len = 0
                params.clear()
        ret.extend(tta.query_taxa_set(",".join(params)))
        return ret

    def get_taxo(self, classif_ids: List[int]) -> List[Tuple[int, str]]:
        """
            Return taxonomy information for given list of IDs
        """
        res = self.query_taxa_set(classif_ids)
        return [(r.id, r.display_name) for r in res]

    @staticmethod
    def lt_tree(names: List[str]):
        return ">".join(reversed(names))

    @staticmethod
    def parent_heses(names: List[str]):
        taxo = names[0]
        try:
            parent = names[1]
        except IndexError:  # no parent
            return taxo
        return "%s(%s)" % (taxo, parent)

    def get_taxo2(self, classif_ids: List[int]) -> List[Dict[str, Any]]:
        """
            Return taxonomy information for given list of IDs, another format...
        """
        res = self.query_taxa_set(classif_ids)
        return [{"classif_id": r.id, "nom": r.display_name, "tree": self.lt_tree(r.lineage)}
                for r in res]

    def get_taxo3(self, classif_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
            Return taxonomy information for given list of IDs, third format...
        """
        res = self.query_taxa_set(classif_ids)
        return {r.id: {"id": r.id, "nom": self.parent_heses(r.lineage), "tree": self.lt_tree(r.lineage)}
                for r in res}

    def get_taxo_children(self, classif_ids: List[int], res: List[int]) -> None:
        """
            Get immediate children for each category ID.
        """
        for srch_id in self.query_taxa_set(classif_ids):
            res.extend(srch_id.children)

    def get_taxo_subtree(self, classif_id: int) -> List[int]:
        """
            Get all descendant category IDs + self, for the given one.
        """
        ret = [classif_id]
        search = [classif_id]
        level_res = []
        while True:
            level_res.clear()
            self.get_taxo_children(search, level_res)
            if len(level_res) == 0:
                break
            ret.extend(level_res)
            search = level_res.copy()
        return ret
