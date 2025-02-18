from flask import request, url_for, render_template, redirect, flash
from flask_login import current_user, login_required
from appli import app, gvp
from appli.gui.commontools import is_partial_request
from appli.gui.staticlistes import py_user

NO_STATUS = 10


@app.route("/gui/me")
@login_required
def gui_me():
    return render_template(
        "/v2/me/index.html",
        partial=is_partial_request(request),
    )


@app.route("/gui/me/files", methods=["GET"])
@login_required
def gui_me_files() -> str:
    return render_template("/v2/my_files/list.html")


@app.route("/gui/me/upload", methods=["GET"])
@login_required
async def gui_me_upload() -> dict:

    from appli.gui.files.tools import upload_file

    response, err = await upload_file()

    return {"err": err, "response": response}


@app.route("/gui/me/profile", methods=["GET", "POST"])
@login_required
def gui_me_profile():
    from appli.gui.users.users import user_edit, account_page, ACCOUNT_USER_EDIT

    if not current_user:
        return redirect(url_for("gui_home"))
    if request.method == "POST":
        reponse = user_edit(current_user.api_user.id, isfrom=False)
        if reponse[0] == 0:
            flash(reponse[1], "success")
        else:
            flash(reponse[1], "error")

        if current_user.is_authenticated:
            redir = "gui_me_profile"
        else:
            redir = "gui_login"
        return redirect(url_for(redir))

    return account_page(
        action=ACCOUNT_USER_EDIT,
        usrid=current_user.api_user.id,
        isfrom=False,
        template="v2/me/profile.html",
    )


# ask for account reactivation
@app.route("/gui/me/activate/", defaults={"token": None}, methods=["GET", "POST"])
@app.route("/gui/me/activate/<token>", methods=["GET", "POST"])
def gui_me_activate(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("gui_me_profile"))
    user_id = -1
    from appli.back_config import get_user_constants

    (
        ApiUserStatus,
        ApiUserType,
        API_PASSWORD_REGEXP,
        API_EMAIL_VERIFICATION,
        API_ACCOUNT_VALIDATION,
        SHORT_TOKEN_AGE,
        PROFILE_TOKEN_AGE,
        RECAPTCHAID,
    ) = get_user_constants(request)
    if request.method == "POST":

        from appli.gui.users.users import api_user_activate, get_value_from_token

        partial = is_partial_request(request)

        if token:
            err, user_id = get_value_from_token(token, "id")
            if err == True or user_id is None:
                if partial:
                    response = (
                        1,
                        py_user["profileerror"]["activate"],
                    )
                else:
                    flash(py_user["profileerror"]["activate"], "warning")
                    return redirect(request.referrer)
            else:
                resp = api_user_activate(user_id, NO_STATUS, bot=True, token=token)
                if len(resp) > 3 and resp[0] == 0 and resp[3] == False:
                    if partial:
                        response = (
                            0,
                            py_user["profilesuccess"]["activate"],
                            resp[2],
                            resp[3],
                        )
                    else:
                        flash(py_user["profilesuccess"]["activate"], "success")
                        return redirect(url_for("gui_me"))
                else:
                    response = resp
            return render_template(
                "v2/security/reply.html",
                bg=True,
                type="activate",
                api_email_verification=API_EMAIL_VERIFICATION,
                api_account_validation=API_ACCOUNT_VALIDATION,
                response=response,
                partial=partial,
            )
    if token == "no":
        flash(py_user["profileerror"]["activate"], "warning")
        return redirect(url_for("gui_login"))
    recaptchaid = None
    # google recaptcha or homecaptcha
    if RECAPTCHAID:
        recaptchaid = app.config.get("RECAPTCHAID")
    return render_template(
        "v2/security/activate.html",
        bg=True,
        token=token,
        api_email_verification=API_EMAIL_VERIFICATION,
        api_account_validation=API_ACCOUNT_VALIDATION,
        reCaptchaID=recaptchaid,
        user_id=user_id,
    )


@app.route(
    "/gui/me/forgotten",
    defaults={"token": None},
    methods=["GET", "POST"],
)
@app.route(
    "/gui/me/forgotten/",
    defaults={"token": None},
    methods=["GET", "POST"],
)
@app.route("/gui/me/forgotten/<token>", methods=["GET", "POST"])
def gui_me_forgotten(token: str = ""):
    if current_user.is_authenticated:
        return redirect(url_for("gui_me_profile"))
    from appli.back_config import get_user_constants

    (
        ApiUserStatus,
        ApiUserType,
        API_PASSWORD_REGEXP,
        API_EMAIL_VERIFICATION,
        API_ACCOUNT_VALIDATION,
        SHORT_TOKEN_AGE,
        PROFILE_TOKEN_AGE,
        RECAPTCHAID,
    ) = get_user_constants(request)
    if request.method == "POST":
        partial = True
        email = gvp("request_email")
        pwd = gvp("request_password")
        from appli.gui.users.users import reset_password

        response = reset_password(email, token, pwd)
        return render_template(
            "./v2/security/reply.html",
            bg=True,
            token=token,
            email=email,
            type="forgotten",
            partial=partial,
            response=response,
        )
    recaptchaid = None
    # google recaptcha or homecaptha

    if RECAPTCHAID:
        recaptchaid = app.config.get("RECAPTCHAID")
    return render_template(
        "./v2/security/forgotten.html",
        bg=True,
        token=token,
        reCaptchaID=recaptchaid,
    )
