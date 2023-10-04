import flask
from flask import request, url_for, render_template, redirect, flash
from flask_login import current_user, login_required, fresh_login_required
from appli import app, gvp, gvg
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
@app.route("/gui/me/files/", methods=["GET"])
@login_required
def gui_me_files(subdir: str = "") -> str:
    return render_template("/v2/my_files/list.html")


@app.route("/gui/me/upload", methods=["GET"])
@login_required
async def gui_me_upload(subdir: str = "") -> str:

    from appli.gui.files.tools import upload_file

    response, err = await upload_file(subdir, request)

    return {"err": err, "response": response}


@app.route("/gui/me/profile", methods=["GET", "POST"])
@login_required
def gui_me_profile() -> str:
    from appli.gui.users.commontools import user_edit, account_page, ACCOUNT_USER_EDIT

    if not current_user:
        return redirect(url_for("gui_home"))
    if request.method == "POST":
        reponse = user_edit(current_user.api_user.id, isfrom=None)
        if reponse[0] == 0:
            flash(reponse[1], "success")
        else:
            flash(reponse[1], "error")

        if current_user.is_authenticated:
            redir = "gui_me_profile"
        else:
            return redirect(url_for("gui_login"))

    return account_page(
        action=ACCOUNT_USER_EDIT,
        usrid=current_user.api_user.id,
        isfrom=None,
        template="v2/me/profile.html",
    )


# ask for account reactivation
@app.route("/gui/me/activate/<token>", methods=["GET", "POST"])
def gui_me_activate(token: str) -> str:
    if current_user.is_authenticated:
        return redirect(url_for("gui_me_profile"))
    user_id = -1
    if request.method == "POST":
        from appli.gui.users.commontools import api_user_activate, _get_value_from_token

        partial = is_partial_request(request)
        if token:
            user_id = _get_value_from_token(token, "id")
            if user_id == None:
                if partial:
                    response = response = (
                        1,
                        py_user["profileerror"]["activate"],
                    )
                else:
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
                response=response,
                partial=partial,
            )
    return render_template(
        "v2/security/activate.html",
        bg=True,
        token=token,
        reCaptchaID=app.config.get("RECAPTCHAID"),
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
def gui_me_forgotten(token: str = None) -> str:
    if current_user.is_authenticated:
        return redirect(url_for("gui_me_profile"))
    if request.method == "POST":
        partial = True
        email = gvp("request_email", None)
        pwd = gvp("request_password", None)
        from appli.gui.users.commontools import reset_password

        response = reset_password(email, token, pwd, url="gui_me_forgotten")
        return render_template(
            "./v2/security/reply.html",
            bg=True,
            token=token,
            email=email,
            type="forgotten",
            partial=partial,
            response=response,
        )

    return render_template(
        "./v2/security/forgotten.html",
        bg=True,
        token=token,
        reCaptchaID=app.config.get("RECAPTCHAID"),
    )
