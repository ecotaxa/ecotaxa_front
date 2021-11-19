#
# Holder for interface with 'remote' system, namely EcoTaxa
#
from typing import List, Tuple, Dict, Any, Union, Optional

from flask import Request
from werkzeug.local import LocalProxy

from to_back.ecotaxa_cli_py import ApiClient, TaxonModel, ProjectModel, UsersApi, UserModelWithRights, ApiException, \
    SamplesApi, SampleModel, ObjectsApi, ObjectSetQueryRsp
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi, ProjectsApi


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

    def get_current_user(self) -> Optional[UserModelWithRights]:
        """
            Return currently connected EcoTaxa user
        """
        usa = UsersApi(self._get_client())
        try:
            usr: UserModelWithRights = usa.show_current_user()
            return usr
        except ApiException as ae:
            if ae.status in (401, 403):
                return None

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

    @staticmethod
    def parent_id(id_lineage: List[int]) -> Optional[int]:
        try:
            return id_lineage[1]
        except IndexError:  # no parent
            return None

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
        lineage_of = self.lt_tree
        parent_of = self.parent_id
        return {r.id: {"id": r.id, "pid": parent_of(r.id_lineage),
                       "nom": self.parent_heses(r.lineage),
                       "tree": lineage_of(r.lineage)}
                for r in res}

    def get_taxo_tree(self, classif_id: int, cache: Dict[int, str]) -> str:
        """
            Return textual lineage for the given category, store in cache for cheaper repeated calls.
        """
        ret = cache.get(classif_id)
        if ret is None:
            res = self.query_taxa_set([classif_id])[0]
            ret = self.lt_tree(res.lineage)
            cache[classif_id] = ret
        return ret

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

    def get_taxo_all_parents(self, classif_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
            Get all parent categories + self, for the given ones, recursively until roots.
        """
        parent_ids = set()  # Use a set to avoid overlap
        res = self.query_taxa_set(classif_ids)
        for r in res:
            # queried taxa appear in the id_lineage, so it's self+all parents
            parent_ids.update(r.id_lineage)
        return self.get_taxo3(list(parent_ids))

    def get_visible_projects(self) -> List[ProjectModel]:
        """
            Get all visible projects.
        """
        pra = ProjectsApi(self._get_client())
        ret = pra.search_projects(title_filter="", not_granted=False)
        granted = set([prj.projid for prj in ret])
        not_granted = pra.search_projects(title_filter="", not_granted=True)
        # TODO: below is a workaround for not-logged users, in this case the list is twice the same
        ret.extend([prj for prj in not_granted if prj.projid not in granted])
        return ret

    def get_project(self, project_id: int) -> Optional[ProjectModel]:
        """
            Get a single project by its ID.
            Return None if not found (from API point of view, meaning it could be missing or not visible)
        """
        pra = ProjectsApi(self._get_client())
        a_proj: ProjectModel = pra.project_query(project_id=project_id)
        return a_proj

    def search_samples(self, projid: int, orig_id: str) -> List[SampleModel]:
        """
            Inside given project, look for samples by orig_id.
        """
        sma = SamplesApi(self._get_client())
        res = sma.samples_search(str(projid), orig_id)
        # Search is case-insensitive and we need exact match
        return [a_sam for a_sam in res
                if a_sam.orig_id == orig_id]

    def all_samples_for_project(self, projid: int):
        sma = SamplesApi(self._get_client())
        return sma.samples_search(str(projid), "")

    def get_objects_for_sample(self, projid: int, sampleid: int, cols: List[str], only_validated: bool):
        """
            Query all objects in given sample, return the prefix-less column names.
        """
        oba = ObjectsApi(self._get_client())
        filters = {"samples": str(sampleid)}
        if only_validated:
            filters["statusfilter"] = 'V'
        res: ObjectSetQueryRsp = oba.get_object_set(fields=",".join(cols),
                                                    project_id=projid,
                                                    project_filters=filters)
        ret = []
        for an_obj in res.details:
            db_like_obj = {col.split(".", 1)[1]: val for col, val in zip(cols, an_obj)}
            ret.append(db_like_obj)
        return ret
