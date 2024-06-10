import flask
from flask import request, render_template, flash, redirect, url_for
from werkzeug.exceptions import NotFound, Forbidden, UnprocessableEntity
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
    RECAPTCHAID,
) = get_user_constants(request)

ACCOUNT_USER_CREATE = "create"
ACCOUNT_USER_EDIT = "edit"


def _get_captcha() -> list:
    if RECAPTCHAID == True:
        response = gvp("g-recaptcha-response", None)
    else:
        response = encode_homecaptcha()

    remoteip = _public_ip()
    no_bot = [remoteip, response]
    return no_bot


def check_is_users_admin() -> bool:
    # app admins are users admins
    return current_user.is_authenticated and current_user.is_admin == True


def make_user_response(code, message: str) -> tuple:
    return code, message, API_EMAIL_VERIFICATION, API_ACCOUNT_VALIDATION


def user_register(token: str = None, partial: bool = False) -> str:
    if token is None and current_user.is_authenticated:
        raise UnprocessableEntity()
    reCaptchaID = None
    # google recaptcha or homecaptcha
    if RECAPTCHAID == True:
        reCaptchaID = app.config.get("RECAPTCHAID")
    action = ACCOUNT_USER_CREATE
    usrid = -1
    if token is not None:
        err, resp = _get_value_from_token(token, "id", age=PROFILE_TOKEN_AGE)
        if err == True:
            raise Forbidden(resp)
        else:
            usrid = int(resp)
        if usrid == -1:
            # short token life for account creation
            err, resp = _get_value_from_token(token, "id", age=SHORT_TOKEN_AGE)
            if err == True:
                raise Forbidden(resp)
            elif int(resp) != usrid:
                raise UnprocessableEntity(py_user["invaliddata"])
            pwd = None

        if request.method == "POST" or int(usrid) == -1:
            id = gvp("id", -1)
            if id == -1:
                return account_page(
                    action=action,
                    usrid=int(usrid),
                    isfrom=False,
                    template="v2/register.html",
                    token=token,
                )
    if request.method == "POST":
        id = gvp("id", -1)
        if int(id) == int(usrid):
            return user_create(int(id), isfrom=False, token=token, partial=partial)
        return account_page(
            action=action,
            usrid=int(usrid),
            isfrom=False,
            template="v2/register.html",
            api_email_verification=API_EMAIL_VERIFICATION,
            api_account_validation=API_ACCOUNT_VALIDATION,
            reCaptchaID=reCaptchaID,
            token=token,
        )

    return render_template(
        "v2/register.html",
        bg=True,
        token=token,
        usrid=usrid,
        api_email_verification=API_EMAIL_VERIFICATION,
        api_account_validation=API_ACCOUNT_VALIDATION,
        reCaptchaID=reCaptchaID,
    )


def _verifiy_validation_throw(
    usrid: int, isfrom: bool, action: str, age: int = SHORT_TOKEN_AGE
) -> tuple:
    token = gvp("token", None)
    if isfrom == True:
        if not check_is_users_admin():
            description = py_user["notadmin"]
            raise Forbidden(description=description)
    elif action == ACCOUNT_USER_CREATE:
        if API_EMAIL_VERIFICATION == True or (
            API_ACCOUNT_VALIDATION == True and usrid != -1
        ):
            if token != None:
                err, resp = _get_value_from_token(token, "id", age)
                if err == True:
                    raise Forbidden(resp)
                else:
                    usrid = int(resp)
            else:
                raise Forbidden(py_user["notauthorized"])

    return usrid, token


def _verify_pending_user_throw(id: int, email: str):
    pwd = gvp("password", None)
    if id != -1 and pwd != None:
        from appli.security_on_backend import login_validate

        yes, userdata = login_validate(email, pwd)
        if yes == True and userdata is not None:
            user = UserModelWithRights(**userdata)
            reason = (
                user.status_admin_comment or user.status == ApiUserStatus["pending"]
            )
            return user
    elif id == -1:
        return dict({"id": int(id), "email": email, "status_admin_comment": None})
    else:
        raise Forbidden(py_user["notauthorized"])


def user_create(
    usrid: int, isfrom: bool = False, token: str = None, partial: bool = False
) -> tuple:
    action = ACCOUNT_USER_CREATE
    posted = {}
    if usrid == -1:
        age = SHORT_TOKEN_AGE
    else:
        age = PROFILE_TOKEN_AGE
    if isfrom == True or API_EMAIL_VERIFICATION == False:
        resp = user_account(-1, isfrom, action=action, token=token)
        return resp
    elif token != None or API_EMAIL_VERIFICATION == False:
        if token != None:
            usrid, token = _verifiy_validation_throw(
                usrid, isfrom, action=action, age=age
            )
        posted = _user_posted_data(usrid, isfrom, action)
        resp = api_user_create(posted, token)
    # verify email before register to get a token or verify pass
    elif usrid == -1:
        posted = {
            "id": -1,
            "email": gvp("register_email"),
            "name": "",
        }
        resp = api_user_create(posted, token)

    redir = url_for("gui_index")
    if token is None:
        if resp[0] == 0:
            message = py_user["mailsuccess"] + py_user["checkspam"]
            type = "success"
        else:
            redir = url_for("gui_register")
            message = resp[1] + " " + py_user["mailerror"]
            type = "error"
    else:
        if resp[0] == 0:
            if len(resp) <= 3 or resp[3] == False:
                message = py_user["profilesuccess"]["create"]
            elif len(resp) >= 3 and resp[3] == True:
                message = py_user["statusnotauthorized"]["01"]
            else:
                message = resp[1]

            type = "success"
        else:
            redir = url_for("gui_register") + "/" + token
            err, action = _get_value_from_token(token, "action", age=PROFILE_TOKEN_AGE)
            if str(action or "") != "update":
                action = create
            message = resp[1] + py_user["profileerror"][action]
            type = "error"
    if partial:
        response = (resp[0], message, resp[2], resp[3])
        if posted and "email" in posted:
            email = posted["email"]
        else:
            email = ""
        return render_template(
            "v2/security/reply.html",
            bg=True,
            type="register",
            token=token,
            email=email,
            action=action,
            api_email_verification=API_EMAIL_VERIFICATION,
            api_account_validation=API_ACCOUNT_VALIDATION,
            response=response,
            partial=partial,
        )
    else:
        flash(message, type)
        return redirect(redir)


def user_edit(usrid: int, isfrom: bool = False) -> tuple:
    if isfrom == True and (not check_is_users_admin()):
        return make_user_response(None, py_user["notadmin"])
    elif usrid != current_user.api_user.id and isfrom != True:
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
    no_bot = _get_captcha()
    new_user = UserModelWithRights(**posted)
    with ApiClient(UsersApi, request) as api:
        try:
            user_id = api.create_user(
                user_model_with_rights=new_user, no_bot=no_bot, token=token
            )
            if user_id == -1:
                return make_user_response(1, py_user["profileerror"]["create"])
            elif API_ACCOUNT_VALIDATION == True:
                message = py_user["statusnotauthorized"]["01"]
            else:
                message = py_user["profilesuccess"]["create"]
            return make_user_response(0, message)
        except ApiException as ae:
            code = ae.status
            if ae.status in (401, 403):
                message = py_user["notauthorized"]
            elif ae.status == 404:
                message = py_user["notfound"]
            else:
                code, message = format_exception(ae)
            return make_user_response(code, message)


def api_user_activate(
    user_id: int, status: int, token: str = None, reason: str = None, bot: bool = False
) -> tuple:
    if API_EMAIL_VERIFICATION != True and API_ACCOUNT_VALIDATION != True:
        return make_user_response(403, py_user["novalidationservices"])
    password = None
    message = ""
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
        activatereq = UserActivateReq(reason=reason)
    if len(st):
        status_name = st[0]
    with ApiClient(UsersApi, request) as api:
        try:
            api.activate_user(
                user_id,
                status_name,
                activatereq,
                no_bot=no_bot,
            )
            api_current_user()
            # if current_user.is_authenticated:
            #   message = None
            status = gvp("status", "None")
            if token:
                if API_ACCOUNT_VALIDATION != False:
                    message = py_user["statusnotauthorized"]["0"]
                else:
                    message = py_user["profilesuccess"]["activate"]
            elif status == ApiUserStatus["pending"]:
                message = py_user["statusnotauthorized"]["waiting"]
            elif status == ApiUserStatus["active"]:
                message = py_user["status"]["active"]
            elif status == ApiUserStatus["inactive"]:
                message = py_user["status"]["inactive"]
            elif status == ApiUserStatus["blocked"]:
                message = py_user["status"]["blocked"]
            return make_user_response(0, message)

        except ApiException as ae:
            exception = format_exception(ae)
            return make_user_response(ae.status, exception[1])


def _user_posted_data(usrid: int, isfrom: bool, action: str = "create") -> dict:
    fields = [
        "email",
        "organisation",
        "country",
        "orcid",
        "usercreationreason",
    ]
    if action == "create":
        if usrid == -1:
            fields = ["firstname", "lastname", "password"] + fields
        else:
            fields = ["name", "password"] + fields
    else:
        fields = ["name", "newpassword"] + fields
    posted = {a_field: gvp(a_field).strip() for a_field in fields}
    posted["id"] = usrid
    posted["email"] = posted["email"].strip()
    posted["orcid"] = posted["orcid"].strip()
    if "lastname" in posted.keys():
        posted["name"] = posted["firstname"] + " " + posted["lastname"]
        del posted["firstname"]
        del posted["lastname"]

    if "newpassword" in posted.keys():
        if len(posted["newpassword"]) > 6:
            posted["password"] = posted["newpassword"]
        else:
            del posted["newpassword"]
    if isfrom == True:
        posted["status"] = int(gvp("status", 0))
        posted["can_do"] = gvpm("can_do")
    return posted


def user_account(
    usrid: int, isfrom: bool = False, action: str = None, token: str = None
) -> tuple:
    if isfrom == True and (not check_is_users_admin()):
        return None, py_user["notadmin"]
    if action != None:
        if isinstance(usrid, int) == False:
            return make_user_response(None, py_user["invaliddata"])
    posted = _user_posted_data(usrid, isfrom, action)
    response = None
    redir = None
    currentemail = gvp("currentemail", None)
    if action == ACCOUNT_USER_EDIT:
        if "newpassword" in posted:
            del posted["newpassword"]
        elif "password" in posted:
            del posted["password"]
        if usrid == -1:
            return 1, "nouserid"
        elif current_user.id == usrid:
            api_user = current_user.api_user.to_dict()
            api_user.update(posted)
        else:
            api_user = UserModelWithRights(**posted).to_dict()
        if "password" not in posted and "password" in api_user:
            del api_user["password"]
        if isfrom == True:
            if current_user.is_admin == True and current_user.id == usrid:
                api_user["status"] = current_user.api_user.status
                api_user["status_date"] = current_user.api_user.status_date
        else:
            del api_user["status"]
            del api_user["status_date"]
        del api_user["mail_status"]
        del api_user["mail_status_date"]

        with ApiClient(UsersApi, request) as api:
            try:
                user_id = api.update_user(
                    user_id=usrid, user_model_with_rights=api_user
                )
            except ApiException as ae:
                code = ae.status
                if ae.status in (401, 403):
                    message = py_messages["notauthorized"]
                elif ae.status == 404:
                    message = py_messages["notfound"]
                else:
                    message = format_exception(ae)[1]
                return make_user_response(code, message)
        if user_id == -1:
            return make_user_response(1, py_user["notmodified"])
        else:
            api_current_user()
            message = py_user["profilesuccess"]["update"]
            if not isfrom:
                if API_EMAIL_VERIFICATION != False:
                    if api_user["email"] != currentemail and (
                        current_user.is_anonymous or not current_user.active
                    ):
                        message = (
                            py_user["statusnotauthorized"]["emailchanged"]
                            + py_user["checkspam"]
                        )
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
    action: str, usrid: int, isfrom: bool, template: str, token: str = None
) -> str:
    reCaptchaID = None
    if action != ACCOUNT_USER_CREATE and not isinstance(usrid, int):
        raise NotFound()
    if action == ACCOUNT_USER_CREATE:
        user = {"id": -1}
        if isfrom != True:
            # google recaptcha or homecaptcha
            if RECAPTCHAID == True:
                reCaptchaID = app.config.get("RECAPTCHAID")
            if token is not None:
                err, resp = _get_value_from_token(token, "id", age=PROFILE_TOKEN_AGE)
                if err == True:
                    raise Forbidden(resp)
                else:
                    id = int(resp)
                err, resp = _get_mail_from_token(token, age=PROFILE_TOKEN_AGE)
                if err == True:
                    raise Forbidden(resp)
                else:
                    email = resp
                    if email is None or id is None:
                        return redirect(url_for("gui_register"))
                    user = _verify_pending_user_throw(id, email)

    else:
        user = api_get_user(usrid)
        if user == None:
            raise NotFound(description=py_user["notfound"])

    if (
        (token is not None or API_EMAIL_VERIFICATION == False)
        or isfrom == True
        or action == ACCOUNT_USER_EDIT
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
        api_email_verification=API_EMAIL_VERIFICATION,
        api_account_validation=API_ACCOUNT_VALIDATION,
        token=token,
        isfrom=isfrom,
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
        try:
            api.reset_user_password(resetreq, no_bot=no_bot, token=token)
            return 0, None
        except ApiException as ae:
            code = ae.status
            if ae.status in (401, 403, 404):
                message = py_user["notauthorized"]
            else:
                # dont give too much infos
                return make_user_response(code, "")


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
    token: str, name: str, age: int = SHORT_TOKEN_AGE, salt: str = None, verifip=False
) -> list:
    if token == None:
        raise Forbidden(py_user["notauthorized"])
    from itsdangerous import (
        TimestampSigner,
        SignatureExpired,
        URLSafeTimedSerializer,
        BadPayload,
        BadSignature,
        BadData,
        BadTimeSignature,
        BadHeader,
    )

    if salt == None:
        salt = app.config["MAILSERVICE_SALT"].encode("UTF-8")
    auths = URLSafeTimedSerializer(
        app.config["MAILSERVICE_SECRET_KEY"],
        salt=salt,
        signer=TimestampSigner,
    )
    description = []
    try:
        max_age = age * 3600
        value = auths.loads(token, max_age=age * 3600)
    except SignatureExpired as e:
        description.append(py_user["signexpired"])
    except (BadSignature, BadHeader, BadData, BadTimeSignature, BadPayload) as e:
        description.append(py_user["badsignature"])
    except:
        description.append(py_user["badsignature"])
    # return None
    if len(description):
        description = set(description)
        return True, ", ".join(description)
    if value.get(name):
        if verifip == False or (value.get("ip") == _public_ip()):
            return False, value.get(name)
    if name == "id":
        return False, str(-1)
    return False, None


def _get_mail_from_token(token: str, verifip=False, age: int = SHORT_TOKEN_AGE) -> str:
    err, email = _get_value_from_token(token, "email", age)
    if email is None:
        flash("Error invalid token", "error")
    return err, email


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

        # if the current_user is not an admin and the email was changed
        if (
            (
                curr_user.email != current_user.email
                and (curr_user.is_admin != True or current_user.is_users_admin != True)
            )
            or curr_user.id <= 0
            or curr_user.status != ApiUserStatus["active"]
        ):
            logout_user()
        # TODO solve problems here
        elif current_user.is_authenticated:
            confirm_login()


def _backend_ip() -> str:
    ip = app.config["BACKEND_URL"].split("//")
    backendip = ip[1].split(":")[0]
    if backendip == "localhost":
        backendip = _public_ip()
    return backendip


def encode_homecaptcha() -> str:
    tokenreq = dict({})
    # tempo to test
    tokenreq["action"] = "REPONSE"
    tokenreq["ip"] = _backend_ip()
    from itsdangerous import TimestampSigner, URLSafeTimedSerializer

    auths = URLSafeTimedSerializer(
        app.config["MAILSERVICE_SECRET_KEY"],
        salt=app.config["MAILSERVICE_SECRET_KEY"],
        signer=TimestampSigner,
    )
    return str(auths.dumps(tokenreq) or "")


# replace googlecaptcha with homemade captcha
def check_homecaptcha(token: str) -> dict:
    from flask import jsonify, make_response

    err, verif_ip = _get_value_from_token(
        token, "ip", age=0.01, salt=app.config["MAILSERVICE_SECRET_KEY"]
    )
    err, verif_response = _get_value_from_token(
        token, "action", salt=app.config["MAILSERVICE_SECRET_KEY"]
    )
    code = 403
    response = dict({"detail": ["Not authorized"]})
    # tempo to test
    if err == False and verif_ip == _public_ip() and verif_response == "REPONSE":
        code = 200
        response = dict({"success": True})
    response = make_response(jsonify(response), code)
    return response
    # format_exception
