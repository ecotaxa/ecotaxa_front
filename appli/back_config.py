#
# Data which is not supposed to change during back-end run
#
from urllib import parse
from typing import List
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import MiscApi, Constants


def get_app_manager_mail(request, subject=""):
    with ApiClient(MiscApi, request) as api:
        consts: Constants = api.used_constants()
    mgr_coords = consts.app_manager
    if mgr_coords[0] and mgr_coords[1]:
        if subject:
            subject = "?" + parse.urlencode({"subject": subject}).replace("+", "%20")
        return "<a href='mailto:{1}{2}'>{0} ({1})</a>".format(
            mgr_coords[0], mgr_coords[1], subject
        )
    return ""


def get_country_names(request) -> List[str]:
    with ApiClient(MiscApi, request) as api:
        consts: Constants = api.used_constants()
        return consts.countries


def get_user_constants(request) -> tuple:
    from flask import current_app

    if not "API_USER_CONSTANTS" in current_app.config:
        with ApiClient(MiscApi, request) as api:
            consts: Constants = api.used_constants()
        current_app.config["API_USER_CONSTANTS"] = (
            consts.user_status,
            consts.password_regexp,
            consts.email_verification,
            consts.account_validation,
            consts.short_token_age,
            consts.profile_token_age,
            consts.recaptchaid,
            consts.add_ticket,
        )
    return current_app.config["API_USER_CONSTANTS"]
