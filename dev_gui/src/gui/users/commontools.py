import flask
from flask import request, render_template, flash, redirect, url_for
from werkzeug.exceptions import NotFound
from flask_login import current_user
from flask_babel import _
from typing import List
from appli import app, gvg, gvp, gvpm, constants
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    UsersApi,
    ResetPasswordReq,
    UserActivateReq,
    UserModelWithRights,
    ApiException,
    MiscApi,
)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from appli.gui.commontools import html_to_text, format_exception
from appli.gui.staticlistes import py_user
from appli.back_config import get_user_constants
from appli.security_on_backend import ApiUserWrapper

(
    ApiUserStatus,
    API_PASSWORD_REGEXP,
    API_EMAIL_VERIFICATION,
    API_ACCOUNT_VALIDATION,
    SHORT_TOKEN_AGE,
    PROFILE_TOKEN_AGE,
) = get_user_constants(request)
ACCOUNT_USER_CREATE = "create"
ACCOUNT_USER_EDIT = "edit"
IS_FROM_ADMIN = "admin"


def _get_captcha() -> list:
    no_bot = None
    reCaptchaID = app.config.get("RECAPTCHAID")
    if reCaptchaID:
        response = gvp("g-recaptcha-response")
        remoteip = _public_ip()
        no_bot = [remoteip, response]
    return no_bot


def check_is_users_admin() -> bool:
    # app admins are users admins
    return current_user.is_authenticated and current_user.is_admin == True


def make_user_response(code, message: str) -> tuple:
    return code, message, API_EMAIL_VERIFICATION, API_ACCOUNT_VALIDATION


def user_create(usrid: int, isfrom: str) -> tuple:
    if isfrom == IS_FROM_ADMIN and (not check_is_users_admin()):
        return None, py_user["notadmin"]
    token = gvp("token")
    if token:
        return user_account(-1, isfrom, action=ACCOUNT_USER_CREATE, token=token)
    else:
        # verify email before register
        posted = {"id": -1, "email": gvp("register_email"), "name": ""}
        return api_user_create(posted, token)


def user_edit(usrid: int, isfrom: str) -> tuple:
    if isfrom == IS_FROM_ADMIN and (not check_is_users_admin()):
        return make_user_response(None, py_user["notadmin"])

    elif usrid != current_user.api_user.id and isfrom != IS_FROM_ADMIN:
        return make_user_response(None, py_user["notauthorized"])
    return user_account(usrid, isfrom, action=ACCOUNT_USER_EDIT)


def api_get_user(usrid: int) -> UserModelWithRights:
    with ApiClient(UsersApi, request) as api:
        if isinstance(usrid, int) and usrid > 0:
            if usrid == current_user.id:
                return api.show_current_user()
            elif check_is_users_admin():
                user = api.get_users(ids=str(usrid))
                if len(user):
                    return user[0]
    return None


def api_user_create(posted: dict, token: str = None) -> tuple:
    try:
        no_bot = _get_captcha()
        new_user = UserModelWithRights(**posted)
        with ApiClient(UsersApi, request) as api:
            api.create_user(user_model_with_rights=new_user, no_bot=no_bot, token=token)
        response = 0

    except ApiException as ae:
        return format_exception(ae)

    return make_user_response(response, None)


def api_user_activate(
    user_id: int, status: int, token: str = None, reason: str = None, bot: bool = False
) -> tuple:

    password = None
    try:
        if bot:
            no_bot = _get_captcha()
            st = ["n"]
            password = gvp("password", None)
            if password is None:
                return 1, py_user["passwordrequired"]
            else:
                activatereq = UserActivateReq(token=token, password=password)
        else:
            no_bot = None
            st = [k for k, v in ApiUserStatus.items() if v == status]
            reason = gvp("reason", None)
            activatereq = UserActivateReq(reason=reason)
        if len(st):
            status_name = st[0]
        with ApiClient(UsersApi, request) as api:
            api.activate_user(
                user_id,
                status_name,
                activatereq,
                no_bot=no_bot,
            )
        api_current_user()
        # if current_user.is_authenticated:
        #   message = None
        if API_EMAIL_VERIFICATION != False:
            if token:
                if API_ACCOUNT_VALIDATION != False:
                    message = py_user["statusnotauthorized"]["0"]
                else:
                    message = py_user["profilesuccess"]["activate"]
            else:
                message = py_user["statusnotauthorized"]["waiting"]
        return make_user_response(0, message)

    except ApiException as ae:
        return format_exception(ae)


def user_account(
    usrid: int, isfrom: str, action: str = None, token: str = None
) -> tuple:
    if action != None:
        if isinstance(usrid, int) == False:
            return make_user_response(None, py_user["invaliddata"])
    fields = [
        "email",
        "organisation",
        "country",
        "usercreationreason",
    ]
    if action == "create":
        fields = ["firstname", "lastname", "password"] + fields
    else:
        fields = ["name"] + fields + ["newpassword"]
    posted = {a_field: gvp(a_field).strip() for a_field in fields}
    posted["id"] = usrid
    posted["email"] = posted["email"].strip()
    if "lastname" in posted.keys():
        posted["name"] = posted["firstname"] + " " + posted["lastname"]
        del posted["firstname"]
        del posted["lastname"]

    if "newpassword" in posted.keys():
        if len(posted["newpassword"]) > 6:
            posted["password"] = posted["newpassword"]
        else:
            del posted["newpassword"]
    if isfrom == IS_FROM_ADMIN:
        posted["status"] = int(gvp("status", 0))
        posted["can_do"] = gvpm("can_do")
    response = None
    redir = None
    if action == ACCOUNT_USER_EDIT:
        if usrid == -1:
            return 1, "nouserid"
        elif current_user.id == usrid:
            api_user = current_user.api_user.to_dict()
            api_user.update(posted)
        else:
            api_user = UserModelWithRights(**posted).to_dict()
            currentemail = gvp("currentemail", None)
        if "newpassword" in api_user:
            del api_user["newpassword"]
        else:
            del api_user["password"]
        if isfrom != IS_FROM_ADMIN:
            del api_user["status"]
        del api_user["mail_status"]
        del api_user["status_date"]
        del api_user["mail_status_date"]
        with ApiClient(UsersApi, request) as api:
            user_id = api.update_user(user_id=usrid, user_model_with_rights=api_user)
        if user_id == -1:
            return make_user_response(1, py_user["notmodified"])
        else:
            api_current_user()
            message = py_user["profilesuccess"]["update"]
            if not current_user.is_authenticated:
                if API_EMAIL_VERIFICATION != False:
                    if api_user["email"] != currentemail:
                        message = py_user["statusnotauthorized"]["emailchanged"]
                    elif (
                        token
                        and API_ACCOUNT_VALIDATION != False
                        and api_user != before_user
                    ):
                        message = py_user["statusnotauthorized"]["0"]
                    else:
                        # should not comme here
                        pass
            return make_user_response(0, message)
    elif action == ACCOUNT_USER_CREATE:
        if usrid != -1:
            return make_user_response(1, py_user["errusrid"])
        else:
            response = api_user_create(posted, token)
            return response
    else:
        return make_user_response(1, py_user["usernoaction"])


# def create_verifreq(recipient, token, link):
#    return dict(
#        {"recipient": recipient, "ip": _public_ip(), "token": token, "link": link}
#    )


def account_page(
    action: str, usrid: int, isfrom: str, template: str, token: str = None
) -> str:
    reCaptchaID = None
    if action != ACCOUNT_USER_CREATE and not isinstance(usrid, int):
        raise NotFound()
    if action == ACCOUNT_USER_CREATE:
        user = None
        if isfrom != IS_FROM_ADMIN:
            reCaptchaID = app.config.get("RECAPTCHAID")
            if token is not None:
                id = _get_value_from_token(token, "id", age=PROFILE_TOKEN_AGE)
                email = _get_mail_from_token(token, age=PROFILE_TOKEN_AGE)
                if email is None:
                    return redirect(url_for("gui_register", resp=1))
                if id is None:
                    id = "-1"
                    user = dict({"id": int(id), "email": email})
                else:
                    # it is a request to modify
                    user = dict(
                        {
                            "id": int(id),
                            "email": email,
                            "reason": _get_value_from_token(token, "reason"),
                            "action": _get_value_from_token(token, "acttion"),
                        }
                    )
    else:
        user = api_get_user(usrid)
        if user == None:
            raise NotFound(description=py_user["notfound"])

    if (
        token is not None
        or IS_FROM_ADMIN
        or action == ACCOUNT_USER_EDIT
        or reason is not None
    ):
        with ApiClient(UsersApi, request) as api:
            organisations = api.search_organizations(name="%%")
            organisations.sort()
        roles = [(str(num), lbl) for num, lbl in constants.API_GLOBAL_ROLES.items()]
        country_list = get_country_list(request)
        countries = sorted(country_list)
    else:
        roles = (None,)
        organisations = None
        countries = None

    return render_template(
        template,
        user=user,
        roles=roles,
        countries=countries,
        organisations=organisations,
        createaccount=(action == ACCOUNT_USER_CREATE),
        token=token,
        reCaptchaID=reCaptchaID,
    )


def reset_password(
    email: str, token: str = None, pwd: str = None, url: str = None
) -> str:
    err = None
    no_bot = _get_captcha()
    if token:
        email = None
    resetreq = ResetPasswordReq(id=-1, email=email, password=pwd)
    with ApiClient(UsersApi, request) as api:
        api.reset_user_password(resetreq, no_bot=no_bot, token=token)
    return 0, None


def _public_ip() -> str:
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        return request.environ["REMOTE_ADDR"]
    else:
        return request.environ["HTTP_X_FORWARDED_FOR"]


def get_country_list(request) -> list:
    with ApiClient(MiscApi, request) as api:
        consts: Constants = api.used_constants()
        return consts.countries


def _get_value_from_token(
    token: str, name: str, age: int = SHORT_TOKEN_AGE, verifip=False
) -> str:
    from itsdangerous import (
        BadSignature,
        TimestampSigner,
        SignatureExpired,
        URLSafeTimedSerializer,
    )

    auths = URLSafeTimedSerializer(
        app.config["MAILSERVICE_SECRET_KEY"],
        salt=b"mailservice_salt",
        signer=TimestampSigner,
    )

    try:
        value = auths.loads(token, max_age=age * 3600)
    except (BadSignature, SignatureExpired):
        flash("Bad signature - token has expired", "error")
        return None
    if value.get(name):
        if verifip == False or (value.get("ip") == _public_ip()):
            return value.get(name)
    else:
        return None


def _get_mail_from_token(token: str, verifip=False, age: int = SHORT_TOKEN_AGE) -> str:
    email = _get_value_from_token(token, "email", age)
    if email is None:
        flash("Error invalid token", "error")
    return email


def api_password_regexp() -> str:
    return API_PASSWORD_REGEXP


def api_current_user(redir: bool = True):
    if not current_user.is_authenticated:
        if redir:
            return redirect(url_for("gui_login"))
    else:
        from appli.security_on_backend import user_from_api, anon_user

        curr_user = user_from_api(current_user.id)
        from flask_login import logout_user, confirm_login

        if (
            curr_user.email != current_user.email
            or curr_user.id <= 0
            or curr_user.status != ApiUserStatus["active"]
        ):
            logout_user()
        # TODO solve problems here
        elif current_user.is_authenticated:
            confirm_login()
