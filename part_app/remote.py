#
# Holder for interface with 'remote' system, namely EcoTaxa
#
from datetime import datetime
from typing import List, Tuple, Dict, Any, Union, Optional

from flask import Request
from werkzeug.local import LocalProxy

from to_back.ecotaxa_cli_py import ApiClient, TaxonModel, ProjectModel, UserModelWithRights, ApiException, \
    SampleModel, ObjectSetQueryRsp, UserModel, SampleTaxoStatsModel
from to_back.ecotaxa_cli_py.api import TaxonomyTreeApi, ProjectsApi, SamplesApi, UsersApi, ObjectsApi

from .urls import ECOTAXA_API_URL


class EcoTaxaInstance(object):
    """
        Access to a remote EcoTaxa instance via API calls.
    """

    def __init__(self, request_or_cookie: Union[str, LocalProxy, Request]):
        self.base_url = ECOTAXA_API_URL
        if isinstance(request_or_cookie, LocalProxy):
            request_or_cookie = request_or_cookie.cookies.get('session')
        self.token = request_or_cookie
        # A bit of caching as instances don't survive a HTTP request
        self.users_by_id = {}

    def _get_client(self):
        ret = ApiClient()
        ret.configuration.access_token = self.token
        ret.configuration.host = self.base_url
        return ret

    @staticmethod
    def _valid_URL_chunks(ids: List[int]):
        """
            Generator for coma-separated list of IDs, with a max length for URL compliance.
        """
        params_char_len = 0
        params = []
        for an_id in ids:
            an_id_str = str(an_id)
            params.append(an_id_str)
            params_char_len += 3 + len(an_id_str)  # 3 is '%2C'
            if params_char_len > 32768:
                yield ",".join(params)
                params_char_len = 0
                params.clear()
        yield ",".join(params)

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

    def get_user_by_id(self, userid: int) -> Optional[UserModel]:
        """
            Return any EcoTaxa user information
        """
        if userid in self.users_by_id:
            return self.users_by_id[userid]
        usa = UsersApi(self._get_client())
        try:
            usr: UserModel = usa.get_user(userid)
            ret = usr
        except ApiException as ae:
            if ae.status in (401, 403):
                ret = None
            else:
                raise
        self.users_by_id[userid] = ret
        return ret

    def get_users_admins(self) -> List[UserModel]:
        """
            Return user administrators.
        """
        usa = UsersApi(self._get_client())
        return usa.get_users_admins()

    def query_taxa_set(self, classif_ids: List[int]) -> List[TaxonModel]:
        tta = TaxonomyTreeApi(self._get_client())
        ret = []
        for a_param_chunk in self._valid_URL_chunks(classif_ids):
            ret.extend(tta.query_taxa_set(a_param_chunk))
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
        try:
            a_proj: ProjectModel = pra.project_query(project_id=project_id)
        except ApiException as ae:
            if ae.status in (401, 403):
                return None
            else:
                raise
        return a_proj

    def create_new_project(self, title: str) -> Optional[ProjectModel]:
        """
            Create a project with this title.
        """
        pra = ProjectsApi(self._get_client())
        try:
            req = {"title": title,
                   "visible": False}
            new_projid = pra.create_project(create_project_req=req)
        except ApiException as ae:
            if ae.status in (401, 403):
                return None
            else:
                raise
        return new_projid

    def search_projects(self, title: str) -> List[ProjectModel]:
        """
            Search projects by title (the EcoTaxa way)
            TODO: Factorize with get_visible_projects
        """
        pra = ProjectsApi(self._get_client())
        ret = pra.search_projects(title_filter=title, not_granted=False)
        granted = set([prj.projid for prj in ret])
        not_granted = pra.search_projects(title_filter=title, not_granted=True)
        # TODO: below is a workaround for not-logged users, in this case the list is twice the same
        ret.extend([prj for prj in not_granted if prj.projid not in granted])
        return ret

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

    def get_samples_stats(self, zoo_sample_ids: List[int]) -> List[SampleTaxoStatsModel]:
        """
            Get stats about samples, the usual ones: number, validated or not...
        """
        sma = SamplesApi(self._get_client())
        ret = []
        try:
            for a_param_chunk in self._valid_URL_chunks(zoo_sample_ids):
                ret.extend(sma.sample_set_get_stats(a_param_chunk))
        except ApiException as ae:
            if ae.status in (401, 403):
                return []
            else:
                raise
        return ret

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

    def search_objects_validated_after(self, projid: int, sampleid: Optional[int], part_sample_date: datetime):
        """
            Query all objects in given sample, return the prefix-less column names.
        """
        oba = ObjectsApi(self._get_client())
        filters = {"validfromdate": part_sample_date.strftime("%Y-%m-%d %H:%M"),
                   "window_size": 100}
        if sampleid is not None:
            filters["samples"] = str(sampleid)
        res: ObjectSetQueryRsp = oba.get_object_set(fields="obj.classif_when",
                                                    project_id=projid,
                                                    project_filters=filters)
        return res.object_ids
