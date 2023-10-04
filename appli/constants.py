from typing import Final
from collections import OrderedDict

ClassifQual: Final = {"P": "predicted", "D": "dubious", "V": "validated"}

DayTimeList: Final = {"A": "Dawn", "D": "Day", "U": "Dusk", "N": "Night"}

# The object DB columns that can be mapped by the user, hence queried
# TODO: Put server-side
MappableObjectColumns: Final = [
    "objtime",
    "objdate",
    "latitude",
    "longitude",
    "depth_min",
    "depth_max",
    "random_value",
]
MappableObjectColumnsSet: Final = set(MappableObjectColumns)

SortableObjectFields: Final = OrderedDict(
    [
        ("orig_id", "Image Name"),
        ("classif_auto_score", "Score"),
        ("classif_when", "Validation date"),
        ("classif_auto_when", "Prediction date"),
    ]
)

# We need another paradigm as both sample, acquisition and object have an orig_id column
MappableParentColumns: Final = ["sam_orig_id", "acq_orig_id"]

TaxoType: Final = {"P": "Phylo", "M": "Morpho"}
TaxoStatus: Final = {"A": "Active", "D": "Deprecated", "N": "Not reviewed"}

AdministratorLabel: Final = "Application Administrator"
UserAdministratorLabel: Final = "Users Administrator"

API_GLOBAL_ROLES: Final = {
    2: AdministratorLabel,
    3: UserAdministratorLabel,
}

# Override default home page with some external (to app) files
# TODO: It can be discussed if these files are local to the python front-end or should be stored on the back-end instead
APP_MANAGER_MESSAGE_FILE = "config/appmanagermsg.html"
CUSTOM_HOME_TOP = "config/hometop.html"
CUSTOM_HOME_BOTTOM = "config/homebottom.html"
# settings for account creation - if exists and valid email a mail is sent after registration for external validation of account
# new interface ( path + name of static rep for css and js)
GUI_PATH = "/gui"
# translations path i18n
TRANSLATION_PATH = "i18n"
# translations default locale

KNOWN_LANGUAGES = [
    "en",
    "pt",
    "zh",
    "fr",
]


def is_static_unprotected(path: str) -> bool:
    """For these entry points, we just serve with not much check, security is elsewhere.
    This is for dev. environment, as nginx does proper redirects in production"""
    for a_start in ("/static/", "/vault/", "/api/"):
        if path.startswith(a_start):
            return True
    return False
