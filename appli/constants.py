VUE_PATH = "/gui"

from collections import OrderedDict

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import MiscApi
from to_back.ecotaxa_cli_py.models import Constants

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


def GetClassifQualClass(q):
    """
        Return CSS class from classification qualif.
    """
    return 'status-' + ClassifQual.get(q, "unknown")


def get_app_manager_mail(request):
    with ApiClient(MiscApi, request) as api:
        consts: Constants = api.used_constants_constants_get()
    mgr_coords = consts.app_manager
    if mgr_coords[0] and mgr_coords[1]:
        return "<a href='mailto:{1}'>{0} ({1})</a>".format(mgr_coords[0], mgr_coords[1])
    return ""
