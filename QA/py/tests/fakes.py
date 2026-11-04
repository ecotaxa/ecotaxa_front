"""
Fake back-end for the front-end tests.

Every generated API class (to_back.ecotaxa_cli_py.api.*) used through appli.utils.ApiClient is
replaced by a strict mock: a call to a method that the test did not configure is recorded as
"unexpected" and fails the test at teardown, so no back-end call goes unnoticed.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from unittest.mock import MagicMock

from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.models import (
    Constants,
    UserModelWithRights,
    MinUserModel,
)

DATA_DIR = Path(__file__).parent / "data"

# Role ids, see appli.constants.API_GLOBAL_ROLES
ROLE_APP_ADMIN = 2
ROLE_USERS_ADMIN = 3


class UnexpectedBackendCall(AssertionError):
    pass


class FakeBackend:
    """One strict MagicMock per generated API class."""

    def __init__(self) -> None:
        self._apis: Dict[type, MagicMock] = {}
        self.unexpected: List[str] = []
        self.calls: List[Tuple[str, str, tuple, dict]] = []

    def api(self, api_class: type) -> MagicMock:
        if api_class not in self._apis:
            mock = MagicMock(spec=api_class, name=api_class.__name__)
            for name, _ in inspect.getmembers(api_class, inspect.isfunction):
                if name.startswith("_"):
                    continue
                getattr(mock, name).side_effect = self._unexpected(api_class, name)
            self._apis[api_class] = mock
        return self._apis[api_class]

    def _unexpected(self, api_class: type, name: str) -> Callable:
        def _raise(*args, **kwargs):
            msg = f"unexpected back-end call {api_class.__name__}.{name}(args={args}, kwargs={kwargs})"
            self.unexpected.append(msg)
            raise UnexpectedBackendCall(msg)

        return _raise

    def on(
        self,
        api_class: type,
        method: str,
        returns: Any = None,
        raises: Optional[BaseException] = None,
        side_effect: Optional[Callable] = None,
    ) -> MagicMock:
        """Configure api_class.method, returns the method mock for later assertions."""
        meth = getattr(self.api(api_class), method)
        if raises is not None:
            meth.side_effect = raises
        elif side_effect is not None:
            meth.side_effect = side_effect
        else:
            meth.side_effect = None
            meth.return_value = returns
        return meth


def api_exception(status: int, detail: Any = "error") -> ApiException:
    exc = ApiException(status=status, reason="Fake")
    exc.body = json.dumps({"detail": detail})
    return exc


# ---------------------------------------------------------------- model factories


def load_constants() -> Constants:
    with open(DATA_DIR / "used_constants.json") as f:
        return Constants(**json.load(f))


def make_user(
    id: int = 42,
    roles: Tuple[int, ...] = (),
    status: int = 1,
    email: str = "user@example.org",
    name: str = "Test User",
    **kw,
) -> UserModelWithRights:
    return UserModelWithRights(
        id=id,
        email=email,
        name=name,
        status=status,
        organisation=kw.pop("organisation", "Test Org"),
        country=kw.pop("country", "France"),
        mail_status=kw.pop("mail_status", True),
        can_do=list(roles),
        last_used_projects=kw.pop("last_used_projects", []),
        **kw,
    )


def make_min_user(id: int = 42, name: str = "Test User", email: str = "user@example.org"):
    return MinUserModel(id=id, name=name, email=email, organisation="Test Org")


def model(cls: Type, **kw):
    """Build any generated model without client-side validation (only what the test needs)."""
    from to_back.ecotaxa_cli_py.configuration import Configuration

    conf = Configuration()
    conf.client_side_validation = False
    return cls(local_vars_configuration=conf, **kw)


def make_project(projid=1, status="Annotate", **kw):
    from to_back.ecotaxa_cli_py.models import ProjectModel

    base = dict(
        projid=projid,
        title="Test project",
        status=status,
        access="1",
        instrument="Zooscan",
        managers=[make_min_user(id=42)],
        annotators=[],
        viewers=[],
        formulae=None,
        comments="",
        cnn_network_id=None,
        contact=None,
        obj_free_cols={},
        sample_free_cols={},
        acquisition_free_cols={},
        process_free_cols={},
        highest_right="Manage",
    )
    base.update(kw)
    return model(ProjectModel, **base)


def make_collection(id=1, title="My collection", project_ids=(1,)):
    from to_back.ecotaxa_cli_py.models import CollectionModel

    return model(
        CollectionModel,
        id=id,
        title=title,
        short_title="MC",
        external_id="",
        external_id_system="",
        citation="",
        license="CC BY 4.0",
        abstract="",
        description="",
        project_ids=list(project_ids),
        provider_user=make_min_user(),
        contact_user=make_min_user(),
        creator_users=[],
        creator_organisations=[],
        associate_users=[],
        associate_organisations=[],
        display_order=None,
        is_private=False,
    )


def populate(backend):
    """Plausible answers for the read calls of most pages: project 1, collection 1, organization/guest/user 3."""
    import responses
    from to_back.ecotaxa_cli_py.api import (
        CollectionsApi, GuestsApi, InstrumentsApi, JobsApi, MiscApi, OrganizationsApi,
        ProjectsApi, SamplesApi, TaxonomyTreeApi, UsersApi,
    )
    from to_back.ecotaxa_cli_py.models import GuestModel, OrganizationModel, ProjectTaxoStatsModel

    org = model(OrganizationModel, id=3, name="IMEV", directories="edmo:1278")
    backend.on(ProjectsApi, "project_query", returns=make_project(1))
    backend.on(ProjectsApi, "project_collections", returns=[])
    backend.on(ProjectsApi, "project_set_get_user_stats", returns=[])
    # with taxa_ids="all" the back-end answers one record per used taxon
    backend.on(
        ProjectsApi,
        "project_set_get_stats",
        returns=[
            model(ProjectTaxoStatsModel, projid=1, used_taxa=[45], nb_unclassified=1, nb_validated=2, nb_dubious=0, nb_predicted=3)
        ],
    )
    backend.on(OrganizationsApi, "search_organizations", returns=[org])
    backend.on(OrganizationsApi, "get_organizations", returns=[org])
    backend.on(UsersApi, "get_users", returns=[make_user(id=3)])
    backend.on(UsersApi, "get_current_user_prefs", returns="")
    backend.on(GuestsApi, "get_guests", returns=[
        model(GuestModel, id=3, name="Guest", email="g@example.org", country="France", orcid=None, organisation="IMEV")
    ])
    backend.on(CollectionsApi, "get_collection", returns=make_collection(1))
    backend.on(TaxonomyTreeApi, "query_taxa_set", returns=[])
    backend.on(TaxonomyTreeApi, "pull_taxa_update_from_central", returns={"error": None, "inserts": 0, "updates": 0})
    backend.on(MiscApi, "query_ml_models", returns=[])
    backend.on(InstrumentsApi, "instrument_cnn_networks", returns={})
    backend.on(SamplesApi, "samples_search", returns=[])
    backend.on(SamplesApi, "sample_set_get_stats", returns=[])
    backend.on(JobsApi, "list_jobs", returns=[])
    backend.requests.add(responses.GET, "http://backend.test/projects/search", json=[])
    return backend
