#
# Data which is not supposed to change during back-end run
#
from urllib import parse
from typing import List
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import MiscApi, Constants
from flask import request


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


def get_back_constants(_type) -> tuple:
    from flask import current_app

    if not _type in current_app.config:
        with ApiClient(MiscApi, request) as api:
            consts: Constants = api.used_constants()
        if _type == "USER":
            current_app.config["API_" + _type + "_CONSTANTS"] = (
                consts.user_status,
                consts.user_type,
                consts.password_regexp,
                consts.email_verification,
                consts.account_validation,
                consts.short_token_age,
                consts.profile_token_age,
                consts.recaptchaid,
            )
        elif _type == "ACCESS":
            current_app.config["API_" + _type + "_CONSTANTS"] = consts.access
        elif _type == "LICENSE":
            current_app.config["API_" + _type + "_CONSTANTS"] = (consts.license_texts,)
        elif _type == "MANAGER":
            current_app.config["API_" + _type + "_CONSTANTS"] = consts.app_manager
        elif _type == "PEOPLEORG":
            current_app.config["API_" + _type + "_CONSTANTS"] = (
                consts.people_organization_directories
            )
        elif _type == "FORMULAE":
            current_app.config["API_" + _type + "_CONSTANTS"] = consts.formulae
    return current_app.config["API_" + _type + "_CONSTANTS"]


def get_user_constants() -> tuple:

    return get_back_constants("USER")
