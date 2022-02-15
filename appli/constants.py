VUE_PATH = "/gui"

BACKEND_HOST = "localhost"
BACKEND_PORT = 8000
BACKEND_URL = "http://%s:%d" % (BACKEND_HOST, BACKEND_PORT)

from collections import OrderedDict

ClassifQual = {'P': 'predicted', 'D': 'dubious', 'V': 'validated'}

DayTimeList = {'A': 'Dawn', 'D': 'Day', 'U': 'Dusk', 'N': 'Night'}

# The object DB columns that can be mapped by the user, hence queried
# TODO: Put server-side
MappableObjectColumns = ['objtime', 'objdate', 'latitude', 'longitude', 'depth_min', 'depth_max', 'random_value']
MappableObjectColumnsSet = set(MappableObjectColumns)

SortableObjectFields = OrderedDict([("orig_id", "Image Name"),
                                    ("classif_auto_score", "Score"),
                                    ("classif_when", "Validation date"),
                                    ("classif_auto_when", "Prediction date")])

# We need another paradigm as both sample, acquisition and object have an orig_id column
MappableParentColumns = ["sam_orig_id", "acq_orig_id"]

TaxoType = {'P': 'Phylo', 'M': 'Morpho'}
TaxoStatus = {'A': 'Active', 'D': 'Deprecated', 'N': 'Not reviewed'}


def GetClassifQualClass(q):
    """
        Return CSS class from classification qualif.
    """
    return 'status-' + ClassifQual.get(q, "unknown")


AdministratorLabel = "Application Administrator"
UserAdministratorLabel = "Users Administrator"
ProjectCreatorLabel = "Project creator"
TaxonCreatorLabel = "Taxon Creator"

API_GLOBAL_ROLES = {1: ProjectCreatorLabel,
                    2: AdministratorLabel,
                    3: UserAdministratorLabel,
                    4: TaxonCreatorLabel}


def is_static_unprotected(path: str):
    """ For these entry points, we just serve with not much check, security is elsewhere.
        This is for dev. environment, as nginx does proper redirects in production """
    for a_start in ("/static/", "/vault/", "/api/"):
        if path.startswith(a_start):
            return True
    return False
