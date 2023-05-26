import flask
from flask import request, render_template, flash, redirect, url_for

from flask_login import current_user
from flask_security.decorators import roles_accepted
from flask_babel import _
from typing import List
from appli import app, gvg, gvp, constants
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import (
    UsersApi,
    MinUserModel,
    UserModelWithRights,
    ApiException,
)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from appli.gui.commontools import html_to_text

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


def check_is_admin(user: dict) -> bool:
    thisuser: UserModelWithRights = user
    return thisuser and (2 in thisuser.can_do)


def user_create(usrid: int, isfrom: str) -> list:
    if isfrom == IS_FROM_ADMIN and (not check_is_admin(current_user.api_user)):
        return [None, "Error not admin"]
    # elif current_user.is_anonymous == False and isfrom != IS_FROM_ADMIN:
    #    return [None,"Error connectedunot user account "]
    return user_account(-1, isfrom, action=ACCOUNT_USER_CREATE)


def user_edit(usrid: int, isfrom: str) -> list:
    if isfrom == IS_FROM_ADMIN and (not check_is_admin(current_user.api_user)):
        return [None, "Error not admin "]

    elif usrid != current_user.api_user.id and isfrom != IS_FROM_ADMIN:
        return [None, "Error cannot modifiy user account "]
    return user_account(usrid, isfrom, action=ACCOUNT_USER_EDIT)


def user_account(usrid: int, isfrom: str, action: str = None) -> list:
    if action != None:
        if isinstance(usrid, int) == False:
            return [None, "error"]
    if isfrom == IS_FROM_ADMIN:
        fields = [
            "name",
            "email",
            "organisation",
            "country",
            "usercreationreason",
            "newpassword",
        ]

    else:
        fields = [
            "email",
            "organisation",
            "country",
            "usercreationreason",
            "newpassword",
        ]

    if action == "create":
        fields = ["firstname", "lastname", "password"] + fields
    else:
        fields = ["name"] + fields
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

        del posted["newpassword"]
    if isfrom == IS_FROM_ADMIN:
        posted["active"] = gvp("active", False)
    else:
        try:
            app.config.get("APP_VALIDATE_ACCOUNT")
            if action == ACCOUNT_USER_EDIT:
                currentemail = gvp("currentemail").strip()
                if posted["email"] != currentemail:
                    posted["active"] = False
            else:
                posted["active"] = False
        except:
            pass

    if action == ACCOUNT_USER_EDIT and usrid != -1:
        try:
            with ApiClient(UsersApi, request) as api:
                ret = api.update_user(user_id=usrid, user_model_with_rights=posted)
                return [ret, None]

        except ApiException as ae:
            return [None, str(ae)]
    elif action == ACCOUNT_USER_CREATE and usrid == -1:
        try:
            no_bot = _get_captcha()
            posted["id"] = -1
            posted["usercreationdate"] = None
            new_user = UserModelWithRights(**posted)
            with ApiClient(UsersApi, request) as api:
                ret = api.create_user(user_model_with_rights=new_user, no_bot=no_bot)
            response = [posted, None]
        except ApiException as ae:
            return [None, str(ae)]
    else:
        return [None, "error params"]
    if isfrom != IS_FROM_ADMIN and posted["active"] == False:

        del posted["password"]
        err = account_validate(usrid, posted)
        if err == None:
            flash("Error while creating your account ... contact us ", "error")
            return ["gui_login", None]
        else:
            flash("Your account is created. Validation process ...", "info")
            return ["gui_login", None]
    else:
        flash("Your account is created", "success")
        return ["gui_login", None]


def account_page(
    action: str, usrid: int, isfrom: str, template: str, token: str = None
) -> str:
    reCaptchaID = None
    if action != ACCOUNT_USER_CREATE and not isinstance(usrid, int):
        return render_template("v2/error.html", error=404)

    try:
        if current_user.is_authenticated == True and usrid == current_user.api_user.id:
            user = current_user

        elif action == ACCOUNT_USER_CREATE:
            user = None

            if isfrom != IS_FROM_ADMIN:
                auth_email = False
                reCaptchaID = app.config.get("RECAPTCHAID")
                if token:
                    auth_email = get_mail_from_token(token)
                if auth_email == False:
                    return render_template("v2/error.html", error=403)
                else:
                    user = dict({"id": -1, "email": auth_email})

        with ApiClient(UsersApi, request) as api:

            if isinstance(usrid, int) and usrid > 0:
                if isfrom != IS_FROM_ADMIN:
                    user = api.show_current_user()
                else:
                    user = api.get_users(ids=str(usrid))
                    if len(user):
                        user = user[0]
                    else:
                        return render_template("v2/error.html", error=404)
            organisations = api.search_organizations(name="%%")
            organisations.sort()
    except ApiException as ae:
        errs = ae.body
        return render_template("v2/error.html", error=404)

    roles = [(str(num), lbl) for num, lbl in constants.API_GLOBAL_ROLES.items()]
    from appli.gui.users.staticlistes import country_list

    countries = sorted([country for k, country in country_list.items()])
    # for countries i18N
    # countries = sorted(country_list.items(), key=lambda x: x[1])

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


def reset_password(email: str, token: str, pwd: str) -> str:
    err = None
    if get_mail_from_token(token, True) != False and pwd != None:
        no_bot = _get_captcha()
        try:
            with ApiClient(UsersApi, request) as api:
                ret = api.reset_user_password(
                    resetpassword=pwd,
                    no_bot=no_bot,
                )
                return ["gui_login", None]

        except ApiException as ae:
            err = str(ae)
    else:
        err = True

    return ["gui_forgotten", err]


def _public_ip() -> str:
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        return request.environ["REMOTE_ADDR"]
    else:
        return request.environ["HTTP_X_FORWARDED_FOR"]


def _generate_mail_token(email: str, action: str = "accountrequest") -> str:
    from itsdangerous import URLSafeTimedSerializer

    auths = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="accountrequest")
    # token = build_serializer().dumps({"email": email, "action": "accountrequest"}) // for _back
    token = auths.dumps(
        {
            "email": email,
            "action": action,
            "ip": _public_ip(),
            "instance": app.config.get("APP_INSTANCE_ID"),
        }
    )
    return token


def get_mail_from_token(token: str, verifip=False) -> str:
    from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

    auths = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="accountrequest")
    try:
        email = auths.loads(token, max_age=24 * 3600)
    except (BadSignature, SignatureExpired):
        flash("error bad signature - token for creation has expired", "error")
        return False

    if email.get("email") and email.get("action"):
        if verifip == False or (email.get("ip") == _public_ip()):
            return email.get("email")
    else:
        flash("error invalid token", "error")
        return False


def api_reset_password_message(email: str) -> MIMEMultipart:
    url = "gui_forgotten"
    token = _generate_mail_token(email, "resetpassword")
    recipients = [email]
    msg = MIMEMultipart()
    msg["Subject"] = "EcoTaxa reset password"

    msg["To"] = ", ".join(recipients)
    msg["ReplyTo"] = app.config.get("APP_NOREPLY")
    html = render_template(
        "v2/mail/_mail_reset_password.html",
        email=app.config.get("APP_EMAIL_ASSISTANCE"),
        link=("{0}/{1}/{2}").format(
            request.url_root + "/" + url_for(url),
            app.config.get("APP_INSTANCE_ID"),
            token,
        ),
    )
    text = MIMEText(
        html_to_text(html),
        "plain",
    )
    html = MIMEText(html, "html")
    msg.attach(text)
    msg.attach(html)
    return msg


def reset_password_message(email: str) -> MIMEMultipart:
    url = "gui_forgotten"
    token = _generate_mail_token(email, "resetpassword")
    recipients = [email]
    msg = MIMEMultipart()
    msg["Subject"] = "EcoTaxa reset password"

    msg["To"] = ", ".join(recipients)
    msg["ReplyTo"] = app.config.get("APP_NOREPLY")
    html = render_template(
        "v2/mail/_mail_reset_password.html",
        email=app.config.get("APP_EMAIL_ASSISTANCE"),
        link=("{0}/{1}/{2}").format(
            request.url_root + "/" + url_for(url),
            app.config.get("APP_INSTANCE_ID"),
            token,
        ),
    )
    text = MIMEText(
        html_to_text(html),
        "plain",
    )
    html = MIMEText(html, "html")
    msg.attach(text)
    msg.attach(html)
    return msg


def api_account_validate(usrid: int, account: dict = None) -> dict:
    url = "gui_users_list_page"
    subject = "EcoTaxa account creation"
    replyto = account["email"]
    html = render_template(
        "v2/mail/_mail_account_validation.html",
        account=account,
        usrid=usrid,
        link=("{0}").format(request.url_root + url_for(url)),
    )
    text = html_to_text(html)
    payload = dict(
        {
            "accountreq": None,
            "msg": dict(
                {
                    "subject": subject,
                    "html": html,
                    "text": text,
                    "replyto": account["email"],
                }
            ),
            "tokenStr": None,
        }
    )
    return call_api_direct(payload, "/account/validate")


def call_api_direct(payload: dict, entrypoint: str):
    import requests
    import json

    with ApiClient(UsersApi, request) as apiaccount:
        url = (
            apiaccount.api_client.configuration.host + entrypoint
        )  # endpoint is nowhere available as a const :(
        r = requests.post(url, params=payload, data=json.dumps(payload))

        if r.status_code == 200:
            return r
        else:
            return r


def account_validate(usrid: int, account: dict = None) -> MIMEMultipart:
    url = "gui_users_list_page"
    recipients = [app.config.get("APP_VALIDATE_ACCOUNT")]
    msg = MIMEMultipart()
    msg["Subject"] = "EcoTaxa account creation"

    msg["To"] = ", ".join(recipients)
    msg["ReplyTo"] = account["email"]
    html = render_template(
        "v2/mail/_mail_account_validation.html",
        account=account,
        usrid=usrid,
        link=("{0}").format(request.url_root + url_for(url)),
    )
    text = MIMEText(
        html_to_text(html),
        "plain",
    )
    html = MIMEText(html, "html")
    msg.attach(text)
    msg.attach(html)
    err = send_mail(app.config.get("APP_VALIDATE_ACCOUNT"), msg, account["email"])
    return err


def api_toback_account_verify(email: str) -> dict:
    url = "gui_register"
    subject = "EcoTaxa email validation"
    tokenStr = app.config.get("VERIFY_TOKENSTR")
    html = render_template(
        "v2/mail/_mail_validate.html",
        email=app.config.get("APP_EMAIL_ASSISTANCE"),
        link=("{0}/{1}/{2}").format(
            request.url_root + url_for(url),
            app.config.get("APP_INSTANCE_ID"),
            tokenStr,
        ),
    )
    accountreq = dict(
        {"recipient": email, "ip": _public_ip(), "action": "accountrequest"}
    )
    text = html_to_text(html)
    with ApiClient(AccountManagerService, request) as api:
        ret = api.account_verify(
            accountreq,
            dict({"subject": subject, "html": html, "text": text, "replyto": None}),
            tokenStr,
        )
    return ret


def api_account_verify(email: str) -> dict:
    url = "gui_register"
    subject = "EcoTaxa email validation"
    tokenStr = app.config.get("VERIFY_TOKENSTR")
    html = render_template(
        "v2/mail/_mail_validate.html",
        email=app.config.get("APP_EMAIL_ASSISTANCE"),
        link=("{0}/{1}").format(
            request.url_root + url_for(url),
            tokenStr,
        ),
    )
    accountreq = dict(
        {"recipient": email, "ip": _public_ip(), "action": "accountrequest"}
    )
    text = html_to_text(html)
    payload = dict(
        {
            "accountreq": accountreq,
            "msg": dict(
                {
                    "subject": subject,
                    "html": html,
                    "text": text,
                    "replyto": None,
                }
            ),
            "tokenStr": tokenStr,
        }
    )
    res = call_api_direct(payload, "/account/verify")
    return res


def account_verify(email: str) -> MIMEMultipart:
    url = "gui_register"
    recipients = [email]
    msg = MIMEMultipart()
    msg["Subject"] = "EcoTaxa email validation"

    msg["To"] = ", ".join(recipients)
    msg["ReplyTo"] = app.config.get("APP_NOREPLY")
    token = _generate_mail_token(email)

    html = render_template(
        "v2/mail/_mail_validate.html",
        email=app.config.get("APP_EMAIL_ASSISTANCE"),
        link=("{0}/{1}").format(
            request.url_root + url_for(url),
            token,
        ),
    )
    text = MIMEText(
        html_to_text(html),
        "plain",
    )
    html = MIMEText(html, "html")
    msg.attach(text)
    msg.attach(html)
    return send_mail(email, msg)


def send_mail(email: str, msg: MIMEMultipart, replyto: str = None) -> dict:
    import smtplib, ssl

    # starttls and 587  - avec ssl 465
    sender_email = app.config.get("SENDER_EMAIL")
    pwd = app.config.get("SENDER_PWD")
    msg["From"] = sender_email
    recipients = [email]
    if replyto != None:
        msg["Reply-To"] = replyto
    context = ssl.create_default_context()
    mailhost = app.config.get("APP_MAIL_HOST")
    with smtplib.SMTP_SSL(mailhost, 465, context=context) as smtp:
        # server = smtplib.SMTP("ssl0.ovh.net:587")
        # server.ehlo()
        # server.starttls()
        smtp.login(sender_email, pwd)
        res = smtp.sendmail(sender_email, recipients, msg.as_string())
        smtp.quit()
        if res == {}:
            return None
        else:
            return res
