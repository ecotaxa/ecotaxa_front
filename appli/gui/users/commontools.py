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
            constants.APP_EMAIL_VALIDATE_ACCOUNT
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
        no_bot = None
        reCaptchaID = app.config.get("RECAPTCHAID")
        if reCaptchaID:
            response = gvp("g-recaptcha-response")
            remoteip = request.remote_addr
            no_bot = [remoteip, response]
        try:
            with ApiClient(UsersApi, request) as api:
                ret = api.create_user(user_model_with_rights=posted)
            response = [posted, None]
        except ApiException as ae:
            return [None, str(ae)]
    else:
        return [None, "error params"]
    if isfrom != IS_FROM_ADMIN and posted["active"] == False:

        del posted["password"]
        msg = account_verify_message(usrid, posted)

        if msg == None:
            flash("Error while creating your account ... contact us ", "error")
            return ["gui_login", None]
        else:
            err = send_mail(constants.APP_EMAIL_VALIDATE_ACCOUNT, msg)
            flash("Your account is created. validation process ...", "info")
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
                    auth_email = _get_mail_from_token(token)
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


def _generate_mail_token(email: str) -> str:
    from itsdangerous import URLSafeTimedSerializer

    auths = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="accountrequest")
    # token = build_serializer().dumps({"email": email, "action": "accountrequest"}) // for _back
    token = auths.dumps({"email": email, "action": "accountrequest"})
    return token


def _get_mail_from_token(token: str) -> str:
    from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

    auths = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="accountrequest")
    try:
        # email = build_serializer().loads(token,max_age =24*3600) // for _back
        email = auths.loads(token, max_age=24 * 3600)
    except (BadSignature, SignatureExpired):
        flash("error bad signature - token for creation has expired", "error")
        return False

    if email.get("email") and email.get("action"):
        return email.get("email")
    else:
        flash("error no email", "error")
        return False


def account_verify_message(usrid: int, account: dict = None) -> MIMEMultipart:
    ecotaxainstance = "instanceid1"
    url = "gui_userlist"
    assistemail = "assistance@ecotaxa.org"
    recipients = [constants.APP_EMAIL_VALIDATE_ACCOUNT]
    msg = MIMEMultipart()
    msg["Subject"] = "EcoTaxa account creation"

    msg["To"] = ", ".join(recipients)
    msg["ReplyTo"] = account["email"]
    html = render_template(
        "v2/mail/_mail_account_validation.html",
        account=account,
        usrid=usrid,
        link=("{0}").format(request.url_root + "/" + url_for(url)),
    )
    text = MIMEText(
        html_to_text(html),
        "plain",
    )
    html = MIMEText(html, "html")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(text)
    msg.attach(html)
    return msg


def validation_message(email: str) -> MIMEMultipart:
    ecotaxainstance = "instanceid1"
    url = "gui_register"
    assistemail = "assistance@ecotaxa.org"
    recipients = [email]
    msg = MIMEMultipart()
    msg["Subject"] = "EcoTaxa email validation"

    msg["To"] = ", ".join(recipients)
    msg["ReplyTo"] = "no.reply@ecotaxa.org"
    token = _generate_mail_token(email)
    html = render_template(
        "v2/mail/_mail_validate.html",
        email=assistemail,
        link=("{0}/{1}/{2}").format(
            request.url_root + "/" + url_for(url), ecotaxainstance, token
        ),
    )
    text = MIMEText(
        html_to_text(html),
        "plain",
    )
    html = MIMEText(html, "html")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(text)
    msg.attach(html)
    return msg


def send_mail(email: str, msg: MIMEMultipart) -> dict:
    import smtplib, ssl

    # starttls and 587  - avec ssl 465
    from appli.gui.admin.datamail import SENDER_EMAIL, SENDER_PWD

    sender_email = SENDER_EMAIL
    pwd = SENDER_PWD
    msg["From"] = sender_email
    recipients = [email]
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("ssl0.ovh.net", 465, context=context) as smtp:
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
