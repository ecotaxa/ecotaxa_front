#
# Data which is not supposed to change during back-end run
#
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import MiscApi, Constants


def get_app_manager_mail(request):
    with ApiClient(MiscApi, request) as api:
        consts: Constants = api.used_constants()
    mgr_coords = consts.app_manager
    if mgr_coords[0] and mgr_coords[1]:
        return "<a href='mailto:{1}'>{0} ({1})</a>".format(mgr_coords[0], mgr_coords[1])
    return ""